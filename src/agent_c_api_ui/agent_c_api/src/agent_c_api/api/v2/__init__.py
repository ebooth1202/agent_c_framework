# src/agent_c_api/api/v2/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/v2")

# These routers will be included as they're implemented
from .config import router as config_router
# from .sessions import router as sessions_router
# from .history import router as history_router
# from .debug import router as debug_router

router.include_router(config_router)
# router.include_router(sessions_router)
# router.include_router(history_router)
# router.include_router(debug_router)