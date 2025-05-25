"""
Integration tests for session creation with MnemonicSlugs implementation.

Tests the complete session creation flow including FastAPI dependency injection,
Redis operations, and proper MnemonicSlug ID generation and validation.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from redis import asyncio as aioredis
import json

from agent_c_api.core.repositories.session_repository import SessionRepository
from agent_c_api.api.v2.models.session_models import SessionCreate, SessionDetail, SessionUpdate


@pytest.mark.integration
@pytest.mark.core
@pytest.mark.session_creation
class TestSessionCreationIntegration:
    """Integration tests for session creation with MnemonicSlugs."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a comprehensive mock Redis client for integration testing."""
        client = AsyncMock(spec=aioredis.Redis)
        
        # Mock pipeline operations
        pipeline_mock = AsyncMock()
        pipeline_mock.hset = AsyncMock(return_value=True)
        pipeline_mock.sadd = AsyncMock(return_value=1)
        pipeline_mock.expire = AsyncMock(return_value=True)
        pipeline_mock.execute = AsyncMock(return_value=[True, True, 1])
        pipeline_mock.delete = AsyncMock(return_value=1)
        pipeline_mock.srem = AsyncMock(return_value=1)
        client.pipeline.return_value = pipeline_mock
        
        # Mock individual operations
        client.exists = AsyncMock(return_value=True)
        client.smembers = AsyncMock(return_value={b"tiger-castle", b"apple-banana"})
        
        return client
    
    @pytest_asyncio.fixture
    async def session_repository(self, mock_redis_client):
        """Create a SessionRepository with mocked Redis client."""
        return SessionRepository(mock_redis_client)
    
    @pytest_asyncio.fixture
    def complete_session_data(self):
        """Complete session creation data for integration testing."""
        return SessionCreate(
            model_id="gpt-4",
            persona_id="programmer",
            temperature=0.7,
            reasoning_effort=30,
            budget_tokens=15000,
            max_tokens=2000,
            tools=["search", "calculator", "file_manager"],
            custom_prompt="You are a helpful programming assistant."
        )
    
    @pytest_asyncio.fixture
    def minimal_session_data(self):
        """Minimal session creation data for testing."""
        return SessionCreate(
            model_id="gpt-4"
        )
    
    @patch('agent_c.util.MnemonicSlugs.generate_slug')
    async def test_complete_session_creation_flow(
        self, mock_generate_slug, session_repository, mock_redis_client, complete_session_data
    ):
        """Test complete session creation flow with all features."""
        # Setup
        mock_generate_slug.return_value = "tiger-castle"
        
        # Mock session data retrieval for get_session call at end of create_session
        mock_redis_client.hgetall.side_effect = [
            # First call (data)
            {
                b"model_id": b"gpt-4",
                b"persona_id": b"programmer",
                b"temperature": b"0.7",
                b"reasoning_effort": b"30",
                b"budget_tokens": b"15000",
                b"max_tokens": b"2000",
                b"tools": b'["search", "calculator", "file_manager"]',
                b"custom_prompt": b"You are a helpful programming assistant."
            },
            # Second call (meta)
            {
                b"created_at": b"2025-05-24T13:00:00",
                b"updated_at": b"2025-05-24T13:00:00",
                b"last_activity": b"2025-05-24T13:00:00",
                b"is_active": b"true"
            }
        ]\n        \n        # Execute\n        result = await session_repository.create_session(complete_session_data)\n        \n        # Verify MnemonicSlug generation\n        mock_generate_slug.assert_called_once_with(2)\n        \n        # Verify session creation\n        assert result is not None\n        assert result.id == "tiger-castle"\n        assert result.model_id == "gpt-4"\n        assert result.persona_id == "programmer"\n        assert result.temperature == 0.7\n        assert result.reasoning_effort == 30\n        assert result.budget_tokens == 15000\n        assert result.max_tokens == 2000\n        assert result.tools == ["search", "calculator", "file_manager"]\n        assert result.custom_prompt == "You are a helpful programming assistant."\n        \n        # Verify Redis operations\n        pipeline = mock_redis_client.pipeline.return_value\n        pipeline.hset.assert_called()\n        pipeline.sadd.assert_called_with("active_sessions", "tiger-castle")\n        pipeline.execute.assert_called()\n    \n    @patch('agent_c.util.MnemonicSlugs.generate_slug')\n    async def test_minimal_session_creation_flow(\n        self, mock_generate_slug, session_repository, mock_redis_client, minimal_session_data\n    ):\n        """Test session creation with minimal required data."""\n        # Setup\n        mock_generate_slug.return_value = "apple-banana"\n        \n        # Mock session data retrieval\n        mock_redis_client.hgetall.side_effect = [\n            {b"model_id": b"gpt-4", b"persona_id": b"default"},  # data\n            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}  # meta\n        ]\n        \n        # Execute\n        result = await session_repository.create_session(minimal_session_data)\n        \n        # Verify\n        assert result is not None\n        assert result.id == "apple-banana"\n        assert result.model_id == "gpt-4"\n        assert result.persona_id == "default"  # Should default to "default"\n    \n    async def test_session_creation_with_provided_valid_id(\n        self, session_repository, mock_redis_client\n    ):\n        """Test session creation with user-provided valid MnemonicSlug ID."""\n        session_data = SessionCreate(\n            id="user-provided",\n            model_id="claude-3",\n            persona_id="analyst"\n        )\n        \n        # Mock session data retrieval\n        mock_redis_client.hgetall.side_effect = [\n            {b"model_id": b"claude-3", b"persona_id": b"analyst"},  # data\n            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}  # meta\n        ]\n        \n        # Execute\n        result = await session_repository.create_session(session_data)\n        \n        # Verify user-provided ID was used\n        assert result is not None\n        assert result.id == "user-provided"\n        assert result.model_id == "claude-3"\n    \n    async def test_session_creation_rejects_invalid_formats(\n        self, session_repository, mock_redis_client\n    ):\n        """Test that session creation rejects various invalid ID formats."""\n        invalid_formats = [\n            "550e8400-e29b-41d4-a716-446655440000",  # GUID\n            "single",  # Single word\n            "too-many-words-here",  # Too many words\n            "UPPER-CASE",  # Uppercase\n            "tiger_castle",  # Underscore\n            "tiger castle",  # Space\n            "123-456",  # Numbers\n            "",  # Empty\n        ]\n        \n        for invalid_id in invalid_formats:\n            session_data = SessionCreate(\n                id=invalid_id,\n                model_id="gpt-4"\n            )\n            \n            with pytest.raises(ValueError) as exc_info:\n                await session_repository.create_session(session_data)\n            \n            assert "Invalid session ID format" in str(exc_info.value) or "must be a non-empty string" in str(exc_info.value)\n    \n    async def test_session_lifecycle_integration(\n        self, session_repository, mock_redis_client\n    ):\n        """Test complete session lifecycle: create, get, update, delete."""\n        # Create session\n        with patch('agent_c.util.MnemonicSlugs.generate_slug') as mock_generate:\n            mock_generate.return_value = "lifecycle-test"\n            \n            session_data = SessionCreate(\n                model_id="gpt-4",\n                persona_id="tester",\n                temperature=0.5\n            )\n            \n            # Mock creation\n            mock_redis_client.hgetall.side_effect = [\n                {b"model_id": b"gpt-4", b"persona_id": b"tester", b"temperature": b"0.5"},\n                {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}\n            ]\n            \n            created_session = await session_repository.create_session(session_data)\n            assert created_session.id == "lifecycle-test"\n        \n        # Get session\n        mock_redis_client.exists.return_value = True\n        mock_redis_client.hgetall.side_effect = [\n            {b"model_id": b"gpt-4", b"persona_id": b"tester", b"temperature": b"0.5"},\n            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}\n        ]\n        \n        retrieved_session = await session_repository.get_session("lifecycle-test")\n        assert retrieved_session is not None\n        assert retrieved_session.id == "lifecycle-test"\n        \n        # Update session\n        update_data = SessionUpdate(temperature=0.8)\n        mock_redis_client.hgetall.side_effect = [\n            {b"model_id": b"gpt-4", b"persona_id": b"tester", b"temperature": b"0.8"},\n            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}\n        ]\n        \n        updated_session = await session_repository.update_session("lifecycle-test", update_data)\n        assert updated_session is not None\n        assert updated_session.temperature == 0.8\n        \n        # Delete session\n        pipeline_mock = mock_redis_client.pipeline.return_value\n        pipeline_mock.execute.return_value = [1, 1, 1]  # Successful deletions\n        \n        delete_result = await session_repository.delete_session("lifecycle-test")\n        assert delete_result is True\n    \n    async def test_session_list_with_mnemonic_slugs(\n        self, session_repository, mock_redis_client\n    ):\n        """Test session listing returns only MnemonicSlug format sessions."""\n        # Mock active sessions set with MnemonicSlug IDs\n        mock_redis_client.smembers.return_value = {\n            b"tiger-castle",\n            b"apple-banana",\n            b"hello-world"\n        }\n        \n        # Mock session data for each session\n        mock_redis_client.hgetall.side_effect = [\n            # Session 1\n            {b"model_id": b"gpt-4", b"persona_id": b"programmer"},\n            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"},\n            # Session 2\n            {b"model_id": b"claude-3", b"persona_id": b"analyst"},\n            {b"created_at": b"2025-05-24T14:00:00", b"is_active": b"true"},\n            # Session 3\n            {b"model_id": b"gpt-3.5", b"persona_id": b"default"},\n            {b"created_at": b"2025-05-24T15:00:00", b"is_active": b"true"}\n        ]\n        \n        result = await session_repository.list_sessions(limit=10, offset=0)\n        \n        # Verify all sessions have MnemonicSlug format IDs\n        assert result is not None\n        assert len(result.items) == 3\n        \n        session_ids = [session.id for session in result.items]\n        assert "tiger-castle" in session_ids\n        assert "apple-banana" in session_ids\n        assert "hello-world" in session_ids\n        \n        # Verify all IDs match MnemonicSlug pattern\n        import re\n        mnemonic_pattern = r'^[a-z]+-[a-z]+$'\n        for session_id in session_ids:\n            assert re.match(mnemonic_pattern, session_id), f"Session ID {session_id} doesn't match MnemonicSlug pattern"\n    \n    async def test_redis_pipeline_usage_in_operations(\n        self, session_repository, mock_redis_client\n    ):\n        """Test that Redis pipeline is properly used for atomic operations."""\n        # Test session creation uses pipeline\n        with patch('agent_c.util.MnemonicSlugs.generate_slug') as mock_generate:\n            mock_generate.return_value = "pipeline-test"\n            \n            session_data = SessionCreate(model_id="gpt-4")\n            \n            # Mock get_session call\n            mock_redis_client.hgetall.side_effect = [\n                {b"model_id": b"gpt-4"},\n                {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}\n            ]\n            \n            await session_repository.create_session(session_data)\n            \n            # Verify pipeline was used\n            mock_redis_client.pipeline.assert_called()\n            pipeline = mock_redis_client.pipeline.return_value\n            pipeline.hset.assert_called()\n            pipeline.sadd.assert_called()\n            pipeline.execute.assert_called()\n        \n        # Test session deletion uses pipeline\n        pipeline_mock = mock_redis_client.pipeline.return_value\n        pipeline_mock.execute.return_value = [1, 1, 1]\n        \n        await session_repository.delete_session("pipeline-test")\n        \n        # Verify pipeline operations for deletion\n        pipeline_mock.delete.assert_called()\n        pipeline_mock.srem.assert_called()\n    \n    async def test_error_handling_during_session_operations(\n        self, session_repository, mock_redis_client\n    ):\n        """Test error handling during various session operations."""\n        # Test Redis connection error during creation\n        mock_redis_client.pipeline.side_effect = ConnectionError("Redis connection lost")\n        \n        session_data = SessionCreate(model_id="gpt-4")\n        \n        with pytest.raises(Exception) as exc_info:\n            await session_repository.create_session(session_data)\n        \n        # Should propagate the connection error\n        assert "Redis connection lost" in str(exc_info.value) or isinstance(exc_info.value, ConnectionError)\n        \n        # Reset for next test\n        mock_redis_client.pipeline.side_effect = None\n        pipeline_mock = AsyncMock()\n        pipeline_mock.execute = AsyncMock(return_value=[])\n        mock_redis_client.pipeline.return_value = pipeline_mock\n        \n        # Test validation error before Redis operations\n        invalid_session_data = SessionCreate(\n            id="550e8400-e29b-41d4-a716-446655440000",  # GUID\n            model_id="gpt-4"\n        )\n        \n        with pytest.raises(ValueError) as exc_info:\n            await session_repository.create_session(invalid_session_data)\n        \n        # Should fail validation before any Redis operations\n        assert "Invalid session ID format" in str(exc_info.value)\n        # Pipeline should not have been called due to early validation failure\n        mock_redis_client.pipeline.assert_not_called()


@pytest.mark.integration\n@pytest.mark.core\n@pytest.mark.fastapi_dependencies\nclass TestSessionRepositoryFastAPIDependencies:\n    """Test SessionRepository with FastAPI dependency injection patterns."""\n    \n    @pytest_asyncio.fixture\n    async def mock_redis_dependency(self):\n        """Mock Redis client as FastAPI dependency."""\n        client = AsyncMock(spec=aioredis.Redis)\n        \n        # Configure pipeline\n        pipeline_mock = AsyncMock()\n        pipeline_mock.execute = AsyncMock(return_value=[True, True, 1])\n        client.pipeline.return_value = pipeline_mock\n        \n        return client\n    \n    @pytest_asyncio.fixture\n    async def session_repository_dependency(self, mock_redis_dependency):\n        """SessionRepository as FastAPI dependency."""\n        return SessionRepository(mock_redis_dependency)\n    \n    async def test_dependency_injection_pattern(\n        self, session_repository_dependency, mock_redis_dependency\n    ):\n        """Test that SessionRepository works correctly with FastAPI dependency injection."""\n        # This simulates how the repository would be injected in FastAPI endpoints\n        repository = session_repository_dependency\n        \n        # Verify the repository is properly configured\n        assert repository.redis == mock_redis_dependency\n        assert repository.session_ttl == 24 * 60 * 60\n        \n        # Test basic operation\n        with patch('agent_c.util.MnemonicSlugs.generate_slug') as mock_generate:\n            mock_generate.return_value = "dependency-test"\n            \n            session_data = SessionCreate(model_id="gpt-4")\n            \n            # Mock get_session call\n            mock_redis_dependency.exists.return_value = True\n            mock_redis_dependency.hgetall.side_effect = [\n                {b"model_id": b"gpt-4"},\n                {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}\n            ]\n            \n            result = await repository.create_session(session_data)\n            \n            assert result is not None\n            assert result.id == "dependency-test"\n    \n    async def test_repository_isolation_between_requests(\n        self, mock_redis_dependency\n    ):\n        """Test that repository instances are properly isolated between requests."""\n        # Create two repository instances (simulating different requests)\n        repo1 = SessionRepository(mock_redis_dependency)\n        repo2 = SessionRepository(mock_redis_dependency)\n        \n        # They should share the same Redis client but be separate instances\n        assert repo1.redis == repo2.redis\n        assert repo1 is not repo2\n        \n        # Each should have its own logger instance\n        assert repo1.logger is not None\n        assert repo2.logger is not None\n    \n    async def test_repository_with_different_redis_clients(\n        self\n    ):\n        """Test repository behavior with different Redis client configurations."""\n        # Create different mock Redis clients\n        redis_client_1 = AsyncMock(spec=aioredis.Redis)\n        redis_client_2 = AsyncMock(spec=aioredis.Redis)\n        \n        # Create repositories with different clients\n        repo1 = SessionRepository(redis_client_1)\n        repo2 = SessionRepository(redis_client_2)\n        \n        # Verify they use different Redis clients\n        assert repo1.redis == redis_client_1\n        assert repo2.redis == redis_client_2\n        assert repo1.redis != repo2.redis\n        \n        # Both should have the same configuration\n        assert repo1.session_ttl == repo2.session_ttl