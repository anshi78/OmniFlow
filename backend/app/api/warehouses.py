"""Warehouses API — CRUD endpoints for distribution centers."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.schemas.warehouse import WarehouseCreate, WarehouseResponse, WarehouseWithStats

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])


@router.get("", response_model=list[WarehouseResponse])
async def list_warehouses(db: Annotated[AsyncSession, Depends(get_db)]):
    """List all warehouses."""
    result = await db.execute(
        select(Warehouse).where(Warehouse.is_active == True).order_by(Warehouse.name)
    )
    return result.scalars().all()


@router.get("/{warehouse_id}", response_model=WarehouseWithStats)
async def get_warehouse(warehouse_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """Get a single warehouse with stats."""
    result = await db.execute(select(Warehouse).where(Warehouse.id == warehouse_id))
    wh = result.scalar_one_or_none()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")

    inv_result = await db.execute(
        select(
            func.count(Inventory.id),
            func.coalesce(func.sum(Inventory.quantity), 0),
        ).where(Inventory.warehouse_id == warehouse_id)
    )
    product_count, total_stock = inv_result.one()

    resp = WarehouseWithStats.model_validate(wh)
    resp.total_products = product_count
    resp.total_stock = total_stock
    resp.utilization_percent = round((total_stock / max(wh.capacity, 1)) * 100, 1)
    return resp


@router.post("", response_model=WarehouseResponse, status_code=201)
async def create_warehouse(data: WarehouseCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """Create a new warehouse."""
    wh = Warehouse(**data.model_dump())
    db.add(wh)
    await db.flush()
    return wh
