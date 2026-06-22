from __future__ import annotations
"""Simulation model — records of digital twin simulation runs."""

import uuid
from datetime import datetime
from typing import Optional


from sqlalchemy import String, Float, Text, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Simulation(Base):
    __tablename__ = "simulations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    scenario_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # demand_spike, supplier_strike, warehouse_shutdown, weather_disaster, viral_trend

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # Input parameters for the scenario
    parameters: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Example: {"category": "Electronics", "magnitude": 3.5, "duration_days": 7}

    # Results
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="running"
    )  # running, completed, failed

    inventory_impact: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Example: {"products_affected": 12, "stockouts": 3, "total_units_impact": -450}

    financial_impact: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Example: {"lost_revenue": 12500, "additional_costs": 3200, "total_impact": -15700}

    agent_actions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Example: [{"agent": "warehouse", "action": "emergency_restock", "product": "SKU-001"}]

    carbon_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # kg CO2

    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Simulation(type={self.scenario_type}, status={self.status})>"
