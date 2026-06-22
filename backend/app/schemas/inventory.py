from __future__ import annotations
"""Inventory schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class InventoryBase(BaseModel):
    product_id: str
    store_id: str | None = None
    warehouse_id: str | None = None
    location_type: str = "store"
    quantity: int = Field(0, ge=0)
    safety_stock: int = Field(50, ge=0)
    reorder_point: int = Field(100, ge=0)
    max_stock: int = Field(1000, gt=0)


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: int | None = None
    safety_stock: int | None = None
    reorder_point: int | None = None
    max_stock: int | None = None


class InventoryResponse(InventoryBase):
    id: str
    reserved_quantity: int
    daily_sales_avg: float
    days_of_supply: float
    status: str
    last_restocked: datetime | None
    last_updated: datetime
    # Enriched fields
    product_name: str | None = None
    product_sku: str | None = None
    location_name: str | None = None
    health_score: float = 0.0

    model_config = {"from_attributes": True}


class InventoryHealthSummary(BaseModel):
    total_items: int
    total_quantity: int
    healthy_count: int
    low_count: int
    critical_count: int
    overstock_count: int
    average_health_score: float
    total_value: float
    stockout_risk_percent: float
