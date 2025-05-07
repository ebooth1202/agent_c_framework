# src/agent_c_api/api/v2/models/agent_models.py
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

# Import the models from session_models instead of duplicating them
# This maintains backward compatibility while consolidating implementations
from .session_models import AgentConfig, AgentUpdate

class ModelParameter(BaseModel):
    """LLM model parameter"""
    name: str = Field(..., description="Parameter name")
    value: Any = Field(..., description="Parameter value")
    description: Optional[str] = Field(None, description="Parameter description")
    type: str = Field(..., description="Parameter type (string, int, float, boolean)")

class ModelInfo(BaseModel):
    """Information about an LLM model"""
    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Model name")
    description: Optional[str] = Field(None, description="Model description")
    provider: str = Field(..., description="Model provider (OpenAI, Anthropic, etc.)")
    capabilities: List[str] = Field(default_factory=list, description="Model capabilities")
    parameters: List[ModelParameter] = Field(default_factory=list, description="Available parameters")

class PersonaInfo(BaseModel):
    """Information about a persona"""
    id: str = Field(..., description="Persona ID")
    name: str = Field(..., description="Persona name")
    description: str = Field(..., description="Persona description")
    capabilities: List[str] = Field(default_factory=list, description="Persona capabilities")
    system_message: Optional[str] = Field(None, description="System message template")