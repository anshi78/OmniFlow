"""Warehouse model — distribution centers in the supply chain."""

import uuid
from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(300), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=50000)
    current_utilization: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    inventory_items = relationship(
        "Inventory",
        back_populates="warehouse",
        foreign_keys="Inventory.warehouse_id",
        lazy="selectin",
    )
    outbound_shipments = relationship(
        "Shipment",
        back_populates="from_warehouse",
        foreign_keys="Shipment.from_warehouse_id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Warehouse(code={self.code}, name={self.name})>"
