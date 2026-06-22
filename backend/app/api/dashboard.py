"""Dashboard API — aggregated stats for the main dashboard."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.product import Product
from app.models.store import Store
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.models.shipment import Shipment
from app.models.forecast import Forecast
from app.models.agent_event import AgentEvent
from app.models.recommendation import Recommendation
from app.schemas.dashboard import (
    DashboardStats, DashboardInventoryByCategory,
    DashboardRegionRisk, DashboardResponse,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("", response_model=DashboardResponse)
async def get_dashboard(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get aggregated dashboard data."""

    # Core counts
    products_count = (await db.execute(
        select(func.count()).select_from(Product).where(Product.is_active == True)
    )).scalar()

    stores_count = (await db.execute(
        select(func.count()).select_from(Store).where(Store.is_active == True)
    )).scalar()

    warehouses_count = (await db.execute(
        select(func.count()).select_from(Warehouse).where(Warehouse.is_active == True)
    )).scalar()

    # Inventory totals
    inv_result = (await db.execute(
        select(func.coalesce(func.sum(Inventory.quantity), 0))
    )).scalar()

    # Inventory value
    value_result = (await db.execute(
        select(func.coalesce(func.sum(Inventory.quantity * Product.unit_price), 0)).select_from(
            Inventory
        ).join(Product, Inventory.product_id == Product.id)
    )).scalar()

    # Stockout risk
    critical_count = (await db.execute(
        select(func.count()).select_from(Inventory).where(Inventory.status == "critical")
    )).scalar()
    total_inv = (await db.execute(
        select(func.count()).select_from(Inventory)
    )).scalar()
    stockout_risk = round((critical_count / max(total_inv, 1)) * 100, 1)

    # Predicted demand
    demand_7d = (await db.execute(
        select(func.coalesce(func.sum(Forecast.predicted_demand), 0))
        .where(Forecast.horizon_days == 7)
    )).scalar()

    # Active shipments
    active_shipments = (await db.execute(
        select(func.count()).select_from(Shipment).where(
            Shipment.status.in_(["pending", "in_transit"])
        )
    )).scalar()

    # Active decisions and recommendations
    active_decisions = (await db.execute(
        select(func.count()).select_from(AgentEvent)
    )).scalar()

    pending_recs = (await db.execute(
        select(func.count()).select_from(Recommendation).where(
            Recommendation.status == "pending"
        )
    )).scalar()

    # Health score
    normal_count = (await db.execute(
        select(func.count()).select_from(Inventory).where(Inventory.status == "normal")
    )).scalar()
    health_score = round((normal_count / max(total_inv, 1)) * 100, 1)

    stats = DashboardStats(
        total_inventory=inv_result,
        total_products=products_count,
        total_stores=stores_count,
        total_warehouses=warehouses_count,
        predicted_demand_7d=round(demand_7d, 0),
        stockout_risk_percent=stockout_risk,
        inventory_health_score=health_score,
        active_shipments=active_shipments,
        active_agent_decisions=active_decisions,
        pending_recommendations=pending_recs,
        total_inventory_value=round(value_result, 2),
    )

    # Inventory by category
    cat_result = await db.execute(
        select(
            Product.category,
            func.sum(Inventory.quantity).label("total_qty"),
            func.count(func.distinct(Product.id)).label("product_count"),
            func.sum(Inventory.quantity * Product.unit_price).label("value"),
        )
        .select_from(Inventory)
        .join(Product, Inventory.product_id == Product.id)
        .group_by(Product.category)
        .order_by(desc("total_qty"))
    )
    categories = [
        DashboardInventoryByCategory(
            category=row.category,
            total_quantity=row.total_qty or 0,
            product_count=row.product_count or 0,
            health_score=75.0,  # Simplified
            value=round(row.value or 0, 2),
        )
        for row in cat_result.all()
    ]

    # Region risks
    region_result = await db.execute(
        select(
            Store.region,
            func.count(func.distinct(Store.id)).label("store_count"),
        )
        .select_from(Store)
        .where(Store.is_active == True)
        .group_by(Store.region)
    )
    regions = []
    for row in region_result.all():
        # Get critical items for this region
        crit = (await db.execute(
            select(func.count()).select_from(Inventory)
            .join(Store, Inventory.store_id == Store.id)
            .where(Store.region == row.region, Inventory.status == "critical")
        )).scalar()
        total = (await db.execute(
            select(func.count()).select_from(Inventory)
            .join(Store, Inventory.store_id == Store.id)
            .where(Store.region == row.region)
        )).scalar()
        risk = round((crit / max(total, 1)) * 100, 1)
        regions.append(DashboardRegionRisk(
            region=row.region,
            store_count=row.store_count,
            avg_health_score=round(100 - risk * 1.5, 1),
            stockout_risk=risk,
            critical_items=crit,
        ))

    # Recent agent events
    events_result = await db.execute(
        select(AgentEvent)
        .order_by(desc(AgentEvent.timestamp))
        .limit(10)
    )
    recent_events = [
        {
            "id": e.id,
            "agent_name": e.agent_name,
            "event_type": e.event_type,
            "severity": e.severity,
            "title": e.title,
            "confidence_score": e.confidence_score,
            "timestamp": e.timestamp.isoformat() if e.timestamp else None,
        }
        for e in events_result.scalars().all()
    ]

    # Recent recommendations
    recs_result = await db.execute(
        select(Recommendation)
        .where(Recommendation.status == "pending")
        .order_by(desc(Recommendation.created_at))
        .limit(5)
    )
    recent_recs = [
        {
            "id": r.id,
            "agent_name": r.agent_name,
            "type": r.recommendation_type,
            "title": r.title,
            "priority": r.priority,
            "confidence_score": r.confidence_score,
            "estimated_savings": r.estimated_savings,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in recs_result.scalars().all()
    ]

    return DashboardResponse(
        stats=stats,
        inventory_by_category=categories,
        region_risks=regions,
        recent_agent_events=recent_events,
        recent_recommendations=recent_recs,
    )
