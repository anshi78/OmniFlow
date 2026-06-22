"""Inventory API — inventory management and health monitoring."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.inventory import Inventory
from app.models.product import Product
from app.models.store import Store
from app.models.warehouse import Warehouse
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryResponse, InventoryHealthSummary

router = APIRouter(prefix="/inventory", tags=["Inventory"])


@router.get("", response_model=list[InventoryResponse])
async def list_inventory(
    db: Annotated[AsyncSession, Depends(get_db)],
    location_type: str | None = None,
    status: str | None = None,
    category: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List inventory with filtering by location, status, and category."""
    query = select(Inventory).join(Product, Inventory.product_id == Product.id)

    if location_type:
        query = query.where(Inventory.location_type == location_type)
    if status:
        query = query.where(Inventory.status == status)
    if category:
        query = query.where(Product.category == category)
    if search:
        query = query.where(
            Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
        )

    query = query.offset(skip).limit(limit).order_by(Inventory.status.desc(), Inventory.quantity)
    result = await db.execute(query)
    items = result.scalars().all()

    # Enrich with product and location names
    responses = []
    for inv in items:
        resp = InventoryResponse.model_validate(inv)
        resp.health_score = round(inv.health_score, 1)

        # Get product info
        prod_result = await db.execute(select(Product).where(Product.id == inv.product_id))
        prod = prod_result.scalar_one_or_none()
        if prod:
            resp.product_name = prod.name
            resp.product_sku = prod.sku

        # Get location name
        if inv.store_id:
            store_result = await db.execute(select(Store).where(Store.id == inv.store_id))
            store = store_result.scalar_one_or_none()
            resp.location_name = store.name if store else None
        elif inv.warehouse_id:
            wh_result = await db.execute(select(Warehouse).where(Warehouse.id == inv.warehouse_id))
            wh = wh_result.scalar_one_or_none()
            resp.location_name = wh.name if wh else None

        responses.append(resp)
    return responses


@router.get("/health", response_model=InventoryHealthSummary)
async def get_inventory_health(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get overall inventory health summary."""
    result = await db.execute(
        select(
            func.count(Inventory.id),
            func.coalesce(func.sum(Inventory.quantity), 0),
        )
    )
    total_items, total_qty = result.one()

    # Count by status
    for s in ["normal", "low", "critical", "overstock"]:
        count_result = await db.execute(
            select(func.count()).select_from(Inventory).where(Inventory.status == s)
        )
        locals()[f"{s}_count"] = count_result.scalar()

    # Calculate total value
    value_result = await db.execute(
        select(func.coalesce(func.sum(Inventory.quantity * Product.unit_price), 0)).select_from(
            Inventory
        ).join(Product, Inventory.product_id == Product.id)
    )
    total_value = value_result.scalar()

    healthy = locals().get("normal_count", 0)
    low = locals().get("low_count", 0)
    critical = locals().get("critical_count", 0)
    overstock = locals().get("overstock_count", 0)

    return InventoryHealthSummary(
        total_items=total_items,
        total_quantity=total_qty,
        healthy_count=healthy,
        low_count=low,
        critical_count=critical,
        overstock_count=overstock,
        average_health_score=round(
            ((healthy * 90 + low * 50 + critical * 15 + overstock * 60) / max(total_items, 1)), 1
        ),
        total_value=round(total_value, 2),
        stockout_risk_percent=round((critical / max(total_items, 1)) * 100, 1),
    )


@router.get("/{inventory_id}", response_model=InventoryResponse)
async def get_inventory_item(inventory_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """Get a single inventory record."""
    result = await db.execute(select(Inventory).where(Inventory.id == inventory_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    resp = InventoryResponse.model_validate(inv)
    resp.health_score = round(inv.health_score, 1)
    return resp


@router.put("/{inventory_id}", response_model=InventoryResponse)
async def update_inventory(
    inventory_id: str,
    data: InventoryUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update inventory quantities."""
    result = await db.execute(select(Inventory).where(Inventory.id == inventory_id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(inv, field, value)

    # Recalculate status
    inv.status = (
        "critical" if inv.quantity <= inv.safety_stock
        else "low" if inv.quantity <= inv.reorder_point
        else "overstock" if inv.quantity > inv.max_stock
        else "normal"
    )
    if inv.daily_sales_avg > 0:
        inv.days_of_supply = round(inv.quantity / inv.daily_sales_avg, 1)

    await db.flush()
    resp = InventoryResponse.model_validate(inv)
    resp.health_score = round(inv.health_score, 1)
    return resp
