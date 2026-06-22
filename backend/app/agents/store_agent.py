"""Store Agent — monitors store shelf levels and triggers restock requests."""

import logging
from typing import Dict, Any, List
from sqlalchemy import select

from app.config import get_settings
from app.agents.state import SupplyChainState
from app.models import Inventory, Product, Store

logger = logging.getLogger("omniflow.agents")
settings = get_settings()

class StoreAgent:
    """Agent representing individual retail store inventory monitors."""

    async def run(self, state: SupplyChainState) -> Dict[str, Any]:
        """Scan store inventory levels and publish reorder demands."""
        logger.info("🤖 [Store Agent] Running store shelf scans...")
        
        sim_context = state.get("simulation_context")
        restock_requests = []
        alerts = []
        decisions = []

        # Simulated or actual scan: find stores with low stock levels
        # If we have db_session in a real execution, we'd query, but since this runs inside a graph node,
        # we can retrieve from simulation context or make realistic requests
        if sim_context:
            scenario = sim_context.get("scenario_type")
            if scenario == "demand_spike" or scenario == "viral_trend":
                # Create restocking request simulation
                restock_requests.append({
                    "store_code": "NYC-001",
                    "product_sku": "ELEC-001",
                    "current_qty": 15,
                    "target_qty": 300,
                    "urgency": "high"
                })
                alerts.append({
                    "agent": "store_agent",
                    "type": "stockout_risk",
                    "severity": "critical",
                    "title": "Low Stock Alert (NYC-001)",
                    "description": "Stock of ELEC-001 (Headphones) is projected to run out in 1.5 days under spike.",
                    "confidence": 0.91
                })
                decisions.append({
                    "agent": "store_agent",
                    "action": "trigger_restock",
                    "reasoning": "Spike in Electronics category creates critical supply deficits in Northeast region stores.",
                    "confidence": 0.92
                })
        else:
            # Standard monitoring mock action
            decisions.append({
                "agent": "store_agent",
                "action": "monitor_only",
                "reasoning": "Shelf inventory levels checked. No critical shortages requiring human intervention.",
                "confidence": 0.89
            })

        message_content = f"Store Agent: Inspected shelf stock levels. Triggered {len(restock_requests)} restock request(s)."
        
        if settings.llm_mode == "openai" and settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import HumanMessage
                
                llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model)
                prompt = (
                    f"You are the Store Agent for a retail supply chain. "
                    f"Summarize the restock status of your store shelves in 2 sentences. "
                    f"Simulation context: {sim_context}."
                )
                res = await llm.ainvoke([HumanMessage(content=prompt)])
                message_content = f"Store Agent: {res.content}"
            except Exception as e:
                logger.warning(f"Failed to run OpenAI Chat for StoreAgent: {e}")

        return {
            "restock_requests": restock_requests,
            "alerts": alerts,
            "agent_decisions": decisions,
            "current_agent": "store_agent",
            "messages": [{"role": "assistant", "content": message_content, "agent": "store_agent"}]
        }

store_agent = StoreAgent()
