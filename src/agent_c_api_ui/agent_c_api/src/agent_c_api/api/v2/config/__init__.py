# src/agent_c_api/api/v2/config/__init__.py
from fastapi import APIRouter

router = APIRouter(prefix="/config")

# These routers will be included as they're implemented
# from .models import router as models_router
# from .personas import router as personas_router
# from .tools import router as tools_router
# from .system import router as system_router

# router.include_router(models_router)
# router.include_router(personas_router)
# router.include_router(tools_router)
# router.include_router(system_router)