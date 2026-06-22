from __future__ import annotations
"""Product schemas — request/response models."""

from datetime import datetime
from pydantic import BaseModel, Field


class ProductBase(BaseModel):
    sku: str = Field(..., max_length=50, examples=["SKU-ELEC-001"])
    name: str = Field(..., max_length=200, examples=["Wireless Noise-Cancelling Headphones"])
    category: str = Field(..., max_length=100, examples=["Electronics"])
    subcategory: str | None = Field(None, max_length=100, examples=["Audio"])
    unit_price: float = Field(..., gt=0, examples=[149.99])
    cost_price: float = Field(0.0, ge=0, examples=[75.00])
    description: str | None = None
    image_url: str | None = None
    weight_kg: float | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    subcategory: str | None = None
    unit_price: float | None = None
    cost_price: float | None = None
    description: str | None = None
    image_url: str | None = None
    weight_kg: float | None = None
    is_active: bool | None = None


class ProductResponse(ProductBase):
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProductWithInventory(ProductResponse):
    total_stock: int = 0
    store_stock: int = 0
    warehouse_stock: int = 0
    stock_status: str = "normal"
