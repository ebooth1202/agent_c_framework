from fastapi import APIRouter
from .session import router as sessions_router

router = APIRouter(tags=["avatar"])
router.include_router(sessions_router)