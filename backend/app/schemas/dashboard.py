from __future__ import annotations
"""Dashboard schemas — aggregated stats for the main dashboard."""

from pydantic import BaseModel


class DashboardStats(BaseModel):
    total_inventory: int = 0
    total_products: int = 0
    total_stores: int = 0
    total_warehouses: int = 0
    predicted_demand_7d: float = 0.0
    predicted_demand_30d: float = 0.0
    stockout_risk_percent: float = 0.0
    inventory_health_score: float = 0.0
    active_shipments: int = 0
    active_agent_decisions: int = 0
    pending_recommendations: int = 0
    total_inventory_value: float = 0.0
    carbon_footprint: float = 0.0


class DashboardInventoryByCategory(BaseModel):
    category: str
    total_quantity: int
    product_count: int
    health_score: float
    value: float


class DashboardRegionRisk(BaseModel):
    region: str
    store_count: int
    avg_health_score: float
    stockout_risk: float
    critical_items: int


class DashboardResponse(BaseModel):
    stats: DashboardStats
    inventory_by_category: list[DashboardInventoryByCategory] = []
    region_risks: list[DashboardRegionRisk] = []
    recent_agent_events: list[dict] = []
    recent_recommendations: list[dict] = []
