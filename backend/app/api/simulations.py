"""Simulations API — trigger and view supply chain simulations."""

import uuid
import time
import random
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.simulation import Simulation
from app.models.agent_event import AgentEvent
from app.schemas.simulation import SimulationRequest, SimulationResponse

router = APIRouter(prefix="/simulations", tags=["Simulations"])

# ── Scenario Templates ──────────────────────────────────────────────────
SCENARIO_TEMPLATES = {
    "demand_spike": {
        "title": "Demand Spike Simulation",
        "description": "Simulates a sudden 3-5x increase in demand for a product category, testing the system's ability to respond with emergency restocking.",
    },
    "supplier_strike": {
        "title": "Supplier Strike Simulation",
        "description": "Simulates a key supplier going offline, disrupting the supply chain and requiring alternative sourcing.",
    },
    "warehouse_shutdown": {
        "title": "Warehouse Shutdown Simulation",
        "description": "Simulates a warehouse losing capacity due to equipment failure or emergency, requiring inventory redistribution.",
    },
    "weather_disaster": {
        "title": "Weather Disaster Simulation",
        "description": "Simulates a severe weather event disrupting regional delivery routes and store operations.",
    },
    "viral_trend": {
        "title": "Viral Product Trend Simulation",
        "description": "Simulates a product going viral on social media, creating unexpected demand surges.",
    },
}


def _generate_simulation_results(scenario_type: str, params: dict) -> dict:
    """Generate realistic simulation results (mock for hackathon demo)."""
    magnitude = params.get("magnitude", 3.0)
    duration = params.get("duration_days", 7)
    products_affected = random.randint(5, 20)
    stores_affected = random.randint(2, 8)
    stockouts = random.randint(1, min(products_affected, 5))
    units_impact = -random.randint(200, 2000) * int(magnitude)

    inventory_impact = {
        "products_affected": products_affected,
        "stores_affected": stores_affected,
        "stockouts_predicted": stockouts,
        "total_units_impact": units_impact,
        "most_affected_categories": random.sample(
            ["Electronics", "Groceries", "Apparel", "Home", "Sports"], k=min(3, 5)
        ),
        "recovery_time_days": random.randint(3, 14),
    }

    financial_impact = {
        "lost_revenue": round(random.uniform(5000, 50000) * magnitude, 2),
        "additional_costs": round(random.uniform(2000, 15000), 2),
        "emergency_shipping": round(random.uniform(1000, 8000), 2),
        "total_impact": 0,
    }
    financial_impact["total_impact"] = round(
        -(financial_impact["lost_revenue"] + financial_impact["additional_costs"] + financial_impact["emergency_shipping"]),
        2,
    )

    agent_actions = [
        {
            "agent": "demand_forecast",
            "action": "spike_alert",
            "target": f"{products_affected} products",
            "reasoning": f"Detected {magnitude}x demand anomaly based on scenario parameters. Historical pattern analysis suggests a {duration}-day impact window.",
            "confidence": round(random.uniform(0.78, 0.95), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        {
            "agent": "store_agent",
            "action": "emergency_restock_request",
            "target": f"{stores_affected} stores",
            "reasoning": f"Stock levels projected to drop below safety threshold within 48 hours for {stockouts} products.",
            "confidence": round(random.uniform(0.82, 0.96), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        {
            "agent": "warehouse_agent",
            "action": "inventory_reallocation",
            "target": "Cross-warehouse transfer",
            "reasoning": f"Reallocating {abs(units_impact)} units from surplus warehouses to cover projected shortfall.",
            "confidence": round(random.uniform(0.75, 0.92), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
        {
            "agent": "orchestrator",
            "action": "coordination",
            "target": "All agents",
            "reasoning": f"Coordinated response across 3 agents. Prioritized {stores_affected} stores by revenue contribution and stockout severity.",
            "confidence": round(random.uniform(0.85, 0.98), 2),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    ]

    return {
        "inventory_impact": inventory_impact,
        "financial_impact": financial_impact,
        "agent_actions": agent_actions,
        "carbon_impact": round(random.uniform(50, 500), 1),
    }


@router.get("", response_model=list[SimulationResponse])
async def list_simulations(db: Annotated[AsyncSession, Depends(get_db)]):
    """List all simulations."""
    result = await db.execute(select(Simulation).order_by(desc(Simulation.created_at)).limit(20))
    return result.scalars().all()


@router.get("/scenarios")
async def list_scenarios():
    """List available simulation scenarios."""
    return [
        {"type": k, "title": v["title"], "description": v["description"]}
        for k, v in SCENARIO_TEMPLATES.items()
    ]


from app.services.simulation_service import simulation_service

@router.post("", response_model=SimulationResponse, status_code=201)
async def run_simulation(
    data: SimulationRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Run a supply chain simulation."""
    if data.scenario_type not in SCENARIO_TEMPLATES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid scenario. Choose from: {list(SCENARIO_TEMPLATES.keys())}",
        )

    template = SCENARIO_TEMPLATES[data.scenario_type]
    start_time = time.time()

    # Generate results via the digital twin simulation service
    results = await simulation_service.run_scenario(db, data.scenario_type, data.parameters)

    sim = Simulation(
        id=str(uuid.uuid4()),
        scenario_type=data.scenario_type,
        title=template["title"],
        description=template["description"],
        parameters=data.parameters,
        status="completed",
        inventory_impact=results["inventory_impact"],
        financial_impact=results["financial_impact"],
        agent_actions=results["agent_actions"],
        carbon_impact=results["carbon_impact"],
        duration_seconds=round(time.time() - start_time, 2),
        completed_at=datetime.now(timezone.utc),
    )
    db.add(sim)

    # Log agent events for this simulation
    for action in results["agent_actions"]:
        db.add(AgentEvent(
            id=str(uuid.uuid4()),
            agent_name=action["agent"],
            event_type="simulation_response",
            severity="warning",
            title=f"[SIM] {action['action']}: {action['target']}",
            reasoning=action["reasoning"],
            confidence_score=action["confidence"],
            payload={"simulation_id": sim.id, "scenario": data.scenario_type},
            simulation_id=sim.id,
        ))

    await db.flush()
    return sim



@router.get("/{simulation_id}", response_model=SimulationResponse)
async def get_simulation(simulation_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """Get a single simulation result."""
    result = await db.execute(select(Simulation).where(Simulation.id == simulation_id))
    sim = result.scalar_one_or_none()
    if not sim:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return sim
