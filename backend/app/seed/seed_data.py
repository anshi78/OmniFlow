"""Seed data — populates the database with realistic sample data for the hackathon demo."""

import uuid
import random
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models import Product, Store, Warehouse, Inventory, Forecast, AgentEvent, Recommendation, User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Products
PRODUCTS = [
    # Electronics
    {"sku": "ELEC-001", "name": "Wireless Noise-Cancelling Headphones", "category": "Electronics", "subcategory": "Audio", "unit_price": 149.99, "cost_price": 65.00, "weight_kg": 0.3},
    {"sku": "ELEC-002", "name": "4K Ultra HD Smart TV 55\"", "category": "Electronics", "subcategory": "Displays", "unit_price": 599.99, "cost_price": 320.00, "weight_kg": 18.5},
    {"sku": "ELEC-003", "name": "Bluetooth Portable Speaker", "category": "Electronics", "subcategory": "Audio", "unit_price": 79.99, "cost_price": 32.00, "weight_kg": 0.6},
    {"sku": "ELEC-004", "name": "Smart Watch Pro", "category": "Electronics", "subcategory": "Wearables", "unit_price": 299.99, "cost_price": 120.00, "weight_kg": 0.05},
    {"sku": "ELEC-005", "name": "Wireless Charging Pad", "category": "Electronics", "subcategory": "Accessories", "unit_price": 39.99, "cost_price": 12.00, "weight_kg": 0.15},
    {"sku": "ELEC-006", "name": "USB-C Hub 7-in-1", "category": "Electronics", "subcategory": "Accessories", "unit_price": 49.99, "cost_price": 18.00, "weight_kg": 0.1},
    {"sku": "ELEC-007", "name": "Mechanical Gaming Keyboard", "category": "Electronics", "subcategory": "Peripherals", "unit_price": 129.99, "cost_price": 55.00, "weight_kg": 1.2},
    {"sku": "ELEC-008", "name": "Wireless Ergonomic Mouse", "category": "Electronics", "subcategory": "Peripherals", "unit_price": 69.99, "cost_price": 25.00, "weight_kg": 0.1},
    {"sku": "ELEC-009", "name": "Tablet 10\" with Stylus", "category": "Electronics", "subcategory": "Computing", "unit_price": 449.99, "cost_price": 200.00, "weight_kg": 0.5},
    {"sku": "ELEC-010", "name": "Action Camera 4K", "category": "Electronics", "subcategory": "Cameras", "unit_price": 199.99, "cost_price": 85.00, "weight_kg": 0.12},
    # Groceries
    {"sku": "GROC-001", "name": "Organic Quinoa 1kg", "category": "Groceries", "subcategory": "Grains", "unit_price": 8.99, "cost_price": 4.50, "weight_kg": 1.0},
    {"sku": "GROC-002", "name": "Premium Olive Oil 500ml", "category": "Groceries", "subcategory": "Oils", "unit_price": 12.99, "cost_price": 6.00, "weight_kg": 0.5},
    {"sku": "GROC-003", "name": "Artisan Coffee Beans 500g", "category": "Groceries", "subcategory": "Beverages", "unit_price": 15.99, "cost_price": 7.00, "weight_kg": 0.5},
    {"sku": "GROC-004", "name": "Organic Almond Milk 1L", "category": "Groceries", "subcategory": "Dairy Alt", "unit_price": 4.99, "cost_price": 2.00, "weight_kg": 1.0},
    {"sku": "GROC-005", "name": "Dark Chocolate 72% 200g", "category": "Groceries", "subcategory": "Snacks", "unit_price": 6.99, "cost_price": 3.00, "weight_kg": 0.2},
    {"sku": "GROC-006", "name": "Greek Yogurt 500g", "category": "Groceries", "subcategory": "Dairy", "unit_price": 5.49, "cost_price": 2.50, "weight_kg": 0.5},
    {"sku": "GROC-007", "name": "Granola Mix 750g", "category": "Groceries", "subcategory": "Breakfast", "unit_price": 7.99, "cost_price": 3.50, "weight_kg": 0.75},
    {"sku": "GROC-008", "name": "Sparkling Water 12-Pack", "category": "Groceries", "subcategory": "Beverages", "unit_price": 9.99, "cost_price": 4.00, "weight_kg": 4.2},
    {"sku": "GROC-009", "name": "Avocado Oil 250ml", "category": "Groceries", "subcategory": "Oils", "unit_price": 11.99, "cost_price": 5.50, "weight_kg": 0.25},
    {"sku": "GROC-010", "name": "Protein Bar Box (12 ct)", "category": "Groceries", "subcategory": "Snacks", "unit_price": 24.99, "cost_price": 12.00, "weight_kg": 0.72},
    # Apparel
    {"sku": "APRL-001", "name": "Premium Cotton T-Shirt", "category": "Apparel", "subcategory": "Tops", "unit_price": 29.99, "cost_price": 8.00, "weight_kg": 0.2},
    {"sku": "APRL-002", "name": "Slim Fit Denim Jeans", "category": "Apparel", "subcategory": "Bottoms", "unit_price": 59.99, "cost_price": 18.00, "weight_kg": 0.8},
    {"sku": "APRL-003", "name": "Waterproof Running Jacket", "category": "Apparel", "subcategory": "Outerwear", "unit_price": 89.99, "cost_price": 35.00, "weight_kg": 0.4},
    {"sku": "APRL-004", "name": "Merino Wool Sweater", "category": "Apparel", "subcategory": "Tops", "unit_price": 79.99, "cost_price": 30.00, "weight_kg": 0.35},
    {"sku": "APRL-005", "name": "Athletic Running Shoes", "category": "Apparel", "subcategory": "Footwear", "unit_price": 119.99, "cost_price": 45.00, "weight_kg": 0.7},
    {"sku": "APRL-006", "name": "Casual Canvas Sneakers", "category": "Apparel", "subcategory": "Footwear", "unit_price": 49.99, "cost_price": 15.00, "weight_kg": 0.6},
    {"sku": "APRL-007", "name": "Performance Gym Shorts", "category": "Apparel", "subcategory": "Bottoms", "unit_price": 34.99, "cost_price": 10.00, "weight_kg": 0.15},
    {"sku": "APRL-008", "name": "UV Protection Sunglasses", "category": "Apparel", "subcategory": "Accessories", "unit_price": 44.99, "cost_price": 12.00, "weight_kg": 0.03},
    {"sku": "APRL-009", "name": "Leather Belt", "category": "Apparel", "subcategory": "Accessories", "unit_price": 39.99, "cost_price": 14.00, "weight_kg": 0.2},
    {"sku": "APRL-010", "name": "Winter Beanie Hat", "category": "Apparel", "subcategory": "Accessories", "unit_price": 19.99, "cost_price": 5.00, "weight_kg": 0.08},
    # Home & Living
    {"sku": "HOME-001", "name": "Memory Foam Pillow", "category": "Home", "subcategory": "Bedding", "unit_price": 49.99, "cost_price": 18.00, "weight_kg": 1.5},
    {"sku": "HOME-002", "name": "Stainless Steel Cookware Set", "category": "Home", "subcategory": "Kitchen", "unit_price": 149.99, "cost_price": 60.00, "weight_kg": 8.0},
    {"sku": "HOME-003", "name": "LED Desk Lamp", "category": "Home", "subcategory": "Lighting", "unit_price": 34.99, "cost_price": 12.00, "weight_kg": 1.0},
    {"sku": "HOME-004", "name": "Aromatherapy Diffuser", "category": "Home", "subcategory": "Wellness", "unit_price": 29.99, "cost_price": 10.00, "weight_kg": 0.4},
    {"sku": "HOME-005", "name": "Bamboo Cutting Board Set", "category": "Home", "subcategory": "Kitchen", "unit_price": 24.99, "cost_price": 8.00, "weight_kg": 1.8},
    {"sku": "HOME-006", "name": "Microfiber Towel Set (6)", "category": "Home", "subcategory": "Bath", "unit_price": 39.99, "cost_price": 14.00, "weight_kg": 1.2},
    {"sku": "HOME-007", "name": "Smart WiFi Plug 4-Pack", "category": "Home", "subcategory": "Smart Home", "unit_price": 29.99, "cost_price": 10.00, "weight_kg": 0.3},
    {"sku": "HOME-008", "name": "Vacuum Insulated Water Bottle", "category": "Home", "subcategory": "Kitchen", "unit_price": 24.99, "cost_price": 8.00, "weight_kg": 0.4},
    {"sku": "HOME-009", "name": "Scented Candle Gift Set", "category": "Home", "subcategory": "Decor", "unit_price": 34.99, "cost_price": 12.00, "weight_kg": 1.0},
    {"sku": "HOME-010", "name": "Throw Blanket Plush", "category": "Home", "subcategory": "Bedding", "unit_price": 39.99, "cost_price": 15.00, "weight_kg": 1.5},
    # Sports & Outdoors
    {"sku": "SPRT-001", "name": "Yoga Mat Premium", "category": "Sports", "subcategory": "Fitness", "unit_price": 39.99, "cost_price": 12.00, "weight_kg": 1.8},
    {"sku": "SPRT-002", "name": "Resistance Band Set", "category": "Sports", "subcategory": "Fitness", "unit_price": 19.99, "cost_price": 5.00, "weight_kg": 0.3},
    {"sku": "SPRT-003", "name": "Hiking Backpack 40L", "category": "Sports", "subcategory": "Outdoor", "unit_price": 79.99, "cost_price": 30.00, "weight_kg": 1.2},
    {"sku": "SPRT-004", "name": "Insulated Sports Bottle", "category": "Sports", "subcategory": "Accessories", "unit_price": 19.99, "cost_price": 6.00, "weight_kg": 0.35},
    {"sku": "SPRT-005", "name": "Adjustable Dumbbell Set", "category": "Sports", "subcategory": "Fitness", "unit_price": 199.99, "cost_price": 80.00, "weight_kg": 20.0},
    {"sku": "SPRT-006", "name": "Camping Tent 2-Person", "category": "Sports", "subcategory": "Outdoor", "unit_price": 129.99, "cost_price": 50.00, "weight_kg": 3.5},
    {"sku": "SPRT-007", "name": "Swimming Goggles Pro", "category": "Sports", "subcategory": "Swimming", "unit_price": 24.99, "cost_price": 8.00, "weight_kg": 0.05},
    {"sku": "SPRT-008", "name": "Foam Roller Recovery", "category": "Sports", "subcategory": "Fitness", "unit_price": 29.99, "cost_price": 10.00, "weight_kg": 0.8},
    {"sku": "SPRT-009", "name": "Tennis Racket Pro", "category": "Sports", "subcategory": "Racquet", "unit_price": 89.99, "cost_price": 35.00, "weight_kg": 0.3},
    {"sku": "SPRT-010", "name": "Cycling Helmet", "category": "Sports", "subcategory": "Cycling", "unit_price": 59.99, "cost_price": 22.00, "weight_kg": 0.25},
]

# Stores
STORES = [
    {"code": "NYC-001", "name": "OmniStore Manhattan", "location": "350 5th Ave", "city": "New York", "region": "Northeast", "latitude": 40.7484, "longitude": -73.9857, "capacity": 15000},
    {"code": "LA-001", "name": "OmniStore Los Angeles", "location": "6801 Hollywood Blvd", "city": "Los Angeles", "region": "West", "latitude": 34.1016, "longitude": -118.3267, "capacity": 18000},
    {"code": "CHI-001", "name": "OmniStore Chicago", "location": "233 S Wacker Dr", "city": "Chicago", "region": "Midwest", "latitude": 41.8789, "longitude": -87.6359, "capacity": 12000},
    {"code": "HOU-001", "name": "OmniStore Houston", "location": "1600 Lamar St", "city": "Houston", "region": "South", "latitude": 29.7531, "longitude": -95.3631, "capacity": 14000},
    {"code": "PHX-001", "name": "OmniStore Phoenix", "location": "2 E Jefferson St", "city": "Phoenix", "region": "West", "latitude": 33.4484, "longitude": -112.0740, "capacity": 11000},
    {"code": "SEA-001", "name": "OmniStore Seattle", "location": "600 Pine St", "city": "Seattle", "region": "West", "latitude": 47.6131, "longitude": -122.3360, "capacity": 13000},
    {"code": "MIA-001", "name": "OmniStore Miami", "location": "401 Biscayne Blvd", "city": "Miami", "region": "South", "latitude": 25.7751, "longitude": -80.1868, "capacity": 10000},
    {"code": "DEN-001", "name": "OmniStore Denver", "location": "200 E Colfax Ave", "city": "Denver", "region": "West", "latitude": 39.7392, "longitude": -104.9847, "capacity": 9000},
    {"code": "ATL-001", "name": "OmniStore Atlanta", "location": "68 Mitchell St SW", "city": "Atlanta", "region": "South", "latitude": 33.7489, "longitude": -84.3880, "capacity": 12000},
    {"code": "BOS-001", "name": "OmniStore Boston", "location": "1 City Hall Square", "city": "Boston", "region": "Northeast", "latitude": 42.3601, "longitude": -71.0589, "capacity": 11000},
]

# Warehouses
WAREHOUSES = [
    {"code": "WH-EAST", "name": "East Coast Distribution Center", "location": "Newark, NJ", "city": "Newark", "region": "Northeast", "latitude": 40.7357, "longitude": -74.1724, "capacity": 100000},
    {"code": "WH-WEST", "name": "West Coast Distribution Center", "location": "Ontario, CA", "city": "Ontario", "region": "West", "latitude": 34.0633, "longitude": -117.6509, "capacity": 120000},
    {"code": "WH-CENT", "name": "Central Distribution Hub", "location": "Memphis, TN", "city": "Memphis", "region": "South", "latitude": 35.1495, "longitude": -90.0490, "capacity": 80000},
    {"code": "WH-SOUTH", "name": "Southeast Fulfillment Center", "location": "Jacksonville, FL", "city": "Jacksonville", "region": "South", "latitude": 30.3322, "longitude": -81.6557, "capacity": 60000},
    {"code": "WH-NORTH", "name": "Great Lakes Warehouse", "location": "Columbus, OH", "city": "Columbus", "region": "Midwest", "latitude": 39.9612, "longitude": -82.9988, "capacity": 70000},
]


def _status_from_qty(qty: int, safety: int, reorder: int, max_s: int) -> str:
    if qty <= safety:
        return "critical"
    elif qty <= reorder:
        return "low"
    elif qty > max_s:
        return "overstock"
    return "normal"


async def seed_database(session: AsyncSession) -> dict:
    """Seed the database with sample data. Returns counts of created entities."""

    # Check if already seeded
    result = await session.execute(select(func.count()).select_from(Product))
    if result.scalar() > 0:
        return {"status": "already_seeded"}

    counts = {}

    # Users
    admin = User(
        id=str(uuid.uuid4()),
        email="admin@omniflow.ai",
        hashed_password=pwd_context.hash("admin123"),
        full_name="Admin User",
        role="admin",
    )
    manager = User(
        id=str(uuid.uuid4()),
        email="manager@omniflow.ai",
        hashed_password=pwd_context.hash("manager123"),
        full_name="Manager User",
        role="manager",
    )
    session.add_all([admin, manager])
    counts["users"] = 2

    # Products
    product_ids = {}
    for p in PRODUCTS:
        pid = str(uuid.uuid4())
        product_ids[p["sku"]] = pid
        session.add(Product(id=pid, **p))
    counts["products"] = len(PRODUCTS)

    # Stores
    store_ids = {}
    for s in STORES:
        sid = str(uuid.uuid4())
        store_ids[s["code"]] = sid
        session.add(Store(id=sid, **s))
    counts["stores"] = len(STORES)

    # Warehouses
    wh_ids = {}
    for w in WAREHOUSES:
        wid = str(uuid.uuid4())
        wh_ids[w["code"]] = wid
        session.add(Warehouse(id=wid, current_utilization=random.uniform(0.4, 0.85), **w))
    counts["warehouses"] = len(WAREHOUSES)

    await session.flush()

    # Inventory (store inventory)
    inv_count = 0
    for sku, pid in product_ids.items():
        # Each product in 3-6 random stores
        selected_stores = random.sample(list(store_ids.items()), k=random.randint(3, 6))
        for store_code, sid in selected_stores:
            safety = random.randint(20, 80)
            reorder = safety + random.randint(30, 80)
            max_s = reorder + random.randint(200, 600)
            qty = random.randint(max(0, safety - 30), max_s + 50)
            daily_avg = random.uniform(2, 25)
            dos = qty / daily_avg if daily_avg > 0 else 0

            session.add(Inventory(
                id=str(uuid.uuid4()),
                product_id=pid,
                store_id=sid,
                location_type="store",
                quantity=qty,
                safety_stock=safety,
                reorder_point=reorder,
                max_stock=max_s,
                daily_sales_avg=round(daily_avg, 1),
                days_of_supply=round(dos, 1),
                status=_status_from_qty(qty, safety, reorder, max_s),
                last_restocked=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
            ))
            inv_count += 1

    # Warehouse inventory (bulk stock)
    for sku, pid in product_ids.items():
        selected_whs = random.sample(list(wh_ids.items()), k=random.randint(1, 3))
        for wh_code, wid in selected_whs:
            qty = random.randint(500, 5000)
            session.add(Inventory(
                id=str(uuid.uuid4()),
                product_id=pid,
                warehouse_id=wid,
                location_type="warehouse",
                quantity=qty,
                safety_stock=200,
                reorder_point=500,
                max_stock=8000,
                daily_sales_avg=0,
                days_of_supply=0,
                status=_status_from_qty(qty, 200, 500, 8000),
            ))
            inv_count += 1

    counts["inventory"] = inv_count

    await session.flush()

    # Forecasts (7-day)
    forecast_count = 0
    today = datetime.utcnow().date()
    sample_products = random.sample(list(product_ids.items()), k=min(20, len(product_ids)))
    for sku, pid in sample_products:
        for day_offset in range(7):
            base_demand = random.uniform(10, 80)
            is_spike = random.random() < 0.08
            demand = base_demand * random.uniform(2.5, 4.0) if is_spike else base_demand
            session.add(Forecast(
                id=str(uuid.uuid4()),
                product_id=pid,
                forecast_date=today + timedelta(days=day_offset),
                horizon_days=7,
                predicted_demand=round(demand, 1),
                lower_bound=round(demand * 0.75, 1),
                upper_bound=round(demand * 1.3, 1),
                confidence=round(random.uniform(0.72, 0.96), 2),
                factors_used={
                    "seasonality": round(random.uniform(0.1, 0.4), 2),
                    "trend": round(random.uniform(0.2, 0.5), 2),
                    "promotion": round(random.uniform(0.0, 0.3), 2),
                    "day_of_week": round(random.uniform(0.05, 0.2), 2),
                },
                is_spike=is_spike,
                spike_magnitude=round(demand / base_demand, 1) if is_spike else None,
            ))
            forecast_count += 1
    counts["forecasts"] = forecast_count

    # Agent Events
    agent_names = ["orchestrator", "demand_forecast", "store_agent", "warehouse_agent"]
    event_types = ["decision", "alert", "recommendation"]
    event_titles = [
        "Detected low stock for {sku} at {store}",
        "Demand spike predicted for {category} in {region}",
        "Restock request generated: {qty} units of {sku}",
        "Warehouse allocation optimized for {region}",
        "Seasonal trend detected in {category}",
        "Inventory health degraded at {store}",
        "Emergency reorder triggered for {sku}",
        "Cross-dock shipment recommended for {store}",
    ]

    for i in range(30):
        sku = random.choice(PRODUCTS)["sku"]
        store = random.choice(STORES)["name"]
        category = random.choice(["Electronics", "Groceries", "Apparel", "Home", "Sports"])
        region = random.choice(["Northeast", "West", "Midwest", "South"])
        title = random.choice(event_titles).format(
            sku=sku, store=store, category=category, region=region,
            qty=random.randint(50, 500)
        )
        session.add(AgentEvent(
            id=str(uuid.uuid4()),
            agent_name=random.choice(agent_names),
            event_type=random.choice(event_types),
            severity=random.choice(["info", "info", "warning", "critical"]),
            title=title,
            reasoning=f"Analysis of current inventory levels and forecast data indicates action needed. Confidence based on historical pattern matching and demand model output.",
            confidence_score=round(random.uniform(0.65, 0.98), 2),
            payload={"sku": sku, "region": region},
            timestamp=datetime.utcnow() - timedelta(hours=random.randint(0, 72)),
        ))
    counts["agent_events"] = 30

    # Recommendations
    rec_types = ["restock", "transfer", "reorder", "alert", "optimize"]
    for i in range(15):
        product = random.choice(PRODUCTS)
        session.add(Recommendation(
            id=str(uuid.uuid4()),
            agent_name=random.choice(agent_names),
            recommendation_type=random.choice(rec_types),
            title=f"{'Restock' if random.random() > 0.5 else 'Transfer'} {product['name']}",
            description=f"Based on demand forecast and current stock levels, action is recommended for {product['name']} ({product['sku']}).",
            reason=f"Current stock is below reorder point. Forecasted demand exceeds available supply within the next 7 days.",
            confidence_score=round(random.uniform(0.70, 0.97), 2),
            factors_used={
                "low_stock": round(random.uniform(0.5, 0.9), 2),
                "high_demand": round(random.uniform(0.3, 0.8), 2),
                "seasonal": round(random.uniform(0.1, 0.4), 2),
            },
            priority=random.choice(["low", "medium", "high", "critical"]),
            estimated_cost=round(random.uniform(500, 5000), 2),
            estimated_savings=round(random.uniform(1000, 15000), 2),
            estimated_revenue_impact=round(random.uniform(2000, 25000), 2),
            created_at=datetime.utcnow() - timedelta(hours=random.randint(0, 48)),
        ))
    counts["recommendations"] = 15

    await session.commit()
    return counts
