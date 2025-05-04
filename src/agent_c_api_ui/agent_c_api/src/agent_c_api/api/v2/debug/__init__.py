# src/agent_c_api/api/v2/debug/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/debug")

# Include the debug router
from .debug import router as debug_router

router.include_router(debug_router)