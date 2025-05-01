from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

class ModelParameter(BaseModel):
    """Parameter for a model configuration"""
    name: str
    type: str
    description: Optional[str] = None
    default: Optional[Any] = None

class ModelInfo(BaseModel):
    """Information about an available LLM model"""
    id: str
    name: str
    provider: str = Field(default="unknown")
    description: Optional[str] = None
    capabilities: List[str] = Field(default_factory=list)
    parameters: List[ModelParameter] = Field(default_factory=list)
    allowed_inputs: List[str] = Field(default_factory=list)

class PersonaInfo(BaseModel):
    """Information about an available persona"""
    id: str
    name: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    content: Optional[str] = None

class ToolParameter(BaseModel):
    """Parameter for a tool"""
    name: str
    type: str
    description: Optional[str] = None
    required: bool = False

class ToolInfo(BaseModel):
    """Information about an available tool"""
    id: str
    name: str
    description: Optional[str] = None
    category: str = "general"
    parameters: List[ToolParameter] = Field(default_factory=list)
    is_essential: bool = False

class ModelsResponse(BaseModel):
    """Response containing available models"""
    models: List[ModelInfo]

class PersonasResponse(BaseModel):
    """Response containing available personas"""
    personas: List[PersonaInfo]

class ToolsResponse(BaseModel):
    """Response containing available tools"""
    tools: List[ToolInfo]
    categories: List[str]
    essential_tools: List[str]

class SystemConfigResponse(BaseModel):
    """Combined system configuration response"""
    models: List[ModelInfo]
    personas: List[PersonaInfo]
    tools: List[ToolInfo]
    tool_categories: List[str]
    essential_tools: List[str]