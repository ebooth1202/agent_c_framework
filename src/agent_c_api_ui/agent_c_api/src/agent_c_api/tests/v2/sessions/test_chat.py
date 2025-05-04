import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json

from fastapi import FastAPI
from fastapi.testclient import TestClient

from agent_c_api.api.v2.sessions.chat import ChatService, router
from agent_c_api.api.v2.models.chat_models import ChatMessage, ChatRequest


@pytest.fixture
def app():
    """Create a test FastAPI application"""
    app = FastAPI()
    app.include_router(router, prefix="/{session_id}")
    return app


@pytest.fixture
def client(app):
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_agent_manager():
    """Create a mock agent manager"""
    manager = MagicMock()
    
    # Mock get_session_data to return valid data for test_session_id
    def get_session_data_side_effect(session_id):
        if session_id == "test_session_id":
            return {"agent": MagicMock()}
        return None
    
    manager.get_session_data.side_effect = get_session_data_side_effect
    
    # Mock stream_response to yield test tokens
    async def stream_response_mock(*args, **kwargs):
        yield "Response token 1"
        yield "Response token 2"
    
    manager.stream_response = AsyncMock(side_effect=stream_response_mock)
    
    # Mock cancel_interaction to return True for test_session_id
    def cancel_interaction_side_effect(session_id):
        return session_id == "test_session_id"
    
    manager.cancel_interaction.side_effect = cancel_interaction_side_effect
    
    return manager


@pytest.fixture
def mock_session_service():
    """Create a mock session service"""
    service = MagicMock()
    
    # Mock get_session to return a session for test_session_id
    async def get_session_side_effect(session_id):
        if session_id == "test_session_id":
            return {"id": session_id}
        return None
    
    service.get_session = AsyncMock(side_effect=get_session_side_effect)
    
    return service


@pytest.fixture
def chat_service(mock_agent_manager):
    """Create a ChatService with a mock agent manager"""
    return ChatService(agent_manager=mock_agent_manager)


@pytest.mark.asyncio
async def test_send_message_success(chat_service):
    """Test sending a message successfully"""
    # Create a test message
    message = ChatMessage(
        role="user",
        content=[{"type": "text", "text": "Hello, world!"}]
    )
    
    # Get the generator
    generator = chat_service.send_message("test_session_id", message)
    
    # Collect the response tokens
    tokens = [token async for token in generator]
    
    # Verify the response
    assert len(tokens) == 2
    assert tokens[0] == "Response token 1"
    assert tokens[1] == "Response token 2"
    
    # Verify the manager was called correctly
    chat_service.agent_manager.stream_response.assert_called_once_with(
        "test_session_id",
        user_message="Hello, world!",
        file_ids=None
    )


@pytest.mark.asyncio
async def test_send_message_with_files(chat_service):
    """Test sending a message with file attachments"""
    # Create a test message with file content
    message = ChatMessage(
        role="user",
        content=[
            {"type": "text", "text": "Check this file"},
            {"type": "file", "file_id": "file123"}
        ]
    )
    
    # Get the generator
    generator = chat_service.send_message("test_session_id", message, ["file123"])
    
    # Collect the response tokens
    tokens = [token async for token in generator]
    
    # Verify the manager was called correctly
    chat_service.agent_manager.stream_response.assert_called_once_with(
        "test_session_id",
        user_message="Check this file",
        file_ids=["file123"]
    )


@pytest.mark.asyncio
async def test_send_message_session_not_found(chat_service):
    """Test sending a message to a non-existent session"""
    # Create a test message
    message = ChatMessage(
        role="user",
        content=[{"type": "text", "text": "Hello, world!"}]
    )
    
    # Attempt to send to a non-existent session
    with pytest.raises(Exception) as excinfo:
        async for _ in chat_service.send_message("nonexistent_session", message):
            pass
    
    # Verify the error
    assert "Session not found" in str(excinfo.value)


@pytest.mark.asyncio
async def test_send_message_invalid_role(chat_service):
    """Test sending a message with an invalid role"""
    # Create a test message with invalid role
    message = ChatMessage(
        role="assistant",  # Only 'user' is accepted
        content=[{"type": "text", "text": "Hello, world!"}]
    )
    
    # Attempt to send with invalid role
    with pytest.raises(Exception) as excinfo:
        async for _ in chat_service.send_message("test_session_id", message):
            pass
    
    # Verify the error
    assert "Only 'user' role messages are accepted" in str(excinfo.value)


@pytest.mark.asyncio
async def test_cancel_interaction_success(chat_service):
    """Test cancelling an interaction successfully"""
    # Cancel the interaction
    result = await chat_service.cancel_interaction("test_session_id")
    
    # Verify the result
    assert result is True
    
    # Verify the manager was called
    chat_service.agent_manager.cancel_interaction.assert_called_once_with("test_session_id")


@pytest.mark.asyncio
async def test_cancel_interaction_session_not_found(chat_service):
    """Test cancelling an interaction for a non-existent session"""
    # Attempt to cancel an interaction for a non-existent session
    with pytest.raises(Exception) as excinfo:
        await chat_service.cancel_interaction("nonexistent_session")
    
    # Verify the error
    assert "Session not found" in str(excinfo.value)


# Tests for the REST endpoints
@pytest.mark.asyncio
async def test_send_chat_message_endpoint(client, monkeypatch, mock_session_service):
    """Test the POST endpoint for sending a chat message"""
    # Mock the session_service dependency
    @patch('agent_c_api.api.v2.sessions.chat.SessionService', return_value=mock_session_service)
    @patch('agent_c_api.api.v2.sessions.chat.ChatService')
    def test_endpoint(mock_chat_service, mock_session_svc, client):
        # Mock the chat service to return a generator
        async def mock_send_message(*args, **kwargs):
            yield "Response 1"
            yield "Response 2"
        
        mock_chat_service.return_value.send_message.side_effect = mock_send_message
        
        # Create a test request
        request_data = {
            "message": {
                "role": "user",
                "content": [{"type": "text", "text": "Hello, API!"}]
            },
            "stream": True
        }
        
        # Send the request
        response = client.post(
            "/test_session_id/chat", 
            json=request_data
        )
        
        # Verify the response
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/plain; charset=utf-8"
        assert "Response 1\nResponse 2\n" in response.text
        
        # Verify mocks were called correctly
        mock_session_service.get_session.assert_called_once_with("test_session_id")
        mock_chat_service.return_value.send_message.assert_called_once()
        
    test_endpoint(client=client)


@pytest.mark.asyncio
async def test_cancel_chat_interaction_endpoint(client, monkeypatch, mock_session_service):
    """Test the DELETE endpoint for cancelling a chat interaction"""
    # Mock the dependencies
    @patch('agent_c_api.api.v2.sessions.chat.SessionService', return_value=mock_session_service)
    @patch('agent_c_api.api.v2.sessions.chat.ChatService')
    def test_endpoint(mock_chat_service, mock_session_svc, client):
        # Mock the chat service to return success
        mock_chat_service.return_value.cancel_interaction = AsyncMock(return_value=True)
        
        # Send the request
        response = client.delete("/test_session_id/chat")
        
        # Verify the response
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verify mocks were called correctly
        mock_session_service.get_session.assert_called_once_with("test_session_id")
        mock_chat_service.return_value.cancel_interaction.assert_called_once_with("test_session_id")
        
    test_endpoint(client=client)