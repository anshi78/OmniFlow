"""Warehouse Agent — allocates warehouse stock and coordinates fulfillment shipments."""

import logging
from typing import Dict, Any, List

from app.config import get_settings
from app.agents.state import SupplyChainState

logger = logging.getLogger("omniflow.agents")
settings = get_settings()

class WarehouseAgent:
    """Agent representing distribution warehouses coordinating inventory supply."""

    async def run(self, state: SupplyChainState) -> Dict[str, Any]:
        """Fulfill restock requests and allocate stock."""
        logger.info("🤖 [Warehouse Agent] Checking distribution inventory allocations...")
        
        sim_context = state.get("simulation_context")
        restock_requests = state.get("restock_requests", [])
        decisions = []
        alerts = []
        
        # Analyze and satisfy restock requests
        for req in restock_requests:
            store = req.get("store_code", "NYC-001")
            sku = req.get("product_sku", "ELEC-001")
            qty = req.get("target_qty", 100)
            
            # Simple routing logic: Route to closest warehouse (WH-EAST for NYC, WH-WEST for LA, etc.)
            allocated_wh = "WH-EAST"
            if "LA" in store or "SEA" in store:
                allocated_wh = "WH-WEST"
            elif "CHI" in store or "DEN" in store:
                allocated_wh = "WH-NORTH"
            
            decisions.append({
                "agent": "warehouse_agent",
                "action": "allocate_inventory",
                "target": f"Ship {qty} units of {sku} from {allocated_wh} to {store}",
                "reasoning": f"Sufficient buffer stock exists in {allocated_wh} to cover store reorder request. Distance minimized.",
                "confidence": 0.90
            })

        # Scenario specific perturbations
        if sim_context:
            scenario = sim_context.get("scenario_type")
            if scenario == "warehouse_shutdown":
                alerts.append({
                    "agent": "warehouse_agent",
                    "type": "shutdown_disruption",
                    "severity": "critical",
                    "title": "East Coast Center Offline",
                    "description": "WH-EAST has experienced an emergency system breakdown. Rerouting all Northeast logistics to Great Lakes.",
                    "confidence": 0.95
                })
                decisions.append({
                    "agent": "warehouse_agent",
                    "action": "reroute_logistics",
                    "reasoning": "Rerouting NYC-001 and BOS-001 shipments through Great Lakes Center (WH-NORTH) to prevent warehouse backlog.",
                    "confidence": 0.95
                })

        message_content = f"Warehouse Agent: Assessed reorder requests. Allocated stock for {len(restock_requests)} orders."
        
        if settings.llm_mode == "openai" and settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import HumanMessage
                
                llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model)
                prompt = (
                    f"You are the Warehouse Agent for a retail supply chain. "
                    f"Briefly describe how you will fulfill restock requests under simulation condition: {sim_context} in 2 sentences."
                )
                res = await llm.ainvoke([HumanMessage(content=prompt)])
                message_content = f"Warehouse Agent: {res.content}"
            except Exception as e:
                logger.warning(f"Failed to run OpenAI Chat for WarehouseAgent: {e}")

        return {
            "alerts": alerts,
            "agent_decisions": decisions,
            "current_agent": "warehouse_agent",
            "messages": [{"role": "assistant", "content": message_content, "agent": "warehouse_agent"}]
        }

warehouse_agent = WarehouseAgent()
