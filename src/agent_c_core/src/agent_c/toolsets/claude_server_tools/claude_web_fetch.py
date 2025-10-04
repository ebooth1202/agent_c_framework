from agent_c.toolsets import Toolset
from agent_c.toolsets.claude_server_tools.claude_server_tool_base import ClaudeServerToolBase


class ClaudeWebFetchTools(ClaudeServerToolBase):
    """The web fetch tool allows Claude to retrieve full content from specified web pages and PDF documents."""

    def __init__(self, **kwargs):
        schema={
            "type": "web_fetch_20250910",
            "name": "web_fetch",
            "max_uses": int(kwargs.get("max_web_fetches","5"))

        }
        super().__init__(schema, name="web_fetch",  **kwargs)

Toolset.register(ClaudeWebFetchTools)