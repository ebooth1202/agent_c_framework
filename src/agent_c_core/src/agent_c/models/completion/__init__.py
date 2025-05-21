from typing import TypeAlias

from agent_c.models.completion.common import CommonCompletionParams
from agent_c.models.completion.claude import (
    ClaudeNonReasoningParams,
    ClaudeReasoningParams,
)
from agent_c.models.completion.gpt import (
    GPTNonReasoningCompletionParams,
    GPTReasoningCompletionParams,
)

CompletionParams: TypeAlias = (
    ClaudeNonReasoningParams
    | ClaudeReasoningParams
    | GPTNonReasoningCompletionParams
    | GPTReasoningCompletionParams
)
