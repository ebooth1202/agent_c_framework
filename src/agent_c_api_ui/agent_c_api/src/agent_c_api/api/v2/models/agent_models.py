# src/agent_c_api/api/v2/models/agent_models.py
from typing import Dict, List, Optional, Any, ClassVar
from pydantic import BaseModel, Field, ConfigDict


class ModelParameter(BaseModel):
    """LLM model parameter"""
    name: str = Field(..., description="Parameter name")
    value: Any = Field(..., description="Parameter value")
    description: Optional[str] = Field(None, description="Parameter description")
    type: str = Field(..., description="Parameter type (string, int, float, boolean)")

class AgentConfig(BaseModel):
    """Current agent configuration in a session"""
    model_config = ConfigDict(protected_namespaces=())
    model_id: str = Field(..., description="LLM model ID")
    persona_id: str = Field(..., description="Persona ID")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Model parameters")
    system_message: Optional[str] = Field(None, description="Custom system message")

class AgentUpdate(BaseModel):
    """Parameters for updating agent settings"""
    model_config =  ConfigDict(protected_namespaces=())
    model_id: Optional[str] = Field(None, description="LLM model ID to use")
    persona_id: Optional[str] = Field(None, description="Persona ID to use")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Model parameters to update")
    system_message: Optional[str] = Field(None, description="Custom system message")

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