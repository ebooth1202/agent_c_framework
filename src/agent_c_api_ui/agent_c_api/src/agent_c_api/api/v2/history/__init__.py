# src/agent_c_api/api/v2/history/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/history")

# Import routers
from .history import router as history_router
from .events import router as events_router
# Note: Replay functionality has been incorporated into the events router
# instead of having a separate replay router as originally planned

# Include routers
router.include_router(history_router)
router.include_router(events_router)