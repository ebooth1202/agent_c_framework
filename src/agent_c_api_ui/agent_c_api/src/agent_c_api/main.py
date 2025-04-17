import uvicorn
import logging
import time
from typing import Dict, Any
from pyinstrument import Profiler

from dotenv import load_dotenv
from fastapi.logger import logger as fastapi_logger

from agent_c_api.core.util.logging_utils import LoggingManager
from agent_c_api.config.env_config import settings
from agent_c_api.api import router
from agent_c_api.core.setup import create_application

# Start profiling right at the beginning
startup_profiler = None
if settings.PROFILING_ENABLED:
    startup_profiler = Profiler(async_mode="enabled")
    startup_profiler.start()

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

# Handle optional module imports
optional_modules = {
    "mermaidjs": "Mermaid JS visualization",
    "agent_c_demo.tools": "Demo tools",
    "agent_c_voice.tools": "Voice processing tools",
    "agent_c_rag.tools": "RAG tools"
}

available_modules = {}

for module_name, description in optional_modules.items():
    try:
        module = __import__(module_name, fromlist=[''])
        available_modules[module_name] = module
        logger.debug(f"Optional module loaded: {module_name}")
    except ImportError:
        logger.info(f"{description} not available: No module named '{module_name}'")

logger.info(f"Creating API application")
_timing["app_creation_start"] = time.time()
app = create_application(router=router, settings=settings)
_timing["app_creation_end"] = time.time()
logger.info(f"Application creation took {_timing['app_creation_end'] - _timing['app_creation_start']:.2f} seconds")
logger.info(f"Registered {len(app.routes)} routes")

# Add middleware for per-request profiling
# if settings.PROFILING_ENABLED:
#     from fastapi_profiler import PyInstrumentProfilerMiddleware
#
#     logger.info("Adding request profiler middleware")
#     app.add_middleware(
#         PyInstrumentProfilerMiddleware,
#         server_app=app,
#         profiler_output_type="html",
#         is_print_each_request=False,
#         open_in_browser=False,
#         html_file_name="request_profile.html",
#     )


# Add a startup event handler to capture when the application is fully started
@app.middleware("http")
async def first_request_middleware(request, call_next):
    # This will execute on the first request
    global startup_profiler
    if startup_profiler and hasattr(app.state, "startup_profile_captured") is False:
        # Stop the profiler and generate report
        startup_profiler.stop()
        startup_profiler.write_html("startup_profile.html")
        logger.info("Startup profile captured and saved to startup_profile.html")
        # Open in browser if desired
        if settings.PROFILING_ENABLED:
            try:
                startup_profiler.open_in_browser()
            except Exception as e:
                logger.warning(f"Could not open profile in browser: {e}")
        app.state.startup_profile_captured = True

    response = await call_next(request)
    return response


def run():
    """Entrypoint for the API"""
    global _timing
    # Reset the start time right before starting the server
    _timing["start_time"] = time.time()

    logger.info(f"Starting API server on {settings.HOST}:{settings.PORT}")
    logger.info(f"Starting Uvicorn with settings.RELOAD={settings.RELOAD}")

    log_level = LoggingManager.LOG_LEVEL.lower() if hasattr(LoggingManager, 'LOG_LEVEL') else "info"

    if settings.RELOAD:
        # In reload mode, we use the module import string
        uvicorn.run("agent_c_api.main:app", host=settings.HOST, port=settings.PORT,
                    reload=True, log_level=log_level)
    else:
        # In non-reload mode, use the app object directly
        config = uvicorn.Config(app, host=settings.HOST, port=settings.PORT,
                                log_level=log_level)
        server = uvicorn.Server(config)
        server.run()


if __name__ == "__main__":
    run()