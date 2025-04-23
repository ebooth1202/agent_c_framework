"""JavaScript language support for tree-sitter code exploration.

This module provides JavaScript-specific functionality for parsing and
extracting information from JavaScript code using tree-sitter.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
import re

from tree_sitter import Node, Tree, Parser

from ts_tool.languages.base import BaseLanguage


class JavascriptLanguage(BaseLanguage):
    """JavaScript language support for code exploration.
    
    This class provides JavaScript-specific functionality for parsing and
    extracting information from JavaScript code using tree-sitter.
    """
    
    # Query for finding classes
    CLASS_QUERY = """
    (class_declaration
      name: (identifier) @class.name
      body: (class_body) @class.body)
    
    (class_expression
      name: (identifier) @class.name
      body: (class_body) @class.body)
    """
    
    # Query for finding functions
    FUNCTION_QUERY = """
    (function_declaration
      name: (identifier) @function.name
      body: (statement_block) @function.body)
    
    (method_definition
      name: (property_identifier) @method.name
      body: (statement_block) @method.body)
    
    (arrow_function
      body: (_) @function.body)
    """
    
    # Query for finding variables
    VARIABLE_QUERY = """
    (variable_declaration
      (variable_declarator
        name: (identifier) @variable.name
        value: (_)? @variable.value))
    
    (lexical_declaration
      (variable_declarator
        name: (identifier) @variable.name
        value: (_)? @variable.value))
    """
    
    # Query for finding imports
    IMPORT_QUERY = """
    (import_statement
      source: (string) @import.source
      (import_clause
        (_)? @import.clause))
    """
    
    # Query for finding JSDoc comments
    DOCSTRING_QUERY = """
    (comment) @comment
    """
    
    @property
    def language_name(self) -> str:
        """The name of the language."""
        return "javascript"
    
    def parse(self, code: str) -> Tree:
        """Parse the given JavaScript code string.
        
        Args:
            code: The JavaScript source code to parse.
            
        Returns:
            The parsed syntax tree.
        """
        return self.parser.parse(bytes(code, 'utf8'))
    
    def get_entity_names(self, tree: Tree) -> Dict[str, List[str]]:
        """Get all named entities from the JavaScript syntax tree.
        
        Args:
            tree: The parsed syntax tree.
            
        Returns:
            A dictionary with entity types as keys and lists of entity names as values.
        """
        result = {
            'classes': [],
            'functions': [],
            'variables': []
        }
        
        # Find classes
        class_query = self.get_query(self.CLASS_QUERY)
        for match in class_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "class.name":
                    for node in capture_nodes:
                        class_name = node.text.decode('utf8')
                        if self.is_public(class_name):
                            result['classes'].append(class_name)
        
        # Find functions (only at module level)
        function_query = self.get_query(self.FUNCTION_QUERY)
        for match in function_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "function.name":
                    for node in capture_nodes:
                        # Only capture functions at module level (not methods)
                        if node.parent.parent == tree.root_node:
                            func_name = node.text.decode('utf8')
                            if self.is_public(func_name):
                                result['functions'].append(func_name)
        
        # Find variables (only at module level)
        variable_query = self.get_query(self.VARIABLE_QUERY)
        for match in variable_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "variable.name":
                    for node in capture_nodes:
                        # Only capture variables at module level
                        if node.parent.parent.parent == tree.root_node:
                            var_name = node.text.decode('utf8')
                            if self.is_public(var_name):
                                result['variables'].append(var_name)
        
        return result
    
    def get_entity_node(self, tree: Tree, entity_type: str, entity_name: str) -> Optional[Node]:
        """Get the syntax node for a specific named entity in JavaScript code.
        
        Args:
            tree: The parsed syntax tree.
            entity_type: The type of entity to find (e.g., 'class', 'function', 'method').
            entity_name: The name of the entity to find.
            
        Returns:
            The syntax node for the entity, or None if not found.
        """
        if entity_type == 'class':
            class_query = self.get_query(self.CLASS_QUERY)
            for match in class_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "class.name":
                        for node in capture_nodes:
                            if node.text.decode('utf8') == entity_name:
                                # Return the class_declaration or class_expression node
                                return node.parent
        
        elif entity_type == 'function':
            function_query = self.get_query(self.FUNCTION_QUERY)
            for match in function_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "function.name":
                        for node in capture_nodes:
                            if (node.text.decode('utf8') == entity_name and 
                                node.parent.parent == tree.root_node):
                                # Return the function_declaration node
                                return node.parent
        
        elif entity_type == 'method':
            # Methods are expected to be in format 'ClassName.method_name'
            if '.' in entity_name:
                class_name, method_name = entity_name.split('.')
                
                # First find the class
                class_node = self.get_entity_node(tree, 'class', class_name)
                if class_node:
                    # Then find the method inside the class body
                    body_node = class_node.child_by_field_name('body')
                    if body_node:
                        for child in body_node.children:
                            if child.type == 'method_definition':
                                name_node = child.child_by_field_name('name')
                                if name_node and name_node.text.decode('utf8') == method_name:
                                    return child
        
        elif entity_type == 'variable':
            variable_query = self.get_query(self.VARIABLE_QUERY)
            for match in variable_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "variable.name":
                        for node in capture_nodes:
                            if (node.text.decode('utf8') == entity_name and 
                                node.parent.parent.parent == tree.root_node):
                                # Return the variable_declaration node
                                return node.parent.parent
        
        return None
    
    def get_documentation(self, node: Node, code: str) -> Optional[str]:
        """Extract documentation from a JavaScript node.
        
        Args:
            node: The syntax node to extract documentation from.
            code: The original source code.
            
        Returns:
            The extracted documentation string, or None if not found.
        """
        # For JavaScript, documentation is a JSDoc comment preceding the node
        if node.type in ['function_declaration', 'method_definition', 'class_declaration', 'class_expression']:
            # Look for comments preceding the node
            start_line = node.start_point[0]
            lines = code.split('\n')
            
            # Search for comments above the node
            comment_lines = []
            current_line = start_line - 1
            
            # Collect consecutive comment lines above the node
            while current_line >= 0:
                line = lines[current_line].strip()
                if line.startswith('/**') or line.startswith('/*') or line.startswith('//'):
                    comment_lines.insert(0, line)
                    current_line -= 1
                elif line == '' and comment_lines:  # Allow blank lines within comment blocks
                    current_line -= 1
                elif line == '' and not comment_lines:  # Skip blank lines before comment
                    current_line -= 1
                else:  # Non-comment, non-blank line ends our search
                    break
            
            if comment_lines:
                return self._clean_documentation('\n'.join(comment_lines))
    def get_module_docstring(self, tree: Tree, code: str) -> Optional[str]:
        """Extract the module-level docstring from JavaScript code.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            The module docstring, or None if not found.
        """
        # In JavaScript, look for a JSDoc comment at the top of the file
        if tree.root_node.children:
            for child in tree.root_node.children:
                if child.type == 'comment':
                    comment_text = self.get_node_text(child, code)
                    if comment_text.startswith('/**') and comment_text.endswith('*/'):
                        # It's a JSDoc comment, clean it up
                        return self._clean_jsdoc(comment_text)
                # If we hit a non-comment, stop looking for module docstring
                elif child.type not in ('newline',):
                    break
        
        return None
    
    def _clean_jsdoc(self, comment: str) -> str:
        """Clean a JSDoc comment by removing comment markers and normalizing indentation.
        
        Args:
            comment: The raw JSDoc comment text.
            
        Returns:
            The cleaned comment.
        """
        # Remove the comment markers
        if comment.startswith('/**') and comment.endswith('*/'):
            comment = comment[3:-2].strip()
        
        # Process lines to remove leading asterisks and normalize indentation
        lines = []
        for line in comment.split('\n'):
            line = line.strip()
            # Remove leading asterisks commonly found in JSDoc
            if line.startswith('*'):
                line = line[1:].strip()
            lines.append(line)
        
        return '\n'.join(lines)
    
    def get_imports(self, tree: Tree, code: str) -> List[str]:
        """Extract all import statements from JavaScript code.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            A list of import statements as strings.
        """
        imports = []
        
        # Create a query for import statements if not already defined
        import_query = self.get_query("""
            (import_statement) @import
            (import_clause) @import_clause
            (require_call) @require
        """)
        
        for match in import_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                for node in capture_nodes:
                    imports.append(self.get_node_text(node, code))
        
        return imports
    
    def _clean_documentation(self, doc_text: str) -> str:
        """Clean a JavaScript documentation string.
        
        Args:
            doc_text: The raw documentation text.
            
        Returns:
            The cleaned documentation text.
        """
        # Handle JSDoc style comments
        if doc_text.startswith('/**') and doc_text.endswith('*/'):
            # Remove comment markers
            doc_text = doc_text[3:-2].strip()
            
            # Process each line
            lines = doc_text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # Remove leading asterisks and whitespace
                if line.startswith('*'):
                    line = line[1:].strip()
                cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
        
        # Handle single-line comments
        elif doc_text.startswith('//'):
            # Process each line
            lines = doc_text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # Remove comment marker
                if line.startswith('//'):
                    line = line[2:].strip()
                cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
        
        # Handle regular multi-line comments
        elif doc_text.startswith('/*') and doc_text.endswith('*/'):
            # Remove comment markers
            doc_text = doc_text[2:-2].strip()
            
            # Process each line
            lines = doc_text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                # Remove leading asterisks and whitespace
                if line.startswith('*'):
                    line = line[1:].strip()
                cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
        
        return doc_text
    
    def get_public_interface(self, tree: Tree, code: str) -> Dict[str, Any]:
        """Extract the public interface from a JavaScript syntax tree.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            A dictionary representing the public interface.
        """
        result = {
            'classes': [],
            'functions': [],
            'variables': []
        }
        
        # Get classes and their methods
        class_query = self.get_query(self.CLASS_QUERY)
        for match in class_query.matches(tree.root_node):
            class_info = {}
            class_node = None
            
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "class.name":
                    for node in capture_nodes:
                        class_name = node.text.decode('utf8')
                        if not self.is_public(class_name):
                            continue
                            
                        class_node = node.parent
                        class_info = {
                            'name': class_name,
                            'methods': [],
                            'line_range': self.get_entity_range(class_node),
                            'byte_range': self.get_entity_byte_range(class_node),
                            'docstring': self.get_documentation(class_node, code)
                        }
            
            if class_node and class_info:
                # Get methods for this class
                body_node = class_node.child_by_field_name('body')
                if body_node:
                    for child in body_node.children:
                        if child.type == 'method_definition':
                            name_node = child.child_by_field_name('name')
                            if name_node:
                                method_name = name_node.text.decode('utf8')
                                if not self.is_public(method_name) and method_name != 'constructor':
                                    continue
                                
                                # Get method parameters
                                params_node = child.child_by_field_name('parameters')
                                params_text = self.get_node_text(params_node, code) if params_node else "()"
                                
                                method_info = {
                                    'name': method_name,
                                    'signature': f"{method_name}{params_text}",
                                    'line_range': self.get_entity_range(child),
                                    'byte_range': self.get_entity_byte_range(child),
                                    'docstring': self.get_documentation(child, code)
                                }
                                
                                class_info['methods'].append(method_info)
                
                result['classes'].append(class_info)
        
        # Get standalone functions
        function_query = self.get_query(self.FUNCTION_QUERY)
        for match in function_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "function.name":
                    for node in capture_nodes:
                        # Only process top-level functions
                        if node.parent.parent != tree.root_node:
                            continue
                            
                        function_name = node.text.decode('utf8')
                        if not self.is_public(function_name):
                            continue
                            
                        function_node = node.parent
                        params_node = function_node.child_by_field_name('parameters')
                        params_text = self.get_node_text(params_node, code) if params_node else "()"
                        
                        function_info = {
                            'name': function_name,
                            'signature': f"{function_name}{params_text}",
                            'line_range': self.get_entity_range(function_node),
                            'byte_range': self.get_entity_byte_range(function_node),
                            'docstring': self.get_documentation(function_node, code)
                        }
                        
                        result['functions'].append(function_info)
        
        # Get top-level variables
        variable_query = self.get_query(self.VARIABLE_QUERY)
        for match in variable_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "variable.name":
                    for node in capture_nodes:
                        # Only process top-level variables
                        if node.parent.parent.parent != tree.root_node:
                            continue
                            
                        variable_name = node.text.decode('utf8')
                        if not self.is_public(variable_name):
                            continue
                            
                        declaration_node = node.parent.parent
                        value_node = node.parent.child_by_field_name('value')
                        value_text = self.get_node_text(value_node, code) if value_node else ""
                        
                        # Determine if this is a constant
                        is_constant = False
                        if declaration_node.type == 'lexical_declaration':
                            # Check if it's a 'const' declaration
                            if code[declaration_node.start_byte:declaration_node.start_byte+5] == 'const':
                                is_constant = True
                        elif variable_name.upper() == variable_name and not variable_name.islower():
                            # SCREAMING_SNAKE_CASE is conventionally used for constants
                            is_constant = True
                        
                        variable_info = {
                            'name': variable_name,
                            'value': value_text,
                            'is_constant': is_constant,
                            'line_range': self.get_entity_range(declaration_node),
                            'byte_range': self.get_entity_byte_range(declaration_node)
                        }
                        
                        result['variables'].append(variable_info)
        
        return result
    
    def is_public(self, name: str) -> bool:
        """Check if an entity name indicates a public item in JavaScript.
        
        In JavaScript, there's no strict convention for private members,
        but underscore prefix is commonly used to indicate "private".
        
        Args:
            name: The name to check.
            
        Returns:
            True if the name indicates a public entity, False otherwise.
        """
        return not name.startswith('_')