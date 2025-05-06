# tests/conftest.py

import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from agent_c_api.main import app


#################################################
# Global Setup and Teardown Fixtures
#################################################

@pytest.fixture(autouse=True, scope="function")
async def setup_test_cache():
    """
    Fixture to properly initialize FastAPICache for testing and make the cache decorator a no-op.
    
    This fixture:
    1. Initializes the FastAPICache system (required by the framework)
    2. Makes the @cache decorator function as a pass-through (no actual caching)
    3. Cleans up after each test
    """
    # Save the original cache implementation
    original_cache = FastAPICache.cache
    
    # Initialize the cache system with a test backend
    # This is necessary to avoid "You must call init first!" errors
    FastAPICache.init(InMemoryBackend(), prefix="agent_c_api_cache")
    
    # Replace the cache decorator with a pass-through version
    def pass_through_decorator(*args, **kwargs):
        def inner(func):
            # Just return the original function unchanged
            return func
        return inner
    
    # Apply our no-op version
    FastAPICache.cache = pass_through_decorator
    
    # Let the test run
    yield
    
    # Clean up: restore the original cache implementation and clear the cache
    FastAPICache.cache = original_cache
    await FastAPICache.clear()


#################################################
# API Testing Fixtures
#################################################

@pytest.fixture
def client():
    """
    Test client fixture for the FastAPI application.
    
    Returns:
        TestClient: A configured FastAPI test client.
    """
    return TestClient(app)


#################################################
# Mock Core Services
#################################################

@pytest.fixture
def mock_agent_manager():
    """
    Fixture for a mocked UItoAgentBridgeManager.
    
    Returns:
        MagicMock: A configured mock of the agent manager.
    """
    manager = MagicMock()
    manager.create_session = AsyncMock(return_value=("test_ui_session_id", "test_agent_session_id"))
    manager.update_agent_tools = AsyncMock()
    manager.get_agent_config = AsyncMock(return_value={})
    manager.get_agent_tools = AsyncMock(return_value=["search", "calculator"])
    manager.update_agent_settings = AsyncMock()
    manager.delete_session = AsyncMock(return_value=True)
    
    # Set up mock session data
    manager.ui_sessions = {
        "test_session_1": {
            "model_name": "gpt-4",
            "persona_name": "programmer",
            "created_at": datetime.now(),
            "last_activity": datetime.now(),
            "agent_session_id": "agent_123",
            "temperature": 0.7,
            "reasoning_effort": 30,
            "budget_tokens": None,
            "max_tokens": 2000,
            "custom_prompt": None,
        },
        "test_session_2": {
            "model_name": "claude-3",
            "persona_name": "default",
            "created_at": datetime.now(),
            "last_activity": None,
            "agent_session_id": "agent_456",
            "temperature": 0.9,
            "reasoning_effort": None,
            "budget_tokens": 15000,
            "max_tokens": 4000,
            "custom_prompt": "Custom system prompt",
        }
    }
    
    return manager


#################################################
# Common Test Data Fixtures
#################################################

@pytest.fixture
def sample_session_detail():
    """
    Fixture providing a sample session detail object for testing.
    
    Returns:
        SessionDetail: A populated session detail object.
    """
    from agent_c_api.api.v2.models import SessionDetail
    
    return SessionDetail(
        id="test_session_1",
        model_id="gpt-4",
        persona_id="programmer",
        created_at=datetime.now(),
        last_activity=datetime.now(),
        agent_internal_id="agent_123",
        tools=["search", "calculator"],
        temperature=0.7,
        reasoning_effort=30,
        budget_tokens=None,
        max_tokens=2000,
        custom_prompt=None
    )


@pytest.fixture
def sample_session_list():
    """
    Fixture providing a sample session list response for testing.
    
    Returns:
        SessionListResponse: A populated session list response.
    """
    from agent_c_api.api.v2.models import SessionListResponse, SessionSummary
    
    return SessionListResponse(
        items=[
            SessionSummary(
                id="test_session_1",
                model_id="gpt-4",
                persona_id="programmer",
                created_at=datetime.now(),
                last_activity=datetime.now()
            ),
            SessionSummary(
                id="test_session_2",
                model_id="claude-3",
                persona_id="default",
                created_at=datetime.now(),
                last_activity=None
            )
        ],
        total=2,
        limit=10,
        offset=0
    )