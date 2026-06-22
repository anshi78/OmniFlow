"""Supplier Agent — monitors supplier capacities, delays, and purchase orders."""

import logging
from typing import Dict, Any

from app.config import get_settings
from app.agents.state import SupplyChainState

logger = logging.getLogger("omniflow.agents")
settings = get_settings()

class SupplierAgent:
    """Agent overseeing vendor status and component deliveries."""

    async def run(self, state: SupplyChainState) -> Dict[str, Any]:
        logger.info("🤖 [Supplier Agent] Checking supplier health status...")
        
        sim_context = state.get("simulation_context")
        decisions = []
        alerts = []
        
        if sim_context:
            scenario = sim_context.get("scenario_type")
            if scenario == "supplier_strike":
                alerts.append({
                    "agent": "supplier_agent",
                    "type": "supplier_risk",
                    "severity": "critical",
                    "title": "Vendor Strike (ElectroCorp)",
                    "description": "Supplier ElectroCorp went offline. Lead time increased by 14 days.",
                    "confidence": 0.98
                })
                decisions.append({
                    "agent": "supplier_agent",
                    "action": "source_alternative",
                    "reasoning": "ElectroCorp accounts for 60% of Elec items. Rerouting purchase orders to back-up vendor AlliedGroup.",
                    "confidence": 0.96
                })
        
        message_content = "Supplier Agent: Checked lead times. All suppliers operating in green bounds."
        
        if settings.llm_mode == "openai" and settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import HumanMessage
                
                llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model)
                prompt = (
                    f"You are the Supplier Agent. Summarize supplier conditions under simulation: {sim_context} in 2 sentences."
                )
                res = await llm.ainvoke([HumanMessage(content=prompt)])
                message_content = f"Supplier Agent: {res.content}"
            except Exception as e:
                logger.warning(f"Failed to run OpenAI Chat for SupplierAgent: {e}")

        return {
            "alerts": alerts,
            "agent_decisions": decisions,
            "current_agent": "supplier_agent",
            "messages": [{"role": "assistant", "content": message_content, "agent": "supplier_agent"}]
        }

supplier_agent = SupplierAgent()
