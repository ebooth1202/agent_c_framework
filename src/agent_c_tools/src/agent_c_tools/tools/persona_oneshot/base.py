import glob
import os
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.tool_chest import ToolChest
from agent_c.agents.claude import  ClaudeChatAgent
from agent_c_tools.tools.think.prompt import ThinkSection
from agent_c.prompting.prompt_builder import PromptBuilder
from agent_c_tools.tools.workspace.tool import WorkspaceTools
from agent_c.prompting.basic_sections.persona import DynamicPersonaSection
from agent_c.models.persona_file import PersonaFile


class PersonaOneshotBase(Toolset):
    """
    CssExplorerTools provides methods for working with CSS files in workspaces.
    It enables efficient navigation and manipulation of large CSS files with component-based structure.
    """

    def __init__(self, **kwargs: Any):
        if not 'name' in kwargs:
            kwargs['name'] = 'persona_oneshot'
        super().__init__( **kwargs)
        self._model_name = kwargs.get('persona_oneshot_model_name', 'claude-3-7-sonnet-latest')
        tool_classes = kwargs.get("persona_oneshot_tool_classes", self.tool_chest.available_toolset_classes)
        essential_toolsets = kwargs.get("persona_oneshot_essential_toolsets", self.tool_chest.essential_toolsets)
        opts: Dict[str, Any] = {'tool_cache': self.tool_cache}
        self._personas_list: Optional[List[str]] = None
        if tool_classes is not None:
            opts['available_toolset_classes'] = tool_classes

        if essential_toolsets is not None:
            opts['essential_toolsets'] = essential_toolsets

        self.client_wants_cancel: threading.Event = threading.Event()
        sections = [ThinkSection(), DynamicPersonaSection()]
        prompt_builder = PromptBuilder(sections=sections)
        self.agent = ClaudeChatAgent(model_name=self._model_name, tool_chest=self.tool_chest,
                                     prompt_builder=prompt_builder)

        self.persona_cache: Dict[str, PersonaFile] = {}
        self.workspace_tool: Optional[WorkspaceTools] = None
        self.persona_dir: str = kwargs.get('persona_dir', 'personas')

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
            persona = PersonaFile(persona=file_contents, model_id=self._model_name)

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
       new_style = [os.path.relpath(file_path, self.persona_dir).removesuffix ('.yaml')
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

    async def __chat_params(self, persona: PersonaFile) -> Dict[str, Any]:
        if len(persona.tools):
            self.tool_chest.initialize_toolsets(persona.tools)


        prompt_metadata = await self.__build_prompt_metadata(persona)

        chat_params = {
            "prompt_metadata": prompt_metadata,
            "output_format": 'raw',
            "client_wants_cancel": self.client_wants_cancel,
            "budget_tokens": 10000,
            "max_tokens": 120000,
            "tool_chest": self.tool_chest,
        }

        if len(persona.tools):
            # TODO: openAI
            idata = self.tool_chest.get_inference_data(persona.tools, "claude")
            chat_params['tools'] = idata['schemas']
            chat_params['sections'] = idata['sections']

        return chat_params

    async def __build_prompt_metadata(self, persona: PersonaFile) -> Dict[str, Any]:
        return {
            "session_id": "none",
            "persona_prompt": persona.persona,
            "timestamp": datetime.now().isoformat(),
        }

    async def persona_oneshot(self, user_message: str, persona: PersonaFile) -> str:
        chat_params = await self.__chat_params(persona)
        result: str = await self.agent.one_shot(user_message=user_message, **chat_params)
        return result

    async def parallel_persona_oneshots(self, user_messages: List[str], persona: PersonaFile) -> List[str]:
        chat_params = await self.__chat_params(persona)
        result: List[str] = await self.agent.parallel_one_shots(inputs=user_messages, **chat_params)
        return result


