from typing import Any

from agent_c.prompting.prompt_section import PromptSection, property_bag_item


class WorkspaceSection(PromptSection):
    workspaces: str

    def __init__(self, **data: Any):
        TEMPLATE = ("The workspace tools provide you a way to work with files in one or more workspaces.\n"
                    "The list below contains the workspaces present and available  by name, along with their read/write status, the type of workspace it is and a description of the workspace.\n"
                    "You this list to help you determine the name of the workspace to use with the workspace toolsets:\n"
                    "**important** If the user asks about the available workspaces use the info in this list.\n\n"
                    "### Available Workspace List \n"
                    "${workspace_list}\n\n"
                    "## Important Workspace rules and procedures\n"
                    "- Workspace paths are relative, do not being with a slash\n"
                    "- Path names from users should be assumed to exist. Checking wasts time and resources\n"
                    "- Write operations do a `mkdir -p` to ensure the path exists automatically\n"
                    "- The term `scratchpad` is used to refer to a folder `.scratchpad` set aside for your use in a workspace\n"
                    "  - If the no workspace is specified by the user or your instructions, ask the user for clarification\n"
                    "  - The user may ask you to use a different folder within the workspace as your scratchpad.  PAY ATTENTION ")
        super().__init__(template=TEMPLATE, required=True, name="Workspaces", render_section_header=True,  **data)

    @property_bag_item
    async def workspace_list(self):
        return self.workspaces
