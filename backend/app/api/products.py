"""Products API — CRUD endpoints for retail products."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.inventory import Inventory
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductWithInventory

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductResponse])
async def list_products(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = None,
    search: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """List all products with optional filtering."""
    query = select(Product).where(Product.is_active == True)
    if category:
        query = query.where(Product.category == category)
    if search:
        query = query.where(
            Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%")
        )
    query = query.offset(skip).limit(limit).order_by(Product.name)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/categories", response_model=list[str])
async def list_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    """List all product categories."""
    result = await db.execute(
        select(Product.category).distinct().order_by(Product.category)
    )
    return result.scalars().all()


@router.get("/{product_id}", response_model=ProductWithInventory)
async def get_product(product_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """Get a single product with inventory summary."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Calculate total stock
    inv_result = await db.execute(
        select(
            func.coalesce(func.sum(Inventory.quantity), 0),
            func.coalesce(
                func.sum(Inventory.quantity).filter(Inventory.location_type == "store"), 0
            ),
            func.coalesce(
                func.sum(Inventory.quantity).filter(Inventory.location_type == "warehouse"), 0
            ),
        ).where(Inventory.product_id == product_id)
    )
    total, store_stock, wh_stock = inv_result.one()

    resp = ProductWithInventory.model_validate(product)
    resp.total_stock = total
    resp.store_stock = store_stock
    resp.warehouse_stock = wh_stock
    resp.stock_status = "critical" if total < 100 else "low" if total < 500 else "normal"
    return resp


@router.post("", response_model=ProductResponse, status_code=201)
async def create_product(data: ProductCreate, db: Annotated[AsyncSession, Depends(get_db)]):
    """Create a new product."""
    existing = await db.execute(select(Product).where(Product.sku == data.sku))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="SKU already exists")

    product = Product(**data.model_dump())
    db.add(product)
    await db.flush()
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str, data: ProductUpdate, db: Annotated[AsyncSession, Depends(get_db)]
):
    """Update a product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    await db.flush()
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: str, db: Annotated[AsyncSession, Depends(get_db)]):
    """Soft-delete a product."""
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False
    await db.flush()
