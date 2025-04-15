from typing import Any

from agent_c.prompting.prompt_section import PromptSection, property_bag_item


class WorkspaceSection(PromptSection):
    workspaces: str

    def __init__(self, **data: Any):
        TEMPLATE = ("The workspace tools provide you a way to work with files in one or more workspaces.\n"
                    "Available workspaces are listed below with their name, read/write status, type, and description.\n"
                    "Always use this list when referencing workspaces in your operations:\n\n"
                    "### Available Workspace List \n"
                    "${workspace_list}\n\n"
                    "## Workspace Operations Guide\n"
                    "- **UNC Paths**: Always use UNC-style paths in the format `//WORKSPACE/path/to/file` where WORKSPACE is the workspace name\n"
                    "- **Reading**: Use `read` to get file contents; assume paths exist rather than checking first\n"
                    "- **Updating Files**: Use `replace_strings` or `replace_lines` for targeted modifications.\n"
                    "- **Writing**: Use `write` for creating or replacing files; parent directories are created automatically\n"
                    "- **Appending**: Use `replace_lines` tool with a `start_line` value of `-1` to append to a file\n"
                    "- **Navigation**: Use `ls` to list directory contents and `tree` for hierarchical views\n"
                    "- **File Management**: Use `cp` to copy and `mv` to move files or directories\n"
                    "  - Both source and destination must be in the same workspace\n"    
                    "## CRITICAL: Workspace Traceability rules:\n"
                    "Proper use of the `replace_*` methods are essential for efficiency and tracking purposes.\n"
                    "- Changes to existing files should be made using the `replace_*` methods. \n"
                    "- If you *must* write and entire file use the `write` tool.\n"
                    "## Examples Using UNC-Style Paths:\n"
                    "- To read a file: `read(path=\"//MyWorkspace/folder/file.txt\")`\n"
                    "- To list directory contents: `ls(path=\"//MyWorkspace/folder\")`\n"
                    "- To write to a file: `write(path=\"//MyWorkspace/folder/file.txt\", data=\"content\", mode=\"write\")`\n")
        super().__init__(template=TEMPLATE, required=True, name="Workspaces", render_section_header=True, **data)

    @property_bag_item
    async def workspace_list(self):
        return self.workspaces