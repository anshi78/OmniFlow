"""Forecasts API — demand forecasting endpoints."""

from typing import Annotated
from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.forecast import Forecast
from app.models.product import Product
from app.schemas.forecast import ForecastResponse, ForecastSeries

router = APIRouter(prefix="/forecasts", tags=["Forecasts"])


@router.get("", response_model=list[ForecastResponse])
async def list_forecasts(
    db: Annotated[AsyncSession, Depends(get_db)],
    product_id: str | None = None,
    store_id: str | None = None,
    limit: int = Query(50, ge=1, le=200),
):
    """List forecasts with optional filtering."""
    query = select(Forecast)
    if product_id:
        query = query.where(Forecast.product_id == product_id)
    if store_id:
        query = query.where(Forecast.store_id == store_id)
    query = query.order_by(desc(Forecast.created_at)).limit(limit)

    result = await db.execute(query)
    forecasts = result.scalars().all()

    responses = []
    for f in forecasts:
        resp = ForecastResponse.model_validate(f)
        prod = (await db.execute(select(Product).where(Product.id == f.product_id))).scalar_one_or_none()
        resp.product_name = prod.name if prod else None
        responses.append(resp)
    return responses


@router.get("/series/{product_id}", response_model=ForecastSeries)
async def get_forecast_series(
    product_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    days: int = Query(7, ge=1, le=90),
):
    """Get forecast time series for a product (for charting)."""
    product = (await db.execute(select(Product).where(Product.id == product_id))).scalar_one_or_none()
    if not product:
        return ForecastSeries(product_id=product_id, product_name="Unknown", dates=[], predicted=[], lower=[], upper=[])

    result = await db.execute(
        select(Forecast)
        .where(Forecast.product_id == product_id)
        .order_by(Forecast.forecast_date)
        .limit(days)
    )
    forecasts = result.scalars().all()

    return ForecastSeries(
        product_id=product_id,
        product_name=product.name,
        dates=[f.forecast_date.isoformat() for f in forecasts],
        predicted=[f.predicted_demand for f in forecasts],
        lower=[f.lower_bound or f.predicted_demand * 0.8 for f in forecasts],
        upper=[f.upper_bound or f.predicted_demand * 1.2 for f in forecasts],
    )


from app.schemas.forecast import ForecastRequest
from app.services.forecast_service import forecast_service

@router.post("/generate", status_code=201)
async def generate_forecasts(
    request: ForecastRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Trigger the forecast generation pipeline."""
    results = await forecast_service.generate_system_forecasts(db, horizon_days=request.horizon_days)
    return {
        "status": "success",
        "total_generated": len(results),
        "horizon_days": request.horizon_days
    }

