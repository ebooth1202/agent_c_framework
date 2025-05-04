# src/agent_c_api/api/v2/history/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/history")

# Import routers
from .history import router as history_router
from .events import router as events_router
# from .replay import router as replay_router (will implement later if needed)

# Include routers
router.include_router(history_router)
router.include_router(events_router)
# router.include_router(replay_router)