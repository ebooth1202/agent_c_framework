from typing import Optional
from pydantic import Field

from agent_c.models.base import BaseModel

class AvatarSessionInitParams(BaseModel):
    session_id: Optional[str] = Field(None, description="Optional session ID to resume an existing session")
    agent_key: Optional[str] = Field("default", description="Optional agent key to specify which agent to use")
    avatar_id: Optional[str] = Field(None, description="Optional avatar ID to specify which avatar to use")