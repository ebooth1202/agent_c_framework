"""Python language support for tree-sitter code exploration.

This module provides Python-specific functionality for parsing and
extracting information from Python code using tree-sitter.
"""

from typing import Dict, List, Optional, Any, Tuple, Set
import re

from tree_sitter import Node, Tree, Parser

from ts_tool.languages.base import BaseLanguage


class PythonLanguage(BaseLanguage):
    """Python language support for code exploration.
    
    This class provides Python-specific functionality for parsing and
    extracting information from Python code using tree-sitter.
    """

    CLASS_QUERY = """
    (class_definition
      name: (identifier) @class.name
      body: (block) @class.body)
    """

    FUNCTION_QUERY = """
    (function_definition
      name: (identifier) @function.name
      parameters: (parameters) @function.params
      return_type: (type)? @function.return
      body: (block) @function.body)
    """

    VARIABLE_QUERY = """
    (assignment 
      left: (_) @variable.name
      right: (_) @variable.value)
    """

    IMPORT_QUERY = """
    (import_statement) @import
    (import_from_statement) @import.from
    """

    DOCSTRING_QUERY = """
    (function_definition
      body: (block . (expression_statement (string)) @function.docstring))
    
    (class_definition
      body: (block . (expression_statement (string)) @class.docstring))
    """
    
    @property
    def language_name(self) -> str:
        """The name of the language."""
        return "python"
    
    def parse(self, code: str) -> Tree:
        """Parse the given Python code string.
        
        Args:
            code: The Python source code to parse.
            
        Returns:
            The parsed syntax tree.
        """
        return self.parser.parse(bytes(code, 'utf8'))
    
    def get_entity_names(self, tree: Tree) -> Dict[str, List[str]]:
        """Get all named entities from the Python syntax tree.
        
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
        
        # Find variables (only at module level and only identifiers)
        variable_query = self.get_query(self.VARIABLE_QUERY)
        for match in variable_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "variable.name":
                    for node in capture_nodes:
                        # Only capture variables at module level and only if they're identifiers
                        if node.parent.parent == tree.root_node and node.type == 'identifier':
                            var_name = node.text.decode('utf8')
                            if self.is_public(var_name):
                                result['variables'].append(var_name)
        
        return result
    
    def get_entity_node(self, tree: Tree, entity_type: str, entity_name: str) -> Optional[Node]:
        """Get the syntax node for a specific named entity in Python code.
        
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
                                # Return the class_definition node (parent of the name node)
                                return node.parent
        
        elif entity_type == 'function':
            function_query = self.get_query(self.FUNCTION_QUERY)
            for match in function_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "function.name":
                        for node in capture_nodes:
                            if (node.text.decode('utf8') == entity_name and 
                                node.parent.parent == tree.root_node):
                                # Return the function_definition node (parent of the name node)
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
                        function_query = self.get_query(self.FUNCTION_QUERY)
                        for match in function_query.matches(body_node):
                            for capture_id, capture_nodes in match[1].items():
                                if capture_id == "function.name":
                                    for node in capture_nodes:
                                        if node.text.decode('utf8') == method_name:
                                            # Return the function_definition node (parent of the name node)
                                            return node.parent
        
        elif entity_type == 'variable':
            variable_query = self.get_query(self.VARIABLE_QUERY)
            for match in variable_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "variable.name":
                        for node in capture_nodes:
                            if (node.type == 'identifier' and 
                                node.text.decode('utf8') == entity_name and 
                                node.parent.parent == tree.root_node):
                                # Return the assignment node (parent of the left node)
                                return node.parent.parent
        
        return None
    
    def get_documentation(self, node: Node, code: str) -> Optional[str]:
        """Extract documentation from a Python node.
        
        Args:
            node: The syntax node to extract documentation from.
            code: The original source code.
            
        Returns:
            The extracted documentation string, or None if not found.
        """
        # For Python, documentation is a string literal as the first statement in a function/class body
        if node.type == 'function_definition' or node.type == 'class_definition':
            body_node = node.child_by_field_name('body')
            if body_node and body_node.type == 'block' and len(body_node.children) > 0:
                # Look for the first expression statement containing a string
                for child in body_node.children:
                    if child.type == 'expression_statement':
                        for expr_child in child.children:
                            if expr_child.type == 'string':
                                # Extract and clean the docstring
                                doc_text = self.get_node_text(expr_child, code)
                                return self._clean_docstring(doc_text)
    def get_module_docstring(self, tree: Tree, code: str) -> Optional[str]:
        """Extract the module-level docstring from Python code.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            The module docstring, or None if not found.
        """
        # In Python, a module docstring is the first string literal at the top level
        if tree.root_node.children:
            for child in tree.root_node.children:
                if child.type == 'expression_statement':
                    for expr_child in child.children:
                        if expr_child.type == 'string':
                            doc_text = self.get_node_text(expr_child, code)
                            return self._clean_docstring(doc_text)
                # If we hit a non-docstring statement, stop looking
                elif child.type not in ('comment', 'newline'):
                    break
        
        return None
        
    def get_imports(self, tree: Tree, code: str) -> List[str]:
        """Extract all import statements from Python code.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            A list of import statements as strings.
        """
        imports = []
        import_query = self.get_query(self.IMPORT_QUERY)
        
        for match in import_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                for node in capture_nodes:
                    imports.append(self.get_node_text(node, code))
        
        return imports
    
    def _clean_docstring(self, docstring: str) -> str:
        """Clean a Python docstring by removing quotes and normalizing indentation.
        
        Args:
            docstring: The raw docstring text.
            
        Returns:
            The cleaned docstring.
        """
        # Remove the outer quotes
        if docstring.startswith('"""') and docstring.endswith('"""'):
            docstring = docstring[3:-3]
        elif docstring.startswith("'''") and docstring.endswith("'''"):
            docstring = docstring[3:-3]
        elif docstring.startswith('"') and docstring.endswith('"'):
            docstring = docstring[1:-1]
        elif docstring.startswith("'") and docstring.endswith("'"):
            docstring = docstring[1:-1]
        
        # Split into lines and remove leading/trailing whitespace
        lines = docstring.split('\n')
        
        # Remove empty lines from the beginning and end
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        
        if not lines:
            return ""
        
        # Find the minimum indentation of non-empty lines
        min_indent = min((len(line) - len(line.lstrip())) for line in lines if line.strip())
        
        # Remove the common indentation from all lines
        return '\n'.join(line[min_indent:] for line in lines)
    
    def get_public_interface(self, tree: Tree, code: str) -> Dict[str, Any]:
        """Extract the public interface from a Python syntax tree.
        
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
                    function_query = self.get_query(self.FUNCTION_QUERY)
                    for method_match in function_query.matches(body_node):
                        signature = ""
                        method_node = None
                        method_name = None
                        params_text = "()"
                        return_type = None

                        for method_capture_id, method_capture_nodes in method_match[1].items():
                            if method_capture_id == "function.name":
                                for method_node in method_capture_nodes:
                                    method_name = method_node.text.decode('utf8')
                                    method_def_node = method_node.parent

                            elif method_capture_id == "function.params":
                                params_node = method_capture_nodes[0]
                                params_text = self.get_node_text(params_node, code)

                            elif method_capture_id == "function.return":
                                return_node = method_capture_nodes[0]
                                return_type = self.get_node_text(return_node, code)

                        if method_name and method_node:
                            signature = f"{method_name}{params_text}"
                            if return_type:
                                signature += f" -> {return_type}"

                            method_info = {
                                'name': method_name,
                                'signature': signature,
                                'return_type': return_type or "None",
                                'line_range': self.get_entity_range(method_def_node),
                                'byte_range': self.get_entity_byte_range(method_def_node),
                                'docstring': self.get_documentation(method_def_node, code)
                            }

                            class_info['methods'].append(method_info)

                result['classes'].append(class_info)


        function_query = self.get_query(self.FUNCTION_QUERY)
        for match in function_query.matches(tree.root_node):
            signature = ""
            function_node = None
            function_name = None
            params_text = "()"
            return_type = None

            for capture_id, capture_nodes in match[1].items():
                if capture_id == "function.name":
                    for node in capture_nodes:
                        # Ensure it's a top-level function
                        if node.parent.parent != tree.root_node:
                            continue

                        function_name = node.text.decode('utf8')
                        if not self.is_public(function_name):
                            continue

                        function_node = node.parent

                elif capture_id == "function.params":
                    params_node = capture_nodes[0]
                    params_text = self.get_node_text(params_node, code)

                elif capture_id == "function.return":
                    return_node = capture_nodes[0]
                    return_type = self.get_node_text(return_node, code)

            if function_name and function_node:
                signature = f"{function_name}{params_text}"
                if return_type:
                    signature += f" -> {return_type}"

                function_info = {
                    'name': function_name,
                    'signature': signature,
                    'return_type': return_type or "None",
                    'line_range': self.get_entity_range(function_node),
                    'byte_range': self.get_entity_byte_range(function_node),
                    'docstring': self.get_documentation(function_node, code)
                }

                result['functions'].append(function_info)
        
        # Get top-level variables
        variable_query = self.get_query(self.VARIABLE_QUERY)
        for match in variable_query.matches(tree.root_node):
            variable_name = None
            variable_value = None
            assignment_node = None
            
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "variable.name" and capture_nodes[0].type == 'identifier':
                    variable_name = capture_nodes[0].text.decode('utf8')
                    assignment_node = capture_nodes[0].parent.parent
                    
                    # Only process top-level variables
                    if assignment_node.parent != tree.root_node:
                        variable_name = None
                        continue
                        
                    # Skip private variables
                    if not self.is_public(variable_name):
                        variable_name = None
                        continue
                
                elif capture_id == "variable.value":
                    variable_value = self.get_node_text(capture_nodes[0], code)
            
            if variable_name and assignment_node:
                result['variables'].append({
                    'name': variable_name,
                    'value': variable_value,
                    'line_range': self.get_entity_range(assignment_node),
                    'byte_range': self.get_entity_byte_range(assignment_node)
                })
        
        return result