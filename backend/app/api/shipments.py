"""Shipments API — shipment management."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.shipment import Shipment
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.models.store import Store
from app.schemas.shipment import ShipmentCreate, ShipmentUpdateStatus, ShipmentResponse

router = APIRouter(prefix="/shipments", tags=["Shipments"])


@router.get("", response_model=list[ShipmentResponse])
async def list_shipments(
    db: Annotated[AsyncSession, Depends(get_db)],
    status: str | None = None,
    limit: int = Query(50, ge=1, le=200),
):
    """List shipments with optional status filter."""
    query = select(Shipment)
    if status:
        query = query.where(Shipment.status == status)
    query = query.order_by(desc(Shipment.created_at)).limit(limit)
    result = await db.execute(query)
    shipments = result.scalars().all()

    responses = []
    for s in shipments:
        resp = ShipmentResponse.model_validate(s)
        prod = (await db.execute(select(Product).where(Product.id == s.product_id))).scalar_one_or_none()
        wh = (await db.execute(select(Warehouse).where(Warehouse.id == s.from_warehouse_id))).scalar_one_or_none()
        store = (await db.execute(select(Store).where(Store.id == s.to_store_id))).scalar_one_or_none()
        resp.product_name = prod.name if prod else None
        resp.warehouse_name = wh.name if wh else None
        resp.store_name = store.name if store else None
        responses.append(resp)
    return responses


@router.post("", response_model=ShipmentResponse, status_code=201)
async def create_shipment(data: ShipmentCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """Create a new shipment."""
    shipment = Shipment(**data.model_dump())
    db.add(shipment)
    await db.flush()
    return ShipmentResponse.model_validate(shipment)


@router.put("/{shipment_id}/status", response_model=ShipmentResponse)
async def update_shipment_status(
    shipment_id: str,
    data: ShipmentUpdateStatus,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Update shipment status."""
    result = await db.execute(select(Shipment).where(Shipment.id == shipment_id))
    shipment = result.scalar_one_or_none()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    shipment.status = data.status
    await db.flush()
    return ShipmentResponse.model_validate(shipment)
