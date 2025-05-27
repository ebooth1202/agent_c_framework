import os
from pydantic import Field
from typing import Any, Optional
from agent_c.models.completion.common import CommonCompletionParams

class ClaudeNonReasoningParams(CommonCompletionParams):
    """
    Vendor specific parameters for interacting with the Claude agent.
    """
    temperature: Optional[float] = Field(None, description="The temperature to use for the interaction, do not combine with top_p")

    def __init__(self, **data: Any) -> None:
        if 'model_name' not in data:
            data['model_name'] = os.environ.get("CLAUDE_INTERACTION_MODEL", "claude-3-7-sonnet-latest")

        super().__init__(**data)

class ClaudeReasoningParams(CommonCompletionParams):
    budget_tokens: Optional[int] = Field(None, description="The budget tokens to use for the interaction, must be higher than max tokens")
    max_searches: Optional[int] = Field(None, description="The maximum number of web searches for the claude models to perform")

    def __init__(self, **data: Any) -> None:
        if 'model_name' not in data:
            data['model_name'] = os.environ.get("CLAUDE_REASONING_INTERACTION_MODEL", "claude-4-sonnet-latest")

        super().__init__(**data)