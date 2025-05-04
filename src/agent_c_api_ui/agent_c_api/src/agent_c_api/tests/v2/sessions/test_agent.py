import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent_c_api.api.v2.sessions.models import AgentConfig, AgentUpdate, AgentUpdateResponse
from agent_c_api.api.v2.sessions.services import SessionService
from agent_c_api.api.v2.sessions.agent import get_agent_config, update_agent_config


class TestAgentService:
    @pytest.fixture
    def mock_agent_manager(self):
        # Create a mock agent manager
        mock_manager = MagicMock()
        
        # Create a mock agent
        mock_agent = MagicMock()
        
        # Setup agent's _get_agent_config method
        mock_agent._get_agent_config.return_value = {
            "model_name": "gpt-4",
            "persona_name": "developer",
            "custom_prompt": None,
            "agent_parameters": {
                "temperature": 0.7,
                "reasoning_effort": 5,
                "budget_tokens": None,
                "max_tokens": 2000
            },
            "initialized_tools": ["search", "calculator"]
        }
        
        # Setup get_session_data to return a valid session with the mock agent
        mock_manager.get_session_data.return_value = {
            "model_name": "gpt-4",
            "persona_name": "developer",
            "created_at": "2023-01-01T00:00:00",
            "last_activity": "2023-01-01T01:00:00",
            "agent_c_session_id": "agent_123",
            "agent": mock_agent
        }
        
        # Setup agent's attributes for testing updates
        mock_agent.temperature = 0.7
        mock_agent.persona_name = "developer"
        mock_agent.reasoning_effort = 5
        mock_agent.budget_tokens = None
        mock_agent.max_tokens = 2000
        mock_agent.custom_prompt = None
        mock_agent.initialize_agent_parameters = AsyncMock()
        
        return mock_manager

    @pytest.mark.asyncio
    async def test_get_agent_config(self, mock_agent_manager):
        # Create the service with the mock manager
        service = SessionService(mock_agent_manager)
        
        # Call the method
        config = await service.get_agent_config("test_session")
        
        # Check the result
        assert config is not None
        assert config.model_id == "gpt-4"
        assert config.persona_id == "developer"
        assert config.temperature == 0.7
        assert config.reasoning_effort == 5
        assert config.max_tokens == 2000
        assert config.tools == ["search", "calculator"]
        
        # Verify the get_session_data method was called
        mock_agent_manager.get_session_data.assert_called_with("test_session")

    @pytest.mark.asyncio
    async def test_get_agent_config_session_not_found(self, mock_agent_manager):
        # Setup get_session_data to return None
        mock_agent_manager.get_session_data.return_value = None
        
        # Create the service with the mock manager
        service = SessionService(mock_agent_manager)
        
        # Call the method
        config = await service.get_agent_config("test_session")
        
        # Check that None is returned
        assert config is None

    @pytest.mark.asyncio
    async def test_update_agent_config(self, mock_agent_manager):
        # Get the mock agent
        mock_agent = mock_agent_manager.get_session_data.return_value["agent"]
        
        # Create the service with the mock manager
        service = SessionService(mock_agent_manager)
        
        # Create an update request
        update = AgentUpdate(temperature=0.8, persona_id="researcher")
        
        # Call the method
        result = await service.update_agent_config("test_session", update)
        
        # Check the result
        assert result is not None
        assert "temperature" in result.changes_applied
        assert "persona_name" in result.changes_applied  # Note: persona_id maps to persona_name
        assert result.changes_skipped == {}
        
        # Verify the agent attributes were updated
        assert mock_agent.temperature == 0.8
        assert mock_agent.persona_name == "researcher"
        
        # Verify initialize_agent_parameters was called
        mock_agent.initialize_agent_parameters.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_agent_config_session_not_found(self, mock_agent_manager):
        # Setup get_session_data to return None
        mock_agent_manager.get_session_data.return_value = None
        
        # Create the service with the mock manager
        service = SessionService(mock_agent_manager)
        
        # Create an update request
        update = AgentUpdate(temperature=0.8, persona_id="researcher")
        
        # Call the method
        result = await service.update_agent_config("test_session", update)
        
        # Check that None is returned
        assert result is None


class TestAgentRouter:
    @pytest.fixture
    def mock_service(self):
        # Create a mock service
        mock_svc = AsyncMock()
        
        # Set up get_agent_config
        mock_svc.get_agent_config.return_value = AgentConfig(
            model_id="gpt-4",
            persona_id="developer",
            custom_prompt=None,
            temperature=0.7,
            reasoning_effort=5,
            budget_tokens=None,
            max_tokens=2000,
            tools=["search", "calculator"]
        )
        
        # Set up update_agent_config
        mock_svc.update_agent_config.return_value = AgentUpdateResponse(
            agent_config=AgentConfig(
                model_id="gpt-4",
                persona_id="researcher",
                custom_prompt=None,
                temperature=0.8,
                reasoning_effort=5,
                budget_tokens=None,
                max_tokens=2000,
                tools=["search", "calculator"]
            ),
            changes_applied={"temperature": 0.8, "persona_id": "researcher"},
            changes_skipped={}
        )
        
        return mock_svc
    
    @pytest.mark.asyncio
    async def test_get_agent_config_endpoint(self, mock_service):
        # Call the endpoint
        result = await get_agent_config("test_session", mock_service)
        
        # Check the result
        assert result.model_id == "gpt-4"
        assert result.persona_id == "developer"
        assert result.temperature == 0.7
        
        # Verify the service method was called
        mock_service.get_agent_config.assert_called_once_with("test_session")
    
    @pytest.mark.asyncio
    async def test_get_agent_config_endpoint_not_found(self, mock_service):
        # Setup the mock to return None
        mock_service.get_agent_config.return_value = None
        
        # Call the endpoint and expect an exception
        with pytest.raises(Exception) as exc_info:
            await get_agent_config("test_session", mock_service)
        
        # Check the exception
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_update_agent_config_endpoint(self, mock_service):
        # Create an update request
        update = AgentUpdate(temperature=0.8, persona_id="researcher")
        
        # Call the endpoint
        result = await update_agent_config("test_session", update, mock_service)
        
        # Check the result
        assert result.agent_config.persona_id == "researcher"
        assert result.agent_config.temperature == 0.8
        assert result.changes_applied == {"temperature": 0.8, "persona_id": "researcher"}
        
        # Verify the service method was called
        mock_service.update_agent_config.assert_called_once_with("test_session", update)
    
    @pytest.mark.asyncio
    async def test_update_agent_config_endpoint_not_found(self, mock_service):
        # Setup the mock to return None
        mock_service.update_agent_config.return_value = None
        
        # Create an update request
        update = AgentUpdate(temperature=0.8, persona_id="researcher")
        
        # Call the endpoint and expect an exception
        with pytest.raises(Exception) as exc_info:
            await update_agent_config("test_session", update, mock_service)
        
        # Check the exception
        assert exc_info.value.status_code == 404
        assert "not found" in str(exc_info.value.detail)