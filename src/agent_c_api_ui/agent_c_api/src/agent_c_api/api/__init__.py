from fastapi import APIRouter
import logging
from .v1 import router as v1_router
from .v2 import router as v2_router

# Create main API router with explicit /api prefix
router = APIRouter(prefix="/api")

# Include versioned routers with their respective prefixes
router.include_router(v1_router, prefix="/v1")
router.include_router(v2_router, prefix="/v2")

logging.info(f"Main API router configured with prefix: {router.prefix}")
logging.info(f"API endpoints will be accessible at /api/v1/... and /api/v2/...")