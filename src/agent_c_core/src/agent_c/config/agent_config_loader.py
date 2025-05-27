import os
import glob

from pathlib import Path
from typing import Union, Dict, Any, Optional, List

from agent_c import ModelConfigurationFile
from agent_c.config import ModelConfigurationLoader
from agent_c.config.config_loader import ConfigLoader
from agent_c.models.agent_config import AgentConfiguration


class AgentConfigLoader(ConfigLoader):
    def __init__(self, default_model: str = 'claude-sonnet-4-20250514', model_configs: ModelConfigurationFile = None,  config_path: Optional[str] = None):
        super().__init__(config_path)
        if model_configs is None:
            model_configs = ModelConfigurationLoader(config_path).load_from_json()

        self.model_configs = model_configs
        self.agent_config_folder = Path(config_path).joinpath("personas")
        self._agent_config_cache: Dict[str, AgentConfiguration] = {}
        self._default_model = default_model

    def _load_agent(self, agent_config_name: str = None) -> AgentConfiguration:
        file_contents: Optional[str] = None
        agent_config_path = os.path.join(self.agent_config_folder, f"{agent_config_name}.yaml")
        if not os.path.exists(agent_config_path):
            agent_config_path = os.path.join(self.agent_config_folder, f"{agent_config_name}.md")

        if os.path.exists(agent_config_path):
            with open(agent_config_path, 'r') as file:
                file_contents = file.read()
        else:
            raise FileNotFoundError(f"Agent configuration file {agent_config_path} not found.")


        return AgentConfiguration.from_yaml(file_contents)

    @property
    def catalog(self) -> Dict[str, AgentConfiguration]:
        """
        Returns a catalog of all agent configurations.
        """
        if not self._agent_config_cache:
            for agent_name in self.agent_names:
                self._fetch_agent_config(agent_name)

        return self._agent_config_cache


    def _load_agents(self):
        for file_path in glob.glob(os.path.join(self.agent_config_folder, "**/*.yaml"), recursive=True):
            agent = self._load_agent(file_path)


    def _fetch_agent_config(self, agent_name: str = None) -> AgentConfiguration:
        if agent_name in self._agent_config_cache:
            agent_config = self._agent_config_cache[agent_name]
        else:
            try:
                agent_config = self._load_agent(agent_name)
                self._agent_config_cache[agent_name] = agent_config
            except FileNotFoundError:
                raise Exception(f"Agent {agent_name} not found.")

        return agent_config