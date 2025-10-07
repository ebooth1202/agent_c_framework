from agent_c.toolsets.claude_server_tools.claude_server_tool_base import ClaudeServerToolBase


class ClaudeComputerUseTools(ClaudeServerToolBase):
    """Claude can analyze data, create visualizations, perform complex calculations, run system commands, create and edit files, and process uploaded files directly within the API conversation. The code execution tool allows Claude to run Bash commands and manipulate files, including writing code, in a secure, sandboxed environment."""

    def __init__(self, **kwargs):
        schema={
            "type": "computer_20250124",
            "name": "computer",
            "display_width_px": int(kwargs.get("display_width_px", "3840" )),
            "display_height_px": int(kwargs.get("display_height_px", "2160")),
            "display_number": int(kwargs.get("display_number", "1")),
        },
        super().__init__(schema, name="computer",  **kwargs)