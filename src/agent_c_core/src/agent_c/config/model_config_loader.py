"""
Loader class for model configuration data.

This module provides a loader class to handle loading, parsing, and saving
of model configurations from JSON files.
"""

import json
import os
from pathlib import Path
from typing import Union, Dict, Any, Optional

from .vendors import ModelConfigurationFile


class ModelConfigurationLoader:
    """
    Loader for model configuration files.
    
    Handles loading, parsing, validation, and saving of model configuration
    data from JSON files.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the loader.
        
        Args:
            config_path: Optional default path to configuration file
        """
        config_path = os.environ.get("AGENT_C_CONFIG_PATH", None) if config_path is None else config_path
        if config_path is None:
            raise ValueError("No configuration path provided")

        self.config_path = Path(config_path).joinpath("model_config.json")
        self._cached_config: Optional[ModelConfigurationFile] = None
        self.load_from_json()
    
    def load_from_json(self, json_path: Optional[Union[str, Path]] = None) -> ModelConfigurationFile:
        """
        Load model configuration from a JSON file.
        
        Args:
            json_path: Path to the JSON configuration file (uses default if None)
            
        Returns:
            ModelConfigurationFile instance with the loaded configuration
            
        Raises:
            FileNotFoundError: If the JSON file doesn't exist
            json.JSONDecodeError: If the JSON is malformed
            ValidationError: If the JSON doesn't match the expected schema
        """
        path = Path(json_path) if json_path else self.config_path
        
        if not path:
            raise ValueError("No configuration path provided")
        
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        self._cached_config = ModelConfigurationFile.model_validate(config_data)
        return self._cached_config
    
    def load_from_dict(self, config_data: Dict[str, Any]) -> ModelConfigurationFile:
        """
        Load model configuration from a dictionary.
        
        Args:
            config_data: Dictionary containing the configuration data
            
        Returns:
            ModelConfigurationFile instance with the loaded configuration
            
        Raises:
            ValidationError: If the data doesn't match the expected schema
        """
        self._cached_config = ModelConfigurationFile.model_validate(config_data)
        return self._cached_config
    
    def save_to_json(
        self, 
        config: ModelConfigurationFile,
        json_path: Optional[Union[str, Path]] = None,
        indent: int = 2
    ) -> None:
        """
        Save model configuration to a JSON file.
        
        Args:
            config: ModelConfigurationFile instance to save
            json_path: Path where to save the JSON file (uses default if None)
            indent: JSON indentation level (default: 2)
        """
        path = Path(json_path) if json_path else self.config_path
        
        if not path:
            raise ValueError("No save path provided")
        
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(
                config.model_dump(mode='json'),
                f,
                indent=indent,
                ensure_ascii=False
            )
    
    def validate_file(self, json_path: Optional[Union[str, Path]] = None) -> bool:
        """
        Validate a model configuration JSON file.
        
        Args:
            json_path: Path to the JSON configuration file (uses default if None)
            
        Returns:
            True if the file is valid, False otherwise
        """
        try:
            self.load_from_json(json_path)
            return True
        except Exception:
            return False
    
    def get_cached_config(self) -> Optional[ModelConfigurationFile]:
        """
        Get the cached configuration if available.
        
        Returns:
            Cached ModelConfigurationFile or None if not loaded
        """
        return self._cached_config
    
    def reload(self) -> ModelConfigurationFile:
        """
        Reload configuration from the default path.
        
        Returns:
            Reloaded ModelConfigurationFile
            
        Raises:
            ValueError: If no default path is set
        """
        if not self.config_path:
            raise ValueError("No default configuration path set")
        
        return self.load_from_json()

