"""
Unit tests for Redis repository classes with mocked Redis clients.

Tests SessionRepository, UserRepository, and ChatRepository operations
with properly mocked Redis clients to verify business logic without
requiring actual Redis connections.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from redis import asyncio as aioredis
import json

from agent_c_api.core.repositories.session_repository import SessionRepository
from agent_c_api.core.repositories.user_repository import UserRepository
from agent_c_api.core.repositories.chat_repository import ChatRepository


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.repositories
class TestSessionRepository:
    """Test SessionRepository with mocked Redis client and MnemonicSlugs implementation."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a mock Redis client for testing."""
        client = AsyncMock(spec=aioredis.Redis)
        # Mock pipeline
        pipeline_mock = AsyncMock()
        pipeline_mock.execute = AsyncMock(return_value=[True, True, 1])
        pipeline_mock.hset = AsyncMock()
        pipeline_mock.sadd = AsyncMock()
        pipeline_mock.expire = AsyncMock()
        client.pipeline.return_value = pipeline_mock
        return client
    
    @pytest_asyncio.fixture
    async def session_repository(self, mock_redis_client):
        """Create a SessionRepository with mocked Redis client."""
        return SessionRepository(mock_redis_client)
    
    @pytest_asyncio.fixture
    def valid_session_create(self):
        """Valid session creation data with MnemonicSlug ID."""
        from agent_c_api.api.v2.models.session_models import SessionCreate
        return SessionCreate(
            id="tiger-castle",
            model_id="gpt-4",
            persona_id="programmer",
            temperature=0.7,
            reasoning_effort=30,
            budget_tokens=None,
            max_tokens=2000,
            tools=["search", "calculator"],
            custom_prompt=None
        )
    
    @pytest_asyncio.fixture
    def session_create_without_id(self):
        """Session creation data without ID (should generate MnemonicSlug)."""
        from agent_c_api.api.v2.models.session_models import SessionCreate
        return SessionCreate(
            model_id="gpt-4",
            persona_id="programmer",
            temperature=0.7
        )
    
    async def test_session_repository_init(self, mock_redis_client):
        """Test SessionRepository initialization."""
        repo = SessionRepository(mock_redis_client)
        assert repo.redis == mock_redis_client
        assert repo.session_ttl == 24 * 60 * 60  # 24 hours
    
    @patch('agent_c.util.MnemonicSlugs.generate_slug')
    async def test_create_session_with_mnemonic_slug(self, mock_generate_slug, session_repository, mock_redis_client, session_create_without_id):
        """Test creating a session generates MnemonicSlug when no ID provided."""
        # Mock MnemonicSlugs.generate_slug to return a known value
        mock_generate_slug.return_value = "generated-slug"
        
        # Mock Redis operations for get_session call at end of create_session
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.side_effect = [
            {b"model_id": b"gpt-4", b"persona_id": b"programmer"},  # data
            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}  # meta
        ]
        
        result = await session_repository.create_session(session_create_without_id)
        
        # Verify MnemonicSlugs.generate_slug was called with 2 words
        mock_generate_slug.assert_called_once_with(2)
        
        # Verify the session was created with the generated slug
        assert result is not None
        assert result.id == "generated-slug"
    
    async def test_create_session_with_provided_valid_id(self, session_repository, mock_redis_client, valid_session_create):
        """Test creating a session with provided valid MnemonicSlug ID."""
        # Mock Redis operations
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.side_effect = [
            {b"model_id": b"gpt-4", b"persona_id": b"programmer"},  # data
            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}  # meta
        ]
        
        result = await session_repository.create_session(valid_session_create)
        
        # Verify the session was created (no exception raised for valid ID)
        assert result is not None
        assert result.id == "tiger-castle"
    
    async def test_create_session_rejects_guid_format(self, session_repository, mock_redis_client):
        """Test creating a session rejects GUID format ID."""
        from agent_c_api.api.v2.models.session_models import SessionCreate
        
        session_data = SessionCreate(
            id="550e8400-e29b-41d4-a716-446655440000",  # GUID format
            model_id="gpt-4"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await session_repository.create_session(session_data)
        
        assert "Invalid session ID format" in str(exc_info.value)
        assert "MnemonicSlug format" in str(exc_info.value)
    
    async def test_get_session_exists(self, session_repository, mock_redis_client):
        """Test getting an existing session with valid MnemonicSlug ID."""
        session_id = "tiger-castle"
        
        # Mock Redis operations
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.side_effect = [
            {b"model_id": b"gpt-4", b"persona_id": b"programmer"},  # data
            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}  # meta
        ]
        
        result = await session_repository.get_session(session_id)
        
        # Verify Redis was called correctly
        mock_redis_client.exists.assert_called_once()
        
        # Verify returned data
        assert result is not None
        assert result.id == session_id
        assert result.model_id == "gpt-4"
    
    async def test_get_session_not_exists(self, session_repository, mock_redis_client):
        """Test getting a non-existent session."""
        session_id = "apple-banana"
        
        # Mock Redis exists operation returning False
        mock_redis_client.exists.return_value = False
        
        result = await session_repository.get_session(session_id)
        
        # Verify Redis was called correctly
        mock_redis_client.exists.assert_called_once()
        
        # Verify None is returned
        assert result is None
    
    async def test_get_session_rejects_guid_format(self, session_repository, mock_redis_client):
        """Test get_session rejects GUID format session IDs."""
        # Test with GUID format - should be rejected
        with pytest.raises(ValueError) as exc_info:
            await session_repository.get_session("550e8400-e29b-41d4-a716-446655440000")
        
        assert "Invalid session ID format" in str(exc_info.value)
        assert "MnemonicSlug format" in str(exc_info.value)
    
    async def test_update_session(self, session_repository, mock_redis_client):
        """Test updating a session with valid MnemonicSlug ID."""
        from agent_c_api.api.v2.models.session_models import SessionUpdate
        
        session_id = "tiger-castle"
        update_data = SessionUpdate(temperature=0.9)
        
        # Mock Redis operations
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.side_effect = [
            {b"model_id": b"gpt-4", b"persona_id": b"programmer"},  # data for get_session
            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}  # meta for get_session
        ]
        
        result = await session_repository.update_session(session_id, update_data)
        
        # Verify the session was updated
        assert result is not None
        assert result.id == session_id
    
    async def test_update_session_rejects_guid_format(self, session_repository, mock_redis_client):
        """Test update_session rejects GUID format session IDs."""
        from agent_c_api.api.v2.models.session_models import SessionUpdate
        
        update_data = SessionUpdate(temperature=0.8)
        
        # Test with GUID format - should be rejected
        with pytest.raises(ValueError) as exc_info:
            await session_repository.update_session("550e8400-e29b-41d4-a716-446655440000", update_data)
        
        assert "Invalid session ID format" in str(exc_info.value)
    
    async def test_delete_session(self, session_repository, mock_redis_client):
        """Test deleting a session with valid MnemonicSlug ID."""
        session_id = "tiger-castle"
        
        # Mock Redis pipeline operations
        pipeline_mock = mock_redis_client.pipeline.return_value
        pipeline_mock.execute.return_value = [1, 1, 1]  # Successful deletions
        
        result = await session_repository.delete_session(session_id)
        
        # Verify Redis pipeline was used
        mock_redis_client.pipeline.assert_called_once()
        pipeline_mock.delete.assert_called()
        pipeline_mock.srem.assert_called()
        pipeline_mock.execute.assert_called_once()
        
        assert result is True
    
    async def test_delete_session_rejects_guid_format(self, session_repository, mock_redis_client):
        """Test delete_session rejects GUID format session IDs."""
        # Test with GUID format - should be rejected
        with pytest.raises(ValueError) as exc_info:
            await session_repository.delete_session("550e8400-e29b-41d4-a716-446655440000")
        
        assert "Invalid session ID format" in str(exc_info.value)
    
    async def test_list_sessions(self, session_repository, mock_redis_client):
        """Test listing sessions with MnemonicSlug IDs."""
        # Mock Redis smembers operation for active_sessions set
        mock_redis_client.smembers.return_value = {
            b"tiger-castle",
            b"apple-banana"
        }
        
        # Mock Redis hgetall operations for each session
        mock_redis_client.hgetall.side_effect = [
            # Session 1 data
            {b"model_id": b"gpt-4", b"persona_id": b"programmer"},
            # Session 1 meta
            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"},
            # Session 2 data
            {b"model_id": b"claude-3", b"persona_id": b"default"},
            # Session 2 meta
            {b"created_at": b"2025-05-24T14:00:00", b"is_active": b"true"}
        ]
        
        result = await session_repository.list_sessions(limit=10, offset=0)
        
        # Verify Redis operations
        mock_redis_client.smembers.assert_called_once_with("active_sessions")
        
        # Verify results
        assert result is not None
        assert len(result.items) == 2
        assert result.total == 2
    
    async def test_session_id_validation_comprehensive(self, session_repository):
        """Test comprehensive session ID validation."""
        # Valid MnemonicSlug formats
        valid_ids = ["tiger-castle", "apple-banana", "hello-world"]
        for session_id in valid_ids:
            session_repository._validate_session_id(session_id)  # Should not raise
        
        # Invalid formats
        invalid_ids = [
            "550e8400-e29b-41d4-a716-446655440000",  # GUID
            "single",  # Single word
            "too-many-words-here",  # Too many words
            "UPPER-CASE",  # Uppercase
            "tiger_castle",  # Underscore
            "",  # Empty
            None  # None
        ]
        
        for session_id in invalid_ids:
            with pytest.raises(ValueError):
                session_repository._validate_session_id(session_id)
    
    async def test_session_repository_redis_error_handling(self, session_repository, mock_redis_client):
        """Test SessionRepository handles Redis errors gracefully."""
        session_id = "tiger-castle"
        
        # Mock Redis operation to raise an exception
        mock_redis_client.exists.side_effect = Exception("Redis connection error")
        
        # Repository should handle the error appropriately
        with pytest.raises(Exception) as exc_info:
            await session_repository.get_session(session_id)
        
        assert "Redis connection error" in str(exc_info.value)


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.repositories
class TestUserRepository:
    """Test UserRepository with mocked Redis client."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a mock Redis client for testing."""
        client = AsyncMock(spec=aioredis.Redis)
        return client
    
    @pytest_asyncio.fixture
    async def user_repository(self, mock_redis_client):
        """Create a UserRepository with mocked Redis client."""
        return UserRepository(mock_redis_client)
    
    @pytest_asyncio.fixture
    def sample_user_data(self):
        """Sample user data for testing."""
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
    
    async def test_user_repository_init(self, mock_redis_client):
        """Test UserRepository initialization."""
        repo = UserRepository(mock_redis_client)
        assert repo.redis_client == mock_redis_client
    
    async def test_create_user(self, user_repository, mock_redis_client, sample_user_data):
        """Test creating a user."""
        user_id = sample_user_data["id"]
        
        # Mock Redis set operation
        mock_redis_client.set.return_value = True
        
        result = await user_repository.create_user(user_id, sample_user_data)
        
        # Verify Redis was called correctly
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        
        # Check the key format
        key = call_args[0][0]
        assert user_id in key
        
        # Check the data was JSON serialized
        stored_data = call_args[0][1]
        parsed_data = json.loads(stored_data)
        assert parsed_data == sample_user_data
        
        assert result is True
    
    async def test_get_user_exists(self, user_repository, mock_redis_client, sample_user_data):
        """Test getting an existing user."""
        user_id = sample_user_data["id"]
        
        # Mock Redis get operation
        mock_redis_client.get.return_value = json.dumps(sample_user_data)
        
        result = await user_repository.get_user(user_id)
        
        # Verify Redis was called correctly
        mock_redis_client.get.assert_called_once()
        call_args = mock_redis_client.get.call_args
        key = call_args[0][0]
        assert user_id in key
        
        # Verify returned data
        assert result == sample_user_data
    
    async def test_get_user_not_exists(self, user_repository, mock_redis_client):
        """Test getting a non-existent user."""
        user_id = "non-existent-user"
        
        # Mock Redis get operation returning None
        mock_redis_client.get.return_value = None
        
        result = await user_repository.get_user(user_id)
        
        # Verify Redis was called correctly
        mock_redis_client.get.assert_called_once()
        
        # Verify None is returned
        assert result is None
    
    async def test_update_user_preferences(self, user_repository, mock_redis_client, sample_user_data):
        """Test updating user preferences."""
        user_id = sample_user_data["id"]
        new_preferences = {"theme": "light", "language": "es"}
        
        # Mock getting existing user data
        mock_redis_client.get.return_value = json.dumps(sample_user_data)
        mock_redis_client.set.return_value = True
        
        result = await user_repository.update_user_preferences(user_id, new_preferences)
        
        # Verify Redis get was called to fetch existing data
        mock_redis_client.get.assert_called_once()
        
        # Verify Redis set was called to store updated data
        mock_redis_client.set.assert_called_once()
        call_args = mock_redis_client.set.call_args
        stored_data = call_args[0][1]
        parsed_data = json.loads(stored_data)
        
        # Check that preferences were updated
        assert parsed_data["preferences"] == new_preferences
        
        assert result is True


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.repositories
class TestChatRepository:
    """Test ChatRepository with mocked Redis client."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a mock Redis client for testing."""
        client = AsyncMock(spec=aioredis.Redis)
        return client
    
    @pytest_asyncio.fixture
    async def chat_repository(self, mock_redis_client):
        """Create a ChatRepository with mocked Redis client."""
        session_id = "test-session-123"
        return ChatRepository(mock_redis_client, session_id)
    
    @pytest_asyncio.fixture
    def sample_message_data(self):
        """Sample message data for testing."""
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
    
    async def test_chat_repository_init(self, mock_redis_client):
        """Test ChatRepository initialization."""
        session_id = "test-session-123"
        repo = ChatRepository(mock_redis_client, session_id)
        assert repo.redis_client == mock_redis_client
        assert repo.session_id == session_id
    
    async def test_add_message(self, chat_repository, mock_redis_client, sample_message_data):
        """Test adding a message to chat history."""
        # Mock Redis lpush operation
        mock_redis_client.lpush.return_value = 1
        
        result = await chat_repository.add_message(sample_message_data)
        
        # Verify Redis was called correctly
        mock_redis_client.lpush.assert_called_once()
        call_args = mock_redis_client.lpush.call_args
        
        # Check the key format includes session_id
        key = call_args[0][0]
        assert "test-session-123" in key
        
        # Check the message data was JSON serialized
        stored_data = call_args[0][1]
        parsed_data = json.loads(stored_data)
        assert parsed_data == sample_message_data
        
        assert result is True
    
    async def test_get_messages(self, chat_repository, mock_redis_client, sample_message_data):
        """Test getting chat messages."""
        # Mock Redis lrange operation
        mock_redis_client.lrange.return_value = [
            json.dumps(sample_message_data),
            json.dumps({**sample_message_data, "id": "msg-124", "content": "I'm doing well!"})
        ]
        
        result = await chat_repository.get_messages(limit=10)
        
        # Verify Redis was called correctly
        mock_redis_client.lrange.assert_called_once()
        call_args = mock_redis_client.lrange.call_args
        
        # Check the key format
        key = call_args[0][0]
        assert "test-session-123" in key
        
        # Check the range parameters
        assert call_args[0][1] == 0  # start
        assert call_args[0][2] == 9  # end (limit - 1)
        
        # Verify results
        assert len(result) == 2
        assert result[0] == sample_message_data
    
    async def test_get_message_count(self, chat_repository, mock_redis_client):
        """Test getting the count of messages in chat."""
        # Mock Redis llen operation
        mock_redis_client.llen.return_value = 5
        
        result = await chat_repository.get_message_count()
        
        # Verify Redis was called correctly
        mock_redis_client.llen.assert_called_once()
        call_args = mock_redis_client.llen.call_args
        key = call_args[0][0]
        assert "test-session-123" in key
        
        assert result == 5
    
    async def test_clear_messages(self, chat_repository, mock_redis_client):
        """Test clearing all messages from chat."""
        # Mock Redis delete operation
        mock_redis_client.delete.return_value = 1
        
        result = await chat_repository.clear_messages()
        
        # Verify Redis was called correctly
        mock_redis_client.delete.assert_called_once()
        call_args = mock_redis_client.delete.call_args
        key = call_args[0][0]
        assert "test-session-123" in key
        
        assert result is True


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.repositories
class TestRepositoryErrorHandling:
    """Test repository error handling with Redis failures."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a mock Redis client for testing."""
        client = AsyncMock(spec=aioredis.Redis)
        return client
    
    async def test_session_repository_connection_error(self, mock_redis_client):
        """Test SessionRepository handles connection errors."""
        repo = SessionRepository(mock_redis_client)
        
        # Mock Redis operation to raise connection error
        mock_redis_client.get.side_effect = ConnectionError("Redis connection lost")
        
        with pytest.raises(ConnectionError):
            await repo.get_session("test-session")
    
    async def test_user_repository_timeout_error(self, mock_redis_client):
        """Test UserRepository handles timeout errors."""
        repo = UserRepository(mock_redis_client)
        
        # Mock Redis operation to raise timeout error
        mock_redis_client.set.side_effect = TimeoutError("Redis operation timeout")
        
        with pytest.raises(TimeoutError):
            await repo.create_user("test-user", {"name": "Test"})
    
    async def test_chat_repository_memory_error(self, mock_redis_client):
        """Test ChatRepository handles memory errors."""
        repo = ChatRepository(mock_redis_client, "test-session")
        
        # Mock Redis operation to raise memory error
        mock_redis_client.lpush.side_effect = Exception("Redis out of memory")
        
        with pytest.raises(Exception) as exc_info:
            await repo.add_message({"content": "test"})
        
        assert "Redis out of memory" in str(exc_info.value)