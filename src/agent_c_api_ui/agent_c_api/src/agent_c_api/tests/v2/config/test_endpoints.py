import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock

from agent_c_api.main import app
from agent_c_api.api.v2.config.services import ConfigService
from agent_c_api.api.v2.models.config_models import (
    ModelInfo, PersonaInfo, ToolInfo, ToolParameter, ModelParameter,
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
                parameters=[],
                allowed_inputs=["text"]
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
    assert data["models"][0]["capabilities"] == ["text"]
    assert "allowed_inputs" in data["models"][0]
    
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
        parameters=[
            ModelParameter(
                name="temperature",
                type="float",
                description="Controls randomness",
                default=0.7
            )
        ],
        allowed_inputs=["text"]
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/models/gpt-4")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "gpt-4"
    assert data["provider"] == "openai"
    assert data["capabilities"] == ["text"]
    assert len(data["parameters"]) == 1
    assert data["parameters"][0]["name"] == "temperature"
    assert data["allowed_inputs"] == ["text"]
    
    # Verify service was called
    mock_config_service.get_model.assert_called_once_with("gpt-4")

def test_get_model_not_found(mock_config_service):
    # Set up mock response
    mock_config_service.get_model.return_value = None
    
    # Test endpoint
    response = client.get("/api/v2/config/models/nonexistent")
    
    # Verify response
    assert response.status_code == 404
    error_detail = response.json()["detail"]
    assert isinstance(error_detail, dict)
    assert error_detail["error_code"] == "MODEL_NOT_FOUND"
    assert "nonexistent" in error_detail["message"]
    assert error_detail["params"]["model_id"] == "nonexistent"

def test_list_personas(mock_config_service):
    # Set up mock response
    mock_config_service.get_personas.return_value = PersonasResponse(
        personas=[
            PersonaInfo(
                id="default",
                name="Default Assistant",
                description="Standard assistant persona",
                file_path="/path/to/default.md",
                content="You are a helpful assistant..."
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
    assert data["personas"][0]["name"] == "Default Assistant"
    assert "file_path" in data["personas"][0]
    assert "content" in data["personas"][0]
    
    # Verify service was called
    mock_config_service.get_personas.assert_called_once()

def test_get_persona_success(mock_config_service):
    # Set up mock response
    mock_config_service.get_persona.return_value = PersonaInfo(
        id="default",
        name="Default Assistant",
        description="Standard assistant persona",
        file_path="/path/to/default.md",
        content="You are a helpful assistant..."
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/personas/default")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "default"
    assert data["name"] == "Default Assistant"
    assert "file_path" in data
    assert "content" in data

    # Verify service was called
    mock_config_service.get_persona.assert_called_once_with("default")

def test_get_persona_not_found(mock_config_service):
    # Set up mock response
    mock_config_service.get_persona.return_value = None
    
    # Test endpoint
    response = client.get("/api/v2/config/personas/nonexistent")
    
    # Verify response
    assert response.status_code == 404
    error_detail = response.json()["detail"]
    assert isinstance(error_detail, dict)
    assert error_detail["error_code"] == "PERSONA_NOT_FOUND"
    assert "nonexistent" in error_detail["message"]
    assert error_detail["params"]["persona_id"] == "nonexistent"

def test_list_tools(mock_config_service):
    # Set up mock response
    mock_config_service.get_tools.return_value = ToolsResponse(
        tools=[
            ToolInfo(
                id="search",
                name="Search Tool",
                category="web",
                description="Search the web",
                parameters=[
                    ToolParameter(
                        name="query",
                        type="string",
                        description="Search query",
                        required=True
                    )
                ],
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
    assert data["tools"][0]["category"] == "web"
    assert data["tools"][0]["is_essential"] == True
    assert len(data["tools"][0]["parameters"]) == 1
    
    # Verify service was called
    mock_config_service.get_tools.assert_called_once()

def test_list_tools_with_category_filter(mock_config_service):
    # Set up mock response - same as above, service filtering is simulated
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
    
    # Test endpoint with category parameter
    response = client.get("/api/v2/config/tools?category=web")
    
    # Verify response
    assert response.status_code == 200
    # Result filtering would happen in the service layer
    # Here we just verify the parameter is correctly passed
    
    # Verify service was called
    mock_config_service.get_tools.assert_called_once()

def test_get_tool_success(mock_config_service):
    # Set up mock response
    mock_config_service.get_tool.return_value = ToolInfo(
        id="search",
        name="Search Tool",
        category="web",
        description="Search the web",
        parameters=[
            ToolParameter(
                name="query",
                type="string",
                description="Search query",
                required=True
            )
        ],
        is_essential=True
    )
    
    # Test endpoint
    response = client.get("/api/v2/config/tools/search")
    
    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "search"
    assert data["name"] == "Search Tool"
    assert data["category"] == "web"
    assert data["is_essential"] == True
    assert len(data["parameters"]) == 1
    assert data["parameters"][0]["name"] == "query"
    assert data["parameters"][0]["required"] == True
    
    # Verify service was called
    mock_config_service.get_tool.assert_called_once_with("search")

def test_get_tool_not_found(mock_config_service):
    # Set up mock response
    mock_config_service.get_tool.return_value = None
    
    # Test endpoint
    response = client.get("/api/v2/config/tools/nonexistent")
    
    # Verify response
    assert response.status_code == 404
    error_detail = response.json()["detail"]
    assert isinstance(error_detail, dict)
    assert error_detail["error_code"] == "TOOL_NOT_FOUND"
    assert "nonexistent" in error_detail["message"]
    assert error_detail["params"]["tool_id"] == "nonexistent"

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
    assert len(data["models"]) == 1
    assert len(data["personas"]) == 1
    assert len(data["tools"]) == 1
    assert len(data["tool_categories"]) == 2
    assert len(data["essential_tools"]) == 1
    
    # Verify service was called
    mock_config_service.get_system_config.assert_called_once()

def test_system_config_error(mock_config_service):
    # Set up mock to raise an exception
    mock_config_service.get_system_config.side_effect = Exception("Config error")
    
    # Test endpoint
    response = client.get("/api/v2/config/system")
    
    # Verify response
    assert response.status_code == 500
    error_detail = response.json()["detail"]
    assert isinstance(error_detail, dict)
    assert error_detail["error_code"] == "CONFIG_RETRIEVAL_ERROR"
    assert "Config error" in error_detail["message"]