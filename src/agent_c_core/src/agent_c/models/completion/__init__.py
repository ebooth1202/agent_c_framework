from typing import Annotated, Union
from pydantic import Field

from agent_c.models.completion.common import CommonCompletionParams
from agent_c.models.completion.claude import (
    ClaudeNonReasoningParams,
    ClaudeReasoningParams,
)
from agent_c.models.completion.gpt import (
    GPTNonReasoningCompletionParams,
    GPTReasoningCompletionParams,
)

CompletionParams = Annotated[
    Union[
        ClaudeNonReasoningParams,
        ClaudeReasoningParams,
        GPTNonReasoningCompletionParams,
        GPTReasoningCompletionParams,
    ],
    Field(discriminator='type')
]
