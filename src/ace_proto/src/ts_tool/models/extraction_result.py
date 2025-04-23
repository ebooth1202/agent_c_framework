"""Extraction result models for code exploration.

This module defines models for representing the results of code exploration
operations, providing consistent output formats for AI consumption.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
from enum import Enum

from ts_tool.models.code_entity import (
    CodeEntity, ClassEntity, FunctionEntity,
    MethodEntity, VariableEntity, ModuleEntity
)


class DetailLevel(Enum):
    """Enum for different levels of detail in entity representations."""
    SUMMARY = "summary"  # Basic information only
    SIGNATURE = "signature"  # Function/method signatures, class outlines
    FULL = "full"  # Complete code
    
    @classmethod
    def from_string(cls, value: str) -> 'DetailLevel':
        """Convert a string to a DetailLevel enum value.
        
        Args:
            value: The string value to convert.
            
        Returns:
            The corresponding DetailLevel enum value.
            
        Raises:
            ValueError: If the string does not match any DetailLevel.
        """
        for member in cls:
            if member.value == value.lower():
                return member
        raise ValueError(f"Invalid detail level: {value}")


@dataclass
class ExtractionResult:
    """Base class for extraction results.
    
    This class represents the result of a code extraction operation,
    providing metadata about the extraction process.
    """
    successful: bool = True
    error_message: Optional[str] = None
    language: str = ""
    detail_level: DetailLevel = DetailLevel.FULL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the extraction result to a dictionary.
        
        Returns:
            A dictionary representation of the extraction result.
        """
        return {
            'successful': self.successful,
            'error_message': self.error_message,
            'language': self.language,
            'detail_level': self.detail_level.value if self.detail_level else None,
            'result_type': self.__class__.__name__
        }


@dataclass
class EntityExtractionResult(ExtractionResult):
    """Result of extracting a specific entity.
    
    This class represents the result of extracting a specific entity
    from code, such as a class, function, or method.
    """
    entity: Optional[CodeEntity] = None
    entity_type: str = ""
    entity_name: str = ""
    source_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the entity extraction result to a dictionary.
        
        Returns:
            A dictionary representation of the entity extraction result.
        """
        result = super().to_dict()
        
        if self.successful and self.entity:
            result.update({
                'entity': self.entity.to_dict(),
                'entity_type': self.entity_type,
                'entity_name': self.entity_name
            })
            
            if self.detail_level == DetailLevel.FULL and self.source_code:
                result['source_code'] = self.source_code
                
        return result


@dataclass
class ModuleExtractionResult(ExtractionResult):
    """Result of extracting a complete module's structure.
    
    This class represents the result of extracting the complete structure
    of a code module, including all classes, functions, and variables.
    """
    module: Optional[ModuleEntity] = None
    source_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the module extraction result to a dictionary.
        
        Returns:
            A dictionary representation of the module extraction result.
        """
        result = super().to_dict()
        
        if self.successful and self.module:
            result['module'] = self.module.to_dict()
            
            if self.detail_level == DetailLevel.FULL and self.source_code:
                result['source_code'] = self.source_code
                
        return result


@dataclass
class PublicInterfaceResult(ExtractionResult):
    """Result of extracting the public interface of a module.
    
    This class represents the result of extracting just the public
    interface elements of a code module.
    """
    public_classes: List[ClassEntity] = field(default_factory=list)
    public_functions: List[FunctionEntity] = field(default_factory=list)
    public_constants: List[VariableEntity] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the public interface result to a dictionary.
        
        Returns:
            A dictionary representation of the public interface result.
        """
        result = super().to_dict()
        
        if self.successful:
            result.update({
                'public_classes': [cls.to_dict() for cls in self.public_classes],
                'public_functions': [func.to_dict() for func in self.public_functions],
                'public_constants': [const.to_dict() for const in self.public_constants],
                'class_count': len(self.public_classes),
                'function_count': len(self.public_functions),
                'constant_count': len(self.public_constants)
            })
                
        return result


@dataclass
class CodeSummaryResult(ExtractionResult):
    """Result of generating a code summary.
    
    This class represents a high-level summary of code structure.
    """
    class_count: int = 0
    function_count: int = 0
    variable_count: int = 0
    total_lines: int = 0
    class_names: List[str] = field(default_factory=list)
    function_names: List[str] = field(default_factory=list)
    has_documentation: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the code summary result to a dictionary.
        
        Returns:
            A dictionary representation of the code summary result.
        """
        result = super().to_dict()
        
        if self.successful:
            result.update({
                'class_count': self.class_count,
                'function_count': self.function_count,
                'variable_count': self.variable_count,
                'total_lines': self.total_lines,
                'class_names': self.class_names,
                'function_names': self.function_names,
                'has_documentation': self.has_documentation
            })
                
        return result