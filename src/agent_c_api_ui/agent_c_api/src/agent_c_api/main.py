import uvicorn
import logging

from dotenv import load_dotenv
from fastapi.logger import logger as fastapi_logger

from agent_c_api.core.util.logging_utils import LoggingManager

from .config.env_config import settings
from .api import router
from .core.setup import create_application

load_dotenv(override=True)

# Configure root logger
LoggingManager.configure_root_logger()

# Configure external loggers
# There are some loggers that we've configured to only show errors
LoggingManager.configure_external_loggers()

# Custom overrides for Logging
LoggingManager.configure_external_loggers({
    # "httpx": "ERROR",  # Only show errors for httpx
    "agent_c_api.core.util.middleware_logging": "WARNING"  # Show INFO logs for middleware_logging, debug is too noisy
})

# Configure specific loggers for FastAPI components
logging_manager = LoggingManager("agent_c_api")
logger = logging_manager.get_logger()

# Set FastAPI logger to use our configuration
# This ensures FastAPI's own logs use our formatting
fastapi_logger.handlers = []
for handler in logger.handlers:
    fastapi_logger.addHandler(handler)
fastapi_logger.setLevel(logger.level)
fastapi_logger.propagate = False

# Also properly configure uvicorn's loggers
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = []
for handler in logger.handlers:
    uvicorn_logger.addHandler(handler)
uvicorn_logger.setLevel(logger.level)
uvicorn_logger.propagate = False

# Disable specific noisy loggers that might interfere
logging.getLogger("uvicorn.access").handlers = []
logging.getLogger("uvicorn.error").handlers = []


app = create_application(router=router, settings=settings)
# for route in app.routes:
#     logger.info(f"Registered route: {route.path}")

logger.info(f"Registered {len(app.routes)} routes")

def run():
    """Entrypoint for the API"""
    logger.info(f"Starting API server on {settings.HOST}:{settings.PORT}")
    uvicorn.run("agent_c_api.main:app", host=settings.HOST, port=settings.PORT,
                reload=settings.RELOAD, log_level=LoggingManager.LOG_LEVEL.lower())