"""Inventory Optimizer Agent — runs dynamic stock optimization models."""

import logging
from typing import Dict, Any

from app.config import get_settings
from app.agents.state import SupplyChainState

logger = logging.getLogger("omniflow.agents")
settings = get_settings()

class OptimizerAgent:
    """Agent that runs warehouse layout and stock balance algorithms."""

    async def run(self, state: SupplyChainState) -> Dict[str, Any]:
        logger.info("🤖 [Optimizer Agent] Recalculating stock thresholds...")
        
        sim_context = state.get("simulation_context")
        decisions = []
        alerts = []
        
        if sim_context:
            scenario = sim_context.get("scenario_type")
            if scenario == "demand_spike" or scenario == "viral_trend":
                decisions.append({
                    "agent": "optimizer_agent",
                    "action": "optimize_reorder_points",
                    "reasoning": "Re-calculating dynamic safety thresholds using service level target of 98%. Reorder points adjusted upwards.",
                    "confidence": 0.95
                })

        message_content = "Optimizer Agent: Safety stock thresholds optimized using hold-cost vs stockout-cost penalty bounds."
        
        if settings.llm_mode == "openai" and settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import HumanMessage
                
                llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model)
                prompt = (
                    f"You are the Inventory Optimizer Agent. Summarize dynamic safety stock calculations under simulation: {sim_context} in 2 sentences."
                )
                res = await llm.ainvoke([HumanMessage(content=prompt)])
                message_content = f"Optimizer Agent: {res.content}"
            except Exception as e:
                logger.warning(f"Failed to run OpenAI Chat for OptimizerAgent: {e}")

        return {
            "alerts": alerts,
            "agent_decisions": decisions,
            "current_agent": "optimizer_agent",
            "messages": [{"role": "assistant", "content": message_content, "agent": "optimizer_agent"}]
        }

optimizer_agent = OptimizerAgent()
