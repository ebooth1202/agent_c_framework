from typing import Dict, Any, List

from agent_c.models.base import BaseModel
from pydantic import Field

from agent_c.util.logging_utils import LoggingManager

logger = LoggingManager(__name__).get_logger()

class ClientToolInfo(BaseModel):
    """Information about tools available to be added to agents"""
    name: str = Field(..., description="Name of the toolset")
    description: str = Field("", description="Description of the tool's functionality")
    schemas: List[Dict[str, Any]] = Field(..., description="JSON schema defining the tool's parameters and structure for tools in the toolset")

    @classmethod
    def from_toolset(cls, tool_class) -> "ClientToolInfo":
        """Create a ClientToolInfo from a toolset instance"""
        if tool_class.__doc__ is None:
            logger.warning(f"Tool class {tool_class.__name__} is missing a docstring.")

        return cls(
            name=tool_class.__name__,
            description=tool_class.__doc__ or "No description provided.",
            schemas=tool_class.get_tool_schemas()
        )