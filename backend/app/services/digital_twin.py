"""Digital Twin service for real-time inventory state tracking, snapshotting, and rollbacks."""

import json
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import select

from app.config import get_settings
from app.models import Inventory

logger = logging.getLogger("omniflow.services")
settings = get_settings()

# Global in-memory storage for backup/fallback when Redis is not running or mode is 'memory'
_in_memory_state: Dict[str, int] = {}
_snapshots: Dict[str, Dict[str, int]] = {}

class DigitalTwinService:
    """Manages the supply chain digital twin state, providing rapid cache access and simulation rollbacks."""

    def __init__(self):
        self.use_redis = settings.redis_mode == "redis"
        self.redis_client = None
        if self.use_redis:
            try:
                import redis
                self.redis_client = redis.from_url(settings.redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("📡 Connected to Redis for Digital Twin")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed: {e}. Falling back to In-Memory mode.")
                self.use_redis = False

    def _get_key(self, location_type: str, location_id: str, product_id: str) -> str:
        return f"dt:inv:{location_type}:{location_id}:{product_id}"

    async def sync_from_database(self, db_session) -> int:
        """Syncs all inventory records from database to cache."""
        result = await db_session.execute(select(Inventory))
        items = result.scalars().all()
        
        synced_count = 0
        for item in items:
            loc_id = item.store_id or item.warehouse_id
            if not loc_id:
                continue
            
            key = self._get_key(item.location_type, loc_id, item.product_id)
            if self.use_redis:
                self.redis_client.set(key, item.quantity)
            else:
                _in_memory_state[key] = item.quantity
            synced_count += 1
            
        logger.info(f"🔄 Synced {synced_count} inventory items into Digital Twin cache")
        return synced_count

    async def get_stock(self, location_type: str, location_id: str, product_id: str, db_session=None) -> int:
        """Gets current stock from the cache with database fallback."""
        key = self._get_key(location_type, location_id, product_id)
        
        if self.use_redis:
            val = self.redis_client.get(key)
            if val is not None:
                return int(val)
        else:
            if key in _in_memory_state:
                return _in_memory_state[key]
                
        # Database fallback
        if db_session:
            query = select(Inventory).where(Inventory.product_id == product_id)
            if location_type == "store":
                query = query.where(Inventory.store_id == location_id)
            else:
                query = query.where(Inventory.warehouse_id == location_id)
                
            result = await db_session.execute(query)
            item = result.scalar_one_or_none()
            if item:
                # Update cache
                if self.use_redis:
                    self.redis_client.set(key, item.quantity)
                else:
                    _in_memory_state[key] = item.quantity
                return item.quantity
                
        return 0

    async def set_stock(self, location_type: str, location_id: str, product_id: str, quantity: int, db_session=None):
        """Sets stock level in both cache and optionally DB."""
        key = self._get_key(location_type, location_id, product_id)
        
        if self.use_redis:
            self.redis_client.set(key, quantity)
        else:
            _in_memory_state[key] = quantity
            
        if db_session:
            query = select(Inventory).where(Inventory.product_id == product_id)
            if location_type == "store":
                query = query.where(Inventory.store_id == location_id)
            else:
                query = query.where(Inventory.warehouse_id == location_id)
                
            result = await db_session.execute(query)
            item = result.scalar_one_or_none()
            if item:
                item.quantity = quantity
                # Recalculate status
                from app.seed.seed_data import _status_from_qty
                item.status = _status_from_qty(quantity, item.safety_stock, item.reorder_point, item.max_stock)
                await db_session.commit()

    def create_snapshot(self, snapshot_id: str) -> bool:
        """Snapshots current state of all inventory. Used before simulations."""
        try:
            if self.use_redis:
                # Get all keys matching pattern
                keys = self.redis_client.keys("dt:inv:*")
                if not keys:
                    return False
                snapshot_data = {key: int(self.redis_client.get(key)) for key in keys}
                self.redis_client.set(f"dt:snapshot:{snapshot_id}", json.dumps(snapshot_data))
            else:
                _snapshots[snapshot_id] = _in_memory_state.copy()
            logger.info(f"📸 Created inventory snapshot '{snapshot_id}'")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create snapshot: {e}")
            return False

    def rollback_snapshot(self, snapshot_id: str) -> bool:
        """Restores inventory state to a previously saved snapshot."""
        try:
            if self.use_redis:
                data_str = self.redis_client.get(f"dt:snapshot:{snapshot_id}")
                if not data_str:
                    return False
                snapshot_data = json.loads(data_str)
                # Clear current keys and restore
                keys_to_del = self.redis_client.keys("dt:inv:*")
                if keys_to_del:
                    self.redis_client.delete(*keys_to_del)
                for key, val in snapshot_data.items():
                    self.redis_client.set(key, val)
                self.redis_client.delete(f"dt:snapshot:{snapshot_id}")
            else:
                if snapshot_id not in _snapshots:
                    return False
                global _in_memory_state
                _in_memory_state = _snapshots[snapshot_id].copy()
                del _snapshots[snapshot_id]
                
            logger.info(f"↩️ Rolled back to inventory snapshot '{snapshot_id}'")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to rollback snapshot: {e}")
            return False

# Global digital twin service
digital_twin = DigitalTwinService()
