
from typing import Any, Dict, List, Optional, cast
from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from agent_c_tools.tools.planner.prompt import WorkspacePlanSection
from agent_c_tools.tools.workspace.tool import WorkspaceTools

class WorkshopPlanningTools(Toolset):
    """
    WorkshopPlanningTools provides methods for creating and tracking plans using the metadata of a workspace.
    """

    def __init__(self, **kwargs: Any):
        super().__init__(name='wsp', **kwargs)
        self.section = WorkspacePlanSection()
        self.workspace_tool: Optional[WorkspaceTools] = None

    async def post_init(self):
        self.workspace_tool = cast(WorkspaceTools, self.tool_chest.available_tools.get('WorkspaceTools'))


Toolset.register(WorkshopPlanningTools, required_tools=['WorkspaceTools'])
