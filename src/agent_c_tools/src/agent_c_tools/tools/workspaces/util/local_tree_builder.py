import os
import fnmatch
from typing import List, Optional, Tuple


class LocalPathTreeGenerator:
    """
    A utility class for generating directory structure trees with configurable depth limits.

    This class helps create readable directory structure trees with options to:
    1. Limit the maximum depth of directory traversal
    2. Set a separate depth limit for displaying files
    3. Indicate when depth limits have been reached
    """

    DEFAULT_IGNORE_PATTERNS = [
        ".git", "__pycache__", "*.pyc", "*.pyo",
        "*.pyd", ".DS_Store", "*.so", "*.dylib", "*.dll"
    ]

    def __init__(self, ignore_patterns: Optional[List[str]] = None):
        """
        Initialize the LocalPathTreeGenerator with configurable ignore patterns.

        Args:
            ignore_patterns: List of patterns to ignore (glob patterns like "*.pyc")
        """
        self.ignore_patterns = ignore_patterns or self.DEFAULT_IGNORE_PATTERNS

    def generate_tree(
            self,
            start_path: str,
            max_depth: Optional[int] = None,
            max_files_depth: Optional[int] = None
    ) -> List[str]:
        """
        Generate a directory structure tree starting from the given path.

        Args:
            start_path: The root directory to start generating the tree from
            max_depth: Maximum depth to traverse directories (None for unlimited)
            max_files_depth: Maximum depth at which to show files (None for unlimited)

        Returns:
            A list of strings representing the recursive directory structure
        """
        # If max_files_depth is not specified, use the same value as max_depth
        if max_files_depth is None and max_depth is not None:
            max_files_depth = max_depth

        return self._generate_tree_recursive(
            start_path,
            prefix="",
            current_depth=0,
            max_depth=max_depth,
            max_files_depth=max_files_depth
        )

    def _generate_tree_recursive(
            self,
            path: str,
            prefix: str,
            current_depth: int,
            max_depth: Optional[int],
            max_files_depth: Optional[int]
    ) -> List[str]:
        """
        Recursively generate the tree structure.

        Args:
            path: The current directory path
            prefix: String prefix used for visual alignment
            current_depth: Current recursion depth
            max_depth: Maximum directory traversal depth
            max_files_depth: Maximum depth for showing files

        Returns:
            List of strings representing the directory structure at this level
        """
        tree_structure: List[str] = []

        # Check if we've reached max depth
        if max_depth is not None and current_depth >= max_depth:
            # Add placeholder to indicate there's more content
            tree_structure.append(f"{prefix}└── ...")
            return tree_structure

        try:
            contents = os.listdir(path)
            contents.sort()

            # Filter out ignored patterns
            filtered_contents = [
                name for name in contents
                if not any(fnmatch.fnmatch(name, pattern) for pattern in self.ignore_patterns)
            ]

            # Split into directories and files
            dirs_and_files = []
            for name in filtered_contents:
                item_path = os.path.join(path, name)
                is_dir = os.path.isdir(item_path)

                # Only include files if we haven't reached max_files_depth
                if is_dir or max_files_depth is None or current_depth < max_files_depth:
                    dirs_and_files.append((name, is_dir))

            for index, (name, is_dir) in enumerate(dirs_and_files):
                item_path = os.path.join(path, name)
                is_last_item = (index == len(dirs_and_files) - 1)

                # Choose the appropriate connector
                connector = "└── " if is_last_item else "├── "

                # Add current file/folder to the structure
                tree_structure.append(f"{prefix}{connector}{name}")

                # Recursively process directories
                if is_dir:
                    # Calculate the extension for the next level
                    extension = "    " if is_last_item else "│   "

                    # Recursively generate sub-tree
                    subtree = self._generate_tree_recursive(
                        item_path,
                        prefix + extension,
                        current_depth + 1,
                        max_depth,
                        max_files_depth
                    )
                    tree_structure.extend(subtree)

        except (PermissionError, FileNotFoundError) as e:
            # Handle permission errors or deleted directories gracefully
            tree_structure.append(f"{prefix}└── [Error: {str(e)}]")

        return tree_structure