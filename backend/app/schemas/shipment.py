from __future__ import annotations
"""Shipment schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class ShipmentBase(BaseModel):
    from_warehouse_id: str
    to_store_id: str
    product_id: str
    quantity: int = Field(..., gt=0)


class ShipmentCreate(ShipmentBase):
    estimated_departure: datetime | None = None
    estimated_arrival: datetime | None = None
    carrier: str | None = None


class ShipmentUpdateStatus(BaseModel):
    status: str  # pending, in_transit, delivered, delayed, cancelled


class ShipmentResponse(ShipmentBase):
    id: str
    status: str
    estimated_departure: datetime | None
    estimated_arrival: datetime | None
    actual_departure: datetime | None
    actual_arrival: datetime | None
    distance_km: float | None
    carbon_score: float | None
    shipping_cost: float | None
    carrier: str | None
    tracking_number: str | None
    created_at: datetime
    updated_at: datetime
    # Enriched
    product_name: str | None = None
    warehouse_name: str | None = None
    store_name: str | None = None

    model_config = {"from_attributes": True}
