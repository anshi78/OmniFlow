"""Store model — retail stores in the supply chain network."""

import uuid
from datetime import datetime

from sqlalchemy import String, Float, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Store(Base):
    __tablename__ = "stores"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    location: Mapped[str] = mapped_column(String(300), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    store_type: Mapped[str] = mapped_column(String(50), nullable=False, default="retail")
    capacity: Mapped[int] = mapped_column(Integer, nullable=False, default=10000)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    inventory_items = relationship(
        "Inventory",
        back_populates="store",
        foreign_keys="Inventory.store_id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Store(code={self.code}, name={self.name})>"
