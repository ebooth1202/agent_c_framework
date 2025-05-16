import time
import uvicorn
import logging
from redis import asyncio as aioredis
from dotenv import load_dotenv
from fastapi.logger import logger as fastapi_logger
from agent_c_api.core.util.logging_utils import LoggingManager
from agent_c_api.api import router
from agent_c_api.config.env_config import settings
from agent_c_api.core.setup import create_application
from fastapi import FastAPI

load_dotenv(override=True)

# dictionary to track performance metrics
_timing = {
    "start_time": time.time(),
    "app_creation_start": 0,
    "app_creation_end": 0
}

# Configure logging
LoggingManager.configure_root_logger()
LoggingManager.configure_external_loggers()
LoggingManager.configure_external_loggers({
    "agent_c_api.core.util.middleware_logging": "WARNING"  # Show INFO logs for middleware_logging, debug is too noisy
})

# Configure specific loggers for FastAPI components
logging_manager = LoggingManager("agent_c_api")
logger = logging_manager.get_logger()

# This ensures sub-loggers own logs use our formatting
uvicorn_logger = logging.getLogger("uvicorn")
sub_loggers = [fastapi_logger, uvicorn_logger]

for sub_logger in sub_loggers:
    sub_logger.handlers = []
    for handler in logger.handlers:
        sub_logger.addHandler(handler)
    sub_logger.setLevel(logger.level)
    sub_logger.propagate = False

# Adjust levels for specific uvicorn loggers rather than removing handlers
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)

# Redis connection instance
redis_client = None

async def init_redis() -> None:
    """Initialize Redis connection."""
    global redis_client
    logger.info("Initializing Redis connection...")

    try:
        redis_client = await aioredis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            username=settings.REDIS_USERNAME,
            password=settings.REDIS_PASSWORD,
            encoding="utf8",
            decode_responses=True
        )
        await redis_client.ping()
        logger.info("Redis connection established successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Redis: {str(e)}")
        raise

async def close_redis() -> None:
    """Close Redis connection."""
    global redis_client
    if redis_client:
        logger.info("Closing Redis connection...")
        await redis_client.close()
        logger.info("Redis connection closed")

# Create and configure the FastAPI application
logger.info("Creating API application")
_timing["app_creation_start"] = time.time()

# Create the application with our router
app = create_application(router=router, settings=settings)

# Add startup and shutdown events for Redis
@app.on_event("startup")
async def startup_event():
    await init_redis()

@app.on_event("shutdown")
async def shutdown_event():
    await close_redis()

_timing["app_creation_end"] = time.time()
logger.info(f"Registered {len(app.routes)} routes")
logger.info(f"API application created in {(_timing['app_creation_end'] - _timing['app_creation_start']):.2f} seconds")
logger.info("API versioning using directory structure with paths '/api/v1' and '/api/v2'")

def run():
    """Entrypoint for the API"""
    logger.info(f"FastAPI Reload Setting is: {settings.RELOAD}. Starting Uvicorn")
    logger.info(f"Agent_C API server running on {settings.HOST}:{settings.PORT}")
    
    # If reload is enabled, we must use the import string
    if settings.RELOAD:
        uvicorn.run(
            "agent_c_api.main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=settings.RELOAD,
            log_level=LoggingManager.LOG_LEVEL.lower() if hasattr(LoggingManager, 'LOG_LEVEL') else "info"
        )
    else:
        # Otherwise, we can use the app object directly for better debugging
        uvicorn.run(
            app,
            host=settings.HOST,
            port=settings.PORT,
            log_level=LoggingManager.LOG_LEVEL.lower() if hasattr(LoggingManager, 'LOG_LEVEL') else "info"
        )
    logger.info(f"Exiting Run Loop: {time.time()}")

if __name__ == "__main__":
    run()