"""
Configuration and fixtures for v2 API unit tests.

Provides common fixtures and configuration for testing the v2 API
including Redis mocking and dependency injection overrides.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock
from redis import asyncio as aioredis
from fastapi.testclient import TestClient

from agent_c_api.main import app
from agent_c_api.api.dependencies import (
    get_redis_client,
    get_redis_client_optional,
    get_redis_client_managed
)
from agent_c_api.core.repositories.dependencies import (
    get_session_repository,
    get_session_repository_optional,
    get_user_repository,
    get_user_repository_optional
)


@pytest_asyncio.fixture
async def mock_redis_client():
    """
    Create a mock Redis client for testing.
    
    Returns:
        AsyncMock: A properly configured mock Redis client
    """
    client = AsyncMock(spec=aioredis.Redis)
    
    # Configure common Redis operations
    client.get.return_value = None
    client.set.return_value = True
    client.delete.return_value = 1
    client.exists.return_value = False
    client.keys.return_value = []
    client.mget.return_value = []
    client.lpush.return_value = 1
    client.lrange.return_value = []
    client.llen.return_value = 0
    client.aclose.return_value = None
    
    return client


@pytest_asyncio.fixture
async def mock_session_repository(mock_redis_client):
    """
    Create a mock SessionRepository for testing.
    
    Returns:
        MagicMock: A configured mock SessionRepository
    """
    from agent_c_api.core.repositories.session_repository import SessionRepository
    
    repo = MagicMock(spec=SessionRepository)
    repo.redis_client = mock_redis_client
    
    # Configure common repository operations
    repo.create_session = AsyncMock(return_value=True)
    repo.get_session = AsyncMock(return_value=None)
    repo.update_session = AsyncMock(return_value=True)
    repo.delete_session = AsyncMock(return_value=True)
    repo.list_sessions = AsyncMock(return_value=[])
    
    return repo


@pytest_asyncio.fixture
async def mock_user_repository(mock_redis_client):
    """
    Create a mock UserRepository for testing.
    
    Returns:
        MagicMock: A configured mock UserRepository
    """
    from agent_c_api.core.repositories.user_repository import UserRepository
    
    repo = MagicMock(spec=UserRepository)
    repo.redis_client = mock_redis_client
    
    # Configure common repository operations
    repo.create_user = AsyncMock(return_value=True)
    repo.get_user = AsyncMock(return_value=None)
    repo.update_user = AsyncMock(return_value=True)
    repo.delete_user = AsyncMock(return_value=True)
    repo.update_user_preferences = AsyncMock(return_value=True)
    
    return repo


@pytest_asyncio.fixture
async def mock_chat_repository(mock_redis_client):
    """
    Create a mock ChatRepository for testing.
    
    Returns:
        MagicMock: A configured mock ChatRepository
    """
    from agent_c_api.core.repositories.chat_repository import ChatRepository
    
    repo = MagicMock(spec=ChatRepository)
    repo.redis_client = mock_redis_client
    repo.session_id = "test-session-123"
    
    # Configure common repository operations
    repo.add_message = AsyncMock(return_value=True)
    repo.get_messages = AsyncMock(return_value=[])
    repo.get_message_count = AsyncMock(return_value=0)
    repo.clear_messages = AsyncMock(return_value=True)
    
    return repo


@pytest_asyncio.fixture
def client_with_mocked_redis(mock_redis_client):
    """
    Create a test client with mocked Redis dependencies.
    
    This fixture overrides the Redis dependencies to use mocked clients,
    allowing tests to run without requiring actual Redis connections.
    
    Returns:
        TestClient: A FastAPI test client with mocked Redis
    """
    # Override Redis dependencies
    app.dependency_overrides[get_redis_client] = lambda: mock_redis_client
    app.dependency_overrides[get_redis_client_optional] = lambda: mock_redis_client
    
    # Create test client
    client = TestClient(app)
    
    yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
def client_with_redis_unavailable():
    """
    Create a test client with Redis dependencies that simulate Redis being unavailable.
    
    This fixture overrides the Redis dependencies to simulate Redis failures,
    allowing tests to verify graceful degradation behavior.
    
    Returns:
        TestClient: A FastAPI test client with failing Redis dependencies
    """
    from fastapi import HTTPException
    
    def failing_redis_client():
        raise HTTPException(status_code=503, detail="Redis service unavailable")
    
    def optional_redis_client():
        return None
    
    # Override Redis dependencies to simulate failures
    app.dependency_overrides[get_redis_client] = failing_redis_client
    app.dependency_overrides[get_redis_client_optional] = optional_redis_client
    
    # Create test client
    client = TestClient(app)
    
    yield client
    
    # Clean up dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture
def sample_session_data():
    """
    Sample session data for testing.
    
    Returns:
        dict: A complete session data structure for testing
    """
    return {
        "id": "test-session-123",
        "model_id": "gpt-4",
        "persona_id": "programmer",
        "created_at": "2025-05-24T13:00:00Z",
        "last_activity": "2025-05-24T13:30:00Z",
        "agent_internal_id": "agent-456",
        "tools": ["search", "calculator"],
        "temperature": 0.7,
        "reasoning_effort": 30,
        "budget_tokens": None,
        "max_tokens": 2000,
        "custom_prompt": None
    }


@pytest.fixture
def sample_user_data():
    """
    Sample user data for testing.
    
    Returns:
        dict: A complete user data structure for testing
    """
    return {
        "id": "test-user-123",
        "email": "test@example.com",
        "name": "Test User",
        "created_at": "2025-05-24T13:00:00Z",
        "last_login": "2025-05-24T13:30:00Z",
        "preferences": {
            "theme": "dark",
            "language": "en"
        }
    }


@pytest.fixture
def sample_message_data():
    """
    Sample message data for testing.
    
    Returns:
        dict: A complete message data structure for testing
    """
    return {
        "id": "msg-123",
        "session_id": "test-session-123",
        "role": "user",
        "content": "Hello, how are you?",
        "timestamp": "2025-05-24T13:00:00Z",
        "metadata": {
            "model": "gpt-4",
            "tokens": 15
        }
    }


# Test markers for categorizing tests
pytest_plugins = []

# Custom markers for Redis tests
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "redis: marks tests as Redis-related"
    )
    config.addinivalue_line(
        "markers", "repositories: marks tests as repository-related"
    )
    config.addinivalue_line(
        "markers", "error_scenarios: marks tests as error scenario tests"
    )
    config.addinivalue_line(
        "markers", "dependencies: marks tests as dependency injection tests"
    )