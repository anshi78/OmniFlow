"""OmniFlow AI — FastAPI Application Entry Point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import init_db, close_db, async_session_factory
from app.seed.seed_data import seed_database
from app.api import auth, products, stores, warehouses, inventory, shipments, forecasts, simulations, agents, dashboard, websocket

settings = get_settings()
logger = logging.getLogger("omniflow")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan — startup and shutdown hooks."""
    # Startup
    logger.info("🚀 Starting OmniFlow AI...")

    # Initialize database tables (dev mode with SQLite)
    if settings.is_sqlite or settings.is_development:
        await init_db()
        logger.info("✅ Database tables created")

        # Seed with sample data
        async with async_session_factory() as session:
            result = await seed_database(session)
            if result.get("status") == "already_seeded":
                logger.info("📦 Database already seeded")
            else:
                logger.info(f"🌱 Database seeded: {result}")

    logger.info("✅ OmniFlow AI is ready!")
    yield

    # Shutdown
    await close_db()
    logger.info("🛑 OmniFlow AI shutdown complete")


app = FastAPI(
    title="OmniFlow AI",
    description="Multi-Agent Retail Inventory Optimization System — AI-powered supply chain Digital Twin",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(auth.router, prefix="/api")
app.include_router(products.router, prefix="/api")
app.include_router(stores.router, prefix="/api")
app.include_router(warehouses.router, prefix="/api")
app.include_router(inventory.router, prefix="/api")
app.include_router(shipments.router, prefix="/api")
app.include_router(forecasts.router, prefix="/api")
app.include_router(simulations.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(websocket.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "name": "OmniFlow AI",
        "version": "1.0.0",
        "status": "operational",
        "description": "Multi-Agent Retail Inventory Optimization System",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "environment": settings.app_env}
