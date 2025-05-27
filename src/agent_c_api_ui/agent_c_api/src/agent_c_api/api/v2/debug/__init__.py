# src/agent_c_api/api/v2/debug/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/debug")

# Include the debug router
from .debug import router as debug_router
from .redis_test import router as redis_test_router
from .health import router as health_router

router.include_router(debug_router)
router.include_router(redis_test_router)
router.include_router(health_router)