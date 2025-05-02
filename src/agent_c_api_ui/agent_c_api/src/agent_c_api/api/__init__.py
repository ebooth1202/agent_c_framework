from fastapi import APIRouter
import logging
from .v1 import router as v1_router
from .v2 import router as v2_router  # Add v2 router import

router = APIRouter(prefix="/api")
router.include_router(v1_router)
router.include_router(v2_router)  # Include v2 router
# logging.debug(f"Main API router prefix: {router.prefix}")