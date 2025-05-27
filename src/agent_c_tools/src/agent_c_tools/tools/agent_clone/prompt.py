from csv import DictReader
from typing import Any, Optional, Dict, List

from agent_c.prompting.prompt_section import PromptSection, property_bag_item


class AgentCloneSection(PromptSection):
    tool: Any

    def __init__(self, **data: Any):
        TEMPLATE = ("The Agent Clone Toolset (act) allows you to chat with a cloned version of yourself "
                    "and have it perform actions on your behalf exactly as you would, allowing you preserve "
                    "precious context window space for interaction with the user, and 'big brain' stuff.\n\n"
                    "## Important information\n"
                    "- The cloned agent will have access to the same tools as you, with the exception of the act toolset.\n"
                    "- The cloned agent will contain an exact copt of your current instructions, prefaced with special instructions.\n"
                    "- The context information you provide will be used as part of the cloned agent's instructions.\n"
                    "  - You can include explicit process instructions for the cloned agent to follow when responding to your chat.\n"
                    "- In order to maximize the output quality and effectiveness of the cloned agents, use a new session for each discrete task or step.\n\n"
                    "\n$clone_sessions")
        super().__init__(template=TEMPLATE, required=True, name="Agent Clone Toolset", render_section_header=True, **data)

    @property_bag_item
    async def clone_sessions(self, prompt_context: Dict[str, Any]) -> str:
        session_id = prompt_context.get('user_session_id', prompt_context.get('session_id', None))
        agent_sessions: List[Dict[str, Any]] = self.tool.list_active_sessions(session_id)
        if len(agent_sessions):
            sess_list = "\n".join([f"- {ses['agent_session_id']} {ses['message_count']} messages" for ses in agent_sessions])
            return f"\n\n## Active Clone Sessions:\n{sess_list}\n\n"

        return ""