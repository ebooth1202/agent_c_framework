from typing import Any, Optional

from agent_c.prompting.prompt_section import PromptSection, property_bag_item


class PersonaOneshotSection(PromptSection):
    tool: Any

    def __init__(self, **data: Any):

        TEMPLATE = ("The persona oneshot tool allows you to leverage other agents to perform tasks or answer questions "
                    "on behalf of the user.\n\n"
                    "## Available Agent IDS:\n${agent_ids}\n\n"
                    "**NOTE:** Agent IDs are in the form of [optional subfoler]/[agent_name]-[agent_role].\n\n"
                    "## Interaction Guidelines:\n"
                    "- The user will often use casual languages such as `ask cora to do X`.\n"
                    "  - If only one agent persona matches that name than use that agent ID to make and "
                    "make an`agent_oneshot` tool call passing the user message.\n"
                    "  - If more than one name matches, inform the user of the ambiguity and list the roles available.\n"
                    "    - For example: I'm sorry, do you mean 'Cora the Agent C core dev' or 'Cora the Fast API dev'?")
        super().__init__(template=TEMPLATE, required=True, name="Persona Oneshot", render_section_header=True, **data)

    @property_bag_item
    async def agent_ids(self):
        return "\n".join([f"- {persona}" for persona in self.tool.personas_list])