from abc import ABC, abstractmethod
from typing import List, Optional, Union

from agent_c_tools.tools.workspace.util.trees.models import DirectoryTree, TreeNode

class TreeBuilder(ABC):
    """
    Abstract base class for directory tree builders.

    Tree builders are responsible for generating a DirectoryTree model
    without being concerned with the rendering details.
    """

    @abstractmethod
    def build_tree(self,
                   start_path: str,
                   ignore_patterns: Optional[Union[List[str], str]] = None) -> DirectoryTree:
        """
        Build a directory tree structure from the given start path.

        Args:
            start_path: The root path to start building the tree from
            ignore_patterns: Patterns to ignore, either as:
                - A list of glob patterns (e.g., ["*.pyc", ".git/"])
                - A string in .gitignore format
                - None to use defaults

        Returns:
            DirectoryTree representing the directory structure
        """
        pass

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