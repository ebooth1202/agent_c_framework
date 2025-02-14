import uvicorn
import logging

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi.logger import logger as fastapi_logger

from agent_c_api.core.util.logging_utils import LoggingManager

from .config.env_config import settings
from .api import router
from .core.setup import create_application

load_dotenv(override=True)

# Disable FastAPI's default logging
logging.getLogger("uvicorn.access").handlers = []
logging.getLogger("uvicorn.error").handlers = []
fastapi_logger.handlers = []
# Setup custom log handling
logging_manager = LoggingManager("main")
logger = logging_manager.get_logger()
# Set FastAPI logger to use the same handlers as our custom logger
fastapi_logger.handlers = logger.handlers
fastapi_logger.setLevel(logger.level)


app = create_application(router=router, settings=settings)
for route in app.routes:
    logger.debug(f"Registered route: {route.path}")

def run():
    """Entrypoint for the API"""
    uvicorn.run("agent_c_api.main:app", host=settings.HOST, port=settings.PORT, reload=settings.RELOAD)