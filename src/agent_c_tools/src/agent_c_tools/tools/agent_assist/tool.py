from typing import Any, Optional, Dict

from agent_c import json_schema
from agent_c.toolsets.tool_set import Toolset
from .base import AgentAssistToolBase
from .prompt import AgentAssistSection

class AgentAssistTools(AgentAssistToolBase):
    def __init__(self, **kwargs: Any):
        if not 'name' in kwargs:
            kwargs['name'] = 'aa'

        super().__init__( **kwargs)
        self.section = AgentAssistSection(tool=self)


    @json_schema(
        ('Make a request of an agent and receive a response. This is a reasoning agent with a large thinking budget. '
         'This is a "oneshot" request, meaning that the agent will not be able to remember anything from this '
         'request in the future.'),
        {
            'request': {
                'type': 'string',
                'description': 'A question, or request for the agent.',
                'required': True
            },
            'persona_id': {
                'type': 'string',
                'description': 'The ID of the persona to use. This is a string that will be used to load the agent from the persona directory.',
                'required': True
            },
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
        'Begin or resume a chat session with an agent assistant. The return value will be the final output from the agent along with the agent session ID.',
        {
            'message': {
                'type': 'string',
                'description': 'The message .',
                'required': True
            },
            'persona_id': {
                'type': 'string',
                'description': 'The ID of the persona to use. This is a string that will be used to load the agent from the persona directory.',
                'required': True
            },
            'session_id': {
                'type': 'string',
                'description': 'Populate this with a an agent session ID to resume a chat session',
                'required': False
            }
        }
    )
    async def chat(self, **kwargs) -> str:
        message: str = kwargs.get('message')
        tool_context: Dict[str, Any] = kwargs.get('tool_context')
        agent_session_id: Optional[str] = kwargs.get('session_id', None)

        try:
            persona = self._load_persona(kwargs.get('persona_id'))
        except FileNotFoundError:
            return f"Error: Persona {kwargs.get('persona_id')} not found in {self.persona_dir}."

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

# Register the toolset
Toolset.register(AgentAssistTools, required_tools=['WorkspaceTools'])