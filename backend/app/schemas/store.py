from __future__ import annotations
"""Store schemas."""

from datetime import datetime
from pydantic import BaseModel, Field


class StoreBase(BaseModel):
    name: str = Field(..., max_length=200)
    code: str = Field(..., max_length=20)
    location: str = Field(..., max_length=300)
    city: str = Field(..., max_length=100)
    region: str = Field(..., max_length=100)
    latitude: float | None = None
    longitude: float | None = None
    store_type: str = Field("retail", max_length=50)
    capacity: int = Field(10000, gt=0)


class StoreCreate(StoreBase):
    pass


class StoreResponse(StoreBase):
    id: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class StoreWithStats(StoreResponse):
    total_products: int = 0
    total_stock: int = 0
    health_score: float = 0.0
    stockout_risk: float = 0.0
