"""
Unit tests for Redis repository dependency injection.

Tests the repository dependency injection functions in core/repositories/dependencies.py
including SessionRepository and UserRepository dependencies.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from redis import asyncio as aioredis

from agent_c_api.core.repositories.dependencies import (
    get_session_repository,
    get_session_repository_optional,
    get_user_repository,
    get_user_repository_optional
)
from agent_c_api.core.repositories.session_repository import SessionRepository
from agent_c_api.core.repositories.user_repository import UserRepository


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.repositories
class TestSessionRepositoryDependencies:
    """Test SessionRepository dependency injection functions."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a mock Redis client for testing."""
        client = AsyncMock(spec=aioredis.Redis)
        return client
    
    async def test_get_session_repository_success(self, mock_redis_client):
        """Test get_session_repository returns repository with Redis client."""
        with patch('agent_c_api.core.repositories.dependencies.get_redis_client') as mock_get_client:
            # Mock the dependency function to return our mock client
            mock_get_client.return_value = mock_redis_client
            
            # Call the dependency function directly (simulating FastAPI injection)
            result = await get_session_repository(mock_redis_client)
            
            assert isinstance(result, SessionRepository)
            assert result.redis_client == mock_redis_client
    
    async def test_get_session_repository_optional_success(self, mock_redis_client):
        """Test get_session_repository_optional returns repository when Redis available."""
        result = await get_session_repository_optional(mock_redis_client)
        
        assert isinstance(result, SessionRepository)
        assert result.redis_client == mock_redis_client
    
    async def test_get_session_repository_optional_none_client(self):
        """Test get_session_repository_optional returns None when Redis unavailable."""
        result = await get_session_repository_optional(None)
        
        assert result is None
    
    async def test_session_repository_dependency_injection_pattern(self):
        """Test that session repository dependencies follow FastAPI pattern."""
        # These functions should be async and suitable for FastAPI Depends()
        assert callable(get_session_repository)
        assert callable(get_session_repository_optional)
        
        # Verify they're async functions
        import inspect
        assert inspect.iscoroutinefunction(get_session_repository)
        assert inspect.iscoroutinefunction(get_session_repository_optional)


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.repositories
class TestUserRepositoryDependencies:
    """Test UserRepository dependency injection functions."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a mock Redis client for testing."""
        client = AsyncMock(spec=aioredis.Redis)
        return client
    
    async def test_get_user_repository_success(self, mock_redis_client):
        """Test get_user_repository returns repository with Redis client."""
        with patch('agent_c_api.core.repositories.dependencies.get_redis_client') as mock_get_client:
            # Mock the dependency function to return our mock client
            mock_get_client.return_value = mock_redis_client
            
            # Call the dependency function directly (simulating FastAPI injection)
            result = await get_user_repository(mock_redis_client)
            
            assert isinstance(result, UserRepository)
            assert result.redis_client == mock_redis_client
    
    async def test_get_user_repository_optional_success(self, mock_redis_client):
        """Test get_user_repository_optional returns repository when Redis available."""
        result = await get_user_repository_optional(mock_redis_client)
        
        assert isinstance(result, UserRepository)
        assert result.redis_client == mock_redis_client
    
    async def test_get_user_repository_optional_none_client(self):
        """Test get_user_repository_optional returns None when Redis unavailable."""
        result = await get_user_repository_optional(None)
        
        assert result is None
    
    async def test_user_repository_dependency_injection_pattern(self):
        """Test that user repository dependencies follow FastAPI pattern."""
        # These functions should be async and suitable for FastAPI Depends()
        assert callable(get_user_repository)
        assert callable(get_user_repository_optional)
        
        # Verify they're async functions
        import inspect
        assert inspect.iscoroutinefunction(get_user_repository)
        assert inspect.iscoroutinefunction(get_user_repository_optional)


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.repositories
class TestRepositoryDependenciesErrorScenarios:
    """Test repository dependencies with various error scenarios."""
    
    async def test_repository_creation_with_invalid_client(self):
        """Test repository creation handles invalid Redis client gracefully."""
        # Test with a non-Redis object
        invalid_client = "not_a_redis_client"
        
        # Repository constructors should handle this gracefully or raise appropriate errors
        # Note: The actual behavior depends on the repository implementation
        try:
            session_repo = await get_session_repository(invalid_client)
            # If it doesn't raise an error, verify it's still a SessionRepository
            assert isinstance(session_repo, SessionRepository)
        except (TypeError, AttributeError):
            # This is acceptable - repository should validate its inputs
            pass
        
        try:
            user_repo = await get_user_repository(invalid_client)
            # If it doesn't raise an error, verify it's still a UserRepository
            assert isinstance(user_repo, UserRepository)
        except (TypeError, AttributeError):
            # This is acceptable - repository should validate its inputs
            pass


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.repositories
class TestRepositoryDependenciesIntegration:
    """Test repository dependencies integration patterns."""
    
    async def test_repository_dependency_composition(self):
        """Test that repository dependencies properly compose Redis dependencies."""
        # Verify that the repository dependencies use the correct Redis dependencies
        import inspect
        
        # Get the signature of get_session_repository
        sig = inspect.signature(get_session_repository)
        params = list(sig.parameters.values())
        
        # Should have one parameter for the Redis client
        assert len(params) == 1
        redis_param = params[0]
        assert redis_param.name == 'redis_client'
        
        # Check that it has a default value (the Depends() call)
        assert redis_param.default is not inspect.Parameter.empty
    
    async def test_optional_repository_dependency_composition(self):
        """Test that optional repository dependencies use optional Redis dependencies."""
        import inspect
        
        # Get the signature of get_session_repository_optional
        sig = inspect.signature(get_session_repository_optional)
        params = list(sig.parameters.values())
        
        # Should have one parameter for the optional Redis client
        assert len(params) == 1
        redis_param = params[0]
        assert redis_param.name == 'redis_client'
        
        # Check that it has a default value (the Depends() call)
        assert redis_param.default is not inspect.Parameter.empty
    
    async def test_repository_types_consistency(self):
        """Test that repository dependencies return consistent types."""
        mock_client = AsyncMock(spec=aioredis.Redis)
        
        # Test session repositories
        session_repo = await get_session_repository(mock_client)
        session_repo_optional = await get_session_repository_optional(mock_client)
        
        assert type(session_repo) == type(session_repo_optional)
        assert isinstance(session_repo, SessionRepository)
        assert isinstance(session_repo_optional, SessionRepository)
        
        # Test user repositories
        user_repo = await get_user_repository(mock_client)
        user_repo_optional = await get_user_repository_optional(mock_client)
        
        assert type(user_repo) == type(user_repo_optional)
        assert isinstance(user_repo, UserRepository)
        assert isinstance(user_repo_optional, UserRepository)
    
    async def test_repository_client_assignment(self):
        """Test that repositories receive the correct Redis client."""
        mock_client = AsyncMock(spec=aioredis.Redis)
        
        # Test that repositories store the client correctly
        session_repo = await get_session_repository(mock_client)
        user_repo = await get_user_repository(mock_client)
        
        assert session_repo.redis_client is mock_client
        assert user_repo.redis_client is mock_client