import copy
from typing import Any, Optional, Dict, cast

from agent_c import json_schema, BaseAgent
from agent_c.models.completion import ClaudeReasoningParams
from agent_c.models.agent_config import AgentConfiguration
from agent_c.toolsets.tool_set import Toolset
from agent_c_tools.tools.agent_assist.base import AgentAssistToolBase
from .prompt import AgentCloneSection

class AgentCloneTools(AgentAssistToolBase):
    def __init__(self, **kwargs: Any):
        if not 'name' in kwargs:
            kwargs['name'] = 'act'

        super().__init__(**kwargs)
        self.section = AgentCloneSection(tool=self)


    @json_schema(
        ('Make a request of clone of yourself and receive a response. '
         'This is a "oneshot" request, meaning that the agent will not be able to remember anything from this '
         'request in the future.'),
        {
            'request': {
                'type': 'string',
                'description': 'A question, or request for the clone.',
                'required': True
            }
        }
    )
    async def oneshot(self, **kwargs) -> str:
        request: str = kwargs.get('request')
        try:
            persona = self._load_persona(kwargs.get('persona_id'))
        except FileNotFoundError:
            return f"Error: Persona {kwargs.get('persona_id')} not found in {self.persona_dir}."

        return await self.persona_oneshot(request, persona)

    @json_schema(
        'Begin or resume a chat session with a clone of yourself. The return value will be the final output from the agent along with the agent session ID.',
        {
            'message': {
                'type': 'string',
                'description': 'The message .',
                'required': True
            },
            'agent_session_id': {
                'type': 'string',
                'description': 'Populate this with a an agent session ID to resume a chat session',
                'required': False
            }
        }
    )
    async def chat(self, **kwargs) -> str:
        message: str = kwargs.get('message')
        tool_context: Dict[str, Any] = kwargs.get('tool_context')
        agent_session_id: Optional[str] = kwargs.get('agent_session_id', None)
        clone_persona: str = tool_context['custom_persona']
        tools = copy.deepcopy(self.tool_chest.active_tools().keys())

        persona = AgentConfiguration(name="Agent Clone", model_id=tool_context['model_id'], agent_description="A clone of the user agent",
                                     agent_params=ClaudeReasoningParams(model_name=tool_context['model_id'], budget_tokens=20000),
                                     persona=clone_persona)

        agent_session_id, messages = await self.persona_chat(message, persona, tool_context['session_id'],  agent_session_id, tool_context)

        return f"Agent Session ID: {agent_session_id}"

    @json_schema(
        'Load an agent persona as a YAML string for you to review',
        {
            'persona_id': {
                'type': 'string',
                'description': 'The ID of the persona to use. This is a string that will be used to load the agent from the persona directory.',
                'required': True
            },
        }
    )
    async def load_persona(self, **kwargs) -> str:
        try:
            return self._load_persona(kwargs.get('persona_id')).to_yaml()
        except FileNotFoundError:
            return f"Error: Persona {kwargs.get('persona_id')} not found in {self.persona_dir}."


Toolset.register(AgentCloneTools, required_tools=['WorkspaceTools'])