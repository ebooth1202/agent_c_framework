"""Query builder for tree-sitter queries.

This module provides utilities for building and manipulating
tree-sitter queries programmatically.
"""

from typing import Dict, List, Optional, Any, Set, Tuple
import re


class QueryBuilder:
    """Builder for tree-sitter queries.
    
    This class provides a fluent interface for constructing tree-sitter
    queries programmatically, making it easier to work with complex queries.
    """
    
    def __init__(self):
        """Initialize the query builder."""
        self._patterns: List[str] = []
    
    def add_pattern(self, pattern: str) -> 'QueryBuilder':
        """Add a raw query pattern.
        
        Args:
            pattern: The raw query pattern to add.
            
        Returns:
            The query builder instance for method chaining.
        """
        self._patterns.append(pattern.strip())
        return self
    
    def add_node_match(self, node_type: str, capture_name: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern to match a specific node type.
        
        Args:
            node_type: The type of node to match.
            capture_name: Optional name to capture the node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        pattern = f"({node_type})"
        if capture_name:
            pattern += f" @{capture_name}"
        self._patterns.append(pattern)
        return self
    
    def add_field_match(self, node_type: str, fields: Dict[str, str], 
                       capture_name: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern to match a node with specific fields.
        
        Args:
            node_type: The type of node to match.
            fields: Dictionary mapping field names to node types.
            capture_name: Optional name to capture the node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        field_str = " ".join([f"{k}: ({v})" for k, v in fields.items()])
        pattern = f"({node_type} {field_str})"
        if capture_name:
            pattern += f" @{capture_name}"
        self._patterns.append(pattern)
        return self
    
    def add_field_capture(self, node_type: str, fields: Dict[str, Tuple[str, str]],
                         capture_name: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern to match a node and capture its fields.
        
        Args:
            node_type: The type of node to match.
            fields: Dictionary mapping field names to (node_type, capture_name) tuples.
            capture_name: Optional name to capture the parent node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        field_str = " ".join([f"{k}: ({v[0]}) @{v[1]}" for k, v in fields.items()])
        pattern = f"({node_type} {field_str})"
        if capture_name:
            pattern += f" @{capture_name}"
        self._patterns.append(pattern)
        return self
    
    def add_nested_match(self, parent_type: str, child_type: str, 
                        parent_capture: Optional[str] = None,
                        child_capture: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern to match a parent node containing a child node.
        
        Args:
            parent_type: The type of parent node to match.
            child_type: The type of child node to match.
            parent_capture: Optional name to capture the parent node under.
            child_capture: Optional name to capture the child node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        child_str = f"({child_type})"
        if child_capture:
            child_str += f" @{child_capture}"
            
        pattern = f"({parent_type} {child_str})"
        if parent_capture:
            pattern += f" @{parent_capture}"
            
        self._patterns.append(pattern)
        return self
    
    def add_wildcard_match(self, parent_type: str, field_name: Optional[str] = None,
                          capture_name: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern to match any node within a parent.
        
        Args:
            parent_type: The type of parent node to match.
            field_name: Optional field name for the wildcard match.
            capture_name: Optional name to capture the matched node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        if field_name:
            pattern = f"({parent_type} {field_name}: (_))"
        else:
            pattern = f"({parent_type} (_))"
            
        if capture_name:
            pattern += f" @{capture_name}"
            
        self._patterns.append(pattern)
        return self
    
    def add_negated_field(self, node_type: str, negated_field: str,
                         capture_name: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern to match a node that does not have a specific field.
        
        Args:
            node_type: The type of node to match.
            negated_field: The field that should not be present.
            capture_name: Optional name to capture the node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        pattern = f"({node_type} !{negated_field})"
        if capture_name:
            pattern += f" @{capture_name}"
            
        self._patterns.append(pattern)
        return self
    
    def add_text_match(self, node_type: str, text: str,
                      capture_name: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern to match a node with specific text.
        
        Args:
            node_type: The type of node to match.
            text: The text content to match (will be quoted).
            capture_name: Optional name to capture the node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        # Escape quotes in the text
        escaped_text = text.replace('"', '\\"')
        pattern = f"({node_type} [\"{escaped_text}\"])"
        
        if capture_name:
            pattern += f" @{capture_name}"
            
        self._patterns.append(pattern)
        return self
    
    def add_multiple_match(self, node_type: str, options: List[str],
                         capture_name: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern to match a node with one of multiple texts.
        
        Args:
            node_type: The type of node to match.
            options: List of text options to match.
            capture_name: Optional name to capture the node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        # Escape quotes in the options
        escaped_options = [f'"{opt.replace("\"", "\\\"")}"' for opt in options]
        options_str = " ".join(escaped_options)
        
        pattern = f"({node_type} [{options_str}])"
        if capture_name:
            pattern += f" @{capture_name}"
            
        self._patterns.append(pattern)
        return self
    
    def add_quantified_match(self, node_type: str, quantifier: str,
                           capture_name: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern with a quantifier (*, +, ?).
        
        Args:
            node_type: The type of node to match.
            quantifier: The quantifier to use (*, +, ?).
            capture_name: Optional name to capture the node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        if quantifier not in ['*', '+', '?']:
            raise ValueError(f"Invalid quantifier: {quantifier}. Must be one of *, +, ?")
            
        pattern = f"({node_type}){quantifier}"
        if capture_name:
            pattern += f" @{capture_name}"
            
        self._patterns.append(pattern)
        return self
    
    def add_sibling_match(self, first_type: str, second_type: str,
                         first_capture: Optional[str] = None,
                         second_capture: Optional[str] = None) -> 'QueryBuilder':
        """Add a pattern to match sibling nodes.
        
        Args:
            first_type: The type of the first sibling node.
            second_type: The type of the second sibling node.
            first_capture: Optional name to capture the first node under.
            second_capture: Optional name to capture the second node under.
            
        Returns:
            The query builder instance for method chaining.
        """
        first_str = f"({first_type})"
        if first_capture:
            first_str += f" @{first_capture}"
            
        second_str = f"({second_type})"
        if second_capture:
            second_str += f" @{second_capture}"
            
        pattern = f"({first_str} . {second_str})"
        self._patterns.append(pattern)
        return self
    
    def build(self) -> str:
        """Build the complete query string.
        
        Returns:
            The complete query string with all patterns.
        """
        return "\n\n".join(self._patterns)
    
    @staticmethod
    def escape_string(s: str) -> str:
        """Escape a string for use in a tree-sitter query.
        
        Args:
            s: The string to escape.
            
        Returns:
            The escaped string.
        """
        return s.replace('"', '\\"')
    
    # Common query pattern factories
    
    @classmethod
    def class_query(cls, with_methods: bool = False) -> 'QueryBuilder':
        """Create a query for finding classes.
        
        Args:
            with_methods: Whether to include method patterns.
            
        Returns:
            A query builder with class patterns.
        """
        builder = cls()
        builder.add_field_capture('class_definition', {
            'name': ('identifier', 'class.name'),
            'body': ('block', 'class.body')
        }, 'class.def')
        
        if with_methods:
            builder.add_field_capture('function_definition', {
                'name': ('identifier', 'method.name'),
                'parameters': ('parameters', 'method.params'),
                'body': ('block', 'method.body')
            }, 'method.def')
            
        return builder
    
    @classmethod
    def function_query(cls) -> 'QueryBuilder':
        """Create a query for finding functions.
        
        Returns:
            A query builder with function patterns.
        """
        builder = cls()
        builder.add_field_capture('function_definition', {
            'name': ('identifier', 'function.name'),
            'parameters': ('parameters', 'function.params'),
            'body': ('block', 'function.body')
        }, 'function.def')
        
        return builder
    
    @classmethod
    def docstring_query(cls) -> 'QueryBuilder':
        """Create a query for finding docstrings.
        
        Returns:
            A query builder with docstring patterns.
        """
        builder = cls()
        
        # Function docstrings
        builder.add_pattern(
            "(function_definition\n" +
            "  body: (block . (expression_statement (string)) @function.docstring))")
        
        # Class docstrings
        builder.add_pattern(
            "(class_definition\n" +
            "  body: (block . (expression_statement (string)) @class.docstring))")
        
        return builder