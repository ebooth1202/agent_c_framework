from typing import Any

from agent_c import json_schema
from agent_c.toolsets.tool_set import Toolset
from .base import PersonaOneshotBase
from .prompt import PersonaOneshotSection

class PersonaOneshotTools(PersonaOneshotBase):
    def __init__(self, **kwargs: Any):
        if not 'name' in kwargs:
            kwargs['name'] = 'persona_oneshot'
        super().__init__( **kwargs)
        self.section = PersonaOneshotSection(tool=self)


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
    async def agent_oneshot(self, **kwargs) -> str:
        request: str = kwargs.get('request')
        try:
            persona = self._load_persona(kwargs.get('persona_id'))
        except FileNotFoundError:
            return f"Error: Persona {kwargs.get('persona_id')} not found in {self.persona_dir}."

        return await self.persona_oneshot(request, persona)

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
Toolset.register(PersonaOneshotTools, required_tools=['WorkspaceTools'])