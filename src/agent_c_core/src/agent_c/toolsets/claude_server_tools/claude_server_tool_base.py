from agent_c.toolsets.tool_set import Toolset


class ClaudeServerToolBase(Toolset):
    """Base class for Claude server tools."""
    def __init__(self, schema: dict, **kwargs):
        super().__init__(use_prefix=False, **kwargs)
        self._schemas = [schema]
