from typing import Any, Optional, Dict

import markdown
import yaml
from fastapi_pagination import response
from markdownify import markdownify

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
            'agent_id': {
                'type': 'string',
                'description': 'The ID of the agent to make a request of.',
                'required': True
            },
        }
    )
    async def oneshot(self, **kwargs) -> str:
        request: str = kwargs.get('request')
        tool_context: Dict[str, Any] = kwargs.get('tool_context')
        try:
            agent = self.agent_loader.catalog[kwargs.get('agent_id')]
        except FileNotFoundError:
            return f"Error: Agent {kwargs.get('agent_id')} not found in catalog."

        await self._raise_render_media(
            sent_by_class=self.__class__.__name__,
            sent_by_function='oneshot',
            content_type="text/html",
            content=markdown.markdown(f"**Domo** agent requesting assistance from '*{agent.name}*':\n\n{request}</p>")
        )

        messages = await self.agent_oneshot(request, agent, tool_context['session_id'], tool_context)
        last_message = messages[-1] if messages else None
        agent_response = yaml.dump(last_message, allow_unicode=True) if last_message else "No response from agent."
        await self._raise_render_media(
            sent_by_class=self.__class__.__name__,
            sent_by_function='oneshot',
            content_type="text/html",
            content=markdown.markdown(f"**{agent.name}** response:\n\n{agent_response}"))

        return agent_response


    @json_schema(
        'Begin or resume a chat session with an agent assistant. The return value will be the final output from the agent along with the agent session ID.',
        {
            'message': {
                'type': 'string',
                'description': 'The message .',
                'required': True
            },
            'agent_id': {
                'type': 'string',
                'description': 'The ID of the agent to chat with.',
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
            agent = self.agent_loader.catalog[kwargs.get('agent_id')]
        except FileNotFoundError:
            return f"Error: Agent {kwargs.get('agent_id')} not found in catalog."

        content = markdownify(message, heading_style='ATX', escape_asterisks=False, escape_underscores=False)
        await self._raise_render_media(
            sent_by_class=self.__class__.__name__,
            sent_by_function='chat',
            content_type="text/html",
            content=markdown.markdown(f"**Domo agent** requesting assistance from '*{agent.name}*': \n\n{content}")
        )

        agent_session_id, messages = await self.agent_chat(message, agent, tool_context['session_id'], agent_session_id, tool_context)

        if messages is not None and len(messages) > 0:
            last_message = messages[-1]
            agent_response = yaml.dump(last_message, allow_unicode=True)
            content = markdownify(agent_response, heading_style='ATX', escape_asterisks=False, escape_underscores=False)
            await self._raise_render_media(
                sent_by_class=self.__class__.__name__,
                sent_by_function='oneshot',
                content_type="text/html",
                content=markdown.markdown(f"**{agent.name}** Response:\n\n{content}")
            )
            return f"Agent Session ID: {agent_session_id}\n{agent_response}"

        return f"No messages returned from agent session {agent_session_id}."

    @json_schema(
        'Load an agent agent as a YAML string for you to review',
        {
            'agent_id': {
                'type': 'string',
                'description': 'The ID of the agent to load.',
                'required': True
            },
        }
    )
    async def load_agent(self, **kwargs) -> str:
        try:
            return self.agent_loader.catalog[kwargs.get('agent_id')].to_yaml()
        except FileNotFoundError:
            return f"Error: Agent {kwargs.get('agent_id')} not found in catalog."

# Register the toolset
Toolset.register(AgentAssistTools, required_tools=['WorkspaceTools'])