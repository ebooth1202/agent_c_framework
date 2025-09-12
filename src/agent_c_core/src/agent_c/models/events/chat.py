from pydantic import Field
from typing import Optional, List, Dict, Any, Literal

from agent_c.models.events import BaseEvent
from agent_c.models.events.session_event import SessionEvent

class SystemPromptEvent(SessionEvent):
    """
    Sent to notify the UI that the system prompt has been updated.
    """
    def __init__(self, **data):
        super().__init__(type = "system_prompt", **data)

    content: str = Field(..., description="The content of the system prompt")
    format: str = Field("markdown", description="The format of the content, default is markdown")

class UserRequestEvent(SessionEvent):
    """
    Sent to notify the UI that a user request has been initiated.
    This is typically used to indicate that the user has requested a new interaction.
    """
    data: Dict[str, Any] = Field(..., description="The data associated with the user request, such as the input text or other parameters")


class UserMessageEvent(SessionEvent):
    """
    Sent to notify the UI that a user message has been added to the chat session.
    """
    vendor: str = Field(..., description="The vendor of the model being used for the user request, e.g., 'openai', 'anthropic', etc.")

class OpenAIUserMessageEvent(UserMessageEvent):
    vendor: str = Field( "openai", description="The vendor of the model being used for the user request, e.g., 'openai', 'anthropic', etc.")
    message: Dict[str, Any] = Field(..., description="The user message that was added to the chat session")

class AnthropicUserMessageEvent(UserMessageEvent):
    vendor: str = Field( "anthropic", description="The vendor of the model being used for the user request, e.g., 'openai', 'anthropic', etc.")
    message: Dict[str, Any] = Field(..., description="The user message that was added to the chat session")

class InteractionEvent(SessionEvent):
    """
    Sent to notify the UI that an interaction has been initiated or completed.
    While an interaction is running, the UI should not allow input from the user.
    """
    def __init__(self, **data):
        super().__init__(type = "interaction", **data)

    started: bool = Field(..., description="If False, the interaction has been completed. And the UI should allow input from the use")
    id: str = Field(..., description="The ID of the interaction")

class CompletionEvent(SessionEvent):
    """
    Sent to notify the UI that the completion call
    """
    def __init__(self, **data):
        super().__init__(type = "completion", **data)

    running: bool = Field(..., description="If True, the completion will run immediately after the event goes out.")
    completion_options: dict = Field(..., description="The completion options used, in vendor format")
    stop_reason: Optional[str] = Field(None, description="The reason the completion was stopped")
    input_tokens: Optional[int] = Field(0, description="The number of tokens in the input")
    output_tokens: Optional[int] = Field(0, description="The number of tokens in the output")

class MessageEvent(SessionEvent):
    """
    Sent to notify the UI to display an entire message.
    """
    def __init__(self, **data):
        super().__init__(type = "message", **data)

    content: str = Field(..., description="The content of the message")
    format: str = Field("markdown", description="The format of the content, default is markdown")

class SystemMessageEvent(SessionEvent):
    """
    Sent to notify the UI to display an entire message.
    """
    def __init__(self, **data):
        super().__init__(type = "system_message", **data)

    content: str = Field(..., description="The content of the message")
    format: str = Field("markdown", description="The format of the content, default is markdown")
    severity: str = Field("error", description="The severity of the message, default is error, can be 'info', 'warning', or 'error'")

class TextDeltaEvent(SessionEvent):
    """
    Sent to notify the UI that a chunk of content text has been received.
    - Clients should handle this event by appending the content to the current message,
      for the role, within the current interaction.
    - If there isn't a message for the role in the current interaction,
      a new message should be created.
    """
    def __init__(self, **data):
        if data.get('type', None) == None:
            data['type'] = "text_delta"

        super().__init__( **data)

    content: str = Field(..., description="A chunk of content text.")
    format: str = Field("markdown", description="The format of the content, default is markdown")

class ThoughtDeltaEvent(TextDeltaEvent):
    def __init__(self, **data):
        super().__init__(type = "thought_delta", **data)
        self.role = self.role + " (thought)"

class CompleteThoughtEvent(TextDeltaEvent):
    def __init__(self, **data):
        super().__init__(type = "complete_thought", **data)
        self.role = self.role + " (thought)"

class AudioInputDeltaEvent(BaseEvent):
    content: str = Field(..., description="A base64s encoded chunk of audio data")
    content_type: str = Field("audio/L16", description="The type of audio data")

class ReceivedAudioDeltaEvent(SessionEvent):
    """
    Sent to notify the UI that a chunk of audio has been received from the competion API.
    - Clients should handle this event by appending the audio to the current message,
      for the role, within the current interaction.
    - If there isn't a message for the role in the current interaction,
      a new message should be created.
    """
    def __init__(self, **data):
        super().__init__(type = "audio_delta", **data)
    id: Optional[str] = Field(None, description="The audio ID the audio delta is part of")
    content: str = Field(..., description="A base64s encoded chunk of audio data")
    content_type: str = Field("audio/L16", description="The type of audio data")

class HistoryEvent(SessionEvent):
    """
    Sent to notify the UI that the message history has been updated.
    """
    def __init__(self, **data):
        super().__init__(type = "history", **data)

    messages: List[dict] = Field(..., description="The list of messages in the current chat history")

class HistoryDeltaEvent(SessionEvent):
    """
    Sent to notify the UI that messages have been added to the history.
    """
    def __init__(self, **data):
        super().__init__(type = "history_delta", **data)

    messages: List[dict] = Field(..., description="The list of messages that have been added to the history")

class SubsessionStartedEvent(SessionEvent):
    """
    Set to notify the UI that a subsession has started.

    Events that follow this, until the SubsessionEndedEvent, are part of the subsession, not the user session
    - The client should display these events, as typical chat events, with  an indicator that they're from a subsession.
    - The server will not add these events to the user session, but will maintain them as part of the subsession.

    Note: Subsessions are often nested. There will be a matching end for each start.
    """
    sub_session_type: Literal["chat", "oneshot"] = Field(..., description="The type of the subsession, either 'chat' or 'oneshot'")
    sub_agent_type: Literal["clone", "team", "assist", "tool"] = Field(..., description="The type of the sub-agent that started the subsession, either 'clone', 'team', 'assist', or 'tool'")
    prime_agent_key: str = Field(..., description="The key of the prime agent that started the subsession, if applicable")
    sub_agent_key: str = Field(..., description="The key of the sub-agent that the prime is talking to in  the subsession")

class SubsessionEndedEvent(SessionEvent):
    """
    Set to notify the UI that a subsession has ended.

    Note: Subsessions are often nested. There will be a matching end for each start.
    """
    pass