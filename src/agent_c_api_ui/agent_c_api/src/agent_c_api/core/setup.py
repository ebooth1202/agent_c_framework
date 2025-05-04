import os
import re

from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import your settings and AgentManager
from agent_c_api.config.env_config import settings
from agent_c_api.core.agent_manager import UItoAgentBridgeManager
from agent_c_api.core.util.logging_utils import LoggingManager
from agent_c_api.core.util.middleware_logging import APILoggingMiddleware

logging_manager = LoggingManager(__name__)
logger = logging_manager.get_logger()


def get_origins_regex():
    allowed_hosts_str = os.getenv("API_ALLOWED_HOSTS", "localhost,.local")
    patterns = [pattern.strip() for pattern in allowed_hosts_str.split(",")]

    regex_parts = []
    for pattern in patterns:
        if pattern.startswith("."):
            # Domain suffix like .local or .company.com
            suffix = re.escape(pattern)
            regex_parts.append(f"[^/]+{suffix}")
        else:
            # Specific host like localhost (with optional port)
            host = re.escape(pattern)
            regex_parts.append(f"{host}(:\\d+)?")

    # Combine all patterns with OR operator
    return f"^https?://({"|".join(regex_parts)})$"

def create_application(router: APIRouter, **kwargs) -> FastAPI:
    """
    Create and configure the FastAPI application.

    This function sets up the application metadata, initializes the shared
    AgentManager resource via a lifespan handler, adds any required middleware,
    and includes the given router.
    """

    # Define a lifespan handler for startup and shutdown tasks.
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Startup: Initialize your shared AgentManager instance.
        app.state.agent_manager = UItoAgentBridgeManager()
        yield
        # Shutdown: Optionally, perform any cleanup tasks.
        # For example: await app.state.agent_manager.cleanup_all_sessions()

    # Set up basic metadata from your settings (or fallback defaults).
    metadata = {
        "title": getattr(settings, "APP_NAME", "Agent C FastAPI Backend"),
        "description": getattr(settings, "APP_DESCRIPTION", "A FastAPI backend for Agent C"),
        "contact": {
            "name": getattr(settings, "CONTACT_NAME", "Joseph Ours"),
            "email": getattr(settings, "CONTACT_EMAIL", "joseph.ours@centricconsulting.com")
        },
        "license_info": {
            "name": getattr(settings, "LICENSE_NAME", "BSD")
        }
    }
    kwargs.update(metadata)

    # Create the FastAPI application with the lifespan handler.
    app = FastAPI(lifespan=lifespan, **kwargs)
    print(get_origins_regex())
    # Add CORS middleware (adjust origins as necessary)
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=get_origins_regex(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Try to get the environment from settings, environment variables, or default to 'development'
    environment = getattr(settings, "ENV", os.getenv("ENV", "development")).lower()
    is_production = environment == "production"

    logger.info(f"Application running in {environment} environment")

    # Add our custom logging middleware
    # Enable request body logging in development but not in production
    app.add_middleware(
        APILoggingMiddleware,
        log_request_body=not is_production,
        log_response_body=False
    )

    # Include your router containing your API endpoints.
    app.include_router(router)

    logger.info(
        f"Application created: {getattr(settings, 'APP_NAME', 'Agent C API')} v{getattr(settings, 'APP_VERSION')}")
    logger.debug(f"API documentation available at: {getattr(settings, 'DOCS_URL', '/docs')}")

    return app
