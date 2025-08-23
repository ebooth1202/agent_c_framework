from typing import List

from pydantic import Field

from agent_c.models.agent_config import CurrentAgentConfiguration, AgentCatalogEntry
from agent_c.models.events import BaseEvent
from agent_c.models.heygen import Avatar, HeygenAvatarSessionData, NewSessionRequest


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