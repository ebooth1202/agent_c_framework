import uvicorn
import logging
import time

from dotenv import load_dotenv
from fastapi.logger import logger as fastapi_logger
# Removed VersionedFastAPI import - using directory structure for versioning

from agent_c_api.core.util.logging_utils import LoggingManager

from agent_c_api.config.env_config import settings
from agent_c_api.api import router
from agent_c_api.core.setup import create_application

load_dotenv(override=True)

# Initialize timing dictionary to track performance metrics
_timing = {
    "start_time": time.time(),
    "app_creation_start": 0,
    "app_creation_end": 0
}

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

# Configure uvicorn's loggers
uvicorn_logger = logging.getLogger("uvicorn")
uvicorn_logger.handlers = []
for handler in logger.handlers:
    uvicorn_logger.addHandler(handler)
uvicorn_logger.setLevel(logger.level)
uvicorn_logger.propagate = False

# Adjust levels for specific uvicorn loggers rather than removing handlers
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)

logger.info(f"Creating API application")
_timing["app_creation_start"] = time.time()

# Create the application with our router
app = create_application(router=router, settings=settings)

_timing["app_creation_end"] = time.time()
logger.info(f"Registered {len(app.routes)} routes")
logger.info(f"API application created in {(_timing['app_creation_end'] - _timing['app_creation_start']):.2f} seconds")
logger.info("API versioning using directory structure with paths '/api/v1' and '/api/v2'")
logger.info(f"FastAPI Reload Setting is: {settings.RELOAD}.  Starting Uvicorn")
logger.info(f"Agent_C API server running on {settings.HOST}:{settings.PORT}")

def run():
    """Entrypoint for the API"""
    # If reload is enabled, we must use the import string
    if settings.RELOAD:
        uvicorn.run("agent_c_api.main:app", host=settings.HOST, port=settings.PORT,
                    reload=settings.RELOAD, log_level=LoggingManager.LOG_LEVEL.lower() if hasattr(LoggingManager, 'LOG_LEVEL') else "info")
    else:
        # Otherwise, we can use the app object directly for better debugging
        uvicorn.run(app, host=settings.HOST, port=settings.PORT,
                    log_level=LoggingManager.LOG_LEVEL.lower() if hasattr(LoggingManager, 'LOG_LEVEL') else "info")
    logger.info(f"Exiting Run Loop: {time.time()}")

if __name__ == "__main__":
    run()