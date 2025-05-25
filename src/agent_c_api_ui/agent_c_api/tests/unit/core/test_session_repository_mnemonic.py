"""
Unit tests for SessionRepository with MnemonicSlugs implementation.

Tests the updated SessionRepository that uses MnemonicSlugs for session ID generation
and validates session ID format according to Agent C framework standards.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from redis import asyncio as aioredis
import json

from agent_c_api.core.repositories.session_repository import SessionRepository
from agent_c_api.api.v2.models.session_models import SessionCreate, SessionDetail


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.repositories
class TestSessionRepositoryMnemonicSlugs:
    """Test SessionRepository with MnemonicSlugs implementation."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a mock Redis client for testing."""
        client = AsyncMock(spec=aioredis.Redis)
        # Mock pipeline
        pipeline_mock = AsyncMock()
        pipeline_mock.execute = AsyncMock(return_value=[])
        client.pipeline.return_value = pipeline_mock
        return client
    
    @pytest_asyncio.fixture
    async def session_repository(self, mock_redis_client):
        """Create a SessionRepository with mocked Redis client."""
        return SessionRepository(mock_redis_client)
    
    @pytest_asyncio.fixture
    def valid_session_create(self):
        """Valid session creation data with MnemonicSlug ID."""
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
        return SessionCreate(
            model_id="gpt-4",
            persona_id="programmer",
            temperature=0.7
        )
    
    async def test_validate_session_id_valid_mnemonic_slug(self, session_repository):
        """Test validation accepts valid MnemonicSlug format."""
        valid_ids = ["tiger-castle", "apple-banana", "hello-world"]
        
        for session_id in valid_ids:
            # Should not raise exception
            session_repository._validate_session_id(session_id)
    
    async def test_validate_session_id_rejects_guid_format(self, session_repository):
        """Test validation rejects GUID format session IDs."""
        guid_ids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
            "12345678-1234-1234-1234-123456789abc"
        ]
        
        for session_id in guid_ids:
            with pytest.raises(ValueError) as exc_info:
                session_repository._validate_session_id(session_id)
            assert "Invalid session ID format" in str(exc_info.value)
            assert "MnemonicSlug format" in str(exc_info.value)
    
    async def test_validate_session_id_rejects_invalid_formats(self, session_repository):
        """Test validation rejects various invalid formats."""
        invalid_ids = [
            "",  # empty string
            "single-word",  # missing second word
            "too-many-words-here",  # too many words
            "UPPER-CASE",  # uppercase
            "tiger_castle",  # underscore instead of dash
            "tiger castle",  # space instead of dash
            "123-456",  # numbers only
            "tiger-",  # missing second word
            "-castle",  # missing first word
        ]
        
        for session_id in invalid_ids:
            with pytest.raises(ValueError) as exc_info:
                session_repository._validate_session_id(session_id)
            assert "Invalid session ID format" in str(exc_info.value) or "must be a non-empty string" in str(exc_info.value)
    
    async def test_validate_session_id_rejects_none_and_non_string(self, session_repository):
        """Test validation rejects None and non-string values."""
        invalid_values = [None, 123, [], {}, True]
        
        for value in invalid_values:
            with pytest.raises(ValueError) as exc_info:
                session_repository._validate_session_id(value)
            assert "must be a non-empty string" in str(exc_info.value)
    
    @patch('agent_c.util.MnemonicSlugs.generate_slug')
    async def test_create_session_generates_mnemonic_slug_when_no_id(
        self, mock_generate_slug, session_repository, mock_redis_client, session_create_without_id
    ):
        """Test session creation generates MnemonicSlug when no ID provided."""
        # Mock MnemonicSlugs.generate_slug to return a known value
        mock_generate_slug.return_value = "generated-slug"
        
        # Mock Redis operations
        mock_redis_client.exists.return_value = False
        mock_redis_client.hgetall.side_effect = [
            {b"model_id": b"gpt-4", b"persona_id": b"programmer"},  # data
            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}  # meta
        ]
        
        result = await session_repository.create_session(session_create_without_id)
        
        # Verify MnemonicSlugs.generate_slug was called with 2 words
        mock_generate_slug.assert_called_once_with(2)
        
        # Verify the session was created with the generated slug
        assert result is not None
    
    async def test_create_session_uses_provided_valid_id(
        self, session_repository, mock_redis_client, valid_session_create
    ):
        """Test session creation uses provided valid MnemonicSlug ID."""
        # Mock Redis operations
        mock_redis_client.exists.return_value = False
        mock_redis_client.hgetall.side_effect = [
            {b"model_id": b"gpt-4", b"persona_id": b"programmer"},  # data
            {b"created_at": b"2025-05-24T13:00:00", b"is_active": b"true"}  # meta
        ]
        
        result = await session_repository.create_session(valid_session_create)
        
        # Verify the session was created (no exception raised for valid ID)
        assert result is not None
    
    async def test_create_session_rejects_guid_id(self, session_repository, mock_redis_client):
        """Test session creation rejects GUID format ID."""
        session_data = SessionCreate(
            id="550e8400-e29b-41d4-a716-446655440000",  # GUID format
            model_id="gpt-4"
        )
        
        with pytest.raises(ValueError) as exc_info:
            await session_repository.create_session(session_data)
        
        assert "Invalid session ID format" in str(exc_info.value)
        assert "MnemonicSlug format" in str(exc_info.value)
    
    async def test_get_session_validates_id_format(self, session_repository, mock_redis_client):
        """Test get_session validates session ID format."""
        # Test with GUID format - should be rejected
        with pytest.raises(ValueError) as exc_info:
            await session_repository.get_session("550e8400-e29b-41d4-a716-446655440000")
        
        assert "Invalid session ID format" in str(exc_info.value)
        
        # Test with valid MnemonicSlug format - should proceed
        mock_redis_client.exists.return_value = False
        result = await session_repository.get_session("tiger-castle")
        assert result is None  # Session doesn't exist, but validation passed
    
    async def test_update_session_validates_id_format(self, session_repository, mock_redis_client):
        """Test update_session validates session ID format."""
        from agent_c_api.api.v2.models.session_models import SessionUpdate
        
        update_data = SessionUpdate(temperature=0.8)
        
        # Test with GUID format - should be rejected
        with pytest.raises(ValueError) as exc_info:
            await session_repository.update_session("550e8400-e29b-41d4-a716-446655440000", update_data)
        
        assert "Invalid session ID format" in str(exc_info.value)
    
    async def test_delete_session_validates_id_format(self, session_repository, mock_redis_client):
        """Test delete_session validates session ID format."""
        # Test with GUID format - should be rejected
        with pytest.raises(ValueError) as exc_info:
            await session_repository.delete_session("550e8400-e29b-41d4-a716-446655440000")
        
        assert "Invalid session ID format" in str(exc_info.value)
    
    async def test_session_repository_documentation_updated(self, session_repository):
        """Test that SessionRepository class documentation mentions MnemonicSlugs."""
        class_doc = SessionRepository.__doc__
        assert "MnemonicSlugs" in class_doc
        assert "GUID format session IDs are not supported" in class_doc
    
    async def test_create_session_documentation_updated(self, session_repository):
        """Test that create_session method documentation mentions MnemonicSlugs."""
        method_doc = session_repository.create_session.__doc__
        assert "MnemonicSlug" in method_doc
        assert "GUID format session IDs are rejected" in method_doc
        assert "ValueError" in method_doc


@pytest.mark.unit
@pytest.mark.core
@pytest.mark.repositories
class TestSessionRepositoryMnemonicSlugsIntegration:
    """Integration-style tests for SessionRepository MnemonicSlugs implementation."""
    
    @pytest_asyncio.fixture
    async def mock_redis_client(self):
        """Create a comprehensive mock Redis client."""
        client = AsyncMock(spec=aioredis.Redis)
        
        # Mock pipeline operations
        pipeline_mock = AsyncMock()
        pipeline_mock.hset = AsyncMock()
        pipeline_mock.sadd = AsyncMock()
        pipeline_mock.execute = AsyncMock(return_value=[True, True, 1])
        client.pipeline.return_value = pipeline_mock
        
        # Mock TTL operations
        client.expire = AsyncMock(return_value=True)
        
        return client
    
    @pytest_asyncio.fixture
    async def session_repository(self, mock_redis_client):
        """Create a SessionRepository with mocked Redis client."""
        return SessionRepository(mock_redis_client)
    
    @patch('agent_c.util.MnemonicSlugs.generate_slug')
    async def test_full_session_lifecycle_with_mnemonic_slugs(
        self, mock_generate_slug, session_repository, mock_redis_client
    ):
        """Test complete session lifecycle using MnemonicSlugs."""
        # Setup
        mock_generate_slug.return_value = "apple-banana"
        
        # Mock session data retrieval for get_session call at end of create_session
        mock_redis_client.exists.return_value = True
        mock_redis_client.hgetall.side_effect = [
            # First call (data)
            {
                b"model_id": b"gpt-4",
                b"persona_id": b"programmer",
                b"temperature": b"0.7"
            },
            # Second call (meta)
            {
                b"created_at": b"2025-05-24T13:00:00",
                b"updated_at": b"2025-05-24T13:00:00",
                b"last_activity": b"2025-05-24T13:00:00",
                b"is_active": b"true"
            }
        ]
        
        # Create session without ID (should generate MnemonicSlug)
        session_data = SessionCreate(
            model_id="gpt-4",
            persona_id="programmer",
            temperature=0.7
        )
        
        result = await session_repository.create_session(session_data)
        
        # Verify MnemonicSlug was generated
        mock_generate_slug.assert_called_once_with(2)
        
        # Verify session was created successfully
        assert result is not None
        assert result.id == "apple-banana"
        assert result.model_id == "gpt-4"
        assert result.persona_id == "programmer"
        
        # Verify Redis operations were called correctly
        pipeline = mock_redis_client.pipeline.return_value
        pipeline.hset.assert_called()
        pipeline.sadd.assert_called()
        pipeline.execute.assert_called()
    
    async def test_session_id_validation_prevents_guid_storage(
        self, session_repository, mock_redis_client
    ):
        """Test that GUID format IDs are prevented from being stored."""
        # Attempt to create session with GUID ID
        session_data = SessionCreate(
            id="550e8400-e29b-41d4-a716-446655440000",
            model_id="gpt-4"
        )
        
        # Should raise ValueError before any Redis operations
        with pytest.raises(ValueError) as exc_info:
            await session_repository.create_session(session_data)
        
        # Verify error message
        assert "Invalid session ID format" in str(exc_info.value)
        assert "550e8400-e29b-41d4-a716-446655440000" in str(exc_info.value)
        
        # Verify no Redis operations were attempted
        mock_redis_client.pipeline.assert_not_called()
    
    async def test_mnemonic_slug_format_examples(self, session_repository):
        """Test various valid MnemonicSlug format examples."""
        valid_examples = [
            "tiger-castle",
            "apple-banana", 
            "hello-world",
            "quick-brown",
            "lazy-dog",
            "red-blue",
            "fast-car",
            "big-house"
        ]
        
        for session_id in valid_examples:
            # Should not raise any exception
            session_repository._validate_session_id(session_id)