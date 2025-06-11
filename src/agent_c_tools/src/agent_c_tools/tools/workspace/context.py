from pydantic import Field
from typing import Optional, List
from agent_c.models.context.base import BaseContext

class WorkspaceToolsContext(BaseContext):
    default_workspace: str = Field(default="desktop", description="The default workspace to use if no other is specified. ")
    allowed_workspaces: Optional[List[str]] = Field(default_factory=list, description="If provided, only these workspaces will be used in the interaction. "
                                                                                      "If not provided, any workspace not disallowed.")
    disallowed_workspaces: Optional[List[str]] = Field(default_factory=list, description="If provided, these workspaces will not be used in the interaction. "
                                                                                         "If not provided, all workspaces are allowed.")
    force_read_only: bool = Field(default=False, description="If True, all workspace operations will be read-only. "
                                                             "This is used to prevent accidental writes to workspaces.")
