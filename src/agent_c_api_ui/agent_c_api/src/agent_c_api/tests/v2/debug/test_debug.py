# src/agent_c_api/tests/v2/debug/test_debug.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from agent_c_api.api.v2.debug.debug import get_session_debug_info, get_agent_debug_info
from agent_c_api.core.agent_manager import UItoAgentBridgeManager


@pytest.fixture
def mock_agent_manager():
    """Create a mock agent manager for testing."""
    manager = MagicMock(spec=UItoAgentBridgeManager)
    manager.debug_session = AsyncMock()
    manager.get_session_data = MagicMock()
    return manager


class TestSessionDebugEndpoint:
    """Tests for the session debug endpoint."""

    @pytest.mark.asyncio
    async def test_get_session_debug_info_success(self, mock_agent_manager):
        """Test successful retrieval of session debug info."""
        # Setup mock response
        session_id = "test-session-id"
        mock_debug_info = {
            "session_id": session_id,
            "agent_c_session_id": "internal-session-id",
            "agent_name": "Test Agent",
            "created_at": "2025-05-04T15:30:00",
            "backend": "openai",
            "model_name": "gpt-4",
            "session_manager": {"exists": True, "user_id": "test-user", "has_chat_session": True},
            "chat_session": {"session_id": "chat-session-id", "has_active_memory": True},
            "messages": {"count": 10, "user_messages": 5, "assistant_messages": 5, "latest_message": "Hello..."},
            "recent_messages": [
                {"role": "user", "content_preview": "Hello", "timestamp": "2025-05-04T15:35:00"},
                {"role": "assistant", "content_preview": "Hi there", "timestamp": "2025-05-04T15:35:10"}
            ],
            "current_chat_Log": {"exists": True, "count": 10},
            "tool_chest": {"exists": True, "active_tools": ["tool1", "tool2"]}
        }
        mock_agent_manager.debug_session.return_value = mock_debug_info

        # Call the endpoint function
        response = await get_session_debug_info(session_id, mock_agent_manager)

        # Verify the response
        assert response.status.success == True
        assert response.status.message == "Session debug information retrieved successfully"
        assert response.data == mock_debug_info
        mock_agent_manager.debug_session.assert_called_once_with(session_id)

    @pytest.mark.asyncio
    async def test_get_session_debug_info_session_not_found(self, mock_agent_manager):
        """Test session debug info when session is not found."""
        # Setup mock to raise ValueError
        session_id = "nonexistent-session"
        mock_agent_manager.debug_session.side_effect = ValueError(f"Invalid session ID: {session_id}")

        # Call the endpoint function and expect an exception
        with pytest.raises(HTTPException) as exc_info:
            await get_session_debug_info(session_id, mock_agent_manager)

        # Verify the exception
        assert exc_info.value.status_code == 404
        assert f"Invalid session ID: {session_id}" in str(exc_info.value.detail)
        mock_agent_manager.debug_session.assert_called_once_with(session_id)

    @pytest.mark.asyncio
    async def test_get_session_debug_info_error(self, mock_agent_manager):
        """Test session debug info when an unexpected error occurs."""
        # Setup mock to raise an unexpected exception
        session_id = "error-session"
        mock_agent_manager.debug_session.side_effect = Exception("Unexpected error")

        # Call the endpoint function and expect an exception
        with pytest.raises(HTTPException) as exc_info:
            await get_session_debug_info(session_id, mock_agent_manager)

        # Verify the exception
        assert exc_info.value.status_code == 500
        assert "Error retrieving debug information" in str(exc_info.value.detail)
        mock_agent_manager.debug_session.assert_called_once_with(session_id)


class TestAgentDebugEndpoint:
    """Tests for the agent debug endpoint."""

    @pytest.mark.asyncio
    async def test_get_agent_debug_info_success(self, mock_agent_manager):
        """Test successful retrieval of agent debug info."""
        # Setup mock response
        session_id = "test-session-id"
        mock_agent = MagicMock()
        mock_agent.temperature = 0.7
        mock_agent.reasoning_effort = "high"
        mock_agent.extended_thinking = True
        mock_agent.budget_tokens = 4000
        mock_agent.max_tokens = 2000

        # Setup mock internal agent
        mock_internal_agent = MagicMock()
        mock_internal_agent.__class__.__name__ = "TestAgent"
        mock_internal_agent.temperature = 0.8
        mock_internal_agent.reasoning_effort = "medium"
        mock_internal_agent.budget_tokens = 3000
        mock_internal_agent.max_tokens = 1500
        mock_agent.agent = mock_internal_agent

        # Setup mock session data
        mock_agent_manager.get_session_data.return_value = {"agent": mock_agent}

        # Call the endpoint function
        response = await get_agent_debug_info(session_id, mock_agent_manager)

        # Verify the response
        assert response.status.success == True
        assert response.status.message == "Agent debug information retrieved successfully"
        assert response.data["status"] == "success"
        assert response.data["agent_bridge_params"]["temperature"] == 0.7
        assert response.data["agent_bridge_params"]["reasoning_effort"] == "high"
        assert response.data["agent_bridge_params"]["extended_thinking"] == True
        assert response.data["agent_bridge_params"]["budget_tokens"] == 4000
        assert response.data["agent_bridge_params"]["max_tokens"] == 2000
        assert response.data["internal_agent_params"]["type"] == "TestAgent"
        assert response.data["internal_agent_params"]["temperature"] == 0.8
        assert response.data["internal_agent_params"]["reasoning_effort"] == "medium"
        assert response.data["internal_agent_params"]["budget_tokens"] == 3000
        assert response.data["internal_agent_params"]["max_tokens"] == 1500
        mock_agent_manager.get_session_data.assert_called_once_with(session_id)

    @pytest.mark.asyncio
    async def test_get_agent_debug_info_session_not_found(self, mock_agent_manager):
        """Test agent debug info when session is not found."""
        # Setup mock to return None for session data
        session_id = "nonexistent-session"
        mock_agent_manager.get_session_data.return_value = None

        # Call the endpoint function and expect an exception
        with pytest.raises(HTTPException) as exc_info:
            await get_agent_debug_info(session_id, mock_agent_manager)

        # Verify the exception
        assert exc_info.value.status_code == 404
        assert "Session not found" in str(exc_info.value.detail)
        mock_agent_manager.get_session_data.assert_called_once_with(session_id)

    @pytest.mark.asyncio
    async def test_get_agent_debug_info_no_internal_agent(self, mock_agent_manager):
        """Test agent debug info when there's no internal agent."""
        # Setup mock response without internal agent
        session_id = "test-session-id"
        mock_agent = MagicMock()
        mock_agent.temperature = 0.7
        mock_agent.agent = None  # No internal agent

        # Setup mock session data
        mock_agent_manager.get_session_data.return_value = {"agent": mock_agent}

        # Call the endpoint function
        response = await get_agent_debug_info(session_id, mock_agent_manager)

        # Verify the response contains agent_bridge_params but internal_agent_params is empty
        assert response.status.success == True
        assert response.data["agent_bridge_params"]["temperature"] == 0.7
        assert response.data["internal_agent_params"] == {}

    @pytest.mark.asyncio
    async def test_get_agent_debug_info_error(self, mock_agent_manager):
        """Test agent debug info when an unexpected error occurs."""
        # Setup mock to raise an unexpected exception
        session_id = "error-session"
        mock_agent_manager.get_session_data.side_effect = Exception("Unexpected error")

        # Call the endpoint function and expect an exception
        with pytest.raises(HTTPException) as exc_info:
            await get_agent_debug_info(session_id, mock_agent_manager)

        # Verify the exception
        assert exc_info.value.status_code == 500
        assert "Error retrieving agent debug information" in str(exc_info.value.detail)
        mock_agent_manager.get_session_data.assert_called_once_with(session_id)