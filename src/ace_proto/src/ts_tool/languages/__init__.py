"""Language support package for tree-sitter based code exploration.

This module provides a framework for language-specific implementations
that use tree-sitter to parse and analyze code in various programming
languages. It includes utilities for discovering and registering
language implementations.
"""

import importlib
import inspect
import os
import pkgutil
import sys
from typing import Dict, Type, List

from ts_tool.languages.base import BaseLanguage

# Dictionary to store registered language implementations
_language_registry: Dict[str, Type[BaseLanguage]] = {}


def register_language(language_class: Type[BaseLanguage]) -> None:
    """Register a language implementation.
    
    This function adds a language implementation to the registry. It is
    called automatically during module initialization for all classes
    that inherit from BaseLanguage.
    
    Args:
        language_class: The language implementation class to register.
    """
    # Create a temporary instance to get the language name
    # (we don't need an actual parser for this)
    try:
        language_name = language_class.language_name.fget(None)
        _language_registry[language_name] = language_class
    except Exception:
        # Skip registration if we can't get the language name
        pass


def get_language_implementation(language_name: str) -> Type[BaseLanguage]:
    """Get a language implementation by name.
    
    Args:
        language_name: The name of the language to get.
        
    Returns:
        The language implementation class.
        
    Raises:
        ValueError: If the language is not supported.
    """
    language_name = language_name.lower()
    if language_name not in _language_registry:
        raise ValueError(f"Unsupported language: {language_name}")
    return _language_registry[language_name]


def get_supported_languages() -> List[str]:
    """Get a list of supported language names.
    
    Returns:
        A list of supported language names.
    """
    return list(_language_registry.keys())


def _discover_languages() -> None:
    """Discover and register all language implementations.
    
    This function scans the languages package for classes that inherit from
    BaseLanguage and registers them automatically. It is called during
    module initialization.
    """
    # Get the current package path
    package_path = os.path.dirname(__file__)
    
    # Import all modules in the package
    for _, module_name, _ in pkgutil.iter_modules([package_path]):
        if module_name not in ('base', '__init__'):
            try:
                module = importlib.import_module(f"ts_tool.languages.{module_name}")
                
                # Find all classes that inherit from BaseLanguage
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if (issubclass(obj, BaseLanguage) and 
                            obj is not BaseLanguage and 
                            obj.__module__ == module.__name__):
                        register_language(obj)
            except ImportError:
                # Skip modules that can't be imported
                pass


# Discover and register languages during module initialization
_discover_languages()