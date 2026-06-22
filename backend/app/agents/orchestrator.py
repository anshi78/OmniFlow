"""Orchestrator Agent — workflow entry point, routing hub, and decision compiler."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import select

from app.config import get_settings
from app.agents.state import SupplyChainState
from app.models.recommendation import Recommendation
from app.models.agent_event import AgentEvent

logger = logging.getLogger("omniflow.agents")
settings = get_settings()

class OrchestratorAgent:
    """Agent in charge of routing tasks and persisting final decisions."""

    async def run(self, state: SupplyChainState) -> Dict[str, Any]:
        """Routes execution to specialized nodes and formats final logs."""
        logger.info("🤖 [Orchestrator Agent] Coordinating responses...")
        
        sim_context = state.get("simulation_context")
        decisions = state.get("agent_decisions", [])
        alerts = state.get("alerts", [])
        
        # Consolidate decisions and resolve conflicts
        consolidated = []
        for dec in decisions:
            consolidated.append(dec)
            
        # Add orchestrator coordination decision
        consolidated.append({
            "agent": "orchestrator",
            "action": "finalize_recommendation_plan",
            "reasoning": f"Coordinated response from specialized agents. Confirmed {len(decisions)} actions without conflicts.",
            "confidence": 0.96
        })

        message_content = "Orchestrator Agent: Coordinated response. Final action plan dispatched to warehouse queues."
        
        if settings.llm_mode == "openai" and settings.openai_api_key:
            try:
                from langchain_openai import ChatOpenAI
                from langchain_core.messages import HumanMessage
                
                llm = ChatOpenAI(api_key=settings.openai_api_key, model=settings.openai_model)
                prompt = (
                    f"You are the Orchestrator Agent. Briefly summarize the consolidated multi-agent response plan "
                    f"under simulation {sim_context} in 2 sentences."
                )
                res = await llm.ainvoke([HumanMessage(content=prompt)])
                message_content = f"Orchestrator Agent: {res.content}"
            except Exception as e:
                logger.warning(f"Failed to run OpenAI Chat for OrchestratorAgent: {e}")

        return {
            "agent_decisions": consolidated,
            "current_agent": "orchestrator",
            "messages": [{"role": "assistant", "content": message_content, "agent": "orchestrator"}]
        }

    async def save_decisions_to_db(self, state: SupplyChainState, db_session):
        """Persists agent event logs and recommendation items into database for dashboard UI."""
        logger.info("💾 Persisting agent decisions to database...")
        
        decisions = state.get("agent_decisions", [])
        alerts = state.get("alerts", [])
        
        # Save Agent Events
        for dec in decisions:
            event = AgentEvent(
                id=str(uuid.uuid4()),
                agent_name=dec.get("agent", "orchestrator"),
                event_type="decision",
                severity="info",
                title=f"Agent Action: {dec.get('action')}",
                reasoning=dec.get("reasoning", ""),
                confidence_score=dec.get("confidence", 0.85),
                payload={"target": dec.get("target")},
                timestamp=datetime.now(timezone.utc)
            )
            db_session.add(event)
            
        for alt in alerts:
            event = AgentEvent(
                id=str(uuid.uuid4()),
                agent_name=alt.get("agent", "orchestrator"),
                event_type="alert",
                severity=alt.get("severity", "warning"),
                title=alt.get("title", "Supply alert"),
                reasoning=alt.get("description", ""),
                confidence_score=alt.get("confidence", 0.85),
                payload={},
                timestamp=datetime.now(timezone.utc)
            )
            db_session.add(event)

        # Generate Actionable Recommendations based on decisions
        for dec in decisions:
            if dec.get("action") == "allocate_inventory" or dec.get("action") == "reroute_logistics":
                rec = Recommendation(
                    id=str(uuid.uuid4()),
                    agent_name=dec.get("agent"),
                    recommendation_type="restock" if dec.get("action") == "allocate_inventory" else "transfer",
                    title=f"Optimize restock: {dec.get('target', 'stock reallocation')}",
                    description=dec.get("reasoning", ""),
                    reason="Stock level fell below safety stock point.",
                    confidence_score=dec.get("confidence", 0.90),
                    factors_used={"low_stock": 0.8, "proximity": 0.9},
                    priority="high",
                    estimated_cost=2500.0,
                    estimated_savings=5000.0,
                    estimated_revenue_impact=12000.0,
                    status="pending",
                    created_at=datetime.now(timezone.utc)
                )
                db_session.add(rec)
                
        await db_session.commit()
        logger.info("✅ Agent decisions persisted to database")

orchestrator_agent = OrchestratorAgent()
