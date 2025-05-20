from typing import Any

from agent_c.toolsets.tool_set import Toolset
from agent_c_tools.tools.persona_oneshot.base import PersonaOneshotBase

class PersonaOneshotTools(PersonaOneshotBase):
    def __init__(self, **kwargs: Any):
        if not 'name' in kwargs:
            kwargs['name'] = 'persona_oneshot'
        super().__init__( **kwargs)



# Register the toolset
Toolset.register(PersonaOneshotTools, required_tools=['WorkspaceTools'])