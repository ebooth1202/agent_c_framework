import pytest
import json
from fastapi import status
from fastapi.testclient import TestClient

from agent_c_api.api.v2.models.config_models import (
    ModelInfo, PersonaInfo, ToolInfo, ModelParameter, ToolParameter,
    ModelsResponse, PersonasResponse, ToolsResponse, SystemConfigResponse
)

@pytest.mark.unit
@pytest.mark.config
@pytest.mark.router
class TestConfigRouter:
    """Tests for the config module router endpoints.
    
    These tests verify that the router endpoints correctly interact with the
    ConfigService and return proper responses. They use mock dependencies to
    isolate testing of the API layer.
    """
    
    #########################################
    # Models Endpoints Tests
    #########################################
    
    def test_list_models(self, client, mock_config_service):
        """Test the GET /config/models endpoint."""
        response = client.get("/api/v2/config/models")
        
        # Verify response status code
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        data = response.json()
        assert "models" in data
        assert len(data["models"]) > 0
        assert data["models"][0]["id"] == "gpt-4"
        assert data["models"][0]["name"] == "GPT-4"
        assert data["models"][0]["provider"] == "openai"
        
        # Verify service method was called once
        mock_config_service.get_models.assert_called_once_with()
    
    def test_get_model(self, client, mock_config_service):
        """Test the GET /config/models/{model_id} endpoint."""
        response = client.get("/api/v2/config/models/gpt-4")
        
        # Verify response status code
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        data = response.json()
        assert "id" in data
        assert data["id"] == "gpt-4"
        assert data["name"] == "GPT-4"
        assert data["provider"] == "openai"
        assert "parameters" in data
        assert len(data["parameters"]) > 0
        assert data["parameters"][0]["name"] == "temperature"
        
        # Verify service method was called
        mock_config_service.get_model.assert_called_once_with("gpt-4")
    
    def test_get_model_not_found(self, client, mock_config_service):
        """Test the GET /config/models/{model_id} endpoint with a non-existent model."""
        # Set up mock to return None (model not found)
        mock_config_service.get_model.return_value = None
        
        response = client.get("/api/v2/config/models/nonexistent")
        
        # Verify response status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify error response
        data = response.json()
        assert "detail" in data
        assert "MODEL_NOT_FOUND" in str(data["detail"])
        
        # Verify service method was called
        mock_config_service.get_model.assert_called_once_with("nonexistent")
    
    #########################################
    # Personas Endpoints Tests
    #########################################
    
    def test_list_personas(self, client, mock_config_service):
        """Test the GET /config/personas endpoint."""
        response = client.get("/api/v2/config/personas")
        
        # Verify response status code
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        data = response.json()
        assert "personas" in data
        assert len(data["personas"]) > 0
        assert data["personas"][0]["id"] == "default"
        assert data["personas"][0]["name"] == "Default Assistant"
        
        # Verify service method was called
        mock_config_service.get_personas.assert_called_once()
    
    def test_get_persona(self, client, mock_config_service):
        """Test the GET /config/personas/{persona_id} endpoint."""
        response = client.get("/api/v2/config/personas/default")
        
        # Verify response status code
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        data = response.json()
        assert "id" in data
        assert data["id"] == "default"
        assert data["name"] == "Default Assistant"
        assert "content" in data
        assert data["content"] == "You are a helpful assistant..."
        
        # Verify service method was called
        mock_config_service.get_persona.assert_called_once_with("default")
    
    def test_get_persona_not_found(self, client, mock_config_service):
        """Test the GET /config/personas/{persona_id} endpoint with a non-existent persona."""
        # Set up mock to return None (persona not found)
        mock_config_service.get_persona.return_value = None
        
        response = client.get("/api/v2/config/personas/nonexistent")
        
        # Verify response status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify error response
        data = response.json()
        assert "detail" in data
        assert "PERSONA_NOT_FOUND" in str(data["detail"])
        
        # Verify service method was called
        mock_config_service.get_persona.assert_called_once_with("nonexistent")
    
    #########################################
    # Tools Endpoints Tests
    #########################################
    
    def test_list_tools(self, client, mock_config_service):
        """Test the GET /config/tools endpoint."""
        response = client.get("/api/v2/config/tools")
        
        # Verify response status code
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        data = response.json()
        assert "tools" in data
        assert "categories" in data
        assert "essential_tools" in data
        assert len(data["tools"]) > 0
        assert data["tools"][0]["id"] == "search"
        assert data["tools"][0]["is_essential"] == True
        assert "search" in data["essential_tools"]
        
        # Verify service method was called
        mock_config_service.get_tools.assert_called_once()
    
    def test_get_tool(self, client, mock_config_service):
        """Test the GET /config/tools/{tool_id} endpoint."""
        response = client.get("/api/v2/config/tools/search")
        
        # Verify response status code
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        data = response.json()
        assert "id" in data
        assert data["id"] == "search"
        assert data["name"] == "Search Tool"
        assert data["category"] == "web"
        assert data["is_essential"] == True
        assert "parameters" in data
        assert len(data["parameters"]) > 0
        assert data["parameters"][0]["name"] == "query"
        
        # Verify service method was called
        mock_config_service.get_tool.assert_called_once_with("search")
    
    def test_get_tool_not_found(self, client, mock_config_service):
        """Test the GET /config/tools/{tool_id} endpoint with a non-existent tool."""
        # Set up mock to return None (tool not found)
        mock_config_service.get_tool.return_value = None
        
        response = client.get("/api/v2/config/tools/nonexistent")
        
        # Verify response status code
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Verify error response
        data = response.json()
        assert "detail" in data
        assert "TOOL_NOT_FOUND" in str(data["detail"])
        
        # Verify service method was called
        mock_config_service.get_tool.assert_called_once_with("nonexistent")
    
    #########################################
    # System Config Endpoint Tests
    #########################################
    
    def test_get_system_config(self, client, mock_config_service):
        """Test the GET /config/system endpoint."""
        response = client.get("/api/v2/config/system")
        
        # Verify response status code
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response content
        data = response.json()
        assert "models" in data
        assert "personas" in data
        assert "tools" in data
        assert "tool_categories" in data
        assert "essential_tools" in data
        assert len(data["models"]) > 0
        assert len(data["personas"]) > 0
        assert len(data["tools"]) > 0
        assert data["models"][0]["id"] == "gpt-4"
        assert data["personas"][0]["id"] == "default"
        assert data["tools"][0]["id"] == "search"
        assert "web" in data["tool_categories"]
        assert "search" in data["essential_tools"]
        
        # Verify service method was called
        mock_config_service.get_system_config.assert_called_once()
    
    def test_get_system_config_error(self, client, mock_config_service):
        """Test the GET /config/system endpoint with a service error."""
        # Set up mock to raise an exception
        mock_config_service.get_system_config.side_effect = Exception("Database error")
        
        response = client.get("/api/v2/config/system")
        
        # Verify response status code
        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        
        # Verify error response
        data = response.json()
        assert "detail" in data
        assert "CONFIG_RETRIEVAL_ERROR" in str(data["detail"])
        
        # Verify service method was called
        mock_config_service.get_system_config.assert_called_once()