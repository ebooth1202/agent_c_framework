from typing import Any, Optional

from agent_c.prompting.prompt_section import PromptSection, property_bag_item


class AgentAssistSection(PromptSection):
    tool: Any

    def __init__(self, **data: Any):

        TEMPLATE = ("The Agent Assist Toolset (aa) allows you to leverage other agents to perform tasks, answer questions "
                    "on behalf of the user or to execute your plans..\n\n"
                    "## Available Agent IDS:\n${agent_ids}\n\n"
                    "**NOTE:** Agent IDs are in the form of [optional subfoler]/[agent_name]-[agent_role].\n\n"
                    "## Interaction Guidelines:\n"
                    "- The user will often use casual languages such as `ask cora to do X`.\n"
                    "  - If only one agent persona matches that name than use that agent ID to make and "
                    "make an`aa_` tool call.\n"
                    "  - If more than one name matches, inform the user of the ambiguity and list the roles available.\n"
                    "    - For example: I'm sorry, do you mean 'Cora the Agent C core dev' or 'Cora the Fast API dev'?")
        super().__init__(template=TEMPLATE, required=True, name="Agent Assist", render_section_header=True, **data)

    @property_bag_item
    async def agent_ids(self):
        return "\n".join([f"- {persona}" for persona in self.tool.personas_list])