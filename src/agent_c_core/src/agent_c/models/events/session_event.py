from pydantic import Field
from agent_c.models.events.base import BaseEvent

class SessionEvent(BaseEvent):
    session_id: str = Field(..., description="The type of the event")
    role: str = Field(..., description="The role that triggered this event event")