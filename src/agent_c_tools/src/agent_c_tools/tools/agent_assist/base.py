import os
import glob
import threading

from datetime import datetime
from typing import Any, Dict, List, Optional, cast, Tuple

from agent_c import PromptSection
from agent_c.config.model_config_loader import ModelConfigurationLoader, ModelConfigurationFile
from agent_c.config.agent_config_loader import AgentConfigLoader, CurrentAgentConfiguration
from agent_c.models.events import SessionEvent
from agent_c.util.slugs import MnemonicSlugs
from agent_c.toolsets.tool_set import Toolset
from agent_c.models.agent_config import AgentConfiguration
from agent_c_tools.tools.agent_assist.expiring_session_cache import AsyncExpiringCache
from agent_c_tools.tools.agent_clone.prompt import AgentCloneSection
from agent_c_tools.tools.think.prompt import ThinkSection
from agent_c.prompting.prompt_builder import PromptBuilder
from agent_c_tools.tools.workspace.tool import WorkspaceTools
from agent_c.agents.gpt import BaseAgent, GPTChatAgent, AzureGPTChatAgent
from agent_c.agents.claude import ClaudeChatAgent, ClaudeBedrockChatAgent
from agent_c.prompting.basic_sections.persona import DynamicPersonaSection



class AgentAssistToolBase(Toolset):
    __vendor_agent_map = {
        "azure_openai": AzureGPTChatAgent,
        "openai": GPTChatAgent,
        "claude": ClaudeChatAgent,
        "claude_aws": ClaudeBedrockChatAgent
    }

    def __init__(self, **kwargs: Any):
        if not 'name' in kwargs:
            kwargs['name'] = 'aa'
        super().__init__( **kwargs)
        self.agent_loader = AgentConfigLoader()
        self.sections: Optional[List[PromptSection]] = None

        self.session_cache = AsyncExpiringCache(default_ttl=kwargs.get('agent_session_ttl', 300))
        self.model_configs: Dict[str, Any] = self._load_model_config(kwargs.get('model_configs'))
        self.runtime_cache: Dict[str, BaseAgent] = {}
        self._model_name = kwargs.get('agent_assist_model_name', 'claude-3-7-sonnet-latest')

        self.client_wants_cancel: threading.Event = threading.Event()

        self.persona_cache: Dict[str, AgentConfiguration] = {}
        self.workspace_tool: Optional[WorkspaceTools] = None

    async def _streaming_callback(self, event: SessionEvent):
        """
        Callback for streaming events.
        """
        if event.type in ['text_delta', 'thought_delta', 'tool_call', 'render_media']:
            await self.streaming_callback(event)


    async def post_init(self):
        self.workspace_tool = cast(WorkspaceTools, self.tool_chest.available_tools.get('WorkspaceTools'))

    def runtime_for_agent(self, agent_config: AgentConfiguration):
        if agent_config.name in self.runtime_cache:
            return self.runtime_cache[agent_config.name]
        else:
            self.runtime_cache[agent_config.name] = self._runtime_for_agent(agent_config)
            return self.runtime_cache[agent_config.name]

    def _runtime_for_agent(self, agent_config: AgentConfiguration) -> BaseAgent:
        model_config = self.model_configs[agent_config.model_id]
        runtime_cls = self.__vendor_agent_map[model_config["vendor"]]

        auth_info = agent_config.agent_params.auth.model_dump() if agent_config.agent_params.auth is not None else  {}
        client = runtime_cls.client(**auth_info)
        if self.sections is not None:
            agent_sections = self.sections
        elif "ThinkTools" in agent_config.tools:
            agent_sections = [ThinkSection(), DynamicPersonaSection()]
        else:
            agent_sections = [DynamicPersonaSection()]

        return runtime_cls(model_name=model_config["id"], client=client,prompt_builder=PromptBuilder(sections=agent_sections))

    async def __chat_params(self, persona: AgentConfiguration, agent: BaseAgent, user_session_id: Optional[str] = None, **opts) -> Dict[str, Any]:
        tool_params = {}
        if opts:
            streaming_callback = opts['parent_tool_context'].get('streaming_callback', None) if 'parent_tool_context' in opts else None
        else:
            streaming_callback = None
        prompt_metadata = await self.__build_prompt_metadata(persona, user_session_id, **opts)
        chat_params = {"prompt_metadata": prompt_metadata, "output_format": 'raw',
                       "streaming_callback": streaming_callback,
                       "client_wants_cancel": self.client_wants_cancel, "tool_chest": self.tool_chest,
                       "session_id": user_session_id}

        if len(persona.tools):
            await self.tool_chest.initialize_toolsets(persona.tools)
            tool_params = self.tool_chest.get_inference_data(persona.tools, agent.tool_format)
            tool_params["toolsets"] = persona.tools

        agent_params = persona.agent_params.model_dump(exclude_none=True)
        if "model_name" not in agent_params:
            agent_params["model_name"] = persona.model_id

        return chat_params | tool_params | agent_params

    @staticmethod
    async def __build_prompt_metadata(persona: AgentConfiguration, user_session_id: Optional[str] = None, **opts) -> Dict[str, Any]:
        persona_props = persona.prompt_metadata if persona.prompt_metadata else {}

        return {"session_id": user_session_id, "persona_prompt": persona.persona, "persona": persona.model_dump(exclude_none=True, exclude={'prompt_metadata'}),
                "timestamp": datetime.now().isoformat()} | persona_props | opts

    async def agent_oneshot(self, user_message: str, persona: AgentConfiguration, user_session_id: Optional[str] = None,
                            tool_context: Optional[Dict[str, Any]] = None, **additional_metadata) -> str:

        try:
            self.logger.info(f"Running one-shot with persona: {persona.name}, user session: {user_session_id}")
            agent = self.runtime_for_agent(persona)
            chat_params = await self.__chat_params(persona, agent, user_session_id, parent_tool_context=tool_context, **additional_metadata)
            result: str = await agent.one_shot(user_message=user_message, **chat_params)
            return result
        except Exception as e:
            self.logger.exception(f"Error during one-shot with persona {persona.name}: {e}", exc_info=True)
            return f"Error: {str(e)}"

    async def parallel_agent_oneshots(self, user_messages: List[str], persona: AgentConfiguration, user_session_id: Optional[str] = None,
                                      tool_context: Optional[Dict[str, Any]] = None, **additional_metadata) -> List[str]:
        self.logger.info(f"Running parallel one-shots with persona: {persona.name}, user session: {user_session_id}")
        agent = self.runtime_for_agent(persona)
        chat_params = await self.__chat_params(persona, agent, user_session_id, parent_tool_context=tool_context, **additional_metadata)
        result: List[str] = await agent.parallel_one_shots(inputs=user_messages, **chat_params)
        return result

    async def agent_chat(self,
                         user_message: str,
                         persona: AgentConfiguration,
                         user_session_id: Optional[str] = None,
                         agent_session_id: Optional[str] = None,
                         tool_context: Optional[Dict[str, Any]] = None,
                         **additional_metadata) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Chat with a persona, maintaining conversation history.
        """
        self.logger.info(f"Running chat with persona: {persona.name}, user session: {user_session_id}")
        agent = self.runtime_for_agent(persona)

        if agent_session_id is None:
            agent_session_id = MnemonicSlugs.generate_id_slug(2)

        session = self.session_cache.get(agent_session_id)
        if session is None:
            metadata = { 'persona_name': persona.name }
            session = { 'user_session_id': user_session_id,  'messages': [], 'metadata': metadata, 'created_at': datetime.now()}

        try:
            chat_params = await self.__chat_params(persona, agent, user_session_id, parent_tool_context=tool_context, agent_session_id=agent_session_id, **additional_metadata)
            chat_params['messages'] = session['messages']
            messages = await agent.chat(user_message=user_message, **chat_params)

            session['messages'] = messages
            await self.session_cache.set(agent_session_id, session)
        except Exception as e:
            self.logger.exception(f"Error during chat with persona {persona.name}: {e}", exc_info=True)
            return agent_session_id, [{'role': 'error', 'content': str(e)}]

        if len(messages) == 0:
            self.logger.error(f"No messages returned from chat with persona {persona.name}.")
            return agent_session_id, [{'role': 'error', 'content': "No response from agent."}]

        return agent_session_id, messages

    def get_session_info(self, agent_session_id: str) -> Optional[Dict[str, Any]]:
        return self.session_cache.get(agent_session_id)

    def list_active_sessions(self, user_session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all active sessions."""
        active_ids = self.session_cache.list_active()
        sessions = []

        for agent_session_id in active_ids:
            session = self.session_cache.get(agent_session_id)
            if session:  # Just in case it expired between list and get
                if session['user_session_id'] == user_session_id or user_session_id is None:
                    sessions.append({
                        'agent_session_id': agent_session_id,
                        'user_session_id': session['user_session_id'],
                        'created_at': session.get('created_at'),
                        'last_activity': session.get('last_activity', session.get('created_at')),
                        'message_count': len(session.get('messages', [])),
                        'persona_name': session.get('metadata', {}).get('persona_name')
                    })

        return sessions


    @staticmethod
    def _load_model_config(data: dict[str, Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for vendor_info in data["vendors"]:
            vendor_name = vendor_info["vendor"]
            for model in vendor_info["models"]:
                model_with_vendor = model.copy()
                model_with_vendor["vendor"] = vendor_name
                result[model["id"]] = model_with_vendor

        return result


    @property
    def personas_list(self) -> List[str]:
        return self.agent_loader.agent_names


