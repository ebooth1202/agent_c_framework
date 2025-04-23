"""Base language support for tree-sitter code exploration.

This module defines the base class for language-specific implementations,
providing common functionality and interfaces for all supported languages.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple, Set

from tree_sitter import Node, Tree, Parser, Query


class BaseLanguage(ABC):
    """Base class for language-specific functionality.
    
    This abstract class defines the interface that all language implementations
    must provide. It includes common query patterns and utility methods for
    working with tree-sitter nodes.
    """
    
    def __init__(self, parser: Parser):
        """Initialize the language support.
        
        Args:
            parser: A tree-sitter Parser configured for this language.
        """
        self.parser = parser
        self._query_cache: Dict[str, Query] = {}
    
    @property
    @abstractmethod
    def language_name(self) -> str:
        """The name of the language."""
        pass
    
    @abstractmethod
    def parse(self, code: str) -> Tree:
        """Parse the given code string.
        
        Args:
            code: The source code to parse.
            
        Returns:
            The parsed syntax tree.
        """
        pass
    
    @abstractmethod
    def get_entity_names(self, tree: Tree) -> Dict[str, List[str]]:
        """Get all named entities from the syntax tree.
        
        Args:
            tree: The parsed syntax tree.
            
        Returns:
            A dictionary with entity types as keys and lists of entity names as values.
        """
        pass
    
    @abstractmethod
    def get_entity_node(self, tree: Tree, entity_type: str, entity_name: str) -> Optional[Node]:
        """Get the syntax node for a specific named entity.
        
        Args:
            tree: The parsed syntax tree.
            entity_type: The type of entity to find (e.g., 'class', 'function').
            entity_name: The name of the entity to find.
            
        Returns:
            The syntax node for the entity, or None if not found.
        """
        pass
    
    @abstractmethod
    def get_documentation(self, node: Node, code: str) -> Optional[str]:
        """Extract documentation from a node.
        
        Args:
            node: The syntax node to extract documentation from.
            code: The original source code.
            
        Returns:
            The extracted documentation string, or None if not found.
        """
        pass
    
    @abstractmethod
    def get_public_interface(self, tree: Tree, code: str) -> Dict[str, Any]:
        """Extract the public interface from a syntax tree.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            A dictionary representing the public interface.
        """
        pass
    
    @abstractmethod
    def get_module_docstring(self, tree: Tree, code: str) -> Optional[str]:
        """Extract the module-level docstring.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            The module docstring, or None if not found.
        """
        pass
    
    @abstractmethod
    def get_imports(self, tree: Tree, code: str) -> List[str]:
        """Extract import statements.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            A list of import statements as strings.
        """
        pass
    
    def get_query(self, query_string: str) -> Query:
        """Get a cached Query object for the given query string.
        
        Args:
            query_string: The tree-sitter query string.
            
        Returns:
            A compiled Query object.
        """
        if query_string not in self._query_cache:
            self._query_cache[query_string] = Query(self.parser.language, query_string)
        return self._query_cache[query_string]

    def get_node_text(self, node: Node, code: str) -> str:
        """Get the text of a syntax node from the original code.
        
        Args:
            node: The syntax node.
            code: The original source code.
            
        Returns:
            The text of the node.
        """
        if node:
            start_byte = node.start_byte
            end_byte = node.end_byte
            return code[start_byte:end_byte]
        return ""
    
    def is_public(self, name: str) -> bool:
        """Check if an entity name indicates a public item.
        
        This is a common convention across many languages where names
        starting with underscore are considered private/internal.
        Language-specific implementations may override this.
        
        Args:
            name: The name to check.
            
        Returns:
            True if the name indicates a public entity, False otherwise.
        """
        return not name.startswith('_')
    
    def get_entity_range(self, node: Node) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Get the line/column range for a syntax node.
        
        Args:
            node: The syntax node.
            
        Returns:
            A tuple of ((start_line, start_column), (end_line, end_column)).
        """
        return ((node.start_point[0], node.start_point[1]), 
                (node.end_point[0], node.end_point[1]))
    
    def get_entity_byte_range(self, node: Node) -> Tuple[int, int]:
        """Get the byte range for a syntax node.
        
        Args:
            node: The syntax node.
            
        Returns:
            A tuple of (start_byte, end_byte).
        """
        return (node.start_byte, node.end_byte)
    
    def get_children_of_types(self, node: Node, child_types: Set[str]) -> List[Node]:
        """Get all child nodes of specified types.
        
        Args:
            node: The parent node.
            child_types: Set of node types to extract.
            
        Returns:
            List of matching child nodes.
        """
        result = []
        for child in node.children:
            if child.type in child_types:
                result.append(child)
        return result
    
    def find_first_child_of_type(self, node: Node, child_type: str) -> Optional[Node]:
        """Find the first child node of a specific type.
        
        Args:
            node: The parent node.
            child_type: The type of child node to find.
            
        Returns:
            The first matching child node, or None if not found.
        """
        for child in node.children:
            if child.type == child_type:
                return child
        return None
    
    def traverse_tree(self, tree: Tree):
        """Generate all nodes in the tree in pre-order traversal.
        
        Args:
            tree: The syntax tree to traverse.
            
        Yields:
            Each node in the tree.
        """
        cursor = tree.walk()
        visited_children = False
        
        while True:
            if not visited_children:
                yield cursor.node
                if not cursor.goto_first_child():
                    visited_children = True
            elif cursor.goto_next_sibling():
                visited_children = False
            elif cursor.goto_parent():
                visited_children = True
            else:
                break