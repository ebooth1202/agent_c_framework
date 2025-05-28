import copy
from typing import Any, Optional, Dict, cast, List
from agent_c.util.slugs import MnemonicSlugs
from agent_c import json_schema, BaseAgent
from agent_c.models.completion import ClaudeReasoningParams
from agent_c.models.agent_config import AgentConfiguration, AgentConfigurationV2
from agent_c.toolsets.tool_set import Toolset
from agent_c_tools.tools.agent_assist.base import AgentAssistToolBase
from .prompt import AgentCloneSection

class AgentCloneTools(AgentAssistToolBase):
    def __init__(self, **kwargs):
        if not 'name' in kwargs:
            kwargs['name'] = 'act'

        super().__init__(**kwargs)
        self.section = AgentCloneSection(tool=self)
        self.clone_preamble = """# Clone Operating Context

        You are an agent clone created to handle a specific delegated task. Important operating guidelines:

        - You are operating as a specialized clone with focused responsibilities
        - Your role is to complete the specific task assigned by your parent agent
        - Limit your actions and responses to the directives and scope provided
        - Only your final response will be relayed back to the parent agent
        - Focus on delivering complete, actionable results within your assigned scope
        - Do not attempt to expand beyond your delegated responsibilities
        - Provide thorough, high-quality output that addresses the specific request
        """


    @json_schema(
        ('Make a request of clone of yourself and receive a response. '
         'This is a "oneshot" request, meaning that the agent will not be able to remember anything from this '
         'request in the future.'),
        {
            'request': {
                'type': 'string',
                'description': 'A question, or request for the clone.',
                'required': True
            },
            'process_context': {
                'type': 'string',
                'description': 'Optional process rules, context, or specific instructions to provide to the clone. This will be prepended to the clone\'s persona to guide its behavior for this specific task.',
                'required': False
            }
        }
    )
    async def oneshot(self, **kwargs) -> str:
        request: str = kwargs.get('request')
        process_context: Optional[str] = kwargs.get('process_context')
        tool_context: Dict[str, Any] = kwargs.get('tool_context')
        clone_persona: str = tool_context['persona_prompt']

        if process_context:
            enhanced_persona = f"{self.clone_preamble}\n\n# Clone Process Context and Instructions\n\n{process_context}\n\n# Base Agent Persona\n\n{clone_persona}"
        else:
            enhanced_persona = f"{self.clone_preamble}\n\n# Base Agent Persona\n\n{clone_persona}"
        
        tools = [tool for tool in self.tool_chest.active_tools.keys() if tool != 'AgentCloneTools']
        slug = MnemonicSlugs.generate_id_slug(2)
        agent = AgentConfigurationV2(name=f"Agent Clone - {slug}", model_id=tool_context['colling_model_name'], agent_description="A clone of the user agent",
                                     agent_params=ClaudeReasoningParams(model_name=tool_context['colling_model_name'], budget_tokens=20000),
                                     persona=enhanced_persona, tools=tools)
        return await self.agent_oneshot(request, agent, tool_context['session_id'], tool_context)

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
            },
            'process_context': {
                'type': 'string',
                'description': 'Optional process rules, context, or specific instructions to provide to the clone. This will be prepended to the clone\'s persona to guide its behavior for this session.',
                'required': False
            }
        }
    )
    async def chat(self, **kwargs) -> str:
        message: str = kwargs.get('message')
        process_context: Optional[str] = kwargs.get('process_context')
        tool_context: Dict[str, Any] = kwargs.get('tool_context')
        agent_session_id: Optional[str] = kwargs.get('agent_session_id', None)
        clone_persona: str = tool_context['persona_prompt']

        if process_context:
            enhanced_persona = f"{self.clone_preamble}\n\n# Clone Process Context and Instructions\n\n{process_context}\n\n# Base Agent Persona\n\n{clone_persona}"
        else:
            enhanced_persona = f"{self.clone_preamble}\n\n# Base Agent Persona\n\n{clone_persona}"
        
        tools: List[str] = [tool for tool in self.tool_chest.active_tools.keys() if tool != 'AgentCloneTools']
        slug = MnemonicSlugs.generate_id_slug(2)
        agent = AgentConfigurationV2(name=f"Agent Clone - {slug}", model_id=tool_context['colling_model_name'], agent_description="A clone of the user agent",
                                     agent_params=ClaudeReasoningParams(model_name=tool_context['colling_model_name'], budget_tokens=20000),
                                     persona=enhanced_persona, tools=tools)

        agent_session_id, messages = await self.agent_chat(message, agent, tool_context['session_id'], agent_session_id, tool_context)

        return f"Agent Session ID: {agent_session_id}"


Toolset.register(AgentCloneTools, required_tools=['WorkspaceTools'])