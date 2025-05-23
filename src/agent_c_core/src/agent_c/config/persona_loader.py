import os
import glob

from pathlib import Path
from typing import Union, Dict, Any, Optional, List

from agent_c import ModelConfigurationFile
from agent_c.config import ModelConfigurationLoader
from agent_c.config.config_loader import ConfigLoader
from agent_c.models.persona_file import PersonaFile


class PersonaLoader(ConfigLoader):
    """
    Loader for model configuration files.

    Handles loading, parsing, validation, and saving of model configuration
    data from JSON files.
    """

    def __init__(self, default_model: str = 'claude-3-7-sonnet-latest', model_configs: ModelConfigurationFile = None,  config_path: Optional[str] = None):
        super().__init__(config_path)
        if model_configs is None:
            model_configs = ModelConfigurationLoader(config_path).load_from_json()

        self.model_configs = model_configs
        self.persona_folder = Path(config_path).joinpath("personas")
        self.persona_cache: Dict[str, PersonaFile] = {}
        self._default_model = default_model
        self._personas_list: Optional[List[str]] = None

    def _load_persona(self, persona_name: str = None) -> PersonaFile:
        """
        Load the persona prompt from a file based on the given persona name.

        Returns:
            str: Loaded persona prompt text.

        Raises:
            Exception: If the persona file cannot be loaded.
        """
        file_contents: Optional[str] = None
        persona_path = os.path.join(self.persona_folder, f"{persona_name}.yaml")
        if not os.path.exists(persona_path):
            persona_path = os.path.join(self.persona_folder, f"{persona_name}.md")

        if os.path.exists(persona_path):
            with open(persona_path, 'r') as file:
                file_contents = file.read()
        else:
            raise FileNotFoundError(f"Persona file {persona_path} not found.")

        if persona_path.endswith('yaml'):
            persona = PersonaFile.from_yaml(file_contents)
        else:
            persona = PersonaFile(persona=file_contents, model_id=self._default_model, uid=str(persona_path), agent_description='Legacy persona')

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
        new_style = [os.path.relpath(file_path, self.persona_folder).removesuffix('.yaml')
                     for file_path in glob.glob(os.path.join(self.persona_folder, "**/*.yaml"), recursive=True)]
        old_style = [os.path.relpath(file_path, self.persona_folder).removesuffix('.md')
                     for file_path in glob.glob(os.path.join(self.persona_folder, "**/*.md"), recursive=True)]
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