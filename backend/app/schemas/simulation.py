from __future__ import annotations
"""Simulation schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class SimulationRequest(BaseModel):
    scenario_type: str = Field(
        ...,
        description="One of: demand_spike, supplier_strike, warehouse_shutdown, weather_disaster, viral_trend",
    )
    parameters: dict = Field(
        default_factory=dict,
        description="Scenario-specific parameters",
        examples=[{"category": "Electronics", "magnitude": 3.0, "duration_days": 7, "region": "West"}],
    )


class SimulationImpact(BaseModel):
    products_affected: int = 0
    stores_affected: int = 0
    stockouts_predicted: int = 0
    total_units_impact: int = 0
    inventory_before: dict = {}
    inventory_after: dict = {}


class FinancialImpact(BaseModel):
    lost_revenue: float = 0.0
    additional_costs: float = 0.0
    emergency_shipping: float = 0.0
    total_impact: float = 0.0


class AgentAction(BaseModel):
    agent: str
    action: str
    target: str
    reasoning: str
    confidence: float
    timestamp: str


class SimulationResponse(BaseModel):
    id: str
    scenario_type: str
    title: str
    description: str | None
    parameters: dict | None
    status: str
    inventory_impact: dict | None
    financial_impact: dict | None
    agent_actions: dict | None
    carbon_impact: float | None
    duration_seconds: float | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
