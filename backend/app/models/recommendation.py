from __future__ import annotations
"""Recommendation model — AI-generated actionable recommendations."""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Float, Text, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    recommendation_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # restock, transfer, reorder, alert, optimize

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    factors_used: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Example: {"low_stock": 0.8, "high_demand_forecast": 0.6, "seasonal_trend": 0.4}

    priority: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )  # low, medium, high, critical

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending, accepted, rejected, auto_executed

    # Financial impact
    estimated_cost: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_savings: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_revenue_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Related entities
    related_product_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    related_store_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    related_warehouse_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    simulation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return f"<Recommendation(type={self.recommendation_type}, title={self.title[:30]})>"
