import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

from agent_c_api.api.v2.models import SessionCreate, SessionDetail, SessionUpdate
from agent_c_api.api.v2.sessions.services import SessionService


@pytest.fixture
def mock_agent_manager():
    """Fixture for a mocked UItoAgentBridgeManager"""
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


@pytest.fixture
def service(mock_agent_manager):
    """Fixture for the SessionService with a mocked agent manager"""
    return SessionService(agent_manager=mock_agent_manager)


class TestSessionService:
    """Tests for the SessionService class"""
    
    @pytest.mark.asyncio
    async def test_create_session(self, service, mock_agent_manager):
        """Test creating a new session"""
        # Arrange
        session_data = SessionCreate(
            model_id="gpt-4",
            persona_id="researcher",
            temperature=0.8,
            tools=["search", "calculator"]
        )
        
        # Act
        result = await service.create_session(session_data)
        
        # Assert
        assert isinstance(result, SessionDetail)
        assert result.id == "test_ui_session_id"
        assert result.model_id == "gpt-4"
        assert result.persona_id == "researcher"
        assert result.agent_internal_id == "test_agent_session_id"
        assert result.tools == ["search", "calculator"]
        assert result.temperature == 0.8
        
        # Verify manager calls
        mock_agent_manager.create_session.assert_called_once()
        mock_agent_manager.update_agent_tools.assert_called_once_with(
            "test_ui_session_id", ["search", "calculator"]
        )
    
    @pytest.mark.asyncio
    async def test_get_sessions(self, service):
        """Test listing sessions with pagination"""
        # Act
        result = await service.get_sessions(limit=10, offset=0)
        
        # Assert
        assert result.total == 2
        assert len(result.items) == 2
        assert result.limit == 10
        assert result.offset == 0
        
        # Test pagination
        result_paginated = await service.get_sessions(limit=1, offset=1)
        assert result_paginated.total == 2
        assert len(result_paginated.items) == 1
        assert result_paginated.limit == 1
        assert result_paginated.offset == 1
    
    @pytest.mark.asyncio
    async def test_get_session_existing(self, service):
        """Test getting an existing session"""
        # Act
        result = await service.get_session("test_session_1")
        
        # Assert
        assert isinstance(result, SessionDetail)
        assert result.id == "test_session_1"
        assert result.model_id == "gpt-4"
        assert result.persona_id == "programmer"
        assert result.agent_internal_id == "agent_123"
        assert result.tools == ["search", "calculator"]
        assert result.temperature == 0.7
    
    @pytest.mark.asyncio
    async def test_get_session_nonexistent(self, service):
        """Test getting a non-existent session"""
        # Act
        result = await service.get_session("nonexistent_session")
        
        # Assert
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update_session(self, service, mock_agent_manager):
        """Test updating a session"""
        # Arrange
        update_data = SessionUpdate(
            persona_id="researcher",
            temperature=0.8
        )
        
        # Mock get_session to return a predefined response
        service.get_session = AsyncMock(return_value=SessionDetail(
            id="test_session_1",
            model_id="gpt-4",
            persona_id="researcher",  # Updated
            created_at=datetime.now(),
            last_activity=datetime.now(),
            agent_internal_id="agent_123",
            tools=["search", "calculator"],
            temperature=0.8,  # Updated
            reasoning_effort=30,
            budget_tokens=None,
            max_tokens=2000,
            custom_prompt=None
        ))
        
        # Act
        result = await service.update_session("test_session_1", update_data)
        
        # Assert
        assert isinstance(result, SessionDetail)
        assert result.persona_id == "researcher"
        assert result.temperature == 0.8
        
        # Verify manager calls
        mock_agent_manager.update_agent_settings.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_session_existing(self, service, mock_agent_manager):
        """Test deleting an existing session"""
        # Act
        result = await service.delete_session("test_session_1")
        
        # Assert
        assert result is True
        mock_agent_manager.delete_session.assert_called_once_with("test_session_1")
    
    @pytest.mark.asyncio
    async def test_delete_session_nonexistent(self, service, mock_agent_manager):
        """Test deleting a non-existent session"""
        # Act
        result = await service.delete_session("nonexistent_session")
        
        # Assert
        assert result is False
        mock_agent_manager.delete_session.assert_not_called()