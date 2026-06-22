from __future__ import annotations
"""Shipment model — tracks goods movement between warehouses and stores."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Shipment(Base):
    __tablename__ = "shipments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    from_warehouse_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("warehouses.id"), nullable=False, index=True
    )
    to_store_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("stores.id"), nullable=False, index=True
    )
    product_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("products.id"), nullable=False, index=True
    )

    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, default="pending"
    )  # pending, in_transit, delivered, delayed, cancelled

    estimated_departure: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    estimated_arrival: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_departure: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    actual_arrival: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    distance_km: Mapped[float] = mapped_column(Float, nullable=True)
    carbon_score: Mapped[float] = mapped_column(Float, nullable=True)  # kg CO2
    shipping_cost: Mapped[float] = mapped_column(Float, nullable=True)

    carrier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    from_warehouse = relationship(
        "Warehouse", back_populates="outbound_shipments", foreign_keys=[from_warehouse_id]
    )
    product = relationship("Product")

    def __repr__(self) -> str:
        return f"<Shipment(id={self.id[:8]}, status={self.status})>"
