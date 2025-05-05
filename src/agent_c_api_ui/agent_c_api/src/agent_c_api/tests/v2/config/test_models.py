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

def test_config_model_creation():
    """Test that config models can be instantiated properly"""
    # Test ModelInfo with nested ModelParameter
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
    assert model.provider == "OpenAI"
    assert len(model.parameters) == 1
    assert model.parameters[0].name == "temperature"
    
    # Test PersonaInfo
    persona = PersonaInfo(
        id="assistant",
        name="Assistant",
        description="A helpful assistant",
        file_path="/path/to/file.md",
        content="You are a helpful assistant"
    )
    
    assert persona.id == "assistant"
    assert persona.description == "A helpful assistant"
    
    # Test response models
    models_response = ModelsResponse(models=[model])
    assert len(models_response.models) == 1