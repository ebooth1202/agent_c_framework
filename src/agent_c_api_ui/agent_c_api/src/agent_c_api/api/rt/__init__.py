from fastapi import APIRouter, Request
from .session import router as sessions_router

def get_agent_manager(request: Request) -> 'RealtimeSessionManager':
    return request.app.state.realtime_manager

router = APIRouter(tags=["rt"])
router.include_router(sessions_router)