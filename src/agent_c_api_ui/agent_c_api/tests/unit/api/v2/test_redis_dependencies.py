"""
Unit tests for Redis dependency injection.

Tests the Redis dependency injection functions in api/dependencies.py
including standard, optional, and managed Redis client dependencies.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from redis import asyncio as aioredis

from agent_c_api.api.dependencies import (
    get_redis_client,
    get_redis_client_optional,
    get_redis_client_managed,
    RedisClientManager
)


@pytest.mark.unit
@pytest.mark.api
class TestRedisClientManager:
    """Test the RedisClientManager context manager."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a mock Redis client for testing."""
        client = AsyncMock(spec=aioredis.Redis)
        client.aclose = AsyncMock()
        return client
    
    async def test_redis_client_manager_init(self, mock_redis_client):
        """Test RedisClientManager initialization."""
        manager = RedisClientManager(mock_redis_client)
        assert manager.redis_client == mock_redis_client
    
    async def test_redis_client_manager_context_success(self, mock_redis_client):
        """Test RedisClientManager context manager successful flow."""
        manager = RedisClientManager(mock_redis_client)
        
        # Test entering context
        async with manager as client:
            assert client == mock_redis_client
        
        # Verify cleanup was called
        mock_redis_client.aclose.assert_called_once()
    
    async def test_redis_client_manager_context_with_exception(self, mock_redis_client):
        """Test RedisClientManager context manager when exception occurs."""
        manager = RedisClientManager(mock_redis_client)
        
        # Test that cleanup happens even when exception occurs
        with pytest.raises(ValueError):
            async with manager as client:
                assert client == mock_redis_client
                raise ValueError("Test exception")
        
        # Verify cleanup was still called
        mock_redis_client.aclose.assert_called_once()
    
    async def test_redis_client_manager_cleanup_error(self, mock_redis_client):
        """Test RedisClientManager handles cleanup errors gracefully."""
        # Make aclose raise an exception
        mock_redis_client.aclose.side_effect = Exception("Cleanup error")
        
        manager = RedisClientManager(mock_redis_client)
        
        # Should not raise exception even if cleanup fails
        async with manager as client:
            assert client == mock_redis_client
        
        # Verify cleanup was attempted
        mock_redis_client.aclose.assert_called_once()
    
    async def test_redis_client_manager_none_client(self):
        """Test RedisClientManager with None client."""
        manager = RedisClientManager(None)
        
        async with manager as client:
            assert client is None
        
        # Should not raise exception with None client


@pytest.mark.unit
@pytest.mark.api
class TestRedisClientDependencies:
    """Test Redis client dependency injection functions."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a mock Redis client for testing."""
        client = AsyncMock(spec=aioredis.Redis)
        return client
    
    async def test_get_redis_client_success(self, mock_redis_client):
        """Test get_redis_client returns client when Redis is available."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.return_value = mock_redis_client
            
            result = await get_redis_client()
            
            assert result == mock_redis_client
            mock_get_client.assert_called_once()
    
    async def test_get_redis_client_failure(self):
        """Test get_redis_client raises HTTPException when Redis fails."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = Exception("Redis connection failed")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client()
            
            assert exc_info.value.status_code == 503
            assert "Redis service is currently unavailable" in exc_info.value.detail
            mock_get_client.assert_called_once()
    
    async def test_get_redis_client_optional_success(self, mock_redis_client):
        """Test get_redis_client_optional returns client when Redis is available."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.return_value = mock_redis_client
            
            result = await get_redis_client_optional()
            
            assert result == mock_redis_client
            mock_get_client.assert_called_once()
    
    async def test_get_redis_client_optional_failure(self):
        """Test get_redis_client_optional returns None when Redis fails."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = Exception("Redis connection failed")
            
            result = await get_redis_client_optional()
            
            assert result is None
            mock_get_client.assert_called_once()
    
    async def test_get_redis_client_managed_success(self, mock_redis_client):
        """Test get_redis_client_managed returns manager when Redis is available."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.return_value = mock_redis_client
            
            result = await get_redis_client_managed()
            
            assert isinstance(result, RedisClientManager)
            assert result.redis_client == mock_redis_client
            mock_get_client.assert_called_once()
    
    async def test_get_redis_client_managed_failure(self):
        """Test get_redis_client_managed raises HTTPException when Redis fails."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = Exception("Redis connection failed")
            
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client_managed()
            
            assert exc_info.value.status_code == 503
            assert "Redis service is currently unavailable" in exc_info.value.detail
            mock_get_client.assert_called_once()


@pytest.mark.unit
@pytest.mark.api
class TestRedisClientDependenciesErrorScenarios:
    """Test Redis client dependencies with various error scenarios."""
    
    async def test_redis_connection_timeout(self):
        """Test Redis client dependencies handle connection timeouts."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = TimeoutError("Connection timeout")
            
            # Standard client should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client()
            assert exc_info.value.status_code == 503
            
            # Optional client should return None
            result = await get_redis_client_optional()
            assert result is None
            
            # Managed client should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client_managed()
            assert exc_info.value.status_code == 503
    
    async def test_redis_connection_refused(self):
        """Test Redis client dependencies handle connection refused errors."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = ConnectionRefusedError("Connection refused")
            
            # Standard client should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client()
            assert exc_info.value.status_code == 503
            
            # Optional client should return None
            result = await get_redis_client_optional()
            assert result is None
            
            # Managed client should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client_managed()
            assert exc_info.value.status_code == 503
    
    async def test_redis_authentication_error(self):
        """Test Redis client dependencies handle authentication errors."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = Exception("Authentication failed")
            
            # Standard client should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client()
            assert exc_info.value.status_code == 503
            
            # Optional client should return None
            result = await get_redis_client_optional()
            assert result is None
            
            # Managed client should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client_managed()
            assert exc_info.value.status_code == 503


@pytest.mark.unit
@pytest.mark.api
class TestRedisClientDependenciesIntegration:
    """Test Redis client dependencies integration with FastAPI."""
    
    async def test_dependency_injection_pattern(self):
        """Test that dependencies follow proper FastAPI injection pattern."""
        # These functions should be async and suitable for FastAPI Depends()
        assert callable(get_redis_client)
        assert callable(get_redis_client_optional)
        assert callable(get_redis_client_managed)
        
        # Verify they're async functions
        import inspect
        assert inspect.iscoroutinefunction(get_redis_client)
        assert inspect.iscoroutinefunction(get_redis_client_optional)
        assert inspect.iscoroutinefunction(get_redis_client_managed)
    
    async def test_redis_client_manager_async_context(self):
        """Test RedisClientManager implements async context manager protocol."""
        mock_client = AsyncMock(spec=aioredis.Redis)
        manager = RedisClientManager(mock_client)
        
        # Verify it has the required async context manager methods
        assert hasattr(manager, '__aenter__')
        assert hasattr(manager, '__aexit__')
        assert callable(manager.__aenter__)
        assert callable(manager.__aexit__)
        
        # Verify they're async methods
        import inspect
        assert inspect.iscoroutinefunction(manager.__aenter__)
        assert inspect.iscoroutinefunction(manager.__aexit__)