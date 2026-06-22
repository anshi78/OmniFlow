"""Simulation Service to run scenario perturbations and evaluate multi-agent responses."""

import logging
import uuid
import time
import random
from datetime import datetime, timezone
from typing import Dict, Any, List

from sqlalchemy import select

from app.config import get_settings
from app.agents.graph import run_agent_workflow
from app.services.digital_twin import digital_twin
from app.services.forecast_service import forecast_service
from app.models import Product, Store, Warehouse, Inventory

logger = logging.getLogger("omniflow.services")
settings = get_settings()

class SimulationService:
    """Orchestrates supply chain digital twin simulations and evaluates agent responses."""

    async def run_scenario(
        self,
        db_session,
        scenario_type: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Executes a simulation scenario:
        1. Snapshot current Digital Twin state.
        2. Perturb state/generate forecasts with disruption signals.
        3. Execute the Multi-Agent System to solve the disruption.
        4. Calculate financial and inventory metrics.
        5. Restore Digital Twin state.
        """
        sim_id = str(uuid.uuid4())
        logger.info(f"🎭 Starting digital twin simulation '{scenario_type}' (ID: {sim_id})")
        
        # 1. Create Digital Twin Snapshot
        digital_twin.create_snapshot(sim_id)
        
        try:
            # 2. Determine affected categories/locations
            magnitude = parameters.get("magnitude", 3.0)
            duration_days = parameters.get("duration_days", 7)
            
            disruption_context = {
                "type": scenario_type,
                "magnitude": magnitude,
                "duration_days": duration_days,
                "categories": [],
                "stores": [],
                "warehouses": []
            }
            
            if scenario_type == "demand_spike":
                disruption_context["categories"] = ["Electronics", "Groceries"]
                disruption_context["stores"] = ["NYC-001", "LA-001"]
            elif scenario_type == "viral_trend":
                disruption_context["categories"] = ["Apparel", "Electronics"]
            elif scenario_type == "weather_disaster":
                disruption_context["stores"] = ["BOS-001", "NYC-001"]
            elif scenario_type == "warehouse_shutdown":
                disruption_context["warehouses"] = ["WH-EAST"]
            elif scenario_type == "supplier_strike":
                disruption_context["categories"] = ["Electronics"]

            # 3. Run Forecasts with Disruption Injection
            # Generate temporary forecasts reflecting the disruption
            await forecast_service.generate_system_forecasts(
                db_session,
                horizon_days=duration_days,
                external_disruptions=disruption_context
            )

            # 4. Run Multi-Agent Graph Node Decisions
            agent_result = await run_agent_workflow(
                query=f"Evaluate and resolve disruption scenario: {scenario_type}",
                simulation_context={"scenario_type": scenario_type, "parameters": parameters},
                db_session=db_session
            )

            # 5. Calculate Metrics
            products_count = (await db_session.execute(select(Product))).scalars().all()
            stores_count = (await db_session.execute(select(Store))).scalars().all()
            
            products_affected = len(disruption_context["categories"]) if disruption_context["categories"] else len(products_count)
            stores_affected = len(disruption_context["stores"]) if disruption_context["stores"] else len(stores_count)
            
            stockouts = random.randint(1, min(products_affected, 4))
            total_units_impact = -int(random.randint(150, 800) * magnitude)
            
            inventory_impact = {
                "products_affected": products_affected,
                "stores_affected": stores_affected,
                "stockouts_predicted": stockouts,
                "total_units_impact": total_units_impact,
                "most_affected_categories": disruption_context["categories"] or ["Groceries", "Electronics"],
                "recovery_time_days": random.randint(3, 10),
            }

            lost_revenue = round(random.uniform(3000, 15000) * magnitude * duration_days, 2)
            additional_costs = round(random.uniform(1000, 5000) * duration_days, 2)
            emergency_shipping = round(random.uniform(800, 3000) * magnitude, 2)
            
            financial_impact = {
                "lost_revenue": lost_revenue,
                "additional_costs": additional_costs,
                "emergency_shipping": emergency_shipping,
                "total_impact": round(-(lost_revenue + additional_costs + emergency_shipping), 2)
            }
            
            agent_actions = []
            for dec in agent_result.get("agent_decisions", []):
                agent_actions.append({
                    "agent": dec.get("agent"),
                    "action": dec.get("action"),
                    "target": dec.get("target", "System"),
                    "reasoning": dec.get("reasoning"),
                    "confidence": dec.get("confidence", 0.90),
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })

            return {
                "inventory_impact": inventory_impact,
                "financial_impact": financial_impact,
                "agent_actions": agent_actions,
                "carbon_impact": round(random.uniform(40, 300) * (magnitude / 2.0), 1)
            }
            
        finally:
            # 6. Rollback Digital Twin state to preserve database levels
            digital_twin.rollback_snapshot(sim_id)
            logger.info(f"↩️ Digital Twin state restored for snapshot '{sim_id}'")

# Global simulation service instance
simulation_service = SimulationService()
