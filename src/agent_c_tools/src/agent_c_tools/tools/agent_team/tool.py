from typing import Any
from agent_c.toolsets.tool_set import Toolset
from agent_c_tools.tools.agent_assist.tool import AgentAssistTools

from .prompt import AgentTeamSection

class AgentTeamTools(AgentAssistTools):
    """
    Enables your agent to collaborate as part of a structured team of AI agents, each with specific roles
    and expertise. Your agent can coordinate with team members, delegate tasks to specialists, and work
    together on complex multi-faceted projects that require diverse skills and perspectives.
    """
    def __init__(self, **kwargs: Any):
        if not 'name' in kwargs:
            kwargs['name'] = 'ateam'

        super().__init__( **kwargs)
        self.section = AgentTeamSection(tool=self)

# Register the toolset
Toolset.register(AgentTeamTools, required_tools=['WorkspaceTools'])