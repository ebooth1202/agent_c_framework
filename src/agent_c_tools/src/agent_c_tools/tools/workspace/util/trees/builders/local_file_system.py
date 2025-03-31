import os
import fnmatch
from typing import List, Optional, Union

from agent_c_tools.tools.workspace.util.trees.builders.base import TreeBuilder
from agent_c_tools.tools.workspace.util.trees.models import DirectoryTree, TreeNode


class LocalFileSystemTreeBuilder(TreeBuilder):
    """
    Tree builder implementation for the local file system.

    Builds a DirectoryTree model by traversing the local file system.
    """


    @classmethod
    def load_agent_c_ignore_patterns(cls) -> List[str]:
        ignore_path = os.environ.get("AGENT_C_IGNOREFILE", ".agentcignore")
        if os.path.exists(ignore_path):
            with open(ignore_path, "r") as f:
                content = f.read()
                return cls.parse_ignore_file_content(content)

        DEFAULT_IGNORE_PATTERNS = [
            ".git", "__pycache__", "*.pyc", "*.pyo",
            "*.pyd", ".DS_Store", "*.so", "*.dylib", "*.dll",
            ".venv"
        ]
        return DEFAULT_IGNORE_PATTERNS

    def __init__(self, ignore_patterns: Optional[Union[List[str], str]] = None):
        """
        Initialize the LocalFileSystemTreeBuilder with configurable ignore patterns.

        Args:
            ignore_patterns: Patterns to ignore, either as:
                - A list of glob patterns (e.g., ["*.pyc", ".git/"])
                - A string in .gitignore format
                - None to use defaults
        """
        self.ignore_patterns = self.__class__.load_agent_c_ignore_patterns()

        # Process ignore patterns if provided
        if ignore_patterns is not None:
            if isinstance(ignore_patterns, list):
                # Add list of patterns directly
                self.ignore_patterns.extend(ignore_patterns)
            elif isinstance(ignore_patterns, str):
                # Parse string as .gitignore format
                parsed_patterns = self.__class__.parse_ignore_file_content(ignore_patterns)
                self.ignore_patterns.extend(parsed_patterns)
            else:
                raise TypeError("ignore_patterns must be a list of strings or a string in .gitignore format")

    def build_tree(self,
                   start_path: str,
                   ignore_patterns: Optional[Union[List[str], str]] = None,
                   root_name: Optional[str] = None) -> DirectoryTree:
        """
        Build a directory tree structure from the given start path.

        Args:
            start_path: The root path to start building the tree from
            ignore_patterns: Additional patterns to ignore for this specific call
            root_name: Optional name for the root node

        Returns:
            DirectoryTree representing the directory structure
        """
        # Create a local copy of ignore patterns for this call
        local_ignore_patterns = self.ignore_patterns.copy()

        # Add any call-specific patterns
        if ignore_patterns is not None:
            if isinstance(ignore_patterns, list):
                local_ignore_patterns.extend(ignore_patterns)
            elif isinstance(ignore_patterns, str):
                additional_patterns = self.parse_ignore_file_content(ignore_patterns)
                local_ignore_patterns.extend(additional_patterns)
            else:
                raise TypeError("ignore_patterns must be a list of strings or a string in .gitignore format")

        # Create the root node using the start path's basename
        if root_name is None:
            root_name = os.path.basename(os.path.abspath(start_path))
            if not root_name:  # Handle case for root directory
                root_name = start_path

        root_node = TreeNode(name=root_name, is_dir=True)

        # Build the tree recursively
        self._build_tree_recursive(
            path=start_path,
            node=root_node,
            start_path=start_path,
            local_ignore_patterns=local_ignore_patterns
        )

        # Create and return the DirectoryTree with metadata
        metadata = {
            "builder": "LocalFileSystemTreeBuilder",
            "start_path": os.path.abspath(start_path),
            "ignore_patterns": local_ignore_patterns
        }

        return DirectoryTree(root=root_node, metadata=metadata)

    def _should_ignore(self, name: str, rel_path: str, is_dir: bool, patterns: List[str]) -> bool:
        """
        Check if a file or directory should be ignored.

        Args:
            name: The name of the file or directory
            rel_path: The relative path from the start path
            is_dir: Whether the item is a directory
            patterns: List of ignore patterns to check against

        Returns:
            True if the item should be ignored, False otherwise
        """
        for pattern in patterns:
            # Check for exact matches and glob pattern matches
            if (fnmatch.fnmatch(name, pattern) or
                    fnmatch.fnmatch(rel_path, pattern) or
                    fnmatch.fnmatch(rel_path, f"{pattern}/**") or
                    (is_dir and fnmatch.fnmatch(f"{rel_path}/", f"{pattern}/"))):
                return True

        return False

    def _build_tree_recursive(self,
                              path: str,
                              node: TreeNode,
                              start_path: str,
                              local_ignore_patterns: List[str]) -> None:
        """
        Recursively build the tree structure.

        Args:
            path: The current directory path
            node: The current node to populate with children
            start_path: The original starting path
            local_ignore_patterns: List of ignore patterns to apply
        """
        try:
            contents = os.listdir(path)
            contents.sort()

            # Process each item in the directory
            for name in contents:
                # Get the full path and check if it should be ignored
                full_path = os.path.join(path, name)
                rel_path = os.path.relpath(full_path, start_path)
                is_dir = os.path.isdir(full_path)

                # Skip if matches any ignore pattern
                if self._should_ignore(name, rel_path, is_dir, local_ignore_patterns):
                    continue

                # Create a new node for this item
                child_node = TreeNode(name=name, is_dir=is_dir)
                node.add_child(child_node)

                # Recursively process if it's a directory
                if is_dir:
                    self._build_tree_recursive(
                        path=full_path,
                        node=child_node,
                        start_path=start_path,
                        local_ignore_patterns=local_ignore_patterns
                    )

        except (PermissionError, FileNotFoundError) as e:
            # Add an error node to indicate there was a problem
            error_node = TreeNode(name=f"[Error: {str(e)}]", is_dir=False)
            node.add_child(error_node)