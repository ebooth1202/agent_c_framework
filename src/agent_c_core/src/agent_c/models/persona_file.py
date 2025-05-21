from typing import Optional, List, ClassVar

import yaml
from pydantic import Field, ConfigDict

from agent_c.models.base import BaseModel


class PersonaFile(BaseModel):
    persona: str = Field(..., description="Persona prompt of the persona defining the agent's behavior")
    model_id: str = Field(..., description="ID of the LLM model being used by the agent")
    tools: List[str] = Field(default_factory=list, description="List of enabled toolset names the agent can use")
    agent_description: Optional[str] = Field(None, description="A description of the agent's purpose and capabilities")
    temperature: Optional[float] = Field(None, ge=0.0, le=1.0, description="Temperature parameter controlling randomness (0.0 to 1.0)")
    reasoning_effort: Optional[int] = Field(None, ge=0, le=10, description="Reasoning effort parameter for OpenAI models (0 to 10)")
    budget_tokens: Optional[int] = Field(None, ge=0, description="Budget tokens parameter for Claude models")
    max_tokens: Optional[int] = Field(None, ge=0, description="Maximum tokens limit for model output")


    model_config = ConfigDict(
        protected_namespaces=(),
        json_schema_extra={
            "example": {
                "model_id": "claude-3-7-sonnet-latest",
                "persona": "You are a helpful coding assistant.",
                "budget_tokens": 20000,
                "max_tokens": 128000,
                "tools": ["ThinkTools", "WorkspaceTools", "CssExplorerTools", "XmlExplorerTools"]
            }
        }
    )

    # YAML serialization methods
    def to_yaml(self) -> str:
        """Convert the persona file model to a YAML string.

        Returns:
            str: The model serialized as a YAML string.
        """
        return yaml.dump(self.model_dump(), default_flow_style=False, sort_keys=False)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> 'PersonaFile':
        """Create a PersonaFile instance from a YAML string.

        Args:
            yaml_str (str): YAML string representing a PersonaFile.

        Returns:
            PersonaFile: An instance created from the YAML string.
        """
        data = yaml.safe_load(yaml_str)
        return cls.model_validate(data)