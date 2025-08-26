from typing import List, Optional, Any

from pydantic import Field

from agent_c.models import ChatSession
from agent_c.models.agent_config import CurrentAgentConfiguration, AgentCatalogEntry
from agent_c.models.events import BaseEvent
from agent_c.models.heygen import Avatar, HeygenAvatarSessionData, NewSessionRequest
from agent_c_api.core.voice.models import AvailableVoiceModel


class GetAgentsEvent(BaseEvent):
    """
    Event to request a list of available agents.

    This event does not require any additional data.
    """
    pass

class AgentListEvent(BaseEvent):
    """
    Event to send a list of available agents.

    Attributes:
        agents (list): A list of available agent keys.
    """
    agents: List[AgentCatalogEntry]

class SetAgentEvent(BaseEvent):
    """
    Event to set the agent for the current session.

    Attributes:
        agent_key (str): The key of the agent to set.
    """
    agent_key: str

class AgentConfigurationChangedEvent(BaseEvent):
    """
    Event to notify that the agent configuration has changed.

    Attributes:
        agent_config (CurrentAgentConfiguration): The new agent configuration.
    """
    agent_config: CurrentAgentConfiguration

class GetAvatarsEvent(BaseEvent):
    """
    Event to request a list of available avatars.

    This event does not require any additional data.
    """
    pass

class AvatarListEvent(BaseEvent):
    avatars: List[Avatar]

class SetAvatarSessionEvent(BaseEvent):
    """
    Contains the access token and avatar session ID to allow the server to drive the HeyGen avatar speech.
    """
    access_token: str
    avatar_session_id: str

class SetAvatarEvent(BaseEvent):
    """
    Event to set the avatar for the current session.

    Attributes:
        avatar_id (str): The ID of the avatar to set.
    """
    avatar_id: str
    quality: str = "medium"
    video_encoding: str = "H264"

class AvatarConnectionChangedEvent(BaseEvent):
    avatar_session_request: NewSessionRequest
    avatar_session: HeygenAvatarSessionData


class TextInputEvent(BaseEvent):
    """
    Event to send text input to the avatar.

    Attributes:
        text (str): The text input to send.
    """
    text: str
    file_ids: List[str] =  Field(list)

class ErrorEvent(BaseEvent):
    """
    Event to send an error message.

    Attributes:
        message (str): The error message to send.
    """
    message: str
    source: Optional[str] = None

class NewChatSessionEvent(BaseEvent):
    """
    Event to request a new chat session.

    This event does not require any additional data.
    """
    agent_key: Optional[str] = None

class ResumeChatSessionEvent(BaseEvent):
    """
    Event to request resuming a chat session.

    Attributes:
        session_id (str): The ID of the session to resume.
    """
    session_id: str

class ChatSessionChangedEvent(BaseEvent):
    """
    Event to notify that the chat session has changed.

    Attributes:
        chat_session (ChatSession): The updated chat session.
    """
    chat_session: ChatSession

class SetChatSessionNameEvent(BaseEvent):
    """
    Event to set the name of the current chat session.

    Attributes:
        session_name (str): The new name for the chat session.
    """
    session_name: str

class ChatSessionNameChangedEvent(BaseEvent):
    """
    Event to notify that the chat session name has changed.

    Attributes:
        session_name (str): The updated name of the chat session.
    """
    session_name: str

class SetSessionMetadataEvent(BaseEvent):
    """
    Event to set metadata for the current chat session.
    """
    meta: dict

class SessionMetadataChangedEvent(BaseEvent):
    """
    Event to notify that the chat session metadata has changed.

    Attributes:
        meta (dict): The updated metadata of the chat session.
    """
    meta: dict

class SetSessionMessagesEvent(BaseEvent):
    """
    Event to set messages for the current chat session.
    """
    messages: List[dict[str, Any]] = Field(default_factory=list, description="New list of messages in the session")

class SetAgentVoiceEvent(BaseEvent):
    """
    Event to set the voice for the current agent.

    Attributes:
        voice_id (str): The ID of the voice to set.
    """
    voice_id: str

class AgentVoiceChangedEvent(BaseEvent):
    """
    Event to notify that the agent voice has changed.

    Attributes:
        voice (AvailableVoiceModel): The updated voice of the agent.
    """
    voice: AvailableVoiceModel

class UserTurnStartEvent(BaseEvent):
    """
    Event to notify that the client we're accepting user input

    This event does not require any additional data.
    """
    pass

class UserTurnEndEvent(BaseEvent):
    """
    Event to notify that the client we're accepting user input

    This event does not require any additional data.
    """
    pass