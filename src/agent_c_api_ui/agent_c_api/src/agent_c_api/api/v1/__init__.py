from fastapi import APIRouter

from .sessions import router as sessions_router
from .models import router as models_router
from .tools import router as tools_router
from .agent import router as agent_router
from .chat import router as chat_router
from .files import router as files_router
from .personas import router as personas_router

import logging
router = APIRouter(prefix="/v1")

# main api routes
router.include_router(sessions_router)
router.include_router(models_router)
router.include_router(tools_router)
router.include_router(agent_router)
router.include_router(chat_router)
router.include_router(files_router)
router.include_router(personas_router)
