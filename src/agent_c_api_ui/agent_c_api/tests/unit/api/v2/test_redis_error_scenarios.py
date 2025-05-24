"""
Unit tests for Redis error scenarios and graceful degradation.

Tests various Redis failure scenarios to ensure the application
handles errors gracefully and provides appropriate fallback behavior.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException
from fastapi.testclient import TestClient
from redis import asyncio as aioredis
from redis.exceptions import ConnectionError, TimeoutError, AuthenticationError

from agent_c_api.main import app
from agent_c_api.api.dependencies import (
    get_redis_client,
    get_redis_client_optional,
    get_redis_client_managed,
    RedisClientManager
)
from agent_c_api.core.repositories.dependencies import (
    get_session_repository,
    get_session_repository_optional,
    get_user_repository,
    get_user_repository_optional
)


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.error_scenarios
class TestRedisConnectionFailures:
    """Test Redis dependency behavior with connection failures."""
    
    async def test_redis_client_connection_refused(self):
        """Test Redis client dependency when connection is refused."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = ConnectionRefusedError("Connection refused")
            
            # Standard client should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client()
            assert exc_info.value.status_code == 503
            assert "Redis service is currently unavailable" in exc_info.value.detail
            
            # Optional client should return None
            result = await get_redis_client_optional()
            assert result is None
            
            # Managed client should raise HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client_managed()
            assert exc_info.value.status_code == 503
    
    async def test_redis_client_timeout_error(self):
        """Test Redis client dependency with timeout errors."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = TimeoutError("Operation timeout")
            
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
    
    async def test_redis_client_authentication_error(self):
        """Test Redis client dependency with authentication errors."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = AuthenticationError("Authentication failed")
            
            # All dependency variants should handle auth errors
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client()
            assert exc_info.value.status_code == 503
            
            result = await get_redis_client_optional()
            assert result is None
            
            with pytest.raises(HTTPException) as exc_info:
                await get_redis_client_managed()
            assert exc_info.value.status_code == 503
    
    async def test_redis_client_network_error(self):
        """Test Redis client dependency with network errors."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = OSError("Network is unreachable")
            
            # Test all dependency variants handle network errors
            with pytest.raises(HTTPException):
                await get_redis_client()
            
            result = await get_redis_client_optional()
            assert result is None
            
            with pytest.raises(HTTPException):
                await get_redis_client_managed()
    
    async def test_redis_client_memory_error(self):
        """Test Redis client dependency with memory errors."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = MemoryError("Out of memory")
            
            # Memory errors should be handled gracefully
            with pytest.raises(HTTPException):
                await get_redis_client()
            
            result = await get_redis_client_optional()
            assert result is None
            
            with pytest.raises(HTTPException):
                await get_redis_client_managed()


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.error_scenarios
class TestRepositoryDependencyFailures:
    """Test repository dependency behavior with Redis failures."""
    
    async def test_session_repository_dependency_with_redis_failure(self):
        """Test session repository dependency when Redis fails."""
        with patch('agent_c_api.core.repositories.dependencies.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = HTTPException(status_code=503, detail="Redis unavailable")
            
            # Standard repository dependency should propagate HTTPException
            with pytest.raises(HTTPException) as exc_info:
                # Simulate FastAPI calling the dependency
                await get_session_repository()
            assert exc_info.value.status_code == 503
    
    async def test_session_repository_optional_with_redis_failure(self):
        """Test optional session repository dependency when Redis fails."""
        with patch('agent_c_api.core.repositories.dependencies.get_redis_client_optional') as mock_get_client:
            mock_get_client.return_value = None
            
            # Optional repository dependency should return None
            result = await get_session_repository_optional()
            assert result is None
    
    async def test_user_repository_dependency_with_redis_failure(self):
        """Test user repository dependency when Redis fails."""
        with patch('agent_c_api.core.repositories.dependencies.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = HTTPException(status_code=503, detail="Redis unavailable")
            
            # Standard repository dependency should propagate HTTPException
            with pytest.raises(HTTPException) as exc_info:
                await get_user_repository()
            assert exc_info.value.status_code == 503
    
    async def test_user_repository_optional_with_redis_failure(self):
        """Test optional user repository dependency when Redis fails."""
        with patch('agent_c_api.core.repositories.dependencies.get_redis_client_optional') as mock_get_client:
            mock_get_client.return_value = None
            
            # Optional repository dependency should return None
            result = await get_user_repository_optional()
            assert result is None


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.error_scenarios
class TestRedisOperationFailures:
    """Test Redis operation failures in repositories."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client_with_failures(self):
        """Create a mock Redis client that simulates operation failures."""
        client = AsyncMock(spec=aioredis.Redis)
        return client
    
    async def test_session_repository_get_operation_failure(self, mock_redis_client_with_failures):
        """Test session repository when get operation fails."""
        from agent_c_api.core.repositories.session_repository import SessionRepository
        
        # Mock Redis get to raise an exception
        mock_redis_client_with_failures.get.side_effect = ConnectionError("Connection lost")
        
        repo = SessionRepository(mock_redis_client_with_failures)
        
        # Repository should propagate the Redis error
        with pytest.raises(ConnectionError):
            await repo.get_session("test-session")
    
    async def test_session_repository_set_operation_failure(self, mock_redis_client_with_failures):
        """Test session repository when set operation fails."""
        from agent_c_api.core.repositories.session_repository import SessionRepository
        
        # Mock Redis set to raise an exception
        mock_redis_client_with_failures.set.side_effect = TimeoutError("Operation timeout")
        
        repo = SessionRepository(mock_redis_client_with_failures)
        
        # Repository should propagate the Redis error
        with pytest.raises(TimeoutError):
            await repo.create_session("test-session", {"data": "test"})
    
    async def test_user_repository_operation_failure(self, mock_redis_client_with_failures):
        """Test user repository when Redis operations fail."""
        from agent_c_api.core.repositories.user_repository import UserRepository
        
        # Mock Redis operations to raise exceptions
        mock_redis_client_with_failures.get.side_effect = ConnectionError("Connection lost")
        mock_redis_client_with_failures.set.side_effect = TimeoutError("Operation timeout")
        
        repo = UserRepository(mock_redis_client_with_failures)
        
        # Repository should propagate Redis errors
        with pytest.raises(ConnectionError):
            await repo.get_user("test-user")
        
        with pytest.raises(TimeoutError):
            await repo.create_user("test-user", {"data": "test"})
    
    async def test_chat_repository_operation_failure(self, mock_redis_client_with_failures):
        """Test chat repository when Redis operations fail."""
        from agent_c_api.core.repositories.chat_repository import ChatRepository
        
        # Mock Redis operations to raise exceptions
        mock_redis_client_with_failures.lpush.side_effect = MemoryError("Redis out of memory")
        mock_redis_client_with_failures.lrange.side_effect = ConnectionError("Connection lost")
        
        repo = ChatRepository(mock_redis_client_with_failures, "test-session")
        
        # Repository should propagate Redis errors
        with pytest.raises(MemoryError):
            await repo.add_message({"content": "test"})
        
        with pytest.raises(ConnectionError):
            await repo.get_messages()


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.error_scenarios
class TestRedisClientManagerErrorHandling:
    """Test RedisClientManager error handling scenarios."""
    
    async def test_redis_client_manager_with_failing_client(self):
        """Test RedisClientManager with a client that fails during operations."""
        mock_client = AsyncMock(spec=aioredis.Redis)
        mock_client.set.side_effect = ConnectionError("Connection lost during operation")
        mock_client.aclose.return_value = None  # Cleanup should succeed
        
        manager = RedisClientManager(mock_client)
        
        # Should handle operation failures within the context
        with pytest.raises(ConnectionError):
            async with manager as client:
                await client.set("test_key", "test_value")
        
        # Cleanup should still be called
        mock_client.aclose.assert_called_once()
    
    async def test_redis_client_manager_cleanup_failure(self):
        """Test RedisClientManager when cleanup fails."""
        mock_client = AsyncMock(spec=aioredis.Redis)
        mock_client.aclose.side_effect = Exception("Cleanup failed")
        
        manager = RedisClientManager(mock_client)
        
        # Should not raise exception even if cleanup fails
        async with manager as client:
            assert client == mock_client
        
        # Cleanup should have been attempted
        mock_client.aclose.assert_called_once()
    
    async def test_redis_client_manager_with_exception_in_context(self):
        """Test RedisClientManager when exception occurs in context."""
        mock_client = AsyncMock(spec=aioredis.Redis)
        mock_client.aclose.return_value = None
        
        manager = RedisClientManager(mock_client)
        
        # Should still call cleanup even when exception occurs
        with pytest.raises(ValueError):
            async with manager as client:
                raise ValueError("Test exception in context")
        
        # Cleanup should still be called
        mock_client.aclose.assert_called_once()


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.error_scenarios
class TestGracefulDegradation:
    """Test graceful degradation scenarios."""
    
    @pytest_asyncio.fixture
    def client(self):
        """Create a test client for the FastAPI application."""
        return TestClient(app)
    
    def test_health_endpoint_with_redis_down(self, client):
        """Test health endpoint graceful degradation when Redis is down."""
        with patch('agent_c_api.config.redis_config.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = ConnectionError("Redis is down")
            
            # Health endpoint should still respond
            response = client.get("/api/v2/health")
            
            # Should return a response (may be 200 or 503 depending on implementation)
            assert response.status_code in [200, 503]
            
            data = response.json()
            assert "status" in data
            assert "services" in data
            assert "redis" in data["services"]
            
            # Redis should be marked as unhealthy
            redis_status = data["services"]["redis"]["status"]
            assert redis_status in ["unhealthy", "error", "down"]
    
    def test_readiness_probe_with_redis_down(self, client):
        """Test readiness probe when Redis is down."""
        with patch('agent_c_api.config.redis_config.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = ConnectionError("Redis is down")
            
            response = client.get("/api/v2/health/ready")
            
            # Should indicate not ready when Redis is down
            # (exact behavior depends on implementation)
            assert response.status_code in [200, 503]
            
            data = response.json()
            assert "status" in data
    
    def test_liveness_probe_with_redis_down(self, client):
        """Test liveness probe when Redis is down."""
        with patch('agent_c_api.config.redis_config.RedisConfig.get_redis_client') as mock_get_client:
            mock_get_client.side_effect = ConnectionError("Redis is down")
            
            response = client.get("/api/v2/health/live")
            
            # Liveness should generally return 200 even if Redis is down
            # (the app itself is still alive)
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert data["status"] == "alive"


@pytest.mark.unit
@pytest.mark.api
@pytest.mark.error_scenarios
class TestRedisErrorRecovery:
    """Test Redis error recovery scenarios."""
    
    async def test_redis_dependency_recovery_after_failure(self):
        """Test that Redis dependencies can recover after failures."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            # First call fails
            mock_get_client.side_effect = [
                ConnectionError("Redis is down"),
                AsyncMock(spec=aioredis.Redis)  # Second call succeeds
            ]
            
            # First attempt should fail
            with pytest.raises(HTTPException):
                await get_redis_client()
            
            # Second attempt should succeed
            result = await get_redis_client()
            assert result is not None
    
    async def test_optional_redis_dependency_recovery(self):
        """Test that optional Redis dependencies can recover after failures."""
        with patch('agent_c_api.api.dependencies.RedisConfig.get_redis_client') as mock_get_client:
            # First call fails, second succeeds
            mock_redis_client = AsyncMock(spec=aioredis.Redis)
            mock_get_client.side_effect = [
                ConnectionError("Redis is down"),
                mock_redis_client
            ]
            
            # First attempt should return None
            result1 = await get_redis_client_optional()
            assert result1 is None
            
            # Second attempt should succeed
            result2 = await get_redis_client_optional()
            assert result2 == mock_redis_client
    
    async def test_repository_dependency_recovery(self):
        """Test that repository dependencies can recover after Redis failures."""
        with patch('agent_c_api.core.repositories.dependencies.get_redis_client') as mock_get_client:
            mock_redis_client = AsyncMock(spec=aioredis.Redis)
            
            # First call fails, second succeeds
            mock_get_client.side_effect = [
                HTTPException(status_code=503, detail="Redis unavailable"),
                mock_redis_client
            ]
            
            # First attempt should fail
            with pytest.raises(HTTPException):
                await get_session_repository()
            
            # Second attempt should succeed
            result = await get_session_repository(mock_redis_client)
            assert result is not None
            assert result.redis_client == mock_redis_client