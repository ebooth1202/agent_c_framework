"""Formatting utilities for code exploration output.

This module provides utilities for formatting and presenting
code exploration results in a readable way.
"""

from typing import Dict, List, Any, Optional, Union
import json

from ts_tool.models.code_entity import ModuleEntity, ClassEntity, FunctionEntity, MethodEntity, VariableEntity
from ts_tool.models.extraction_result import DetailLevel, ExtractionResult
some_other_module_var: str = "some_value"
CONSTANT_COLOR = "#FF5733"  # Example color for constants

def format_entity_signature(entity: Union[ClassEntity, FunctionEntity, MethodEntity, VariableEntity]) -> str:
    """Format an entity signature for display.
    
    Args:
        entity: The entity to format.
        
    Returns:
        A formatted signature string.
    """
    if isinstance(entity, ClassEntity):
        return format_class_signature(entity)
    elif isinstance(entity, MethodEntity):
        return format_method_signature(entity)
    elif isinstance(entity, FunctionEntity):
        return format_function_signature(entity)
    elif isinstance(entity, VariableEntity):
        return format_variable_signature(entity)
    else:
        return str(entity)


def format_class_signature(cls: ClassEntity) -> str:
    """Format a class signature for display.
    
    Args:
        cls: The class entity to format.
        
    Returns:
        A formatted class signature string.
    """
    lc = cls.end_line - cls.start_line
    prefix = f"# {lc} lines of code, start: {cls.start_line}, end: {cls.end_line}\n"
    base_classes = f"({', '.join(cls.base_classes)})" if cls.base_classes else ""
    result = f"```\n{prefix}class {cls.name}{base_classes}:\n"
    if cls.docstring:
        ds = cls.docstring.replace('\n', '\n    ')
        result += f"    \"\"\"\n        {ds}\n    \"\"\"\n"

    # Add method signatures if available
    if cls.methods:
        for method in cls.methods:
            method_sig = format_method_signature(method).replace('\n', '\n    ')
            result += f"    {method_sig}\n"
    
    return result


def format_method_signature(method: MethodEntity) -> str:
    """Format a method signature for display.
    
    Args:
        method: The method entity to format.
        
    Returns:
        A formatted method signature string.
    """
    decorators = ""
    if method.decorators:
        decorators = "\n".join([f"@{d}" for d in method.decorators]) + "\n"
    
    prefix = "async " if method.is_async else ""
    
    if method.signature:
        sig = method.signature
    else:
        params = ", ".join(method.parameters)
        sig = f"{method.name}({params})"

    base_sig = f"{decorators}{prefix}def {sig}:"
    lc = method.end_line - method.start_line
    prefix = f"# {lc} lines of code, start: {method.start_line}, end: {method.end_line}\n"
    if method.docstring:
        ds = method.docstring
        #base_sig += f"\n    \"\"\"\n    {ds}\n    \"\"\"\n"
        base_sig += f"\n{method.docstring}\n"
    else:
        base_sig += "\n"

    return prefix + base_sig


def format_function_signature(func: FunctionEntity) -> str:
    """Format a function signature for display.
    
    Args:
        func: The function entity to format.
        
    Returns:
        A formatted function signature string.
    """
    decorators = ""
    if func.decorators:
        decorators = "\n".join([f"@{d}" for d in func.decorators]) + "\n"
    
    prefix = "async " if func.is_async else ""
    
    if func.signature:
        sig = func.signature
    else:
        params = ", ".join(func.parameters)
        sig = f"{func.name}({params})"
    lc = func.end_line - func.start_line
    prefix = f"# {lc} lines of code, start: {func.start_line}, end: {func.end_line}\n"
    return f"{prefix}{decorators}{prefix}def {sig}:"


def format_variable_signature(var: VariableEntity) -> str:
    """Format a variable signature for display.
    
    Args:
        var: The variable entity to format.
        
    Returns:
        A formatted variable signature string.
    """
    type_annotation = f": {var.type_hint}" if var.type_hint else ""
    value = f" = {var.value}" if var.value else ""
    
    return f"{var.name}{type_annotation}{value}"


def format_module_summary(module: ModuleEntity) -> str:
    """Format a module summary for display.
    
    Args:
        module: The module entity to format.
        
    Returns:
        A formatted module summary string.
    """
    result = []
    
    # Add module docstring if available
    if module.docstring:
        result.append(f"""\"\"\"\n{module.docstring}\n\"\"\"\n""")
    
    # Add imports
    if module.imports:
        result.append("# Imports")
        for imp in module.imports:
            result.append(imp)
        result.append("")
    
    # Add classes
    if module.classes:
        result.append("# Classes")
        for cls in module.classes:
            result.append(f"class {cls.name}:")
            if cls.methods:
                method_names = [m.name for m in cls.methods]
                result.append(f"    # Methods: {', '.join(method_names)}")
            result.append("")
    
    # Add functions
    if module.functions:
        result.append("# Functions")
        for func in module.functions:
            result.append(f"def {func.signature}:")
        result.append("")
    
    # Add variables
    if module.variables:
        result.append("# Variables")
        for var in module.variables:
            result.append(format_variable_signature(var))
    
    return "\n".join(result)

def format_function_as_context(entity_type, entity: Union[ClassEntity, FunctionEntity, MethodEntity, VariableEntity],
                             detail_level: Optional[DetailLevel] = DetailLevel.SIGNATURE) -> str:
    md = []
    if detail_level == DetailLevel.SIGNATURE:
        length = entity.end_line - entity.start_line
        line_comment = f"# {length} lines of code, start: {entity.start_line}, end: {entity.end_line}"
        md.append(f"\n```\n{format_entity_signature(entity)}\n")
        md.append(f"    \"\"\"\n    {entity.docstring}\n    \"\"\"\n```\n")
    #elif detail_level == DetailLevel.FULL and hasattr(result, 'source_code') and result.source_code:
    #    md.append(f"\n### Source Code\n\n```{entity.language}\n{result.source_code}\n```\n")

    return "".join(md)

def format_entity_as_context(entity_type, entity: Union[ClassEntity, FunctionEntity, MethodEntity, VariableEntity],
                             detail_level: Optional[DetailLevel] = DetailLevel.SIGNATURE) -> str:
    md = []
    #md.append(f"\n### {entity_type.capitalize()}: {entity.name}")

    #if entity.is_documented and entity.docstring:
        #md.append(f"\n{entity.docstring}")


    if detail_level == DetailLevel.SIGNATURE:
        md.append(f"\n{format_entity_signature(entity)}\n")
        #elif detail_level == DetailLevel.FULL and hasattr(result, 'source_code') and result.source_code:
        #    md.append(f"\n### Source Code\n\n```{entity.language}\n{result.source_code}\n```\n")

    return "".join(md)

def format_result_as_context(result: ExtractionResult) -> str:
    """Format an extraction result as context for an angent, in Markdown.

    Args:
        result: The extraction result to format.

    Returns:
        A Markdown-formatted string representation.
    """
    if not result.successful:
        return f"### Error\n\n{result.error_message}"

    md = []

    # Handle different result types
    if hasattr(result, 'entity') and result.entity:
        entity = result.entity
        md.append(f"## {result.entity_type.capitalize()}: {entity.name}")

        if entity.is_documented and entity.docstring:
            md.append(f"\n### Documentation\n\n```\n{entity.docstring}\n```\n")

        if hasattr(result, 'detail_level'):
            if result.detail_level == DetailLevel.SIGNATURE:
                md.append(f"\n### Signature\n\n```{entity.language}\n{format_entity_signature(entity)}\n```\n")
            elif result.detail_level == DetailLevel.FULL and hasattr(result, 'source_code') and result.source_code:
                md.append(f"\n### Source Code\n\n```{entity.language}\n{result.source_code}\n```\n")

    elif hasattr(result, 'module') and result.module:
        module = result.module
        md.append(f"## Module Summary")

        if module.filename:
            md.append(f"\n**File:** {module.filename}")

        md.append(f"\n**Language:** {module.language}")
        md.append(f"\n**Classes:** {len(module.classes)}")
        md.append(f"\n**Functions:** {len(module.functions)}")
        md.append(f"\n**Variables:** {len(module.variables)}")

        if module.classes:
            md.append("\n### Classes\n")
            for cls in module.classes:
                md.append(f"- **{cls.name}** ({len(cls.methods)} methods)")

        if module.functions:
            md.append("\n### Functions\n")
            for func in module.functions:
                md.append(f"- {func.name}")

    elif hasattr(result, 'public_classes') or hasattr(result, 'public_functions'):
        md.append(f"## Public Interface")

        if hasattr(result, 'public_classes') and result.public_classes:
            md.append("\n### Public Classes\n")
            for cls in result.public_classes:
                md.append(f"- {cls.name}")
                # Add class docstring if available
                if cls.docstring:
                    # Format the docstring with proper indentation
                    doc_lines = cls.docstring.strip().split('\n')
                    for line in doc_lines:
                        md.append(f"    {line}")
                    # Add an empty line after the docstring for readability
                    md.append("")

                if cls.methods:
                    md.append("  - Methods:")
                    for method in cls.methods:
                        # Add method signature instead of just the name
                        signature = method.signature if method.signature else f"{method.name}()"
                        md.append(f"    - {signature}")

                        # Add method docstring if available
                        if method.docstring:
                            # Format the docstring with proper indentation
                            doc_lines = method.docstring.strip().split('\n')
                            for line in doc_lines:
                                md.append(f"        {line}")
                            md.append(" ")

        if hasattr(result, 'public_functions') and result.public_functions:
            md.append("\n### Public Functions\n")
            for func in result.public_functions:
                # Add function signature instead of just the name
                signature = func.signature if func.signature else f"{func.name}()"
                md.append(f"- {signature}")

                # Add function docstring if available
                if func.docstring:
                    # Format the docstring with proper indentation
                    doc_lines = func.docstring.strip().split('\n')
                    for line in doc_lines:
                        md.append(f"    {line}")

                # Add function docstring if available
                if func.docstring:
                    # Format the docstring with proper indentation
                    doc_lines = func.docstring.strip().split('\n')
                    for line in doc_lines:
                        md.append(f"    {line}")

    elif hasattr(result, 'class_count'):
        md.append(f"## Code Summary")

        md.append(f"\n**Language:** {result.language}")
        md.append(f"\n**Total Lines:** {result.total_lines}")
        md.append(f"\n**Classes:** {result.class_count}")
        md.append(f"\n**Functions:** {result.function_count}")
        md.append(f"\n**Variables:** {result.variable_count}")
        md.append(f"\n**Documented:** {'Yes' if result.has_documentation else 'No'}")

    return "\n".join(md)

def format_result_as_markdown(result: ExtractionResult) -> str:
    """Format an extraction result as Markdown.
    
    Args:
        result: The extraction result to format.
        
    Returns:
        A Markdown-formatted string representation.
    """
    if not result.successful:
        return f"### Error\n\n{result.error_message}"
    
    md = []
    
    # Handle different result types
    if hasattr(result, 'entity') and result.entity:
        entity = result.entity
        md.append(f"## {result.entity_type.capitalize()}: {entity.name}")
        
        if entity.is_documented and entity.docstring:
            md.append(f"\n### Documentation\n\n```\n{entity.docstring}\n```\n")
        
        if hasattr(result, 'detail_level'):
            if result.detail_level == DetailLevel.SIGNATURE:
                md.append(f"\n### Signature\n\n```{entity.language}\n{format_entity_signature(entity)}\n```\n")
            elif result.detail_level == DetailLevel.FULL and hasattr(result, 'source_code') and result.source_code:
                md.append(f"\n### Source Code\n\n```{entity.language}\n{result.source_code}\n```\n")
    
    elif hasattr(result, 'module') and result.module:
        module = result.module
        md.append(f"## Module Summary")
        
        if module.filename:
            md.append(f"\n**File:** {module.filename}")
        
        md.append(f"\n**Language:** {module.language}")
        md.append(f"\n**Classes:** {len(module.classes)}")
        md.append(f"\n**Functions:** {len(module.functions)}")
        md.append(f"\n**Variables:** {len(module.variables)}")
        
        if module.classes:
            md.append("\n### Classes\n")
            for cls in module.classes:
                md.append(f"- **{cls.name}** ({len(cls.methods)} methods)")
        
        if module.functions:
            md.append("\n### Functions\n")
            for func in module.functions:
                md.append(f"- {func.name}")
    
    elif hasattr(result, 'public_classes') or hasattr(result, 'public_functions'):
        md.append(f"## Public Interface")
        
        if hasattr(result, 'public_classes') and result.public_classes:
            md.append("\n### Public Classes\n")
            for cls in result.public_classes:
                md.append(f"- {cls.name}")
                # Add class docstring if available
                if cls.docstring:
                    # Format the docstring with proper indentation
                    doc_lines = cls.docstring.strip().split('\n')
                    for line in doc_lines:
                        md.append(f"    {line}")
                    # Add an empty line after the docstring for readability
                    md.append("")
                
                if cls.methods:
                    md.append("  - Methods:")
                    for method in cls.methods:
                        # Add method signature instead of just the name
                        signature = method.signature if method.signature else f"{method.name}()"
                        md.append(f"    - {signature}")
                        
                        # Add method docstring if available
                        if method.docstring:
                            # Format the docstring with proper indentation
                            doc_lines = method.docstring.strip().split('\n')
                            for line in doc_lines:
                                md.append(f"        {line}")
                            md.append(" ")
        
        if hasattr(result, 'public_functions') and result.public_functions:
            md.append("\n### Public Functions\n")
            for func in result.public_functions:
                # Add function signature instead of just the name
                signature = func.signature if func.signature else f"{func.name}()"
                md.append(f"- {signature}")
                
                # Add function docstring if available
                if func.docstring:
                    # Format the docstring with proper indentation
                    doc_lines = func.docstring.strip().split('\n')
                    for line in doc_lines:
                        md.append(f"    {line}")
                
                # Add function docstring if available
                if func.docstring:
                    # Format the docstring with proper indentation
                    doc_lines = func.docstring.strip().split('\n')
                    for line in doc_lines:
                        md.append(f"    {line}")
    
    elif hasattr(result, 'class_count'):
        md.append(f"## Code Summary")
        
        md.append(f"\n**Language:** {result.language}")
        md.append(f"\n**Total Lines:** {result.total_lines}")
        md.append(f"\n**Classes:** {result.class_count}")
        md.append(f"\n**Functions:** {result.function_count}")
        md.append(f"\n**Variables:** {result.variable_count}")
        md.append(f"\n**Documented:** {'Yes' if result.has_documentation else 'No'}")
    
    return "".join(md)


def format_result_as_json(result: ExtractionResult, pretty: bool = False) -> str:
    """Format an extraction result as JSON.
    
    Args:
        result: The extraction result to format.
        pretty: Whether to pretty-print the JSON.
        
    Returns:
        A JSON string representation.
    """
    result_dict = result.to_dict()
    
    if pretty:
        return json.dumps(result_dict, indent=2)
    else:
        return json.dumps(result_dict)