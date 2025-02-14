from fastapi import APIRouter
import logging
from .v1 import router as v1_router

router = APIRouter(prefix="/api")
router.include_router(v1_router)
# logging.debug(f"Main API router prefix: {router.prefix}")