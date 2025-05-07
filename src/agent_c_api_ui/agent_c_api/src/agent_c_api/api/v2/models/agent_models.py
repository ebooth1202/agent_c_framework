# src/agent_c_api/api/v2/models/agent_models.py
"""Agent model definitions for the v2 API.

This module contains models related to agent capabilities, LLM models, and personas.

IMPORTANT NOTE ON MODEL IMPORTS:
  - AgentConfig and AgentUpdate are defined in session_models.py but re-exported here
  - Always import AgentConfig and AgentUpdate from session_models.py directly
  - This re-export is maintained only for backward compatibility
  - Any changes to these models should be made in session_models.py

Relationships:
  - ModelInfo describes properties of LLM models used in AgentConfig
  - PersonaInfo describes personas referenced by persona_id in AgentConfig
  - ModelParameter describes parameters of LLM models that can be adjusted in AgentUpdate
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, ConfigDict

# Import the models from session_models instead of duplicating them
# This maintains backward compatibility while consolidating implementations
from .session_models import AgentConfig, AgentUpdate  # Re-exported for backward compatibility

class ModelParameter(BaseModel):
    """LLM model parameter definition.
    
    This model represents a parameter that can be adjusted for a specific LLM model,
    such as temperature, max_tokens, or other model-specific settings. These parameters
    are referenced by AgentConfig and can be modified via AgentUpdate.
    
    Relationships:
      - Used by ModelInfo to describe available parameters for a model
      - Referenced by AgentConfig/AgentUpdate when setting specific parameter values
    """
    name: str = Field(..., description="Parameter name")
    value: Any = Field(..., description="Parameter value")
    description: Optional[str] = Field(None, description="Parameter description")
    type: str = Field(..., description="Parameter type (string, int, float, boolean)")

class ModelInfo(BaseModel):
    """Information about an LLM model.
    
    This model contains comprehensive information about a specific LLM model
    available in the system, including its capabilities and configurable parameters.
    The model_id in AgentConfig references these models.
    
    Relationships:
      - Referenced by AgentConfig via model_id field
      - Contains a list of ModelParameter objects describing available settings
    """
    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Model name")
    description: Optional[str] = Field(None, description="Model description")
    provider: str = Field(..., description="Model provider (OpenAI, Anthropic, etc.)")
    capabilities: List[str] = Field(default_factory=list, description="Model capabilities")
    parameters: List[ModelParameter] = Field(default_factory=list, description="Available parameters")

class PersonaInfo(BaseModel):
    """Information about a persona.
    
    This model contains comprehensive information about an agent persona,
    which defines the agent's personality, capabilities, and behavior.
    The persona_id in AgentConfig references these personas.
    
    Relationships:
      - Referenced by AgentConfig via persona_id field
      - The system_message provides the prompt template for the agent
      - Can be changed via AgentUpdate by updating the persona_id field
    """
    id: str = Field(..., description="Persona ID")
    name: str = Field(..., description="Persona name")
    description: str = Field(..., description="Persona description")
    capabilities: List[str] = Field(default_factory=list, description="Persona capabilities")
    system_message: Optional[str] = Field(None, description="System message template")