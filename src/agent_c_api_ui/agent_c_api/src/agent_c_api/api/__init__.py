from fastapi import APIRouter
from .v1 import router as v1_router
from .v2 import router as v2_router
from .rt import router as rt_router

# Create main API router with explicit /api prefix
router = APIRouter(prefix="/api")

# Include versioned routers with their respective prefixes
router.include_router(v1_router, prefix="/v1")
router.include_router(v2_router, prefix="/v2")
router.include_router(rt_router, prefix="/rt")
