import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock

from agent_c_api.api.v2.config.services import ConfigService
from agent_c_api.api.v2.config.models import (
    ModelInfo, PersonaInfo, ToolInfo,
    ModelsResponse, PersonasResponse, ToolsResponse
)

@pytest.fixture
def mock_config_loader():
    with patch('agent_c_api.config.config_loader.get_config_value') as mock_get_config:
        # Sample models config structure - simplified for testing
        mock_get_config.return_value = {
            "openai": {
                "gpt-4": {
                    "label": "GPT-4",
                    "description": "Advanced language model",
                    "capabilities": ["text"],
                    "parameters": {
                        "temperature": {
                            "type": "float",
                            "default": 0.7,
                            "description": "Controls randomness"
                        }
                    },
                    "allowed_inputs": ["text"]
                }
            }
        }
        yield mock_get_config

@pytest.fixture
def mock_agent_manager():
    with patch('agent_c_api.core.agent_manager.get_available_personas') as mock_personas:
        # Sample personas structure
        mock_personas.return_value = [
            {
                "id": "default",
                "name": "Default Assistant",
                "description": "Standard assistant persona",
                "file_path": "/path/to/default.md",
                "content": "You are a helpful assistant."
            }
        ]
        yield mock_personas

@pytest.fixture
def mock_tools():
    with patch('agent_c_api.core.setup.get_available_tools') as mock_tools:
        # Sample tools structure
        mock_tools.return_value = [
            {
                "id": "search",
                "name": "Search Tool",
                "description": "Search the web",
                "category": "web",
                "essential": True,
                "parameters": [
                    {
                        "name": "query",
                        "type": "string",
                        "description": "Search query",
                        "required": True
                    }
                ]
            }
        ]
        yield mock_tools

@pytest.mark.asyncio
async def test_get_models(mock_config_loader):
    service = ConfigService()
    result = await service.get_models()
    
    assert isinstance(result, ModelsResponse)
    assert len(result.models) == 1
    assert result.models[0].id == "gpt-4"
    assert result.models[0].name == "GPT-4"
    assert result.models[0].provider == "openai"
    assert len(result.models[0].parameters) == 1
    assert result.models[0].parameters[0].name == "temperature"
    assert result.models[0].parameters[0].type == "float"

@pytest.mark.asyncio
async def test_get_model(mock_config_loader):
    service = ConfigService()
    
    # Test existing model
    model = await service.get_model("gpt-4")
    assert model is not None
    assert model.id == "gpt-4"
    
    # Test non-existent model
    model = await service.get_model("nonexistent")
    assert model is None

@pytest.mark.asyncio
async def test_get_personas(mock_agent_manager):
    service = ConfigService()
    result = await service.get_personas()
    
    assert isinstance(result, PersonasResponse)
    assert len(result.personas) == 1
    assert result.personas[0].id == "default"
    assert result.personas[0].name == "Default Assistant"
    assert result.personas[0].content == "You are a helpful assistant."

@pytest.mark.asyncio
async def test_get_tools(mock_tools):
    service = ConfigService()
    result = await service.get_tools()
    
    assert isinstance(result, ToolsResponse)
    assert len(result.tools) == 1
    assert result.tools[0].id == "search"
    assert result.tools[0].category == "web"
    assert result.tools[0].is_essential == True
    assert len(result.tools[0].parameters) == 1
    assert result.categories == ["web"]
    assert result.essential_tools == ["search"]

@pytest.mark.asyncio
async def test_get_system_config(mock_config_loader, mock_agent_manager, mock_tools):
    service = ConfigService()
    result = await service.get_system_config()
    
    assert len(result.models) == 1
    assert len(result.personas) == 1
    assert len(result.tools) == 1
    assert result.tool_categories == ["web"]
    assert result.essential_tools == ["search"]