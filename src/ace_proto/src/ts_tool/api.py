"""API for AI agents to explore and extract information from code.

This module provides a simple interface for AI agents to use the
Code Explorer functionality to analyze and extract information from code.
"""

from typing import Dict, List, Optional, Any, Union
import json

from ts_tool.core.code_explorer import CodeExplorer
from ts_tool.models.extraction_result import (
    DetailLevel, ExtractionResult, EntityExtractionResult,
    ModuleExtractionResult, PublicInterfaceResult, CodeSummaryResult
)
from ts_tool.utils.formatting import format_result_as_markdown, format_result_as_json, format_function_as_context
from ts_tool.utils.formatting import format_entity_as_context


# Create a singleton instance of the CodeExplorer
_explorer = CodeExplorer()


def get_supported_languages() -> List[str]:
    """Get a list of supported programming languages.
    
    Returns:
        A list of supported language names.
    """
    return _explorer.get_supported_languages()


def detect_language(code: str, filename: Optional[str] = None) -> Optional[str]:
    """Detect the programming language of the given code.
    
    Args:
        code: The source code to analyze.
        filename: Optional filename which may contain an extension hint.
        
    Returns:
        The detected language name, or None if detection failed.
    """
    return _explorer.detect_language(code, filename)

def get_code_context(code: str, language: Optional[str] = None,
                     filename: Optional[str] = None, format: str = 'markdown') -> str:
    result = _explorer.explore_code(code, language, filename)
    source_lines = result.source_code.split("\n") if result.source_code else []
    ds = result.module.docstring if result.module and result.module.docstring else ""

    md = [f"# Module Overview {result.module.filename}\n"
          f"{ds}"
          f"\n- Module size: {len(source_lines)} lines, {len(result.source_code)} characters\n"]

    if len(result.module.functions) == 0:
        md.append(f"- No methods found.\n")

    if len(result.module.classes) == 0:
        md.append(f"- No classes found.\n")

    if len(result.module.variables) == 0:
        md.append(f"- No module level variables found.\n")

    if len(result.module.functions):
        md.append(f"\n## Methods:\n")
        for entity in result.module.functions:
            md.append(format_function_as_context("function", entity))

    # classes = []
    # for class_name in summary.class_names:
    #     class_info = _explorer.get_entity(code, 'class', class_name, DetailLevel.FULL, language, filename)
    #     classes.append(class_info)
    if len(result.module.classes) > 0:
        md.append(f"\n## Classes:\n")
        for entity in result.module.classes:
            md.append(format_entity_as_context("class", entity))

    return "".join(md)




def get_code_summary(code: str, language: Optional[str] = None, 
                   filename: Optional[str] = None, format: str = 'dict') -> str | dict[str, Any] | CodeSummaryResult:
    """Get a high-level summary of code structure.
    
    This function provides a quick overview of the code structure,
    including counts of classes, functions, and variables.
    
    Args:
        code: The source code to analyze.
        language: Optional language name. If not provided, will be detected.
        filename: Optional filename which may help with language detection.
        format: Output format ('dict', 'json', or 'markdown').
        
    Returns:
        A summary of the code structure in the requested format.
    """
    result = _explorer.get_summary(code, language, filename)
    
    if format == 'dict':
        return result.to_dict()
    elif format == 'json':
        return format_result_as_json(result)
    elif format == 'markdown':
        return format_result_as_markdown(result)
    else:
        return result


def get_public_interface(code: str, language: Optional[str] = None,
                        filename: Optional[str] = None, format: str = 'dict') -> str | dict[str, Any] | PublicInterfaceResult:
    """Extract the public interface from code.
    
    This function extracts only the public elements of the code, such as
    public classes, functions, and constants.
    
    Args:
        code: The source code to analyze.
        language: Optional language name. If not provided, will be detected.
        filename: Optional filename which may help with language detection.
        format: Output format ('dict', 'json', or 'markdown').
        
    Returns:
        The public interface in the requested format.
    """
    result = _explorer.get_public_interface(code, language, filename)
    
    if format == 'dict':
        return result.to_dict()
    elif format == 'json':
        return format_result_as_json(result)
    elif format == 'markdown':
        return format_result_as_markdown(result)
    else:
        return result


def get_entity(code: str, entity_type: str, entity_name: str, 
              detail_level: str = 'full', language: Optional[str] = None,
              filename: Optional[str] = None, format: str = 'dict') -> Union[Dict[str, Any], str]:
    """Get a specific entity from code.
    
    This function extracts a specific named entity from the code, such as
    a class, function, or method, with the specified level of detail.
    
    Args:
        code: The source code to analyze.
        entity_type: The type of entity to extract ('class', 'function', 'method', 'variable').
        entity_name: The name of the entity to extract.
        detail_level: The level of detail to include ('summary', 'signature', 'full').
        language: Optional language name. If not provided, will be detected.
        filename: Optional filename which may help with language detection.
        format: Output format ('dict', 'json', or 'markdown').
        
    Returns:
        The extracted entity in the requested format.
    """
    result = _explorer.get_entity(code, entity_type, entity_name, detail_level, language, filename)
    
    if format == 'dict':
        return result.to_dict()
    elif format == 'json':
        return format_result_as_json(result)
    elif format == 'markdown':
        return format_result_as_markdown(result)
    else:
        raise ValueError(f"Unsupported format: {format}. Must be one of 'dict', 'json', or 'markdown'.")


def explore_code(code: str, language: Optional[str] = None,
                filename: Optional[str] = None, format: str = 'dict') -> str | dict[str, Any] | ModuleExtractionResult:
    """Explore code and extract its complete structure.
    
    This function parses the given code and extracts its complete structure,
    including all classes, functions, and variables.
    
    Args:
        code: The source code to explore.
        language: Optional language name. If not provided, will be detected.
        filename: Optional filename which may help with language detection.
        format: Output format ('dict', 'json', or 'markdown').
        
    Returns:
        The complete code structure in the requested format.
    """
    result = _explorer.explore_code(code, language, filename)
    
    if format == 'dict':
        return result.to_dict()
    elif format == 'json':
        return format_result_as_json(result)
    elif format == 'markdown':
        return format_result_as_markdown(result)
    else:
        return result


def get_source_code(code: str, entity_type: str, entity_name: str,
                   language: Optional[str] = None, filename: Optional[str] = None) -> Optional[str]:
    """Get the source code for a specific entity.
    
    This is a convenience function to directly get the source code
    of a specific entity without additional metadata.
    
    Args:
        code: The source code to analyze.
        entity_type: The type of entity to extract ('class', 'function', 'method', 'variable').
        entity_name: The name of the entity to extract.
        language: Optional language name. If not provided, will be detected.
        filename: Optional filename which may help with language detection.
        
    Returns:
        The source code of the entity, or None if not found.
    """
    result = _explorer.get_entity(code, entity_type, entity_name, DetailLevel.FULL, language, filename)
    
    if result.successful and hasattr(result, 'source_code') and result.source_code:
        return result.source_code
    
    return None


def get_signature(code: str, entity_type: str, entity_name: str,
                 language: Optional[str] = None, filename: Optional[str] = None) -> Optional[str]:
    """Get the signature for a specific entity.
    
    This is a convenience function to directly get the signature
    of a specific entity without additional metadata.
    
    Args:
        code: The source code to analyze.
        entity_type: The type of entity to extract ('class', 'function', 'method').
        entity_name: The name of the entity to extract.
        language: Optional language name. If not provided, will be detected.
        filename: Optional filename which may help with language detection.
        
    Returns:
        The signature of the entity, or None if not found.
    """
    result = _explorer.get_entity(code, entity_type, entity_name, DetailLevel.SIGNATURE, language, filename)
    
    if result.successful and result.entity:
        if hasattr(result.entity, 'signature'):
            return result.entity.signature
    
    return None


def get_documentation(code: str, entity_type: str, entity_name: str,
                     language: Optional[str] = None, filename: Optional[str] = None) -> Optional[str]:
    """Get the documentation for a specific entity.
    
    This is a convenience function to directly get the documentation
    of a specific entity without additional metadata.
    
    Args:
        code: The source code to analyze.
        entity_type: The type of entity to extract ('class', 'function', 'method', 'module').
        entity_name: The name of the entity to extract (use '' for module).
        language: Optional language name. If not provided, will be detected.
        filename: Optional filename which may help with language detection.
        
    Returns:
        The documentation of the entity, or None if not found or not documented.
    """
    if entity_type == 'module':
        result = _explorer.explore_code(code, language, filename)
        if result.successful and result.module and result.module.docstring:
            return result.module.docstring
    else:
        result = _explorer.get_entity(code, entity_type, entity_name, DetailLevel.SUMMARY, language, filename)
        if result.successful and result.entity and result.entity.docstring:
            return result.entity.docstring
    
    return None