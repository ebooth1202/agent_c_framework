# src/agent_c_api/api/v2/models/tool_models.py
from typing import Dict, List, Optional, Any, ClassVar
from pydantic import BaseModel, Field

class ToolParameter(BaseModel):
    """Tool parameter definition"""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(False, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value if any")

class ToolInfo(BaseModel):
    """Information about a tool"""
    id: str = Field(..., description="Tool ID")
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    category: str = Field(..., description="Tool category")
    parameters: List[ToolParameter] = Field(default_factory=list, description="Tool parameters")
    examples: List[str] = Field(default_factory=list, description="Usage examples")

class ToolCategory(BaseModel):
    """A category of tools"""
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    tools: List[ToolInfo] = Field(..., description="Tools in this category")

class ToolsList(BaseModel):
    """Comprehensive list of available tools"""
    categories: List[ToolCategory] = Field(..., description="Tool categories")
    
class SessionTools(BaseModel):
    """Tools currently enabled in a session"""
    enabled_tools: List[str] = Field(..., description="Enabled tool IDs")
    available_tools: List[str] = Field(..., description="Available but not enabled tool IDs")

class ToolsUpdate(BaseModel):
    """Parameters for updating session tools"""
    enabled_tools: List[str] = Field(..., description="Tool IDs to enable")
    
class ToolCall(BaseModel):
    """A call to a tool"""
    tool_id: str = Field(..., description="Tool ID")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    
class ToolResult(BaseModel):
    """Result of a tool call"""
    tool_id: str = Field(..., description="Tool ID")
    success: bool = Field(..., description="Whether call was successful")
    result: Any = Field(..., description="Result value")
    error: Optional[str] = Field(None, description="Error message if failed")