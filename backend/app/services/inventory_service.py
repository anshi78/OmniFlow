"""Inventory Service to handle operational calculations, stock adjustments, and reorder triggers."""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List
from sqlalchemy import select

from app.models import Inventory, Product, Store, Warehouse, Shipment
from app.services.digital_twin import digital_twin
from app.services.event_bus import event_bus

logger = logging.getLogger("omniflow.services")

class InventoryService:
    """Business operations for tracking inventory, triggering reorders, and shipping stock."""

    async def get_inventory_health_stats(self, db_session) -> Dict[str, Any]:
        """Calculates and returns stock counts by status across the entire system."""
        result = await db_session.execute(select(Inventory))
        items = result.scalars().all()
        
        stats = {
            "total_items": len(items),
            "normal": 0,
            "low": 0,
            "critical": 0,
            "overstock": 0
        }
        for item in items:
            stats[item.status] = stats.get(item.status, 0) + 1
            
        return stats

    async def adjust_stock(
        self,
        db_session,
        product_id: str,
        location_type: str,
        location_id: str,
        amount: int,
        reason: str = "adjustment"
    ) -> bool:
        """Adjusts stock levels (positive or negative) and syncs cache/database."""
        query = select(Inventory).where(Inventory.product_id == product_id)
        if location_type == "store":
            query = query.where(Inventory.store_id == location_id)
        else:
            query = query.where(Inventory.warehouse_id == location_id)
            
        result = await db_session.execute(query)
        item = result.scalar_one_or_none()
        
        if not item:
            logger.warning(f"Inventory item not found for product {product_id} at {location_id}")
            return False
            
        new_qty = max(0, item.quantity + amount)
        item.quantity = new_qty
        
        # Recalculate status
        from app.seed.seed_data import _status_from_qty
        item.status = _status_from_qty(new_qty, item.safety_stock, item.reorder_point, item.max_stock)
        item.last_updated = datetime.now(timezone.utc)
        
        await db_session.commit()
        
        # Sync to digital twin
        await digital_twin.set_stock(location_type, location_id, product_id, new_qty)
        
        # Publish event
        await event_bus.publish("inventory.updated", {
            "product_id": product_id,
            "location_type": location_type,
            "location_id": location_id,
            "adjustment": amount,
            "new_quantity": new_qty,
            "status": item.status,
            "reason": reason
        })
        
        return True

    async def process_reorder_checks(self, db_session) -> List[Dict[str, Any]]:
        """Checks for items below reorder point and triggers alerts/shipments."""
        result = await db_session.execute(
            select(Inventory).where(Inventory.quantity <= Inventory.reorder_point)
        )
        low_items = result.scalars().all()
        alerts = []
        
        for item in low_items:
            loc_id = item.store_id or item.warehouse_id
            if not loc_id:
                continue
                
            # Skip if it is warehouse, or if there is already a pending shipment
            if item.location_type == "warehouse":
                continue
                
            shipment_exists = (await db_session.execute(
                select(Shipment).where(
                    Shipment.to_store_id == item.store_id,
                    Shipment.product_id == item.product_id,
                    Shipment.status.in_(["pending", "in_transit"])
                )
            )).scalar() is not None
            
            if shipment_exists:
                continue
                
            # Trigger alert
            alert = {
                "product_id": item.product_id,
                "store_id": item.store_id,
                "current_qty": item.quantity,
                "reorder_point": item.reorder_point,
                "severity": "warning" if item.quantity > item.safety_stock else "critical"
            }
            alerts.append(alert)
            
            await event_bus.publish("inventory.low", alert)
            
        return alerts

# Global inventory service instance
inventory_service = InventoryService()
