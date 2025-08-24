from typing import Dict, Any

from agent_c.models.base import BaseModel
from pydantic import Field

class ClientToolInfo(BaseModel):
    """Information about a tool available to the client"""
    name: str = Field(..., description="Name of the toolset")
    description: str = Field("", description="Description of the tool's functionality")
    schemas: Dict[str, Any] = Field(..., description="JSON schema defining the tool's parameters and structure for tools in the toolset")

    @classmethod
    def from_toolset(cls, tool_class) -> "ClientToolInfo":
        """Create a ClientToolInfo from a toolset instance"""
        return cls(
            name=tool_class.__name__,
            description=tool_class.__doc__,
            schemas=tool_class.get_tool_schemas()
        )