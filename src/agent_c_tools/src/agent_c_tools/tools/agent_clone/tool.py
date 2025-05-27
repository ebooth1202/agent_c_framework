import copy
from typing import Any, Optional, Dict, cast, List

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
        tool_context: Dict[str, Any] = kwargs.get('tool_context')
        clone_persona: str = tool_context['custom_persona']
        tools = copy.deepcopy(self.tool_chest.active_tools().keys())
        if 'AgentCloneTools' in tools:
            tools.remove('AgentCloneTools')

        agent = AgentConfiguration(name="Agent Clone", model_id=tool_context['model_id'], agent_description="A clone of the user agent",
                                     agent_params=ClaudeReasoningParams(model_name=tool_context['model_id'], budget_tokens=20000),
                                     persona=clone_persona, tools=tools)
        return await self.agent_oneshot(request, agent)

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
        tools: List[str] = copy.deepcopy(self.tool_chest.active_tools().keys())
        if 'AgentCloneTools' in tools:
            tools.remove('AgentCloneTools')

        agent = AgentConfiguration(name="Agent Clone", model_id=tool_context['model_id'], agent_description="A clone of the user agent",
                                     agent_params=ClaudeReasoningParams(model_name=tool_context['model_id'], budget_tokens=20000),
                                     persona=clone_persona, tools=tools)

        agent_session_id, messages = await self.agent_chat(message, agent, tool_context['session_id'], agent_session_id, tool_context)

        return f"Agent Session ID: {agent_session_id}"


Toolset.register(AgentCloneTools, required_tools=['WorkspaceTools'])