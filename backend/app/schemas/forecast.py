from __future__ import annotations
"""Forecast schemas."""

from datetime import datetime, date
from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    product_id: str
    store_id: str | None = None
    horizon_days: int = Field(7, ge=1, le=90)


class ForecastResponse(BaseModel):
    id: str
    product_id: str
    store_id: str | None
    forecast_date: date
    horizon_days: int
    predicted_demand: float
    lower_bound: float | None
    upper_bound: float | None
    confidence: float
    model_version: str
    factors_used: dict | None
    is_spike: bool
    spike_magnitude: float | None
    created_at: datetime
    # Enriched
    product_name: str | None = None

    model_config = {"from_attributes": True}


class ForecastSeries(BaseModel):
    """Time series of forecasts for charting."""
    product_id: str
    product_name: str
    dates: list[str]
    predicted: list[float]
    lower: list[float]
    upper: list[float]
    actual: list[float | None] = []
