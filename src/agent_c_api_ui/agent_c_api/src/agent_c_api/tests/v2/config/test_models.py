import pytest
from typing import Dict, List, Any

from agent_c_api.api.v2.models.config_models import (
    ModelParameter, ModelInfo, PersonaInfo, ToolParameter, ToolInfo,
    ModelsResponse, PersonasResponse, ToolsResponse, SystemConfigResponse
)

def test_config_models_imports():
    """Verify that config models can be imported correctly from the centralized location"""
    # This test just verifies imports work, so we don't need to do anything else
    pass

def test_model_parameter():
    """Test ModelParameter creation and validation"""
    param = ModelParameter(
        name="temperature",
        type="float",
        description="Controls randomness",
        default=0.7
    )
    
    assert param.name == "temperature"
    assert param.type == "float"
    assert param.description == "Controls randomness"
    assert param.default == 0.7

def test_model_info():
    """Test ModelInfo creation and validation"""
    model_param = ModelParameter(
        name="temperature",
        type="float",
        description="Controls randomness",
        default=0.7
    )
    
    model = ModelInfo(
        id="gpt-4",
        name="GPT-4",
        provider="OpenAI",
        description="Advanced language model",
        capabilities=["chat", "completion"],
        parameters=[model_param],
        allowed_inputs=["text"]
    )
    
    assert model.id == "gpt-4"
    assert model.name == "GPT-4"
    assert model.provider == "OpenAI"
    assert model.description == "Advanced language model"
    assert "chat" in model.capabilities
    assert "completion" in model.capabilities
    assert len(model.parameters) == 1
    assert model.parameters[0].name == "temperature"
    assert model.allowed_inputs == ["text"]

def test_persona_info():
    """Test PersonaInfo creation and validation"""
    persona = PersonaInfo(
        id="assistant",
        name="Assistant",
        description="A helpful assistant",
        file_path="/path/to/file.md",
        content="You are a helpful assistant"
    )
    
    assert persona.id == "assistant"
    assert persona.name == "Assistant"
    assert persona.description == "A helpful assistant"
    assert persona.file_path == "/path/to/file.md"
    assert persona.content == "You are a helpful assistant"

def test_tool_parameter():
    """Test ToolParameter creation and validation"""
    param = ToolParameter(
        name="query",
        type="string",
        description="Search query",
        required=True
    )
    
    assert param.name == "query"
    assert param.type == "string"
    assert param.description == "Search query"
    assert param.required == True

def test_tool_info():
    """Test ToolInfo creation and validation"""
    param = ToolParameter(
        name="query",
        type="string",
        description="Search query",
        required=True
    )
    
    tool = ToolInfo(
        id="search",
        name="Search Tool",
        description="Search the web",
        category="web",
        parameters=[param],
        is_essential=True
    )
    
    assert tool.id == "search"
    assert tool.name == "Search Tool"
    assert tool.description == "Search the web"
    assert tool.category == "web"
    assert len(tool.parameters) == 1
    assert tool.parameters[0].name == "query"
    assert tool.is_essential == True

def test_models_response():
    """Test ModelsResponse creation and validation"""
    model = ModelInfo(
        id="gpt-4",
        name="GPT-4",
        provider="OpenAI"
    )
    
    response = ModelsResponse(models=[model])
    
    assert len(response.models) == 1
    assert response.models[0].id == "gpt-4"

def test_personas_response():
    """Test PersonasResponse creation and validation"""
    persona = PersonaInfo(
        id="assistant",
        name="Assistant"
    )
    
    response = PersonasResponse(personas=[persona])
    
    assert len(response.personas) == 1
    assert response.personas[0].id == "assistant"

def test_tools_response():
    """Test ToolsResponse creation and validation"""
    tool = ToolInfo(
        id="search",
        name="Search Tool",
        category="web",
        is_essential=True
    )
    
    response = ToolsResponse(
        tools=[tool],
        categories=["web", "utility"],
        essential_tools=["search"]
    )
    
    assert len(response.tools) == 1
    assert response.tools[0].id == "search"
    assert "web" in response.categories
    assert "search" in response.essential_tools

def test_system_config_response():
    """Test SystemConfigResponse creation and validation"""
    model = ModelInfo(id="gpt-4", name="GPT-4", provider="openai")
    persona = PersonaInfo(id="assistant", name="Assistant")
    tool = ToolInfo(id="search", name="Search Tool", category="web")
    
    response = SystemConfigResponse(
        models=[model],
        personas=[persona],
        tools=[tool],
        tool_categories=["web", "utility"],
        essential_tools=["search"]
    )
    
    assert len(response.models) == 1
    assert response.models[0].id == "gpt-4"
    assert len(response.personas) == 1
    assert response.personas[0].id == "assistant"
    assert len(response.tools) == 1
    assert response.tools[0].id == "search"
    assert "web" in response.tool_categories
    assert "search" in response.essential_tools