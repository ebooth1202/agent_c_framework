import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from agent_c_api.main import app
from agent_c_api.api.v2.config.services import ConfigService
from agent_c_api.api.v2.models import (
    ModelInfo, PersonaInfo, ToolInfo,
    ModelsResponse, PersonasResponse, ToolsResponse, SystemConfigResponse
)

client = TestClient(app)

@pytest.fixture
def mock_config_service():
    with patch('agent_c_api.api.v2.config.router.get_config_service') as mock_service_factory:
        mock_service = MagicMock(spec=ConfigService)
        # Setup async methods with AsyncMock
        mock_service.get_models = AsyncMock()
        mock_service.get_model = AsyncMock()
        mock_service.get_personas = AsyncMock()
        mock_service.get_persona = AsyncMock()
        mock_service.get_tools = AsyncMock()
        mock_service.get_tool = AsyncMock()
        mock_service.get_system_config = AsyncMock()
        mock_service_factory.return_value = mock_service
        yield mock_service

def test_list_models(mock_config_service):
    # Set up mock response
    mock_config_service.get_models.return_value = ModelsResponse(
        models=[
            ModelInfo(
                id="gpt-4",
                name="GPT-4",
                provider="openai",
                description="Advanced language model",
                capabilities=["text"],
                parameters=[]
            )
        ]
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/models")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) == 1
    assert data["models"][0]["id"] == "gpt-4"
    assert data["models"][0]["provider"] == "openai"
    
    # Verify service was called
    mock_config_service.get_models.assert_called_once()

def test_get_model_success(mock_config_service):
    # Set up mock response
    mock_config_service.get_model.return_value = ModelInfo(
        id="gpt-4",
        name="GPT-4",
        provider="openai",
        description="Advanced language model",
        capabilities=["text"],
        parameters=[]
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/models/gpt-4")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "gpt-4"
    assert data["provider"] == "openai"
    
    # Verify service was called
    mock_config_service.get_model.assert_called_once_with("gpt-4")

def test_get_model_not_found(mock_config_service):
    # Set up mock response
    mock_config_service.get_model.return_value = None
    
    # Test endpoint
    response = client.get("/api/v2/config/models/nonexistent")
    
    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_list_personas(mock_config_service):
    # Set up mock response
    mock_config_service.get_personas.return_value = PersonasResponse(
        personas=[
            PersonaInfo(
                id="default",
                name="Default Assistant",
                description="Standard assistant persona"
            )
        ]
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/personas")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "personas" in data
    assert len(data["personas"]) == 1
    assert data["personas"][0]["id"] == "default"
    
    # Verify service was called
    mock_config_service.get_personas.assert_called_once()

def test_get_persona(mock_config_service):
    # Set up mock response
    mock_config_service.get_persona.return_value = PersonaInfo(
        id="default",
        name="Default Assistant",
        description="Standard assistant persona"
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/personas/default")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "default"

def test_list_tools(mock_config_service):
    # Set up mock response
    mock_config_service.get_tools.return_value = ToolsResponse(
        tools=[
            ToolInfo(
                id="search",
                name="Search Tool",
                category="web",
                is_essential=True
            )
        ],
        categories=["web"],
        essential_tools=["search"]
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/tools")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    assert "categories" in data
    assert "essential_tools" in data
    assert len(data["tools"]) == 1
    assert data["tools"][0]["id"] == "search"

def test_get_system_config(mock_config_service):
    # Set up mock response
    mock_config_service.get_system_config.return_value = SystemConfigResponse(
        models=[
            ModelInfo(id="gpt-4", name="GPT-4", provider="openai")
        ],
        personas=[
            PersonaInfo(id="default", name="Default Persona")
        ],
        tools=[
            ToolInfo(id="search", name="Search Tool", category="web")
        ],
        tool_categories=["web", "utility"],
        essential_tools=["search"]
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/system")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert "personas" in data
    assert "tools" in data
    assert "tool_categories" in data
    assert "essential_tools" in data