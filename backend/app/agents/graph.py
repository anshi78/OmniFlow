"""LangGraph StateGraph construction and execution workflow."""

import logging
from typing import Dict, Any, List

from langgraph.graph import StateGraph, END

from app.agents.state import SupplyChainState
from app.agents.orchestrator import orchestrator_agent
from app.agents.demand_forecast import demand_agent
from app.agents.store_agent import store_agent
from app.agents.warehouse_agent import warehouse_agent
from app.agents.supplier_agent import supplier_agent
from app.agents.logistics_agent import logistics_agent
from app.agents.trend_agent import trend_agent
from app.agents.optimizer_agent import optimizer_agent

logger = logging.getLogger("omniflow.agents")

def build_workflow() -> StateGraph:
    """Builds the compiled StateGraph connecting all supply chain agents."""
    
    workflow = StateGraph(SupplyChainState)
    
    # Register Nodes
    workflow.add_node("orchestrator", orchestrator_agent.run)
    workflow.add_node("trend_agent", trend_agent.run)
    workflow.add_node("demand_forecast", demand_agent.run)
    workflow.add_node("store_agent", store_agent.run)
    workflow.add_node("warehouse_agent", warehouse_agent.run)
    workflow.add_node("supplier_agent", supplier_agent.run)
    workflow.add_node("logistics_agent", logistics_agent.run)
    workflow.add_node("optimizer_agent", optimizer_agent.run)
    
    # Define Connections (Sequential Chain for Hackathon Simplicity)
    # This ensures all agents contribute to the final state in order
    workflow.set_entry_point("orchestrator")
    
    workflow.add_edge("orchestrator", "trend_agent")
    workflow.add_edge("trend_agent", "demand_forecast")
    workflow.add_edge("demand_forecast", "store_agent")
    workflow.add_edge("store_agent", "warehouse_agent")
    workflow.add_edge("warehouse_agent", "supplier_agent")
    workflow.add_edge("supplier_agent", "logistics_agent")
    workflow.add_edge("logistics_agent", "optimizer_agent")
    
    # Optimizer sends state back to Orchestrator to finalize and resolve conflicts
    workflow.add_node("finalizer", orchestrator_agent.run)
    workflow.add_edge("optimizer_agent", "finalizer")
    workflow.add_edge("finalizer", END)
    
    return workflow

# Compile the workflow
compiled_graph = build_workflow().compile()

async def run_agent_workflow(
    query: str,
    simulation_context: Dict[str, Any] = None,
    db_session = None
) -> Dict[str, Any]:
    """
    Executes the multi-agent system workflow.
    Optionally persists decisions and returns the final state.
    """
    logger.info(f"🚀 Running Multi-Agent Workflow for query: '{query}'")
    
    initial_state = {
        "query": query,
        "inventory_data": {},
        "forecasts": {},
        "alerts": [],
        "restock_requests": [],
        "agent_decisions": [],
        "messages": [],
        "simulation_context": simulation_context,
        "current_agent": "orchestrator"
    }
    
    final_state = await compiled_graph.ainvoke(initial_state)
    
    # If a database session is provided, save decisions
    if db_session:
        await orchestrator_agent.save_decisions_to_db(final_state, db_session)
        
    return final_state
