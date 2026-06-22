"""Supply chain multi-agent state definition."""

import operator
from typing import Annotated, Any, Dict, List, TypedDict, Union

class SupplyChainState(TypedDict):
    """Shared state for the LangGraph supply chain optimization workflow."""
    
    query: str
    """User query or event triggering the workflow."""
    
    inventory_data: Dict[str, Any]
    """Current inventory data collected by agents (e.g. key stockout risks)."""
    
    forecasts: Dict[str, Any]
    """Generated demand forecasts and factors."""
    
    alerts: List[Dict[str, Any]]
    """Active inventory or disruption alerts detected by agents."""
    
    restock_requests: List[Dict[str, Any]]
    """Store restock requests generated or processed."""
    
    agent_decisions: List[Dict[str, Any]]
    """Record of decisions and actions taken by each agent."""
    
    messages: Annotated[List[Dict[str, Any]], operator.add]
    """Chat/event communication history between agents and orchestrator."""
    
    simulation_context: Union[Dict[str, Any], None]
    """Simulation scenario context if running inside a digital twin simulation."""
    
    current_agent: str
    """Name of the currently executing agent."""
