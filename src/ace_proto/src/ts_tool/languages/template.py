"""Template for adding new language support to ts_tool.

This template provides a standardized structure for implementing
support for a new programming language. Replace placeholders with
language-specific implementations.

Usage:
1. Copy this file to a new file named after your language (e.g., `ruby.py`)
2. Rename the class to match your language (e.g., `RubyLanguage`)
3. Implement all required abstract methods following the guidance in each section
4. Define language-specific queries for extracting entities
5. Register your language in `code_explorer.py` and add language detection in `parser_manager.py`

See the `python.py` and `javascript.py` implementations for complete examples.
Refer to the language support guide in the documentation for more details.
"""

from typing import Dict, List, Optional, Any, Tuple, Set

from tree_sitter import Node, Tree, Parser

from ts_tool.languages.base import BaseLanguage


class LanguageTemplate(BaseLanguage):
    """Template for language support implementation.
    
    To implement support for a new language:
    1. Rename this class to match your language (e.g., JavascriptLanguage)
    2. Implement all required abstract methods
    3. Define language-specific queries
    4. Add language-specific parsing logic
    
    Example implementation flow:
    1. Explore your language's syntax tree structure using a simple script
    2. Write queries to capture important language elements
    3. Implement methods to extract and process those elements
    4. Register your language in the code_explorer and parser_manager
    """
    
    # STEP 1: Define language-specific queries for entity types
    # These queries should extract the main structural elements of the language
    
    # Query for finding classes or equivalent structures
    CLASS_QUERY = """
    # Replace with language-specific query for classes
    # Example for JavaScript:
    (class_declaration
      name: (identifier) @class.name
      body: (class_body) @class.body)
    
    (class_expression
      name: (identifier) @class.name
      body: (class_body) @class.body)
    
    # Example for Python:
    # (class_definition
    #   name: (identifier) @class.name
    #   body: (block) @class.body)
    """
    
    # Query for finding functions or methods
    FUNCTION_QUERY = """
    # Replace with language-specific query for functions
    # Example for JavaScript:
    (function_declaration
      name: (identifier) @function.name
      parameters: (formal_parameters) @function.params
      body: (statement_block) @function.body)
    
    (method_definition
      name: (property_identifier) @method.name
      parameters: (formal_parameters) @method.params
      body: (statement_block) @method.body)
    
    # Example for Python:
    # (function_definition
    #   name: (identifier) @function.name
    #   parameters: (parameters) @function.params
    #   body: (block) @function.body)
    """
    
    # Query for finding variables
    VARIABLE_QUERY = """
    # Replace with language-specific query for variables
    # Example for JavaScript:
    (variable_declaration
      (variable_declarator
        name: (identifier) @variable.name
        value: (_)? @variable.value))
    
    # Example for Python:
    # (assignment 
    #   left: (_) @variable.name
    #   right: (_) @variable.value)
    """
    
    # Query for finding imports
    IMPORT_QUERY = """
    # Replace with language-specific query for imports
    # Example for JavaScript:
    (import_statement) @import
    (import_specifier
      name: (identifier) @import.name) @import.specifier
    
    # Example for Python:
    # (import_statement) @import
    # (import_from_statement) @import.from
    """
    
    # Query for finding docstrings or comments
    DOCSTRING_QUERY = """
    # Replace with language-specific query for documentation
    # Example for JavaScript JSDoc:
    (comment) @comment
    
    # Example for Python docstrings:
    # (function_definition
    #   body: (block . (expression_statement (string)) @function.docstring))
    # 
    # (class_definition
    #   body: (block . (expression_statement (string)) @class.docstring))
    """
    
    @property
    def language_name(self) -> str:
        """The name of the language.
        
        This should match the tree-sitter language module name without the
        'tree_sitter_' prefix, e.g., 'python', 'javascript', 'ruby'.
        It's used for language detection and parser loading.
        """
        # STEP 2: Set the language name
        return "language_name"  # e.g., "javascript", "python", "ruby"
    
    def parse(self, code: str) -> Tree:
        """Parse the given code string into a syntax tree.
        
        This implementation is typically standard across most languages,
        unless special encoding or parsing options are needed.
        
        Args:
            code: The source code to parse.
            
        Returns:
            The parsed syntax tree.
        """
        # STEP 3: Implement parsing logic
        # This is usually the same for most languages
        return self.parser.parse(bytes(code, 'utf8'))
    
    def get_entity_names(self, tree: Tree) -> Dict[str, List[str]]:
        """Get all named entities from the syntax tree.
        
        This method extracts the names of all classes, functions, and variables
        in the code using tree-sitter queries. It filters out private entities
        based on language conventions.
        
        Args:
            tree: The parsed syntax tree.
            
        Returns:
            A dictionary with entity types as keys and lists of entity names as values.
        """
        # STEP 4: Implement entity name extraction
        # Use the queries defined above to extract entity names
        result = {
            'classes': [],
            'functions': [],
            'variables': []
        }
        
        # Extract class names
        class_query = self.get_query(self.CLASS_QUERY)
        for match in class_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "class.name":
                    for node in capture_nodes:
                        class_name = node.text.decode('utf8')
                        if self.is_public(class_name):
                            result['classes'].append(class_name)
        
        # Extract function names - similar pattern
        function_query = self.get_query(self.FUNCTION_QUERY)
        for match in function_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "function.name":
                    for node in capture_nodes:
                        # Check if it's a top-level function (not a method)
                        # This will vary by language - adapt as needed
                        if node.parent.parent == tree.root_node:  # Example check
                            func_name = node.text.decode('utf8')
                            if self.is_public(func_name):
                                result['functions'].append(func_name)
        
        # Extract variable names - will vary significantly by language
        variable_query = self.get_query(self.VARIABLE_QUERY)
        for match in variable_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "variable.name":
                    for node in capture_nodes:
                        # Filter for top-level variables and appropriate node types
                        # This example is simplified - adapt to your language
                        if node.type == 'identifier':  # Common check
                            var_name = node.text.decode('utf8')
                            if self.is_public(var_name):
                                result['variables'].append(var_name)
        
        return result
    
    def get_entity_node(self, tree: Tree, entity_type: str, entity_name: str) -> Optional[Node]:
        """Get the syntax node for a specific named entity.
        
        This method finds and returns the complete syntax node for a named entity,
        which is useful for getting the full definition, including body, parameters,
        and other details.
        
        Args:
            tree: The parsed syntax tree.
            entity_type: The type of entity to find (e.g., 'class', 'function').
            entity_name: The name of the entity to find.
            
        Returns:
            The syntax node for the entity, or None if not found.
        """
        # STEP 5: Implement entity node lookup
        # This should handle different entity types appropriately
        
        if entity_type == 'class':
            class_query = self.get_query(self.CLASS_QUERY)
            for match in class_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "class.name":
                        for node in capture_nodes:
                            if node.text.decode('utf8') == entity_name:
                                # Return the complete class node (parent of the name node)
                                return node.parent
        
        elif entity_type == 'function':
            function_query = self.get_query(self.FUNCTION_QUERY)
            for match in function_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "function.name":
                        for node in capture_nodes:
                            if (node.text.decode('utf8') == entity_name and
                                node.parent.parent == tree.root_node):  # Only top-level functions
                                # Return the complete function node (parent of the name node)
                                return node.parent
        
        elif entity_type == 'method':
            # Methods are typically part of a class - often referenced as 'ClassName.method_name'
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
                                if capture_id == "function.name" or capture_id == "method.name":
                                    for node in capture_nodes:
                                        if node.text.decode('utf8') == method_name:
                                            return node.parent
        
        elif entity_type == 'variable':
            variable_query = self.get_query(self.VARIABLE_QUERY)
            for match in variable_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "variable.name":
                        for node in capture_nodes:
                            # Adjust this condition based on your language's AST structure
                            if node.text.decode('utf8') == entity_name:
                                # Return the variable declaration node
                                # This may vary by language - might be node.parent or node.parent.parent
                                return node.parent.parent
        
        return None
    
    def get_documentation(self, node: Node, code: str) -> Optional[str]:
        """Extract documentation from a node.
        
        This method extracts documentation comments or strings associated with
        a node. The implementation varies significantly between languages due
        to different documentation conventions.
        
        Args:
            node: The syntax node to extract documentation from.
            code: The original source code.
            
        Returns:
            The extracted documentation string, or None if not found.
        """
        # STEP 6: Implement documentation extraction
        # This should handle language-specific documentation styles
        
        # Example implementation for JavaScript-style comments
        if node.type in ['function_declaration', 'method_definition', 'class_declaration']:
            # Look for comments preceding the node
            start_line = node.start_point[0]
            start_byte = node.start_byte
            comment_query = self.get_query(self.DOCSTRING_QUERY)
            
            # Find all comments in the file
            for match in comment_query.matches(node.tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "comment":
                        for comment_node in capture_nodes:
                            # Check if comment is right before the node
                            if comment_node.end_point[0] == start_line - 1 or \
                               (comment_node.end_byte < start_byte and \
                                comment_node.end_point[0] >= start_line - 3):
                                # Extract and clean the comment text
                                comment_text = code[comment_node.start_byte:comment_node.end_byte]
                                return self._clean_documentation(comment_text)
        
        # Example implementation for Python-style docstrings
        # if node.type in ['function_definition', 'class_definition']:
        #     body_node = node.child_by_field_name('body')
        #     if body_node and body_node.type == 'block' and len(body_node.children) > 0:
        #         # Look for the first expression statement containing a string
        #         for child in body_node.children:
        #             if child.type == 'expression_statement':
        #                 for expr_child in child.children:
        #                     if expr_child.type == 'string':
        #                         # Extract the docstring
        #                         docstring = code[expr_child.start_byte:expr_child.end_byte]
        #                         return self._clean_documentation(docstring)
    def get_module_docstring(self, tree: Tree, code: str) -> Optional[str]:
        """Extract the module-level docstring.
        
        Most languages have some concept of module or file-level documentation,
        though the conventions vary widely:
        - Python: String literal at the beginning of the file
        - JavaScript: JSDoc comment at the top of the file
        - Java: Block comment or JavaDoc at the top
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            The module docstring, or None if not found.
        """
        # TEMPLATE IMPLEMENTATION - Replace with language-specific logic
        if tree.root_node.children:
            for child in tree.root_node.children:
                # Look for a documentation comment or string at the top of the file
                # This is just a placeholder; implement based on language conventions
                if child.type in ('comment', 'string', 'documentation_comment'):
                    return self.get_node_text(child, code)
                # Skip over whitespace and other non-code elements
                elif child.type not in ('newline', 'whitespace'):
                    # Stop looking once we hit actual code
                    break
                    
        return None
    
    def get_imports(self, tree: Tree, code: str) -> List[str]:
        """Extract import statements.
        
        Different languages have different import/include mechanisms:
        - Python: import, from...import
        - JavaScript: import, require()
        - Java: import
        - C/C++: #include
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            A list of import statements as strings.
        """
        # TEMPLATE IMPLEMENTATION - Replace with language-specific logic
        # Define import query based on language syntax
        import_query = self.get_query("""
            (import_statement) @import
            (import_from_statement) @import.from
            # Add other import patterns relevant to your language
        """)
        
        imports = []
        for match in import_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                for node in capture_nodes:
                    imports.append(self.get_node_text(node, code))
                    
        return imports
    
    def _clean_documentation(self, doc_text: str) -> str:
        """Clean documentation text according to language conventions.
        
        This helper method removes comment markers, normalizes whitespace,
        and formats documentation text according to language-specific conventions.
        
        Args:
            doc_text: The raw documentation text.
            
        Returns:
            The cleaned documentation text.
        """
        # STEP 7: Implement documentation cleaning
        # This should handle language-specific documentation formats
        
        # Example implementation for JavaScript JSDoc comments
        if doc_text.startswith('/**') and doc_text.endswith('*/'):
            # Remove the comment markers
            doc_text = doc_text[3:-2].strip()
            
            # Process each line to remove leading asterisks and normalize whitespace
            lines = doc_text.split('\n')
            cleaned_lines = []
            for line in lines:
                line = line.strip()
                if line.startswith('*'):
                    line = line[1:].strip()
                cleaned_lines.append(line)
            
            return '\n'.join(cleaned_lines)
        
        # Example implementation for Python docstrings
        # if doc_text.startswith('"""') and doc_text.endswith('"""'):
        #     # Remove the triple quotes
        #     doc_text = doc_text[3:-3]
        #     
        #     # Split into lines and remove leading/trailing whitespace
        #     lines = doc_text.split('\n')
        #     
        #     # Remove empty lines from the beginning and end
        #     while lines and not lines[0].strip():
        #         lines.pop(0)
        #     while lines and not lines[-1].strip():
        #         lines.pop()
        #     
        #     if not lines:
        #         return ""
        #     
        #     # Find the minimum indentation of non-empty lines
        #     min_indent = min((len(line) - len(line.lstrip())) for line in lines if line.strip())
        #     
        #     # Remove the common indentation from all lines
        #     return '\n'.join(line[min_indent:] for line in lines)
        
        # Default case - return as is if no specific format is detected
        return doc_text
    
    def get_public_interface(self, tree: Tree, code: str) -> Dict[str, Any]:
        """Extract the public interface from a syntax tree.
        
        This comprehensive method builds a detailed representation of the code's
        structure, including all public classes, methods, functions, and variables
        with their associated metadata like documentation, line ranges, and signatures.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            A dictionary representing the public interface.
        """
        # STEP 8: Implement public interface extraction
        # This should combine the other methods to build a complete interface
        
        result = {
            'classes': [],
            'functions': [],
            'variables': []
        }
        
        # Extract classes and their methods
        class_query = self.get_query(self.CLASS_QUERY)
        for match in class_query.matches(tree.root_node):
            class_info = {}
            class_node = None
            
            # Get class name and node
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
            
            # If we found a valid class, extract its methods
            if class_node and class_info:
                # Get methods for this class
                body_node = class_node.child_by_field_name('body')
                if body_node:
                    function_query = self.get_query(self.FUNCTION_QUERY)
                    for method_match in function_query.matches(body_node):
                        method_info = {}
                        
                        # Extract method details
                        for method_capture_id, method_capture_nodes in method_match[1].items():
                            if method_capture_id == "function.name" or method_capture_id == "method.name":
                                for method_node in method_capture_nodes:
                                    method_name = method_node.text.decode('utf8')
                                    # Skip private methods (except special methods like __init__ in Python)
                                    if not self.is_public(method_name) and method_name != '__init__':
                                        continue
                                        
                                    method_def_node = method_node.parent
                                    # Get parameters for method signature
                                    params_node = method_def_node.child_by_field_name('parameters') or \
                                                method_def_node.child_by_field_name('params')
                                    params_text = self.get_node_text(params_node, code) if params_node else "()"
                                    
                                    method_info = {
                                        'name': method_name,
                                        'signature': f"{method_name}{params_text}",
                                        'line_range': self.get_entity_range(method_def_node),
                                        'byte_range': self.get_entity_byte_range(method_def_node),
                                        'docstring': self.get_documentation(method_def_node, code)
                                    }
                        
                        if method_info:
                            class_info['methods'].append(method_info)
                
                result['classes'].append(class_info)
        
        # Extract standalone functions (not methods)
        function_query = self.get_query(self.FUNCTION_QUERY)
        for match in function_query.matches(tree.root_node):
            function_info = {}
            
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "function.name":
                    for node in capture_nodes:
                        # Make sure it's a top-level function, not a method
                        # This check may vary by language
                        if node.parent.parent != tree.root_node:
                            continue
                            
                        function_name = node.text.decode('utf8')
                        if not self.is_public(function_name):
                            continue
                            
                        function_node = node.parent
                        # Get parameters for function signature
                        params_node = function_node.child_by_field_name('parameters') or \
                                    function_node.child_by_field_name('params')
                        params_text = self.get_node_text(params_node, code) if params_node else "()"
                        
                        function_info = {
                            'name': function_name,
                            'signature': f"{function_name}{params_text}",
                            'line_range': self.get_entity_range(function_node),
                            'byte_range': self.get_entity_byte_range(function_node),
                            'docstring': self.get_documentation(function_node, code)
                        }
            
            if function_info:
                result['functions'].append(function_info)
        
        # Extract top-level variables
        variable_query = self.get_query(self.VARIABLE_QUERY)
        for match in variable_query.matches(tree.root_node):
            variable_name = None
            variable_value = None
            variable_node = None
            
            # Extract variable details - implementation will vary by language
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "variable.name" and len(capture_nodes) > 0:
                    # This example assumes the variable name is a simple identifier
                    # For more complex patterns, additional logic would be needed
                    if capture_nodes[0].type == 'identifier':
                        variable_name = capture_nodes[0].text.decode('utf8')
                        variable_node = capture_nodes[0].parent.parent  # Adjust based on language
                        
                        # Only process top-level variables - check will vary by language
                        if variable_node.parent != tree.root_node:
                            variable_name = None
                            continue
                            
                        # Skip private variables
                        if not self.is_public(variable_name):
                            variable_name = None
                            continue
                
                elif capture_id == "variable.value" and len(capture_nodes) > 0:
                    variable_value = self.get_node_text(capture_nodes[0], code)
            
            if variable_name and variable_node:
                result['variables'].append({
                    'name': variable_name,
                    'value': variable_value,
                    'line_range': self.get_entity_range(variable_node),
                    'byte_range': self.get_entity_byte_range(variable_node)
                })
        
        return result
    
    def is_public(self, name: str) -> bool:
        """Check if an entity name indicates a public item.
        
        Different languages have different conventions for marking entities as private:
        - Python: Leading underscore (_variable)
        - JavaScript: No strict convention, but often underscore or hash (_variable, #variable)
        - Java: 'private' keyword (but we'd check node attributes, not the name)
        - Ruby: Leading @ sign for instance variables
        
        This method should implement the appropriate convention for your language.
        
        Args:
            name: The name to check.
            
        Returns:
            True if the name indicates a public entity, False otherwise.
        """
        # STEP 9: Implement public entity detection
        # This should follow language-specific conventions
        
        # Example implementation for JavaScript
        # return not name.startswith('_') and not name.startswith('#')
        
        # Example implementation for Python
        # return not name.startswith('_')
        
        # Example implementation for Java - this would need to be combined with checking modifiers
        # return True  # In Java, we'd check the 'private' keyword, not the name
        
        # Default implementation - works for many languages
        return False # not name.startswith('_')


# IMPLEMENTATION NOTES
# ===================
#
# To implement support for a new language:
#
# 1. Create a new file named after your language (e.g., ruby.py)
# 2. Copy this template into that file
# 3. Rename the class to match your language (e.g., RubyLanguage)
# 4. Implement all required methods following the guidance in each section
# 5. Define language-specific queries for extracting entities
# 6. Register your language in `code_explorer.py` and add language detection in `parser_manager.py`
#
# Development Tips:
# - Use `tree.root_node.sexp()` to explore the structure of your language's AST
# - Start with simple queries and gradually add complexity
# - Refer to the Python and JavaScript implementations for examples
# - Test your implementation with a variety of code examples
# - Consider writing a simple script to explore your language's tree-sitter nodes
#
# For detailed guidance, see the language support guide in the documentation.