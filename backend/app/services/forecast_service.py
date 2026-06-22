"""Forecast Service to orchestrate ML forecasting runs and database persistence."""

import logging
import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Dict, Any, List
from sqlalchemy import select, delete

from app.models import Forecast, Product, Store, Inventory
from app.ml.forecaster import forecaster
from app.services.event_bus import event_bus

logger = logging.getLogger("omniflow.services")

class ForecastService:
    """Manages generation and storage of demand forecasting data."""

    async def generate_system_forecasts(
        self,
        db_session,
        horizon_days: int = 7,
        external_disruptions: Dict[str, Any] = None
    ) -> List[Forecast]:
        """Generates predictions for all active product-store combinations over the horizon."""
        logger.info(f"🔮 Generating {horizon_days}-day demand forecasts...")
        
        # 1. Fetch active products and stores
        result_inv = await db_session.execute(
            select(Inventory).where(Inventory.location_type == "store")
        )
        inventories = result_inv.scalars().all()
        
        today = datetime.now(timezone.utc).date()
        generated_forecasts = []
        
        # We process each item
        for inv in inventories:
            prod_result = await db_session.execute(
                select(Product).where(Product.id == inv.product_id)
            )
            product = prod_result.scalar_one_or_none()
            
            store_result = await db_session.execute(
                select(Store).where(Store.id == inv.store_id)
            )
            store = store_result.scalar_one_or_none()
            
            if not product or not store:
                continue

            # Clear older forecasts for this product/store combination in the horizon
            end_date = today + timedelta(days=horizon_days)
            await db_session.execute(
                delete(Forecast).where(
                    Forecast.product_id == product.id,
                    Forecast.store_id == store.id,
                    Forecast.forecast_date >= today,
                    Forecast.forecast_date < end_date
                )
            )
            
            # Predict for each day in horizon
            for i in range(horizon_days):
                forecast_date = today + timedelta(days=i)
                
                # Check if this category matches a disruption parameter
                disruption = None
                if external_disruptions:
                    affected_categories = external_disruptions.get("categories", [])
                    affected_stores = external_disruptions.get("stores", [])
                    
                    if (not affected_categories or product.category in affected_categories) and \
                       (not affected_stores or store.code in affected_stores):
                        disruption = external_disruptions
                
                pred = forecaster.predict_demand(
                    product_sku=product.sku,
                    category=product.category,
                    store_code=store.code,
                    forecast_date=forecast_date,
                    promotions_active=(i % 3 == 0),  # simulate dynamic promotions
                    external_disruptions=disruption
                )
                
                f = Forecast(
                    id=str(uuid.uuid4()),
                    product_id=product.id,
                    store_id=store.id,
                    forecast_date=forecast_date,
                    horizon_days=horizon_days,
                    predicted_demand=pred["predicted_demand"],
                    lower_bound=pred["lower_bound"],
                    upper_bound=pred["upper_bound"],
                    confidence=pred["confidence"],
                    model_version="xgboost-v1",
                    factors_used=pred["factors_used"],
                    is_spike=pred["is_spike"],
                    spike_magnitude=pred["spike_magnitude"]
                )
                db_session.add(f)
                generated_forecasts.append(f)
                
        await db_session.commit()
        
        logger.info(f"✅ Generated {len(generated_forecasts)} forecast entries")
        
        # Publish notification
        await event_bus.publish("forecast.generated", {
            "horizon_days": horizon_days,
            "total_entries": len(generated_forecasts),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        return generated_forecasts

# Global forecast service instance
forecast_service = ForecastService()
