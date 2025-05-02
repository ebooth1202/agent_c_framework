# src/agent_c_api/api/v2/sessions/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/sessions")

# These routers will be included as they're implemented
# from .sessions import router as sessions_router
# from .agent import router as agent_router
# from .tools import router as tools_router
# from .chat import router as chat_router
# from .files import router as files_router

# router.include_router(sessions_router)
# router.include_router(agent_router)
# router.include_router(tools_router)
# router.include_router(chat_router)
# router.include_router(files_router)