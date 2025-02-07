from pydantic import Field
from typing import Optional, List, Union

from agent_c.models.base import BaseModel

class BaseEvent(BaseModel):
    type: str = Field(..., description="The type of the event")
