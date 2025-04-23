"""C# language support for tree-sitter code exploration.

This module provides C#-specific functionality for parsing and
extracting information from C# code using tree-sitter.
"""

from typing import Dict, List, Optional, Any, Tuple, Set

from tree_sitter import Node, Tree, Parser

from ts_tool.languages.base import BaseLanguage


class CSharpLanguage(BaseLanguage):
    """C# language support for code exploration.
    
    This class provides C#-specific functionality for parsing and
    extracting information from C# code using tree-sitter.
    """
    
    # Query for finding classes, interfaces, structs, and enums
    CLASS_QUERY = """
    (class_declaration
      name: (identifier) @class.name
      body: (declaration_list) @class.body)
    
    (interface_declaration
      name: (identifier) @interface.name
      body: (declaration_list) @interface.body)
    
    (struct_declaration
      name: (identifier) @struct.name
      body: (declaration_list) @struct.body)
      
    (enum_declaration
      name: (identifier) @enum.name
      body: (enum_member_declaration_list) @enum.body)
    """
    
    # Query for finding methods, properties, and constructors
    FUNCTION_QUERY = """
    (method_declaration
      name: (identifier) @method.name
      parameters: (parameter_list) @method.params
      body: (block) @method.body)
    
    (constructor_declaration
      name: (identifier) @constructor.name
      parameters: (parameter_list) @constructor.params
      body: (block) @constructor.body)
      
    (property_declaration
      name: (identifier) @property.name
      body: (accessor_list)? @property.body)
      
    (property_declaration
      name: (identifier) @property.name
      body: (arrow_expression_clause)? @property.body)
      
    (indexer_declaration
      (bracketed_parameter_list) @indexer.params
      (accessor_list) @indexer.body)
    """

    # Query for finding variables, fields, and constants
    VARIABLE_QUERY = """
    (field_declaration
      (variable_declaration
        (variable_declarator
          name: (identifier) @field.name
          value: (_)? @field.value)))

    (variable_declaration
      (variable_declarator
        name: (identifier) @variable.name
        value: (_)? @variable.value))

    (field_declaration
      (modifier) @modifier
      (#eq? @modifier "const")
      (variable_declaration
        (variable_declarator
          name: (identifier) @constant.name
          value: (_)? @constant.value)))
    """
    
    # Query for finding using directives (imports)
    IMPORT_QUERY = """
    (using_directive) @using
    """
    
    # Query for finding comments and XML documentation
    DOCSTRING_QUERY = """
    (comment) @comment
    """
    
    # Query for finding namespaces
    NAMESPACE_QUERY = """
    (namespace_declaration
      name: (_) @namespace.name
      body: (declaration_list) @namespace.body)
    """
    
    # C# access modifiers to check for public entities
    PUBLIC_MODIFIERS = ["public"]
    
    @property
    def language_name(self) -> str:
        """The name of the language."""
        return "c_sharp"
    
    def parse(self, code: str) -> Tree:
        """Parse the given C# code string.
        
        Args:
            code: The C# source code to parse.
            
        Returns:
            The parsed syntax tree.
        """
        return self.parser.parse(bytes(code, 'utf8'))
    
    def get_entity_names(self, tree: Tree) -> Dict[str, List[str]]:
        """Get all named entities from the C# syntax tree.
        
        Args:
            tree: The parsed syntax tree.
            
        Returns:
            A dictionary with entity types as keys and lists of entity names as values.
        """
        result = {
            'classes': [],
            'interfaces': [],
            'structs': [],
            'enums': [],
            'functions': [],
            'methods': [],
            'properties': [],
            'variables': []
        }
        # Extract class, interface, struct, and enum names
        class_query = self.get_query(self.CLASS_QUERY)
        for match in class_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "class.name":
                    class_name = capture_nodes[0].text.decode('utf8')
                    if self._is_public_entity(capture_nodes[0].parent, tree):
                        result['classes'].append(class_name)
                elif capture_id == "interface.name":
                    interface_name = capture_nodes[0].text.decode('utf8')
                    if self._is_public_entity(capture_nodes[0].parent, tree):
                        result['interfaces'].append(interface_name)
                elif capture_id == "struct.name":
                    struct_name = capture_nodes[0].text.decode('utf8')
                    if self._is_public_entity(capture_nodes[0].parent, tree):
                        result['structs'].append(struct_name)
                elif capture_id == "enum.name":
                    enum_name = capture_nodes[0].text.decode('utf8')
                    if self._is_public_entity(capture_nodes[0].parent, tree):
                        result['enums'].append(enum_name)
        
        # Extract method, property names
        function_query = self.get_query(self.FUNCTION_QUERY)
        for match in function_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "method.name":
                    node = capture_nodes[0]
                    method_name = node.text.decode('utf8')
                    # Check if it's a top-level method (not in a class)
                    if node.parent.parent.parent == tree.root_node and self._is_public_entity(node.parent):
                        result['functions'].append(method_name)
                    else:
                        # It's a class method, track it separately
                        if self._is_public_entity(node.parent):
                            result['methods'].append(method_name)
                elif capture_id == "property.name":
                    node = capture_nodes[0]
                    property_name = node.text.decode('utf8')
                    if self._is_public_entity(node.parent):
                        result['properties'].append(property_name)
        
        # Extract variable names
        variable_query = self.get_query(self.VARIABLE_QUERY)
        for match in variable_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id in ["variable.name", "field.name", "constant.name"]:
                    node = capture_nodes[0]
                    var_name = node.text.decode('utf8')
                    if self._is_public_entity(node.parent.parent.parent):
                        result['variables'].append(var_name)
        
        return result

    def get_entity_node(self, tree: Tree, entity_type: str, entity_name: str) -> Optional[Node]:
        """Get the syntax node for a specific named entity.
        
        Args:
            tree: The parsed syntax tree.
            entity_type: The type of entity to find ('class', 'function', etc.).
            entity_name: The name of the entity to find.
            
        Returns:
            The syntax node for the entity, or None if not found.
        """
        return self.find_entity(tree, entity_type, entity_name)
        
    def find_entity(self, tree: Tree, entity_type: str, entity_name: str) -> Optional[Node]:
        """Find a specific entity in the C# syntax tree.
        
        Args:
            tree: The parsed syntax tree.
            entity_type: The type of entity to find ('class', 'function', etc.).
            entity_name: The name of the entity to find.
            
        Returns:
            The tree-sitter node for the entity, or None if not found.
        """
        if entity_type == 'class':
            class_query = self.get_query(self.CLASS_QUERY)
            for match in class_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "class.name" and capture_nodes[0].text.decode('utf8') == entity_name:
                        # Return the class_definition node (parent of the name node)
                        return capture_nodes[0].parent
        
        elif entity_type == 'interface':
            class_query = self.get_query(self.CLASS_QUERY)
            for match in class_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "interface.name" and capture_nodes[0].text.decode('utf8') == entity_name:
                        # Return the interface_definition node (parent of the name node)
                        return capture_nodes[0].parent
        
        elif entity_type == 'struct':
            class_query = self.get_query(self.CLASS_QUERY)
            for match in class_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "struct.name" and capture_nodes[0].text.decode('utf8') == entity_name:
                        # Return the struct_definition node (parent of the name node)
                        return capture_nodes[0].parent
                
        elif entity_type == 'enum':
            class_query = self.get_query(self.CLASS_QUERY)
            for match in class_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "enum.name" and capture_nodes[0].text.decode('utf8') == entity_name:
                        # Return the enum_definition node (parent of the name node)
                        return capture_nodes[0].parent
        
        elif entity_type == 'function':
            function_query = self.get_query(self.FUNCTION_QUERY)
            for match in function_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if (capture_id == "method.name" and 
                        capture_nodes[0].text.decode('utf8') == entity_name and
                        capture_nodes[0].parent.parent.parent == tree.root_node):
                        # Return the function_definition node (parent of the name node)
                        return capture_nodes[0].parent
        
        elif entity_type == 'method':
            # For methods, we need to handle the format 'ClassName.method_name'
            if '.' in entity_name:
                class_name, method_name = entity_name.split('.', 1)
                class_node = self.find_entity(tree, 'class', class_name)
                if class_node:
                    body_node = None
                    for child in class_node.children:
                        if child.type == 'declaration_list':
                            body_node = child
                            break
                    
                    if body_node:
                        function_query = self.get_query(self.FUNCTION_QUERY)
                        for match in function_query.matches(body_node):
                            for capture_id, capture_nodes in match[1].items():
                                if (capture_id == "method.name" and 
                                    capture_nodes[0].text.decode('utf8') == method_name):
                                    return capture_nodes[0].parent
        
        elif entity_type == 'property':
            function_query = self.get_query(self.FUNCTION_QUERY)
            for match in function_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if capture_id == "property.name" and capture_nodes[0].text.decode('utf8') == entity_name:
                        return capture_nodes[0].parent
        
        elif entity_type == 'variable' or entity_type == 'field' or entity_type == 'constant':
            variable_query = self.get_query(self.VARIABLE_QUERY)
            for match in variable_query.matches(tree.root_node):
                for capture_id, capture_nodes in match[1].items():
                    if ((capture_id == "variable.name" or 
                         capture_id == "field.name" or 
                         capture_id == "constant.name") and 
                        capture_nodes[0].text.decode('utf8') == entity_name):
                        # Return the variable declaration node
                        return capture_nodes[0].parent.parent.parent
        
        return None
    
    def get_module_docstring(self, tree: Tree, code: str) -> Optional[str]:
        """Extract the module-level docstring from a C# file.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            The module docstring, or None if not found.
        """
        doc_query = self.get_query(self.DOCSTRING_QUERY)
        
        # Find the first documentation comment or normal comment
        xml_doc_comments = []
        first_comment = None
        
        for match in doc_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "comment":
                    node = capture_nodes[0]
                    # Check if it's at the beginning of the file
                    if node.start_point[0] < 5:  # Within first 5 lines
                        comment_text = self.get_node_text(node, code)
                        # Check if it's an XML documentation comment (starts with ///)
                        if comment_text.strip().startswith("///"):
                            xml_doc_comments.append((node.start_point[0], comment_text))
                        # If we haven't found a regular comment yet, store this one
                        elif first_comment is None:
                            first_comment = node
        
        # Prefer XML documentation over normal comments
        if xml_doc_comments:
            # Sort by line number to ensure correct order
            xml_doc_comments.sort(key=lambda x: x[0])
            combined_doc = "\n".join([text for _, text in xml_doc_comments])
            return self._clean_xml_documentation(combined_doc)
        elif first_comment:
            return self._clean_comment_documentation(self.get_node_text(first_comment, code))
        
        return None
    
    def get_documentation(self, node: Node, code: str, tree: Tree = None) -> Optional[str]:
        """Extract documentation for a specific node.
        
        Args:
            node: The node to extract documentation for.
            code: The original source code.
            tree: The parsed syntax tree (required in tree-sitter >= 0.20.1).
            
        Returns:
            The documentation for the node, or None if not found.
        """
        start_line = node.start_point[0]
        
        # Search for comments above the node that might be XML documentation
        xml_doc_comments = []
        doc_query = self.get_query(self.DOCSTRING_QUERY)
        
        # In tree-sitter >= 0.20.1, Node objects don't have a 'tree' attribute
        # We need to use the root_node from the provided tree
        root_node = tree.root_node if tree else None
        if root_node is None:
            # If no tree was provided, we can't continue
            return None
            
        # Find all comments
        for match in doc_query.matches(root_node):
            for capture_id, capture_nodes in list(match[1].items()):
                if capture_id == "comment":
                    comment_node = capture_nodes[0]
                    comment_end_line = comment_node.end_point[0]
                    comment_text = self.get_node_text(comment_node, code)
                    
                    # Check if this comment is just before our node
                    if comment_end_line < start_line and comment_end_line >= start_line - 5:
                        # Check if it's an XML documentation comment (starts with ///)
                        if comment_text.strip().startswith("///"):
                            xml_doc_comments.append((comment_end_line, comment_text))
                        # Regular comment that's immediately before the node
                        elif comment_end_line == start_line - 1:
                            return self._clean_comment_documentation(comment_text)
        
        # If we found XML doc comments, combine them and return
        if xml_doc_comments:
            # Sort by line number to ensure correct order
            xml_doc_comments.sort(key=lambda x: x[0])
            combined_doc = "\n".join([text for _, text in xml_doc_comments])
            return self._clean_xml_documentation(combined_doc)
        
        return None
    
    def get_imports(self, tree: Tree, code: str) -> List[str]:
        """Extract import statements from a C# file.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            A list of import statements.
        """
        imports = []
        import_query = self.get_query(self.IMPORT_QUERY)
        
        for match in import_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "using":
                    imports.append(self.get_node_text(capture_nodes[0], code))
        
        return imports
    
    def get_public_interface(self, tree: Tree, code: str) -> Dict[str, Any]:
        """Extract the public interface from a C# syntax tree.
        
        Args:
            tree: The parsed syntax tree.
            code: The original source code.
            
        Returns:
            A dictionary representing the public interface.
        """
        result = {
            'classes': [],
            'interfaces': [],
            'structs': [],
            'enums': [],
            'functions': [],
            'variables': [],
            'namespaces': []
        }
        
        # Extract namespaces first
        namespace_query = self.get_query(self.NAMESPACE_QUERY)
        for match in namespace_query.matches(tree.root_node):
            namespace_info = {}
            namespace_node = None
            namespace_name = None
            
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "namespace.name":
                    namespace_name = self.get_node_text(capture_nodes[0], code)
                    namespace_node = capture_nodes[0].parent
                    namespace_info = {
                        'name': namespace_name,
                        'classes': [],
                        'interfaces': [],
                        'structs': [],
                        'enums': [],
                        'line_range': self.get_entity_range(namespace_node),
                        'byte_range': self.get_entity_byte_range(namespace_node),
                        'docstring': self.get_documentation(namespace_node, code, tree)
                    }
            
            if namespace_node and namespace_info:
                result['namespaces'].append(namespace_info)
        
        # Extract classes and their members
        class_query = self.get_query(self.CLASS_QUERY)
        for match in class_query.matches(tree.root_node):
            class_info = {}
            class_node = None
            class_name = None
            entity_type = None
            
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "class.name":
                    class_name = capture_nodes[0].text.decode('utf8')
                    if not self._is_public_entity(capture_nodes[0].parent, tree):
                        continue
                        
                    class_node = capture_nodes[0].parent
                    entity_type = 'classes'
                    class_info = {
                        'name': class_name,
                        'type': 'class',
                        'methods': [],
                        'properties': [],
                        'fields': [],
                        'line_range': self.get_entity_range(class_node),
                        'byte_range': self.get_entity_byte_range(class_node),
                        'docstring': self.get_documentation(class_node, code, tree)
                    }
                elif capture_id == "interface.name":
                    class_name = capture_nodes[0].text.decode('utf8')
                    if not self._is_public_entity(capture_nodes[0].parent, tree):
                        continue
                        
                    class_node = capture_nodes[0].parent
                    entity_type = 'interfaces'
                    class_info = {
                        'name': class_name,
                        'type': 'interface',
                        'methods': [],
                        'properties': [],
                        'line_range': self.get_entity_range(class_node),
                        'byte_range': self.get_entity_byte_range(class_node),
                        'docstring': self.get_documentation(class_node, code, tree)
                    }
                elif capture_id == "struct.name":
                    class_name = capture_nodes[0].text.decode('utf8')
                    if not self._is_public_entity(capture_nodes[0].parent, tree):
                        continue
                        
                    class_node = capture_nodes[0].parent
                    entity_type = 'structs'
                    class_info = {
                        'name': class_name,
                        'type': 'struct',
                        'methods': [],
                        'properties': [],
                        'fields': [],
                        'line_range': self.get_entity_range(class_node),
                        'byte_range': self.get_entity_byte_range(class_node),
                        'docstring': self.get_documentation(class_node, code, tree)
                    }
                elif capture_id == "enum.name":
                    class_name = capture_nodes[0].text.decode('utf8')
                    if not self._is_public_entity(capture_nodes[0].parent, tree):
                        continue
                        
                    class_node = capture_nodes[0].parent
                    entity_type = 'enums'
                    class_info = {
                        'name': class_name,
                        'type': 'enum',
                        'members': [],
                        'line_range': self.get_entity_range(class_node),
                        'byte_range': self.get_entity_byte_range(class_node),
                        'docstring': self.get_documentation(class_node, code, tree)
                    }
            
            # If we found a valid class, extract its methods and properties
            if class_node and class_info:
                body_node = None
                for child in class_node.children:
                    if child.type in ['declaration_list', 'enum_member_declaration_list']:
                        body_node = child
                        break
                        
                if body_node:
                    # Get methods and properties
                    function_query = self.get_query(self.FUNCTION_QUERY)
                    for method_match in function_query.matches(body_node):
                        method_info = {}
                        
                        for method_capture_id, method_capture_nodes in method_match[1].items():
                            if method_capture_id == "method.name":
                                method_node = method_capture_nodes[0]
                                method_name = method_node.text.decode('utf8')
                                method_def_node = method_node.parent
                                
                                if not self._is_public_entity(method_def_node, tree):
                                    continue
                                
                                # Get parameters for method signature
                                params_node = None
                                for child in method_def_node.children:
                                    if child.type == 'parameter_list':
                                        params_node = child
                                        break
                                        
                                params_text = self.get_node_text(params_node, code) if params_node else "()"
                                
                                method_info = {
                                    'name': method_name,
                                    'signature': f"{method_name}{params_text}",
                                    'line_range': self.get_entity_range(method_def_node),
                                    'byte_range': self.get_entity_byte_range(method_def_node),
                                    'docstring': self.get_documentation(method_def_node, code, tree)
                                }
                                
                                class_info['methods'].append(method_info)
                            
                            elif method_capture_id == "property.name":
                                property_node = method_capture_nodes[0]
                                property_name = property_node.text.decode('utf8')
                                property_def_node = property_node.parent
                                
                                if not self._is_public_entity(property_def_node, tree):
                                    continue
                                
                                # Get property type
                                property_type = ""
                                for child in property_def_node.children:
                                    if child.type == 'predefined_type' or child.type == 'identifier':
                                        property_type = self.get_node_text(child, code)
                                        break
                                
                                property_info = {
                                    'name': property_name,
                                    'type': property_type,
                                    'line_range': self.get_entity_range(property_def_node),
                                    'byte_range': self.get_entity_byte_range(property_def_node),
                                    'docstring': self.get_documentation(property_def_node, code, tree)
                                }
                                
                                class_info['properties'].append(property_info)
                    
                    # Get fields and constants
                    if entity_type in ['classes', 'structs']:
                        variable_query = self.get_query(self.VARIABLE_QUERY)
                        for var_match in variable_query.matches(body_node):
                            field_info = {}
                            
                            for var_capture_id, var_capture_nodes in var_match[1].items():
                                if var_capture_id in ["field.name", "constant.name"]:
                                    var_node = var_capture_nodes[0]
                                    field_name = var_node.text.decode('utf8')
                                    field_def_node = var_node.parent.parent.parent
                                    
                                    if not self._is_public_entity(field_def_node, tree):
                                        continue
                                    
                                    # Get field type
                                    field_type = ""
                                    for child in field_def_node.children:
                                        if child.type == 'variable_declaration':
                                            for vd_child in child.children:
                                                if vd_child.type == 'predefined_type' or vd_child.type == 'identifier':
                                                    field_type = self.get_node_text(vd_child, code)
                                                    break
                                            break
                                    
                                    field_info = {
                                        'name': field_name,
                                        'type': field_type,
                                        'line_range': self.get_entity_range(field_def_node),
                                        'byte_range': self.get_entity_byte_range(field_def_node),
                                        'docstring': self.get_documentation(field_def_node, code, tree)
                                    }
                                    
                                    class_info['fields'].append(field_info)
                    
                    # Get enum members
                    if entity_type == 'enums':
                        for child in body_node.children:
                            if child.type == 'enum_member_declaration':
                                name_node = None
                                for member_child in child.children:
                                    if member_child.type == 'identifier':
                                        name_node = member_child
                                        break
                                
                                if name_node:
                                    member_name = name_node.text.decode('utf8')
                                    member_info = {
                                        'name': member_name,
                                        'line_range': self.get_entity_range(child),
                                        'byte_range': self.get_entity_byte_range(child),
                                        'docstring': self.get_documentation(child, code, tree)
                                    }
                                    
                                    class_info['members'].append(member_info)
                
                # Add to the appropriate collection
                result[entity_type].append(class_info)
        
        # Extract standalone functions
        function_query = self.get_query(self.FUNCTION_QUERY)
        for match in function_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id == "method.name":
                    # Check if it's a top-level method
                    node = capture_nodes[0]
                    method_node = node.parent
                    if method_node.parent.parent == tree.root_node and self._is_public_entity(method_node, tree):
                        method_name = node.text.decode('utf8')
                        
                        # Get parameters for function signature
                        params_node = None
                        for child in method_node.children:
                            if child.type == 'parameter_list':
                                params_node = child
                                break
                                
                        params_text = self.get_node_text(params_node, code) if params_node else "()"
                        
                        function_info = {
                            'name': method_name,
                            'signature': f"{method_name}{params_text}",
                            'line_range': self.get_entity_range(method_node),
                            'byte_range': self.get_entity_byte_range(method_node),
                            'docstring': self.get_documentation(method_node, code, tree)
                        }
                        
                        result['functions'].append(function_info)
        
        # Extract top-level variables
        variable_query = self.get_query(self.VARIABLE_QUERY)
        for match in variable_query.matches(tree.root_node):
            for capture_id, capture_nodes in match[1].items():
                if capture_id in ["variable.name", "constant.name"]:
                    node = capture_nodes[0]
                    var_node = node.parent.parent.parent
                    
                    # Only process top-level variables
                    if var_node.parent != tree.root_node:
                        continue
                        
                    if not self._is_public_entity(var_node, tree):
                        continue
                    
                    var_name = node.text.decode('utf8')
                    
                    # Get variable type
                    var_type = ""
                    for child in var_node.children:
                        if child.type == 'variable_declaration':
                            for vd_child in child.children:
                                if vd_child.type == 'predefined_type' or vd_child.type == 'identifier':
                                    var_type = self.get_node_text(vd_child, code)
                                    break
                            break
                    
                    result['variables'].append({
                        'name': var_name,
                        'type': var_type,
                        'line_range': self.get_entity_range(var_node),
                        'byte_range': self.get_entity_byte_range(var_node),
                        'docstring': self.get_documentation(var_node, code, tree)
                    })
        
        return result
    
    def _is_public_entity(self, node: Node, tree: Tree = None) -> bool:
        """Check if an entity is public.
        
        Args:
            node: The entity node to check.
            tree: The parsed syntax tree (required in tree-sitter >= 0.20.1).
            
        Returns:
            True if the entity is public, False otherwise.
        """
        parent = node.parent
        
        # Check modifiers
        for child in node.children:
            if child.type == 'modifier':
                modifier = child.text.decode('utf8')
                if modifier in self.PUBLIC_MODIFIERS:
                    return True
        
        # Interface members are public by default
        if parent and parent.type == 'declaration_list':
            grandparent = parent.parent
            if grandparent and grandparent.type == 'interface_declaration':
                # Members of interfaces are public by default
                return True
        
        # For namespace-level entities, they're internal by default
        # In tree-sitter >= 0.20.1, we need to compare with tree.root_node instead of node.tree.root_node
        root_node = tree.root_node if tree else None
        if root_node and parent == root_node:
            # Root level entities are internal by default in C#
            for child in node.children:
                if child.type == 'modifier' and child.text.decode('utf8') == 'public':
                    return True
            return False
            
        # We need more context to determine this properly
        # For simplicity in this implementation, assume class members are not public unless explicitly marked
        has_any_modifier = False
        for child in node.children:
            if child.type == 'modifier':
                has_any_modifier = True
                break
        
        # If it has no modifiers and is in a class, it's private by default
        if not has_any_modifier and parent and parent.type == 'declaration_list':
            return False
            
        # Default to returning true if we can't determine otherwise
        return True
    
    def _clean_xml_documentation(self, doc_text: str) -> str:
        """Clean XML documentation comments.
        
        Args:
            doc_text: The raw documentation text.
            
        Returns:
            The cleaned documentation text.
        """
        if not doc_text:
            return ""
            
        # Remove the XML comment markers
        lines = doc_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Remove /// prefix
            if line.startswith('///'):
                line = line[3:].strip()
            # Remove /** and */ markers
            elif line.startswith('/**'):
                line = line[3:].strip()
            elif line.endswith('*/'):
                line = line[:-2].strip()
            # Remove * prefix from each line in block comments
            elif line.startswith('*'):
                line = line[1:].strip()
                
            cleaned_lines.append(line)
        
        # Remove empty lines from beginning and end
        while cleaned_lines and not cleaned_lines[0]:
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)
    
    def _clean_comment_documentation(self, doc_text: str) -> str:
        """Clean regular comment documentation.
        
        Args:
            doc_text: The raw comment text.
            
        Returns:
            The cleaned comment text.
        """
        if not doc_text:
            return ""
            
        # Remove the comment markers
        lines = doc_text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            # Remove // prefix from each line
            if line.startswith('//'):
                line = line[2:].strip()
            # Remove /* and */ markers
            elif line.startswith('/*'):
                line = line[2:].strip()
            elif line.endswith('*/'):
                line = line[:-2].strip()
            # Remove * prefix from each line in block comments
            elif line.startswith('*'):
                line = line[1:].strip()
                
            cleaned_lines.append(line)
        
        # Remove empty lines from beginning and end
        while cleaned_lines and not cleaned_lines[0]:
            cleaned_lines.pop(0)
        while cleaned_lines and not cleaned_lines[-1]:
            cleaned_lines.pop()
            
        return '\n'.join(cleaned_lines)