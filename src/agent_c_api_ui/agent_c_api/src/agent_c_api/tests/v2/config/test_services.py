import pytest
import pytest_asyncio
from unittest.mock import patch, MagicMock, AsyncMock


from agent_c_api.api.v2.config.services import ConfigService
from agent_c_api.api.v2.models.config_models import (
    ModelInfo, PersonaInfo, ToolInfo, ModelParameter, ToolParameter,
    ModelsResponse, PersonasResponse, ToolsResponse, SystemConfigResponse
)

@pytest.fixture
def mock_models_config():
    with patch('agent_c_api.config.config_loader.MODELS_CONFIG') as mock_config:
        # Sample models config structure - similar to what's used in the real implementation
        mock_config.return_value = {
            "vendors": [
                {
                    "vendor": "openai",
                    "models": [
                        {
                            "id": "gpt-4",
                            "ui_name": "GPT-4",
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
                    ]
                }
            ]
        }
        yield mock_config

@pytest.fixture
def mock_persona_dir():
    with patch('os.path.isdir') as mock_isdir, \
         patch('glob.glob') as mock_glob, \
         patch('builtins.open', create=True) as mock_open:
        # Set up persona directory mock
        mock_isdir.return_value = True
        
        # Mock persona files
        mock_glob.return_value = [
            "/personas/default.md"
        ]
        
        # Mock file read
        mock_file = MagicMock()
        mock_file.__enter__.return_value.read.return_value = "You are a helpful assistant."
        mock_open.return_value = mock_file
        
        yield

@pytest.fixture
def mock_toolset():
    with patch('agent_c.Toolset.tool_registry') as mock_registry, \
         patch('agent_c_api.core.agent_manager.UItoAgentBridgeManager.ESSENTIAL_TOOLS', new=["search"]):
        # Create mock tool classes
        search_tool = MagicMock()
        search_tool.__name__ = "search"
        search_tool.__doc__ = "Search the web"
        search_tool.__module__ = "agent_c_tools.search"
        
        # Add tools to registry
        mock_registry.__iter__.return_value = [search_tool]
        
        yield

@pytest.mark.asyncio
async def test_get_models(mock_models_config):
    service = ConfigService()
    result = await service.get_models()
    
    assert isinstance(result, ModelsResponse)
    assert len(result.models) > 0  # Should have at least one model
    
    # Find the gpt-4 model in the results
    gpt4_model = next((m for m in result.models if m.id == "gpt-4"), None)
    assert gpt4_model is not None
    assert gpt4_model.name == "GPT-4"
    assert gpt4_model.provider == "openai"
    assert gpt4_model.description == "Advanced language model"
    assert "text" in gpt4_model.capabilities
    assert len(gpt4_model.parameters) > 0
    
    # Check temperature parameter
    temp_param = next((p for p in gpt4_model.parameters if p.name == "temperature"), None)
    assert temp_param is not None
    assert temp_param.type == "float"
    assert temp_param.default == 0.7
    assert "randomness" in temp_param.description.lower()
    
    # Check allowed inputs
    assert "text" in gpt4_model.allowed_inputs
    
    # Test cache - second call should use cached result
    result2 = await service.get_models()
    assert result2 is not None
    assert len(result2.models) == len(result.models)

@pytest.mark.asyncio
async def test_get_model(mock_models_config):
    service = ConfigService()
    
    # Test existing model
    model = await service.get_model("gpt-4")
    assert model is not None
    assert model.id == "gpt-4"
    assert model.name == "GPT-4"
    assert model.provider == "openai"
    
    # Test non-existent model
    model = await service.get_model("nonexistent")
    assert model is None
    
    # Test cache - second call should use cached result
    model2 = await service.get_model("gpt-4")
    assert model2 is not None
    assert model2.id == model.id

@pytest.mark.asyncio
async def test_get_personas(mock_persona_dir):
    service = ConfigService()
    result = await service.get_personas()
    
    assert isinstance(result, PersonasResponse)
    assert len(result.personas) > 0  # Should have at least one persona
    
    # Check that the default persona is included
    default_persona = next((p for p in result.personas if "default" in p.id), None)
    assert default_persona is not None
    assert "assistant" in default_persona.content.lower()
    assert default_persona.file_path is not None
    
    # Test cache - second call should use cached result
    result2 = await service.get_personas()
    assert result2 is not None
    assert len(result2.personas) == len(result.personas)

@pytest.mark.asyncio
async def test_get_persona(mock_persona_dir):
    service = ConfigService()
    
    # Test persona retrieval by injecting a get_personas result
    service.get_personas = AsyncMock(return_value=PersonasResponse(
        personas=[
            PersonaInfo(
                id="test-persona",
                name="Test Persona",
                description="For testing",
                file_path="/path/to/test.md",
                content="Test content"
            )
        ]
    ))
    
    # Test existing persona
    persona = await service.get_persona("test-persona")
    assert persona is not None
    assert persona.id == "test-persona"
    assert persona.name == "Test Persona"
    assert persona.content == "Test content"
    
    # Test non-existent persona
    persona = await service.get_persona("nonexistent")
    assert persona is None
    
    # Test cache - second call should use cached result
    persona2 = await service.get_persona("test-persona")
    assert persona2 is not None
    assert persona2.id == persona.id

@pytest.mark.asyncio
async def test_get_tools(mock_toolset):
    service = ConfigService()
    result = await service.get_tools()
    
    assert isinstance(result, ToolsResponse)
    assert len(result.tools) > 0  # Should have at least one tool
    assert len(result.categories) > 0  # Should have at least one category
    assert len(result.essential_tools) > 0  # Should have at least one essential tool
    
    # Find the search tool in results
    search_tool = next((t for t in result.tools if t.id == "search"), None)
    assert search_tool is not None
    assert search_tool.is_essential == True  # Should be in essential_tools list
    assert "search" in result.essential_tools
    
    # Test cache - second call should use cached result
    result2 = await service.get_tools()
    assert result2 is not None
    assert len(result2.tools) == len(result.tools)

@pytest.mark.asyncio
async def test_get_tool(mock_toolset):
    service = ConfigService()
    
    # Test tool retrieval by injecting a get_tools result
    service.get_tools = AsyncMock(return_value=ToolsResponse(
        tools=[
            ToolInfo(
                id="search",
                name="Search Tool",
                description="Search the web",
                category="web",
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
    ))
    
    # Test existing tool
    tool = await service.get_tool("search")
    assert tool is not None
    assert tool.id == "search"
    assert tool.name == "Search Tool"
    assert tool.category == "web"
    assert tool.is_essential == True
    assert len(tool.parameters) == 1
    assert tool.parameters[0].name == "query"
    
    # Test non-existent tool
    tool = await service.get_tool("nonexistent")
    assert tool is None
    
    # Test cache - second call should use cached result
    tool2 = await service.get_tool("search")
    assert tool2 is not None
    assert tool2.id == tool.id

@pytest.mark.asyncio
async def test_get_system_config(mock_models_config, mock_persona_dir, mock_toolset):
    service = ConfigService()
    
    # Mock component methods to return controlled data
    service.get_models = AsyncMock(return_value=ModelsResponse(
        models=[ModelInfo(id="gpt-4", name="GPT-4", provider="openai")]
    ))
    service.get_personas = AsyncMock(return_value=PersonasResponse(
        personas=[PersonaInfo(id="default", name="Default Assistant")]
    ))
    service.get_tools = AsyncMock(return_value=ToolsResponse(
        tools=[ToolInfo(id="search", name="Search Tool", category="web", is_essential=True)],
        categories=["web"],
        essential_tools=["search"]
    ))
    
    result = await service.get_system_config()
    
    assert len(result.models) == 1
    assert result.models[0].id == "gpt-4"
    assert len(result.personas) == 1
    assert result.personas[0].id == "default"
    assert len(result.tools) == 1
    assert result.tools[0].id == "search"
    assert result.tool_categories == ["web"]
    assert result.essential_tools == ["search"]
    
    # Test cache - second call should use cached result
    result2 = await service.get_system_config()
    assert result2 is not None
    assert len(result2.models) == len(result.models)

@pytest.mark.asyncio
async def test_get_system_config_error():
    service = ConfigService()
    
    # Mock component methods to simulate error
    service.get_models = AsyncMock(side_effect=Exception("Database error"))
    
    # Test that exception is propagated
    with pytest.raises(Exception) as exc_info:
        await service.get_system_config()
    
    assert "Database error" in str(exc_info.value)