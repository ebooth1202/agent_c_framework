from typing import List

from agent_c.models.agent_config import AgentCatalogEntry
from agent_c.models.base import BaseModel
from agent_c.models.heygen import Avatar


class AvatarConfig(BaseModel):
    agents: List[AgentCatalogEntry]
    avatars: List[Avatar]