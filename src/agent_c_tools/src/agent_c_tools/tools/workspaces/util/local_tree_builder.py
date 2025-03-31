import os
import fnmatch
import re
from typing import List, Optional, Tuple, Set, Union


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

    def __init__(self, ignore_patterns: Optional[Union[List[str], str]] = None):
        """
        Initialize the LocalPathTreeGenerator with configurable ignore patterns.

        Args:
            ignore_patterns: Patterns to ignore, either as:
                - A list of glob patterns (e.g., ["*.pyc", ".git/"])
                - A string in .gitignore format
                - None to use defaults
        """
        self.ignore_patterns = self.DEFAULT_IGNORE_PATTERNS.copy()

        # Process ignore patterns if provided
        if ignore_patterns is not None:
            if isinstance(ignore_patterns, list):
                # Add list of patterns directly
                self.ignore_patterns.extend(ignore_patterns)
            elif isinstance(ignore_patterns, str):
                # Parse string as .gitignore format
                parsed_patterns = self._parse_ignore_file_content(ignore_patterns)
                self.ignore_patterns.extend(parsed_patterns)
            else:
                raise TypeError("ignore_patterns must be a list of strings or a string in .gitignore format")

    def _parse_ignore_file_content(self, content: str) -> List[str]:
        """
        Parse .gitignore style content into a list of patterns.

        Args:
            content: String content in .gitignore format

        Returns:
            List of ignore patterns
        """
        patterns = []
        for line in content.splitlines():
            # Skip empty lines and comments
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            # Handle negation (we don't support this yet, but acknowledge it)
            if line.startswith('!'):
                # For now, just skip negation patterns
                continue

            # Handle directory-specific patterns (ending with /)
            if line.endswith('/'):
                # Convert to a pattern that will match the directory name
                line = line.rstrip('/')

            # Add the pattern
            patterns.append(line)

        return patterns

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

    def generate_tree(
            self,
            start_path: str,
            max_depth: Optional[int] = None,
            max_files_depth: Optional[int] = None,
            ignore_patterns: Optional[Union[List[str], str]] = None
    ) -> List[str]:
        """
        Generate a directory structure tree starting from the given path.

        Args:
            start_path: The root directory to start generating the tree from
            max_depth: Maximum depth to traverse directories (None for unlimited)
            max_files_depth: Maximum depth at which to show files (None for unlimited)
            ignore_patterns: Additional patterns to ignore for this specific call, either as:
                - A list of glob patterns (e.g., ["*.pyc", ".git/"])
                - A string in .gitignore format
                - None to use only the patterns from initialization

        Returns:
            A list of strings representing the recursive directory structure
        """
        # If max_files_depth is not specified, use the same value as max_depth
        if max_files_depth is None and max_depth is not None:
            max_files_depth = max_depth

        # Create a local copy of ignore patterns for this call
        local_ignore_patterns = self.ignore_patterns.copy()

        # Add any call-specific patterns
        if ignore_patterns is not None:
            if isinstance(ignore_patterns, list):
                local_ignore_patterns.extend(ignore_patterns)
            elif isinstance(ignore_patterns, str):
                additional_patterns = self._parse_ignore_file_content(ignore_patterns)
                local_ignore_patterns.extend(additional_patterns)
            else:
                raise TypeError("ignore_patterns must be a list of strings or a string in .gitignore format")

        return self._generate_tree_recursive(
            start_path,
            prefix="",
            current_depth=0,
            max_depth=max_depth,
            max_files_depth=max_files_depth,
            start_path=start_path,
            local_ignore_patterns=local_ignore_patterns
        )

    def _generate_tree_recursive(
            self,
            path: str,
            prefix: str,
            current_depth: int,
            max_depth: Optional[int],
            max_files_depth: Optional[int],
            start_path: str,
            local_ignore_patterns: List[str]
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
            filtered_contents = []
            for name in contents:
                # Check if the item should be ignored
                full_path = os.path.join(path, name)
                rel_path = os.path.relpath(full_path, start_path)
                is_dir = os.path.isdir(full_path)

                # Skip if matches any ignore pattern
                if self._should_ignore(name, rel_path, is_dir, local_ignore_patterns):
                    continue

                filtered_contents.append(name)

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
                        max_files_depth,
                        start_path,
                        local_ignore_patterns
                    )
                    tree_structure.extend(subtree)

        except (PermissionError, FileNotFoundError) as e:
            # Handle permission errors or deleted directories gracefully
            tree_structure.append(f"{prefix}└── [Error: {str(e)}]")

        return tree_structure