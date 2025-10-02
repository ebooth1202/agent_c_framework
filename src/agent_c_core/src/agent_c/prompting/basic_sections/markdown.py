from typing import Any
from agent_c.prompting.prompt_section import PromptSection


class MarkdownFormatting(PromptSection):
    """
    This class represents a section that provides guidance on Markdown formatting to the agent,
    Args:
        **data (Any): Additional keyword arguments passed to the PromptSection during initialization.
    """

    def __init__(self, **data: Any) -> None:
        TEMPLATE: str = (
            "The user interface supports full Markdown rendering with many exetensions.\n"
            "- Collapsible sections - using syntax identical to GitHub.\n"
            "- Tables - using syntax identical to GitHub.\n"
            " - Full syntax highlighting for code blocks - using syntax identical to GitHub.\n"
            "- LaTeX math rendering - using standard LaTeX math syntax delimited by `$$$$`\n"
            "- Mermaid diagrams - using standard Mermaid syntax delimited by ```mermaid\n"
            "- Alerts - note, tip, important, warning, caution - using syntax like below.\n\n"
            ":::important\n"
            "⚡ This is an **important** alert. Use it for crucial information users need to know.\n\n"
            "**Critical**: Make sure to backup your data before proceeding with the upgrade!\n"
            ":::\n\n"
            "Important! ALWAYS use a language specifier for code blocks, e.g., ```python, ```javascript, ```bash, etc.\n\n"
            "CRITICAL: Use alerts to draw attention to important information, warnings, or tips.\n\n"
            "Note: IF a user asks about how to format markdown use `workspace_render_media` to show them `//project/docs/markdown_examples.md`.\n"
        )
        super().__init__(template=TEMPLATE, name="Runtime Environment", **data)
