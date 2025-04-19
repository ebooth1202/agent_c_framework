from typing import Any, Optional

from agent_c.prompting.prompt_section import PromptSection, property_bag_item


class WorkspaceSection(PromptSection):
    tool: Any  # Reference to the workspace tool

    def __init__(self, **data: Any):
        TEMPLATE = ("The workspace tools provide you a way to work with files in one or more workspaces.\n"
                    "Available workspaces are listed below\n"
                    "### Available Workspace List \n"
                    "${workspace_list}\n\n"
                    "## Workspace Operations Guide\n"
                    "- **UNC Paths**: Always use UNC-style paths in the format `//WORKSPACE/path/to/file` where WORKSPACE is the workspace name\n"
                    "- **Reading**: Use `read` to get file contents; assume paths exist rather than checking first\n"
                    "               Use `read_lines` to read a portion of a file\n"
                    "- **Writing**: Use `write` for creating or replacing files; parent directories are created automatically\n"
                    "- **Appending**: Use `write` with the optional `mode` parameter set to `append`\n"
                    "- **Navigation**: Use `tree` for broader holistic views. Us `ls` to list a specific directory contents\n"
                    "- **File Management**: Use `cp` to copy and `mv` to move files or directories\n"
                    "  - Both source and destination must be in the same workspace\n"    
                    "## CRITICAL: Workspace Traceability rules:\n"
                    "- Prefer `inspect_code` over reading entire code files in Python, or C# code.\n" 
                    "   - This will give you the signatures and doc strings for code files"
                    "   - Line numbers are included for methods allowing you to target reads and updates more easily"
                    "- You can use the line number from `inspect_code` and the `read_lines` tool to grab the source for a single method or class."
                    "- You can use the strings you get from `read_lines` to call `replace_strings`"
                    "- Small changes to existing files should be made using the `replace_strings` methods. If possible\n"
                    "  - Make ALL changes to the same file at once.\n"
                    "  - Batching saves money and time!.\n"
                    "- If you *must* write and entire file use the `write` tool.\n")
        super().__init__(template=TEMPLATE, required=True, name="Workspaces", render_section_header=True, **data)

    @property_bag_item
    async def workspace_list(self):
        """Generate a compact table-like representation of available workspaces."""
        if not hasattr(self, 'tool') or not self.tool:
            return "No workspaces available"
        
        # Create a compact table-like format for workspaces
        workspaces = self.tool.workspaces
        
        if not workspaces:
            return "No workspaces available"
            
        lines = []
        for space in workspaces:
            lines.append(f"- `{space.name}` ({space.write_status}) - {space.description}")
            
        return "\n".join(lines)