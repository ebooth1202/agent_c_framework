from agent_c.toolsets import Toolset
from agent_c.toolsets.claude_server_tools.claude_server_tool_base import ClaudeServerToolBase


class ClaudeCodeExecutionTools(ClaudeServerToolBase):
    """Claude can analyze data, create visualizations, perform complex calculations, run system commands, create and edit files, and process uploaded files directly within the API conversation. The code execution tool allows Claude to run Bash commands and manipulate files, including writing code, in a secure, sandboxed environment."""
    __schema = {"type": "code_execution_20250825", "name": "code_execution"}

    def __init__(self, **kwargs):
        super().__init__(self.__schema, name="code_execution", **kwargs)

Toolset.register(ClaudeCodeExecutionTools)