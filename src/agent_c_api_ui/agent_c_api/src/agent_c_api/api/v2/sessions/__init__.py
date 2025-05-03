from fastapi import APIRouter
from .router import router as sessions_router
from .agent import router as agent_router

router = APIRouter()
router.include_router(sessions_router)
router.include_router(agent_router)

__all__ = ["router"]