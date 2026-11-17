from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.init_db import init_db

# Import routers
from app.api.auth import router as auth_router
from app.api.feed import router as feed_router
from app.api.references import router as references_router
from app.api.manufacturers import router as manufacturers_router
from app.api.products import router as products_router
from app.api.suppliers import router as suppliers_router
from app.api.sourcing import router as sourcing_router
from app.api.locations import router as locations_router
from app.api.quotations import router as quotations_router
from app.api.saved import router as saved_router
from app.api.connectors import router as connectors_router
from app.api.admin import router as admin_router
from app.api.categories import router as categories_router
from app.api.llm import router as llm_router
from app.api.pinterest import router as pinterest_router
from app.api.socialcrawl import router as socialcrawl_router
from app.api.discovery import router as discovery_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    import sys, os
    is_testing = (
        "pytest" in sys.modules
        or "_pytest" in sys.modules
        or bool(os.environ.get("PYTEST_CURRENT_TEST"))
        or os.environ.get("TESTING") == "1"
    )
    if not is_testing:
        # Startup: ensure tables and seed data exist
        init_db()
        # Launch daily 6:00 AM IST automated data collection scheduler in background thread
        from app.services.daily_collection_service import start_daily_collection_scheduler
        start_daily_collection_scheduler()
    yield

app = FastAPI(
    title="Arch_Aware API",
    description="Arch_Aware — Architecture Inspiration, Material Intelligence & Supplier Discovery Platform API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration — strict env allowlist in production, localhost origins in dev
import os as _os
_raw_cors = _os.environ.get("NIVORA_CORS_ORIGINS", "")
_cors_origins = (
    [o.strip() for o in _raw_cors.split(",") if o.strip()]
    if _raw_cors.strip()
    else [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all route groups
api_prefix = settings.API_V1_STR
app.include_router(auth_router, prefix=api_prefix)
app.include_router(feed_router, prefix=api_prefix)
app.include_router(references_router, prefix=api_prefix)
app.include_router(categories_router, prefix=api_prefix)
app.include_router(manufacturers_router, prefix=api_prefix)
app.include_router(products_router, prefix=api_prefix)
app.include_router(suppliers_router, prefix=api_prefix)
app.include_router(sourcing_router, prefix=api_prefix)
app.include_router(locations_router, prefix=api_prefix)
app.include_router(quotations_router, prefix=api_prefix)
app.include_router(saved_router, prefix=api_prefix)
app.include_router(connectors_router, prefix=api_prefix)
app.include_router(admin_router, prefix=api_prefix)
app.include_router(llm_router, prefix=api_prefix)
app.include_router(pinterest_router, prefix=api_prefix)
app.include_router(socialcrawl_router, prefix=api_prefix)
app.include_router(discovery_router, prefix=api_prefix)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Arch_Aware API",
        "version": "1.0.0",
        "demo_mode": settings.DEMO_MODE
    }
