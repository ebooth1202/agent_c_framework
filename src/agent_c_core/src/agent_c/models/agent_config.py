from fnmatch import fnmatch
from typing import Optional, List, Any, Union, Literal, Dict
from pydantic import Field, ConfigDict

from agent_c.models.base import BaseModel
from agent_c.models.completion import CompletionParams

class AgentCatalogEntry(BaseModel):
    """A catalog entry for an agent configuration"""
    name: str = Field(..., description="Name of the agent configuration")
    key: str = Field(..., description="Key for the agent configuration, used for identification")
    agent_description: Optional[str] = Field(None, description="A description of the agent's purpose and capabilities")
    category: List[str] = Field(default_factory=list, description="A list of categories this agent belongs to from most to least general")
    toolsets: List[str] = Field(default_factory=list, description="List of enabled toolset names the agent can use")

class AgentConfigurationBase(BaseModel):
    version: int = Field(..., description="Configuration version")
    name: str = Field(..., description="Name of the agent")
    agent_description: Optional[str] = Field(None, description="A description of the agent's purpose and capabilities")
    tools: List[str] = Field(default_factory=list, description="List of enabled toolset names the agent can use")
    blocked_tool_patterns: List[str] = Field(default_factory=list, description="A list of patterns for blocking individual tools like `run_*`")
    allowed_tool_patterns: List[str] = Field(default_factory=list, description="A list of patterns for allowing individual tools like `run_pnpm` (overrides blocks)")

    def filter_allowed_tools(self, schemas: List[Dict[str, any]]) -> List[Dict[str, Any]]:
        """
        Filter tools based on name patterns.

        A tool is removed if:
        - Its name matches any blocked pattern AND
        - Its name does not match any allowed pattern

        Args:
            schemas (List[Dict[str, any]]): List of tool schemas with 'name' keys

        Returns:
            Filtered list of tools

        Example:
            tools = [
                {"name": "run_npm", "description": "..."},
                {"name": "run_pytest", "description": "..."},
                {"name": "run_pnpm", "description": "..."},
                {"name": "run_git", "description": "..."},
                {"name": "other_tool", "description": "..."}
            ]

            filtered = filter_allowed_tools(
                tools,
                allowed_patterns=["run_pnpm", "run_git"],
                blocked_patterns=["run_*"]
            )
            # Result: run_pnpm, run_git, and other_tool remain
        """

        def matches_any_pattern(name: str, patterns: List[str]) -> bool:
            """Check if name matches any of the given patterns."""
            return any(fnmatch(name, pattern) for pattern in patterns)

        filtered_tools = []

        for tool in schemas:
            tool_name = tool.get("name", "")

            # Check if tool matches any blocked pattern
            is_blocked = matches_any_pattern(tool_name, self.blocked_tool_patterns)

            if is_blocked:
                # If blocked, check if it's also allowed (allowed overrides blocked)
                is_allowed = matches_any_pattern(tool_name, self.allowed_tool_patterns)
                if is_allowed:
                    filtered_tools.append(tool)
                # If blocked and not allowed, skip this tool
            else:
                # If not blocked, keep the tool
                filtered_tools.append(tool)

        return filtered_tools

class AgentConfigurationV1(AgentConfigurationBase):
    """Version 1 of the Agent Configuration"""
    version: Literal[1] = Field(1, description="Configuration version")
    model_id: str = Field(..., description="ID of the LLM model being used by the agent")
    agent_params: Optional[CompletionParams] = Field(None, description="Parameters for the interaction with the agent")
    prompt_metadata: Optional[dict[str, Any]] = Field(None, description="Metadata for the prompt, such as versioning or author information")
    persona: str = Field(..., description="Persona prompt of the persona defining the agent's behavior")
    uid: Optional[str] = Field(None, description="Unique identifier for the configuration")


class AgentConfigurationV2(AgentConfigurationBase):
    """Version 2 of the Agent Configuration - example with new fields"""
    version: Literal[2] = Field(2, description="Configuration version")
    key: str = Field(..., description="Key for the agent configuration, used for identification")
    model_id: str = Field(..., description="ID of the LLM model being used by the agent")
    agent_params: Optional[CompletionParams] = Field(None, description="Parameters for the interaction with the agent")
    prompt_metadata: Optional[dict[str, Any]] = Field(None, description="Metadata for the prompt")
    persona: str = Field(..., description="Persona prompt of the persona defining the agent's behavior")
    uid: Optional[str] = Field(None, description="Unique identifier for the configuration")

    category: List[str] = Field(default_factory=list, description="A list of categories this agent belongs to from most to least general" )

    def as_catalog_entry(self) -> AgentCatalogEntry:
        """Convert this configuration to a catalog entry"""
        return AgentCatalogEntry(
            name=self.name,
            key=self.key,
            agent_description=self.agent_description,
            category=self.category,
            toolsets=self.tools
        )

    def __init__(self, **data) -> None:
        # Ensure the key is set if not provided
        if 'key' not in data:
            data['key'] = data['name']

        super().__init__(**data)


# Union type for all versions
current_agent_configuration_version: int = 2
AgentConfiguration = Union[AgentConfigurationV1, AgentConfigurationV2]

# Current version alias for convenience
CurrentAgentConfiguration = AgentConfigurationV2