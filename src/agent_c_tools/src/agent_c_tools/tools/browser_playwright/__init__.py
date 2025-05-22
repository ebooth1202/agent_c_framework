"""Browser automation toolset using Playwright."""

from agent_c.toolsets.tool_set import Toolset
from agent_c_tools.tools.browser_playwright.tool import BrowserPlaywrightTools

# Register the toolset
Toolset.register(BrowserPlaywrightTools, required_tools=['WorkspaceTools'])