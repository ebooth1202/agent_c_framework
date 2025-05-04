import pytest
from datetime import datetime
from fastapi import HTTPException
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from agent_c_api.api.v2.sessions.models import SessionCreate, SessionDetail, SessionUpdate, SessionListResponse, SessionSummary
from agent_c_api.api.v2.sessions.sessions import router, get_session_service
from agent_c_api.main import app


@pytest.fixture
def mock_session_service():
    """Fixture for a mocked SessionService"""
    service = MagicMock()
    service.create_session = AsyncMock()
    service.get_sessions = AsyncMock()
    service.get_session = AsyncMock()
    service.update_session = AsyncMock()
    service.delete_session = AsyncMock()
    return service


@pytest.fixture
def client(mock_session_service):
    """Fixture for a FastAPI test client with mocked dependencies"""
    app.dependency_overrides[get_session_service] = lambda: mock_session_service
    yield TestClient(app)
    app.dependency_overrides = {}


@pytest.fixture
def sample_session_detail():
    """Fixture for a sample SessionDetail object"""
    return SessionDetail(
        id="test_session_1",
        model_id="gpt-4",
        persona_id="programmer",
        created_at=datetime.now(),
        last_activity=datetime.now(),
        agent_internal_id="agent_123",
        tools=["search", "calculator"],
        temperature=0.7,
        reasoning_effort=30,
        budget_tokens=None,
        max_tokens=2000,
        custom_prompt=None
    )


@pytest.fixture
def sample_session_list():
    """Fixture for a sample SessionListResponse object"""
    return SessionListResponse(
        items=[
            SessionSummary(
                id="test_session_1",
                model_id="gpt-4",
                persona_id="programmer",
                created_at=datetime.now(),
                last_activity=datetime.now()
            ),
            SessionSummary(
                id="test_session_2",
                model_id="claude-3",
                persona_id="default",
                created_at=datetime.now(),
                last_activity=None
            )
        ],
        total=2,
        limit=10,
        offset=0
    )


class TestSessionRouter:
    """Tests for the session router endpoints"""
    
    @pytest.mark.asyncio
    async def test_create_session(self, client, mock_session_service, sample_session_detail):
        """Test creating a session"""
        # Arrange
        mock_session_service.create_session.return_value = sample_session_detail
        
        # Act
        response = client.post(
            "/api/v2/sessions",
            json={
                "model_id": "gpt-4",
                "persona_id": "programmer",
                "temperature": 0.7,
                "tools": ["search", "calculator"]
            }
        )
        
        # Assert
        assert response.status_code == 201
        assert response.json()["id"] == "test_session_1"
        assert response.json()["model_id"] == "gpt-4"
        mock_session_service.create_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_list_sessions(self, client, mock_session_service, sample_session_list):
        """Test listing sessions"""
        # Arrange
        mock_session_service.get_sessions.return_value = sample_session_list
        
        # Act
        response = client.get("/api/v2/sessions")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["total"] == 2
        assert len(response.json()["items"]) == 2
        mock_session_service.get_sessions.assert_called_once_with(10, 0)
        
        # Test with pagination
        response = client.get("/api/v2/sessions?limit=5&offset=1")
        assert response.status_code == 200
        mock_session_service.get_sessions.assert_called_with(5, 1)
    
    @pytest.mark.asyncio
    async def test_get_session_existing(self, client, mock_session_service, sample_session_detail):
        """Test getting an existing session"""
        # Arrange
        mock_session_service.get_session.return_value = sample_session_detail
        
        # Act
        response = client.get("/api/v2/sessions/test_session_1")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["id"] == "test_session_1"
        assert response.json()["model_id"] == "gpt-4"
        mock_session_service.get_session.assert_called_once_with("test_session_1")
    
    @pytest.mark.asyncio
    async def test_get_session_nonexistent(self, client, mock_session_service):
        """Test getting a non-existent session"""
        # Arrange
        mock_session_service.get_session.return_value = None
        
        # Act
        response = client.get("/api/v2/sessions/nonexistent_session")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
        mock_session_service.get_session.assert_called_once_with("nonexistent_session")
    
    @pytest.mark.asyncio
    async def test_update_session(self, client, mock_session_service, sample_session_detail):
        """Test updating a session"""
        # Arrange
        updated_session = sample_session_detail.model_copy()
        updated_session.persona_id = "researcher"
        updated_session.temperature = 0.8
        mock_session_service.get_session.return_value = sample_session_detail
        mock_session_service.update_session.return_value = updated_session
        
        # Act
        response = client.patch(
            "/api/v2/sessions/test_session_1",
            json={
                "persona_id": "researcher",
                "temperature": 0.8
            }
        )
        
        # Assert
        assert response.status_code == 200
        assert response.json()["persona_id"] == "researcher"
        assert response.json()["temperature"] == 0.8
        mock_session_service.update_session.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_session_error(self, client, mock_session_service):
        """Test handling errors during session update"""
        # Arrange
        mock_session_service.update_session.side_effect = Exception("Test error")
        mock_session_service.get_session.return_value = sample_session_detail
        
        # Act
        response = client.patch(
            "/api/v2/sessions/test_session_1",
            json={"temperature": 0.8}
        )
        
        # Assert
        assert response.status_code == 500
        assert "Failed to update session" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_delete_session_existing(self, client, mock_session_service, sample_session_detail):
        """Test deleting an existing session"""
        # Arrange
        mock_session_service.get_session.return_value = sample_session_detail
        mock_session_service.delete_session.return_value = True
        
        # Act
        response = client.delete("/api/v2/sessions/test_session_1")
        
        # Assert
        assert response.status_code == 204
        mock_session_service.delete_session.assert_called_once_with("test_session_1")
    
    @pytest.mark.asyncio
    async def test_delete_session_nonexistent(self, client, mock_session_service):
        """Test deleting a non-existent session"""
        # Arrange
        mock_session_service.get_session.return_value = None
        
        # Act
        response = client.delete("/api/v2/sessions/nonexistent_session")
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
        mock_session_service.delete_session.assert_not_called()
    
    @pytest.mark.asyncio
    async def test_delete_session_failure(self, client, mock_session_service, sample_session_detail):
        """Test failure when deleting a session"""
        # Arrange
        mock_session_service.get_session.return_value = sample_session_detail
        mock_session_service.delete_session.return_value = False
        
        # Act
        response = client.delete("/api/v2/sessions/test_session_1")
        
        # Assert
        assert response.status_code == 500
        assert "Failed to delete session" in response.json()["detail"]
        mock_session_service.delete_session.assert_called_once_with("test_session_1")