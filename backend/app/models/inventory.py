from __future__ import annotations
"""Inventory model — tracks product quantities at stores and warehouses."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id"), nullable=False, index=True
    )
    # Inventory can belong to a store or a warehouse
    store_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("stores.id"), nullable=True, index=True
    )
    warehouse_id: Mapped[Optional[str]] = mapped_column(
        String(36), ForeignKey("warehouses.id"), nullable=True, index=True
    )
    location_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="store"
    )  # "store" or "warehouse"

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reserved_quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    safety_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    reorder_point: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    max_stock: Mapped[int] = mapped_column(Integer, nullable=False, default=1000)

    daily_sales_avg: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    days_of_supply: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="normal"
    )  # normal, low, critical, overstock

    last_restocked: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_updated: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    product = relationship("Product", back_populates="inventory_items")
    store = relationship("Store", back_populates="inventory_items", foreign_keys=[store_id])
    warehouse = relationship(
        "Warehouse", back_populates="inventory_items", foreign_keys=[warehouse_id]
    )

    @property
    def available_quantity(self) -> int:
        return max(0, self.quantity - self.reserved_quantity)

    @property
    def health_score(self) -> float:
        """Inventory health: 0-100. Below safety_stock is critical, above max is overstock."""
        if self.max_stock == 0:
            return 0.0
        ratio = self.quantity / self.max_stock
        if self.quantity <= self.safety_stock:
            return max(0, ratio * 30)  # 0-30: critical
        elif self.quantity <= self.reorder_point:
            return 30 + (ratio * 30)  # 30-60: low
        elif self.quantity <= self.max_stock:
            return 60 + (ratio * 40)  # 60-100: healthy
        else:
            return max(50, 100 - ((ratio - 1) * 50))  # overstock penalty

    def __repr__(self) -> str:
        loc = self.store_id or self.warehouse_id
        return f"<Inventory(product={self.product_id}, location={loc}, qty={self.quantity})>"
