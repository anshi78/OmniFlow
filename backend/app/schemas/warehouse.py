from __future__ import annotations
"""Warehouse schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class WarehouseBase(BaseModel):
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=20)
    location: str = Field(..., max_length=300)
    city: str = Field(..., max_length=100)
    region: str = Field(..., max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    capacity: int = Field(50000, gt=0)


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseResponse(WarehouseBase):
    id: str
    current_utilization: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class WarehouseWithStats(WarehouseResponse):
    total_products: int = 0
    total_stock: int = 0
    utilization_percent: float = 0.0
