# agent_c_api/core/setup.py
from fastapi import FastAPI, APIRouter
from starlette.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import your settings and AgentManager
from agent_c_api.config.env_config import settings
from agent_c_api.core.agent_manager import AgentManager

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
        app.state.agent_manager = AgentManager()
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

    # Add CORS middleware (adjust origins as necessary)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include your router containing your API endpoints.
    app.include_router(router)

    return app
