"""Logistics Agent — optimizes shipment transit paths and calculates ETAs."""

import logging
from typing import Dict, Any

from app.config import get_settings
from app.agents.state import SupplyChainState

logger = logging.getLogger("omniflow.agents")
settings = get_settings()

class LogisticsAgent:
    """Agent in charge of carrier coordination, routes, and emissions calculations."""

    async def run(self, state: SupplyChainState) -> Dict[str, Any]:
        logger.info("🤖 [Logistics Agent] Optimizing distribution transit routes...")
        
        sim_context = state.get("simulation_context")
        decisions = []
        alerts = []
        
        if sim_context:
            scenario = sim_context.get("scenario_type")
            if scenario == "weather_disaster":
                alerts.append({
                    "agent": "logistics_agent",
                    "type": "transit_delay",
                    "severity": "critical",
                    "title": "Severe Blizzard Rerouting",
                    "description": "Northeast roads closed. Standard shipping delayed by 72 hours.",
                    "confidence": 0.94
                })
                decisions.append({
                    "agent": "logistics_agent",
                    "action": "reroute_air_freight",
                    "reasoning": "Rerouting critical medical/grocery restocks from WH-CENT via air-cargo to bypass road blockades.",
                    "confidence": 0.92
                })
                
        message_content = "Logistics Agent: Route paths optimized. Estimated carbon footprint reduced by 8% via intermodal rail routing."
        
        if settings.llm_mode == "openai" and settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import HumanMessage
                
                llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model)
                prompt = (
                    f"You are the Logistics Agent. Summarize shipping impacts under simulation: {sim_context} in 2 sentences."
                )
                res = await llm.ainvoke([HumanMessage(content=prompt)])
                message_content = f"Logistics Agent: {res.content}"
            except Exception as e:
                logger.warning(f"Failed to run OpenAI Chat for LogisticsAgent: {e}")

        return {
            "alerts": alerts,
            "agent_decisions": decisions,
            "current_agent": "logistics_agent",
            "messages": [{"role": "assistant", "content": message_content, "agent": "logistics_agent"}]
        }

logistics_agent = LogisticsAgent()
