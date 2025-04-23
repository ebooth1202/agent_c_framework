"""Parser manager for tree-sitter language parsers.

This module provides functionality to load and manage tree-sitter parsers
for different programming languages. It handles dynamic loading of language
modules and maintains a parser cache for performance.
"""

import importlib
import re
from typing import Dict, Optional, Callable, Any

from tree_sitter import Language, Parser


class ParserManager:
    """Manager for tree-sitter language parsers.
    
    This class handles loading and caching of tree-sitter parsers for
    different programming languages. It can detect languages from content
    when possible and provides a consistent interface for working with
    parsers across languages.
    """
    # Language detection patterns
    LANGUAGE_PATTERNS = {
        'python': [r'^#!/usr/bin/env python', r'^#!/usr/bin/python', r'^from\s+\w+\s+import\s+', r'^import\s+\w+'],
        'javascript': [r'^import\s+{.*}\s+from\s+[\'\"\']', r'^const\s+\w+\s*=\s*require\([\'\"\']'],
        'c_sharp': [r'^using\s+[\w\.]+;', r'^namespace\s+[\w\.]+', r'^\[?public\s+(class|interface|struct|enum)\s+\w+'],
        # Add more language detection patterns as needed
    }
    
    # Common file extensions mapped to languages
    EXTENSION_MAP = {
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.c': 'c',
        '.cpp': 'cpp',
        '.h': 'c',
        '.hpp': 'cpp',
        '.rb': 'ruby',
        '.go': 'go',
        '.rs': 'rust',
        '.cs': 'c_sharp',
        # Add more extensions as needed
    }
    
    def __init__(self):
        """Initialize the parser manager."""
        self._language_cache: Dict[str, Language] = {}
        self._parser_cache: Dict[str, Parser] = {}
    
    def get_parser(self, language_name: str) -> Parser:
        """Get a parser for the specified language.
        
        Args:
            language_name: The name of the language to get a parser for.
            
        Returns:
            A tree-sitter Parser configured for the specified language.
            
        Raises:
            ImportError: If the language module cannot be loaded.
            ValueError: If the language is not supported.
        """
        language_name = language_name.lower()
        
        # Return cached parser if available
        if language_name in self._parser_cache:
            return self._parser_cache[language_name]
        
        # Load language if not in cache
        language = self._load_language(language_name)
        
        # Create and configure parser
        parser = Parser(language)
        
        # Cache the parser
        self._parser_cache[language_name] = parser
        
        return parser
    
    def _load_language(self, language_name: str) -> Language:
        """Load a tree-sitter language by name.
        
        Args:
            language_name: The name of the language to load.
            
        Returns:
            The loaded Language object.
            
        Raises:
            ImportError: If the language module cannot be loaded.
            ValueError: If the language is not supported.
        """
        if language_name in self._language_cache:
            return self._language_cache[language_name]
        
        # Try to import the language module
        try:
            module_name = f"tree_sitter_{language_name}"
            language_module = importlib.import_module(module_name)
            language = Language(language_module.language())
            
            # Cache the language
            self._language_cache[language_name] = language
            
            return language
        except ImportError as e:
            raise ImportError(
                f"Could not load tree-sitter language module for '{language_name}'. "
                f"Make sure the 'tree_sitter_{language_name}' package is installed."
            ) from e
        except Exception as e:
            raise ValueError(f"Error loading language '{language_name}': {str(e)}") from e
    
    def detect_language(self, content: str, filename: Optional[str] = None) -> Optional[str]:
        """Detect the programming language from content and/or filename.
        
        Args:
            content: The source code content to analyze.
            filename: Optional filename which may contain an extension hint.
            
        Returns:
            The detected language name, or None if detection failed.
        """
        # First try to detect from filename extension if available
        if filename:
            ext = self._get_file_extension(filename)
            if ext in self.EXTENSION_MAP:
                return self.EXTENSION_MAP[ext]
        
        # Then try content-based detection
        for language, patterns in self.LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content, re.MULTILINE):
                    return language
        
        return None
    
    @staticmethod
    def _get_file_extension(filename: str) -> str:
        """Extract the file extension from a filename.
        
        Args:
            filename: The filename to extract the extension from.
            
        Returns:
            The file extension including the leading dot.
        """
        if '.' in filename:
            return '.' + filename.split('.')[-1].lower()
        return ''
    
    def get_supported_languages(self) -> list[str]:
        """Get a list of supported language names.
        
        This method returns the names of languages that are registered with
        the parser manager and have detection patterns defined.
        
        Returns:
            A list of supported language names.
        """
        return list(self.LANGUAGE_PATTERNS.keys())
    
    def get_language_by_extension(self, extension: str) -> Optional[str]:
        """Get the language name associated with a file extension.
        
        Args:
            extension: The file extension including the leading dot.
            
        Returns:
            The associated language name, or None if not recognized.
        """
        if not extension.startswith('.'):
            extension = '.' + extension
        return self.EXTENSION_MAP.get(extension.lower())