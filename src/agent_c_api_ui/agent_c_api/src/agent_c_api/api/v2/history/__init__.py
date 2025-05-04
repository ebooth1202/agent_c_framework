# src/agent_c_api/api/v2/history/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/history")

# These routers will be included as they're implemented
from .router import router as history_router
# from .events import router as events_router
# from .replay import router as replay_router

router.include_router(history_router)
# router.include_router(events_router)
# router.include_router(replay_router)