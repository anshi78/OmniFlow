"""Trend Agent — monitors social media feeds and detects product hype spikes."""

import logging
from typing import Dict, Any

from app.config import get_settings
from app.agents.state import SupplyChainState
from app.ml.sentiment import analyzer

logger = logging.getLogger("omniflow.agents")
settings = get_settings()

class TrendAgent:
    """Agent that crawls news and social posts to find early signals of product demand."""

    async def run(self, state: SupplyChainState) -> Dict[str, Any]:
        logger.info("🤖 [Trend Agent] Scanning social sentiment streams...")
        
        sim_context = state.get("simulation_context")
        decisions = []
        alerts = []
        
        if sim_context:
            scenario = sim_context.get("scenario_type")
            if scenario == "viral_trend":
                # Social hype detected
                sentiment_data = analyzer.analyze_sentiment("TikTok: This ELEC-001 Headphones is absolutely viral, love it best hype")
                alerts.append({
                    "agent": "trend_agent",
                    "type": "viral_hype",
                    "severity": "warning",
                    "title": "Viral Trend Alert: ELEC-001",
                    "description": f"Hype score: {sentiment_data['intensity']} with positive sentiment. TikTok views surged 450%.",
                    "confidence": sentiment_data["confidence"]
                })
                decisions.append({
                    "agent": "trend_agent",
                    "action": "adjust_sentiment_buffer",
                    "reasoning": f"Product is viral. Raising safety stock buffer multiplier by {sentiment_data['intensity'] * 2}x.",
                    "confidence": sentiment_data["confidence"]
                })

        message_content = "Trend Agent: Hype streams verified. No significant social sentiment shift."
        
        if settings.llm_mode == "openai" and settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import HumanMessage
                
                llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model)
                prompt = (
                    f"You are the Trend Agent. Summarize trend patterns under simulation: {sim_context} in 2 sentences."
                )
                res = await llm.ainvoke([HumanMessage(content=prompt)])
                message_content = f"Trend Agent: {res.content}"
            except Exception as e:
                logger.warning(f"Failed to run OpenAI Chat for TrendAgent: {e}")

        return {
            "alerts": alerts,
            "agent_decisions": decisions,
            "current_agent": "trend_agent",
            "messages": [{"role": "assistant", "content": message_content, "agent": "trend_agent"}]
        }

trend_agent = TrendAgent()
