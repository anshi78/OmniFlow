from __future__ import annotations
"""AgentEvent model — logs all AI agent actions and decisions."""

import uuid
from datetime import datetime
from typing import Optional


from sqlalchemy import String, Float, Text, DateTime, func, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AgentEvent(Base):
    __tablename__ = "agent_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_name: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )  # orchestrator, demand_forecast, store, warehouse, etc.
    event_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # decision, alert, recommendation, conflict, error
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, default="info"
    )  # info, warning, critical

    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    reasoning: Mapped[str] = mapped_column(Text, nullable=True)  # Agent's chain of thought
    confidence_score: Mapped[float] = mapped_column(Float, nullable=True)

    payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # Stores arbitrary event data: affected products, inventory changes, etc.

    related_entity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    related_entity_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)

    simulation_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)

    timestamp: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), index=True
    )

    def __repr__(self) -> str:
        return f"<AgentEvent(agent={self.agent_name}, type={self.event_type}, title={self.title[:30]})>"
