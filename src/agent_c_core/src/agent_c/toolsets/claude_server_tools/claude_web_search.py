from agent_c.toolsets import Toolset
from agent_c.toolsets.claude_server_tools.claude_server_tool_base import ClaudeServerToolBase


class ClaudeWebSearchTools(ClaudeServerToolBase):
    """The web search tool gives Claude direct access to real-time web content, allowing it to answer questions with up-to-date information beyond its knowledge cutoff. Claude automatically cites sources from search results as part of its answer.."""
    def __init__(self, **kwargs):
        schema={
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": int(kwargs.get("max_web_searches", "5"))
        }
        super().__init__(schema, name="web_search",  **kwargs)

Toolset.register(ClaudeWebSearchTools)