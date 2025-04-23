#!/usr/bin/env python3
"""Tree-Sitter Query Tester

A utility for testing and debugging tree-sitter queries for new language implementations.
This tool allows you to visualize syntax trees and test queries interactively.

Usage:
  python -m ts_tool.utils.query_tester [language_name] [file_path] [query_file]
  python -m ts_tool.utils.query_tester  # For interactive mode

Examples:
  python -m ts_tool.utils.query_tester javascript example.js
  python -m ts_tool.utils.query_tester python example.py queries/function.scm
  python -m ts_tool.utils.query_tester  # Start interactive mode
"""

import argparse
import importlib
import os
import sys
from typing import Dict, List, Optional, Any, Tuple

from tree_sitter import Language, Parser, Tree, Query, Node


class QueryTester:
    """Tool for testing tree-sitter queries.
    
    This class provides functionality for loading languages, parsing code,
    and running queries to visualize the results. It supports both interactive
    and programmatic usage.
    """
    
    def __init__(self, language_name: Optional[str] = None):
        """Initialize the query tester.
        
        Args:
            language_name: Optional name of the language to use (e.g., 'python', 'javascript').
                If not provided, you must call load_language() before parsing code.
        """
        self.parser = None
        self.language = None
        self.language_name = None
        self.tree = None
        self.code = None
        
        if language_name:
            self.load_language(language_name)
    
    def load_language(self, language_name: str) -> bool:
        """Load a tree-sitter language.
        
        Args:
            language_name: The name of the language to load.
            
        Returns:
            True if the language was loaded successfully, False otherwise.
        """
        try:
            # Try to import the language module
            module_name = f"tree_sitter_{language_name}"
            language_module = importlib.import_module(module_name)
            self.language = Language(language_module.language())
            self.parser = Parser(self.language)
            self.language_name = language_name
            return True
        except ImportError:
            print(f"Error: Could not load language '{language_name}'.")
            print(f"Make sure the 'tree_sitter_{language_name}' package is installed.")
            print(f"You can install it with: pip install tree_sitter_{language_name}")
            return False
        except Exception as e:
            print(f"Error loading language '{language_name}': {str(e)}")
            return False
    
    def parse_code(self, code: str) -> bool:
        """Parse code into a syntax tree.
        
        Args:
            code: The code to parse.
            
        Returns:
            True if parsing was successful, False otherwise.
        """
        if not self.parser:
            print("Error: No language loaded. Please load a language first.")
            return False
        
        try:
            self.code = code
            self.tree = self.parser.parse(bytes(code, 'utf8'))
            return True
        except Exception as e:
            print(f"Error parsing code: {str(e)}")
            return False
    
    def parse_file(self, file_path: str) -> bool:
        """Parse code from a file.
        
        Args:
            file_path: The path to the file to parse.
            
        Returns:
            True if parsing was successful, False otherwise.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
            return self.parse_code(code)
        except Exception as e:
            print(f"Error reading file '{file_path}': {str(e)}")
            return False
    
    def run_query(self, query_string: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """Run a query on the parsed code.
        
        Args:
            query_string: The tree-sitter query string.
            
        Returns:
            A tuple of (success, results) where results is a list of
            dictionaries containing match information.
        """
        if not self.tree or not self.language:
            print("Error: No parsed code available. Parse some code first.")
            return False, []
        
        try:
            query = self.language.query(query_string)
            captures = query.captures(self.tree.root_node)
            matches = query.matches(self.tree.root_node)
            
            results = []
            for match_id, match_dict in matches:
                match_info = {}
                for capture_name, nodes in match_dict.items():
                    node_info = []
                    for node in nodes:
                        node_text = self.code[node.start_byte:node.end_byte]
                        node_info.append({
                            'text': node_text,
                            'type': node.type,
                            'start_point': node.start_point,
                            'end_point': node.end_point,
                            'start_byte': node.start_byte,
                            'end_byte': node.end_byte,
                        })
                    match_info[capture_name] = node_info
                results.append(match_info)
            
            return True, results
        except Exception as e:
            print(f"Error running query: {str(e)}")
            return False, []
    
    def run_query_from_file(self, query_file: str) -> Tuple[bool, List[Dict[str, Any]]]:
        """Run a query from a file.
        
        Args:
            query_file: The path to the query file.
            
        Returns:
            A tuple of (success, results) where results is a list of
            dictionaries containing match information.
        """
        try:
            with open(query_file, 'r', encoding='utf-8') as f:
                query_string = f.read()
            return self.run_query(query_string)
        except Exception as e:
            print(f"Error reading query file '{query_file}': {str(e)}")
            return False, []
    
    def print_node(self, node: Node, code: str, indent: int = 0, field_name: Optional[str] = None) -> None:
        """Print a node and its children with indentation.
        
        Args:
            node: The node to print.
            code: The source code.
            indent: The current indentation level.
            field_name: Field name that this node is assigned to in parent.
        """
        # Get node text
        start_byte = node.start_byte
        end_byte = node.end_byte
        text = code[start_byte:end_byte]
        
        # Truncate text if too long
        if len(text) > 50:
            text = text[:47] + "..."
            
        # Replace newlines and tabs for display
        text = text.replace('\n', '\\n').replace('\t', '\\t')
        
        # Print node info
        prefix = " " * indent
        type_str = node.type
        field_str = f" ({field_name})" if field_name else ""
        
        print(f"{prefix}{type_str}{field_str}: '{text}'")
        
        # Print children
        for child_idx, child in enumerate(node.children):
            # Get field name if any
            child_field = None
            for field_idx, field in enumerate(node.fields):
                field_name, field_nodes = field[0], field[1]
                if child_idx in field_nodes:
                    child_field = field_name
                    break
            
            self.print_node(child, code, indent + 2, child_field)
    
    def print_tree(self, node: Optional[Node] = None, indent: int = 0) -> None:
        """Print the syntax tree.
        
        Args:
            node: The node to print. If None, prints the root node.
            indent: The indentation level for pretty printing.
        """
        if not self.tree:
            print("Error: No parsed code available. Parse some code first.")
            return
        
        if node is None:
            node = self.tree.root_node

        node_text = self.code[node.start_byte:node.end_byte][:50].replace('\n', '\\n')
        print(f"{' ' * indent}{node.type}: {node_text}")

        # Recursively print children
        for child in node.children:
            self.print_tree(child, indent + 2)
    
    def visualize_results(self, results: List[Dict[str, Any]]) -> None:
        """Visualize query results in a more user-friendly format.
        
        Args:
            results: The query results to visualize.
        """
        if not results:
            print("No matches found.")
            return
        
        print("\n=== MATCHES ===\n")
        for i, match in enumerate(results):
            print(f"Match #{i+1}:")
            for capture_name, nodes in match.items():
                print(f"  {capture_name}:")
                for node in nodes:
                    text = node['text']
                    if isinstance(text, bytes):
                        text = text.decode('utf8')
                    text = text.replace('\n', '\\n')[:50]
                    print(f"    {node['type']} [{node['start_point']} - {node['end_point']}]: {text}")
    
    def test_query(self, query_string: str) -> None:
        """Test a query and visualize the results.
        
        This method combines running a query and visualizing the results.
        
        Args:
            query_string: The tree-sitter query string.
        """
        success, results = self.run_query(query_string)
        if success:
            self.visualize_results(results)
            
            # Also display the captures format for compatibility with old method
            print("\n=== CAPTURES ===\n")
            query = self.language.query(query_string)
            captures = query.captures(self.tree.root_node)
            for node, capture_name in captures:
                node_text = self.code[node.start_byte:node.end_byte]
                if len(node_text) > 50:
                    node_text = node_text[:47] + "..."
                node_text = node_text.replace('\n', '\\n').replace('\t', '\\t')
                print(f"{capture_name}: '{node_text}' ({node.type} at {node.start_point}-{node.end_point})")
        else:
            print("Failed to run query.")
    
    def interactive_mode(self) -> None:
        """Run in interactive mode.
        
        This method provides a command-line interface for testing tree-sitter
        queries interactively.
        """
        print("Tree-sitter Query Tester Interactive Mode")
        print("----------------------------------------")
        
        # Get language if not already loaded
        if not self.language_name:
            language_name = input("Enter language name (e.g., python, javascript): ")
            if not self.load_language(language_name):
                return
        
        # Get code if not already parsed
        if not self.tree:
            print("\nEnter code (end with a line containing only '###'):")
            code_lines = []
            while True:
                line = input()
                if line == "###":
                    break
                code_lines.append(line)
            
            code = "\n".join(code_lines)
            if not self.parse_code(code):
                return
        
        # Main command loop
        print(f"\nTree-Sitter Query Tester - {self.language_name.capitalize()}")
        print("Type 'help' for commands, 'exit' to quit.")
        
        while True:
            try:
                command = input("\n> ").strip()
                
                if command == "exit":
                    break
                elif command == "help":
                    print("\nCommands:")
                    print("  tree             - Print the entire syntax tree")
                    print("  node <path>      - Print a specific node (e.g., 'node 0.1.2')")
                    print("  query            - Enter a multi-line query (end with '###')")
                    print("  load <language>  - Load a different language")
                    print("  parse            - Enter new code to parse")
                    print("  sexp             - Show the S-expression representation of the tree")
                    print("  help             - Show this help message")
                    print("  exit             - Exit the program")
                elif command == "tree":
                    self.print_tree()
                elif command.startswith("node "):
                    path = command[5:].strip()
                    try:
                        node = self.tree.root_node
                        for idx in path.split('.'):
                            node = node.children[int(idx)]
                        self.print_node(node, self.code)
                    except (IndexError, ValueError) as e:
                        print(f"Error: Invalid node path. {str(e)}")
                elif command == "query":
                    print("Enter your query (end with a line containing only '###'):")
                    query_lines = []
                    while True:
                        line = input()
                        if line == "###":
                            break
                        query_lines.append(line)
                    
                    if query_lines:
                        query_string = "\n".join(query_lines)
                        self.test_query(query_string)
                elif command.startswith("load "):
                    language_name = command[5:].strip()
                    if self.load_language(language_name) and self.code:
                        self.parse_code(self.code)
                elif command == "parse":
                    print("\nEnter new code (end with a line containing only '###'):")
                    code_lines = []
                    while True:
                        line = input()
                        if line == "###":
                            break
                        code_lines.append(line)
                    
                    code = "\n".join(code_lines)
                    self.parse_code(code)
                elif command == "sexp":
                    if self.tree:
                        print(self.tree.root_node.sexp())
                else:
                    print("Unknown command. Type 'help' for available commands.")
            
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {str(e)}")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Tree-Sitter Query Tester")
    parser.add_argument("language", nargs="?", help="Language name (e.g., python, javascript)")
    parser.add_argument("file", nargs="?", help="Path to source code file")
    parser.add_argument("query_file", nargs="?", help="File containing tree-sitter query")
    
    args = parser.parse_args()
    tester = QueryTester()
    
    if args.language and args.file:
        # Non-interactive mode with language and file
        if not tester.load_language(args.language):
            return 1
        
        if not tester.parse_file(args.file):
            return 1
        
        if args.query_file:
            # Run a query from file
            success, results = tester.run_query_from_file(args.query_file)
            if not success:
                return 1
            
            print("Query Results:")
            print("--------------")
            tester.visualize_results(results)
        else:
            # Interactive mode with loaded file
            tester.interactive_mode()
    else:
        # Fully interactive mode
        tester.interactive_mode()
    
    return 0


if __name__ == "__main__":
    main()