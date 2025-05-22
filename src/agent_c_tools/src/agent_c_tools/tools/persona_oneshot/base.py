import os
import glob
import json
import threading

from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from agent_c.toolsets.tool_set import Toolset
from agent_c.models.persona_file import PersonaFile
from agent_c_tools.tools.think.prompt import ThinkSection
from agent_c.prompting.prompt_builder import PromptBuilder
from agent_c_tools.tools.workspace.tool import WorkspaceTools
from agent_c.agents.gpt import BaseAgent, GPTChatAgent, AzureGPTChatAgent
from agent_c.agents.claude import ClaudeChatAgent, ClaudeBedrockChatAgent
from agent_c.prompting.basic_sections.persona import DynamicPersonaSection



class PersonaOneshotBase(Toolset):
    """
    CssExplorerTools provides methods for working with CSS files in workspaces.
    It enables efficient navigation and manipulation of large CSS files with component-based structure.
    """
    __vendor_agent_map = {
        "azure_openai": AzureGPTChatAgent,
        "openai": GPTChatAgent,
        "claude": ClaudeChatAgent,
        "claude_aws": ClaudeBedrockChatAgent
    }

    def __init__(self, **kwargs: Any):
        if not 'name' in kwargs:
            kwargs['name'] = 'persona_oneshot'
        super().__init__( **kwargs)
        self.model_configs: Dict[str, Any] = self._load_model_config(kwargs.get('model_config_path'))
        self.agent_cache: Dict[str, BaseAgent] = {}
        self._model_name = kwargs.get('persona_oneshot_model_name', 'claude-3-7-sonnet-latest')
        self._personas_list: Optional[List[str]] = None

        self.client_wants_cancel: threading.Event = threading.Event()

        self.persona_cache: Dict[str, PersonaFile] = {}
        self.workspace_tool: Optional[WorkspaceTools] = None
        self.persona_dir: str = kwargs.get('persona_dir', 'personas')

    async def post_init(self):
        self.workspace_tool = cast(WorkspaceTools, self.tool_chest.available_tools.get('WorkspaceTools'))

    def agent_for_persona(self, persona: PersonaFile):
        if persona.name in self.agent_cache:
            return self.agent_cache[persona.model_id]
        else:
            self.agent_cache[persona.name] = self._agent_for_persona(persona)
            return self.agent_cache[persona.name]

    def _agent_for_persona(self, persona: PersonaFile) -> BaseAgent:
        model_config = self.model_configs[persona.model_id]
        agent_cls = self.__vendor_agent_map[model_config["vendor"]]

        auth_info = persona.agent_params.auth.model_dump() if persona.agent_params.auth is not None else  {}
        client = agent_cls.client(**auth_info)
        if "ThinkTools" in persona.tools:
            agent_sections = [ThinkSection(), DynamicPersonaSection()]
        else:
            agent_sections = [DynamicPersonaSection()]

        return agent_cls(model_name=model_config["id"], client=client,prompt_builder=PromptBuilder(sections=agent_sections))

    async def __chat_params(self, persona: PersonaFile, agent: BaseAgent, session_id: Optional[str]) -> Dict[str, Any]:
        tool_params = {}
        prompt_metadata = await self.__build_prompt_metadata(persona, session_id)
        chat_params = {"prompt_metadata": prompt_metadata, "output_format": 'raw',
                       "client_wants_cancel": self.client_wants_cancel, "tool_chest": self.tool_chest}

        if len(persona.tools):
            self.tool_chest.initialize_toolsets(persona.tools)
            tool_params = self.tool_chest.get_inference_data(persona.tools, agent.tool_format)

        agent_params = persona.agent_params.model_dump(exclude_none=True)
        if "model" not in agent_params:
            agent_params["model"] = persona.model_id

        return chat_params | tool_params | agent_params

    @staticmethod
    async def __build_prompt_metadata(persona: PersonaFile, session_id: Optional[str] = None) -> Dict[str, Any]:
        persona_props = persona.prompt_metadata if persona.prompt_metadata else {}

        return {"session_id": session_id, "persona_prompt": persona.persona, "persona": persona.model_dump(exclude_none=True, exclude={'prompt_metadata'}),
                "timestamp": datetime.now().isoformat()} | persona_props

    async def persona_oneshot(self, user_message: str, persona: PersonaFile, session_id: Optional[str] = None) -> str:
        agent = self.agent_for_persona(persona)
        chat_params = await self.__chat_params(persona, agent, session_id)
        result: str = await agent.one_shot(user_message=user_message, **chat_params)
        return result

    async def parallel_persona_oneshots(self, user_messages: List[str], persona: PersonaFile, session_id: Optional[str] = None) -> List[str]:
        agent = self.agent_for_persona(persona)
        chat_params = await self.__chat_params(persona, agent, session_id)
        result: List[str] = await agent.parallel_one_shots(inputs=user_messages, **chat_params)
        return result

    @staticmethod
    def _load_model_config(config_path: str) -> Dict[str, Any]:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        result: Dict[str, Any] = {}
        for vendor_info in data["vendors"]:
            vendor_name = vendor_info["vendor"]
            for model in vendor_info["models"]:
                model_with_vendor = model.copy()
                model_with_vendor["vendor"] = vendor_name
                result[model["id"]] = model_with_vendor

        return result

    def _load_persona(self, persona_name: str = None) -> PersonaFile:
        """
        Load the persona prompt from a file based on the given persona name.

        Returns:
            str: Loaded persona prompt text.

        Raises:
            Exception: If the persona file cannot be loaded.
        """
        file_contents: Optional[str] = None
        persona_path = os.path.join(self.persona_dir, f"{persona_name}.yaml")
        if not os.path.exists(persona_path):
            persona_path = os.path.join(self.persona_dir, f"{persona_name}.md")

        if os.path.exists(persona_path):
            with open(persona_path, 'r') as file:
                file_contents = file.read()
        else:
            raise FileNotFoundError(f"Persona file {persona_path} not found.")

        if persona_path.endswith('yaml'):
            persona = PersonaFile.from_yaml(file_contents)
        else:
            persona = PersonaFile(persona=file_contents, model_id=self._model_name, uid=str(persona_path), agent_description='Legacy persona')

        return persona

    @property
    def personas_list(self) -> List[str]:
        """
        Get a list of available personas.

        Returns:
            List[str]: List of persona names.
        """
        if self._personas_list is None:
            self._personas_list = self._load_personas_list()

        return self._personas_list

    def _load_personas_list(self) -> List[str]:
        new_style = [os.path.relpath(file_path, self.persona_dir).removesuffix('.yaml')
                     for file_path in glob.glob(os.path.join(self.persona_dir, "**/*.yaml"), recursive=True)]
        old_style = [os.path.relpath(file_path, self.persona_dir).removesuffix('.md')
                     for file_path in glob.glob(os.path.join(self.persona_dir, "**/*.md"), recursive=True)]
        return new_style + old_style

    def _fetch_persona(self, persona: str = None) -> PersonaFile:
        if persona in self.persona_cache:
            persona_prompt = self.persona_cache[persona]
        else:
            try:
                persona_prompt = self._load_persona(persona)
                self.persona_cache[persona] = persona_prompt
            except FileNotFoundError:
                raise Exception(f"Persona {persona} not found.")

        return persona_prompt

