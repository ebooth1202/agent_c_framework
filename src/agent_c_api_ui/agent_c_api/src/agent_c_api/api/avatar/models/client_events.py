from typing import List

from agent_c.models.agent_config import CurrentAgentConfiguration, AgentCatalogEntry
from agent_c.models.events import BaseEvent
from agent_c.models.heygen import Avatar, HeygenAvatarSessionData


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

class GetAvatarsEvent(BaseEvent):
    """
    Event to request a list of available avatars.

    This event does not require any additional data.
    """
    pass

class AvatarListEvent(BaseEvent):
    avatars: List[Avatar]

class SetAvatarEvent(BaseEvent):
    """
    Event to set the avatar for the current session.

    Attributes:
        avatar_id (str): The ID of the avatar to set.
    """
    avatar_id: str

class AvatarConnectionChangedEvent(BaseEvent):
    token: str
    avatar_session: HeygenAvatarSessionData


class TextInputEvent(BaseEvent):
    """
    Event to send text input to the avatar.

    Attributes:
        text (str): The text input to send.
    """
    text: str

class ErrorEvent(BaseEvent):
    """
    Event to send an error message.

    Attributes:
        message (str): The error message to send.
    """
    message: str