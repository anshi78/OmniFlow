"""Stores API — CRUD endpoints for retail stores."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.store import Store
from app.models.inventory import Inventory
from app.schemas.store import StoreCreate, StoreResponse, StoreWithStats

router = APIRouter(prefix="/stores", tags=["Stores"])


@router.get("", response_model=list[StoreResponse])
async def list_stores(
    db: Annotated[AsyncSession, Depends(get_db)],
    region: str | None = None,
):
    """List all stores with optional region filter."""
    query = select(Store).where(Store.is_active == True)
    if region:
        query = query.where(Store.region == region)
    query = query.order_by(Store.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{store_id}", response_model=StoreWithStats)
async def get_store(store_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """Get a single store with inventory stats."""
    result = await db.execute(select(Store).where(Store.id == store_id))
    store = result.scalar_one_or_none()
    if not store:
        raise HTTPException(status_code=404, detail="Store not found")

    inv_result = await db.execute(
        select(
            func.count(Inventory.id),
            func.coalesce(func.sum(Inventory.quantity), 0),
        ).where(Inventory.store_id == store_id)
    )
    product_count, total_stock = inv_result.one()

    resp = StoreWithStats.model_validate(store)
    resp.total_products = product_count
    resp.total_stock = total_stock

    # Calculate health and risk
    critical_result = await db.execute(
        select(func.count()).select_from(Inventory).where(
            Inventory.store_id == store_id, Inventory.status == "critical"
        )
    )
    critical = critical_result.scalar()
    resp.stockout_risk = round((critical / max(product_count, 1)) * 100, 1)
    resp.health_score = round(max(0, 100 - resp.stockout_risk * 2), 1)
    return resp


@router.post("", response_model=StoreResponse, status_code=201)
async def create_store(data: StoreCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """Create a new store."""
    store = Store(**data.model_dump())
    db.add(store)
    await db.flush()
    return store
