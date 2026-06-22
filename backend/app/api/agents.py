"""Agents API — agent status, events, and execution endpoints."""

from typing import Annotated
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.agent_event import AgentEvent
from app.models.recommendation import Recommendation

router = APIRouter(prefix="/agents", tags=["Agents"])

# Agent registry
AGENTS = {
    "orchestrator": {
        "name": "Orchestrator Agent",
        "description": "Coordinates all agents, resolves conflicts, and manages workflow",
        "status": "active",
        "icon": "🎯",
    },
    "demand_forecast": {
        "name": "Demand Forecast Agent",
        "description": "Predicts future demand using ML models and external signals",
        "status": "active",
        "icon": "📊",
    },
    "store_agent": {
        "name": "Store Agent",
        "description": "Monitors per-store inventory and generates restock requests",
        "status": "active",
        "icon": "🏪",
    },
    "warehouse_agent": {
        "name": "Warehouse Agent",
        "description": "Allocates inventory and fulfills restock requests",
        "status": "active",
        "icon": "🏭",
    },
    "supplier_agent": {
        "name": "Supplier Agent",
        "description": "Monitors supplier reliability and predicts delays",
        "status": "standby",
        "icon": "🚚",
    },
    "logistics_agent": {
        "name": "Logistics Agent",
        "description": "Optimizes shipping routes and calculates ETAs",
        "status": "standby",
        "icon": "🗺️",
    },
    "trend_agent": {
        "name": "Trend Agent",
        "description": "Monitors social trends and predicts demand shifts",
        "status": "standby",
        "icon": "📈",
    },
    "optimizer_agent": {
        "name": "Inventory Optimizer Agent",
        "description": "Calculates dynamic safety stock and recommends transfers",
        "status": "standby",
        "icon": "⚡",
    },
}


@router.get("/status")
async def get_agents_status(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get status of all agents."""
    agents_with_stats = []
    for agent_id, info in AGENTS.items():
        event_count = (await db.execute(
            select(func.count()).select_from(AgentEvent).where(AgentEvent.agent_name == agent_id)
        )).scalar()

        last_event = (await db.execute(
            select(AgentEvent)
            .where(AgentEvent.agent_name == agent_id)
            .order_by(desc(AgentEvent.timestamp))
            .limit(1)
        )).scalar_one_or_none()

        agents_with_stats.append({
            "id": agent_id,
            **info,
            "total_events": event_count,
            "last_activity": last_event.timestamp.isoformat() if last_event else None,
            "last_action": last_event.title if last_event else None,
        })
    return agents_with_stats


@router.get("/events")
async def get_agent_events(
    db: Annotated[AsyncSession, Depends(get_db)],
    agent_name: str | None = None,
    event_type: str | None = None,
    severity: str | None = None,
    limit: int = Query(30, ge=1, le=100),
):
    """Get agent events with optional filtering."""
    query = select(AgentEvent)
    if agent_name:
        query = query.where(AgentEvent.agent_name == agent_name)
    if event_type:
        query = query.where(AgentEvent.event_type == event_type)
    if severity:
        query = query.where(AgentEvent.severity == severity)

    query = query.order_by(desc(AgentEvent.timestamp)).limit(limit)
    result = await db.execute(query)
    events = result.scalars().all()

    return [
        {
            "id": e.id,
            "agent_name": e.agent_name,
            "event_type": e.event_type,
            "severity": e.severity,
            "title": e.title,
            "description": e.description,
            "reasoning": e.reasoning,
            "confidence_score": e.confidence_score,
            "payload": e.payload,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events
    ]


@router.get("/recommendations")
async def get_recommendations(
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = None,
    priority: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    """Get AI recommendations."""
    query = select(Recommendation)
    if status:
        query = query.where(Recommendation.status == status)
    if priority:
        query = query.where(Recommendation.priority == priority)
    query = query.order_by(desc(Recommendation.created_at)).limit(limit)

    result = await db.execute(query)
    recs = result.scalars().all()

    return [
        {
            "id": r.id,
            "agent_name": r.agent_name,
            "type": r.recommendation_type,
            "title": r.title,
            "description": r.description,
            "reason": r.reason,
            "confidence_score": r.confidence_score,
            "factors_used": r.factors_used,
            "priority": r.priority,
            "status": r.status,
            "estimated_cost": r.estimated_cost,
            "estimated_savings": r.estimated_savings,
            "estimated_revenue_impact": r.estimated_revenue_impact,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recs
    ]


@router.get("/graph")
async def get_agent_graph(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get agent communication graph data for visualization."""
    nodes = [
        {"id": k, "label": v["name"], "icon": v["icon"], "status": v["status"]}
        for k, v in AGENTS.items()
    ]

    # Define agent communication edges
    edges = [
        {"from": "orchestrator", "to": "demand_forecast", "label": "forecast_request"},
        {"from": "orchestrator", "to": "store_agent", "label": "inventory_check"},
        {"from": "orchestrator", "to": "warehouse_agent", "label": "allocation_request"},
        {"from": "demand_forecast", "to": "orchestrator", "label": "forecast_result"},
        {"from": "store_agent", "to": "orchestrator", "label": "restock_request"},
        {"from": "warehouse_agent", "to": "orchestrator", "label": "allocation_result"},
        {"from": "orchestrator", "to": "supplier_agent", "label": "supplier_check"},
        {"from": "orchestrator", "to": "logistics_agent", "label": "route_request"},
        {"from": "orchestrator", "to": "trend_agent", "label": "trend_check"},
        {"from": "orchestrator", "to": "optimizer_agent", "label": "optimize_request"},
    ]

    return {"nodes": nodes, "edges": edges}


from pydantic import BaseModel
from app.agents.graph import run_agent_workflow

class AgentRunRequest(BaseModel):
    query: str

@router.post("/run")
async def run_agents(
    request: AgentRunRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Trigger the multi-agent optimization workflow with a query."""
    result = await run_agent_workflow(request.query, db_session=db)
    return {
        "status": "completed",
        "decisions_count": len(result.get("agent_decisions", [])),
        "alerts_count": len(result.get("alerts", [])),
        "messages": result.get("messages", [])
    }

