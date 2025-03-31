from abc import ABC, abstractmethod
from typing import Optional, Any

from agent_c_tools.tools.workspace.util.trees.models import DirectoryTree


class TreeRenderer(ABC):
    """
    Abstract base class for directory tree renderers.

    Tree renderers are responsible for converting DirectoryTree models into
    a specific output format, handling display concerns like max depth,
    filtering, etc.
    """

    @abstractmethod
    def render(self,
               tree: DirectoryTree,
               max_depth: Optional[int] = None,
               max_files_depth: Optional[int] = None,
               **kwargs) -> Any:
        """
        Render a DirectoryTree into a specific output format.

        Args:
            tree: The DirectoryTree to render
            max_depth: Maximum depth to display in the output (None for unlimited)
            max_files_depth: Maximum depth for displaying files (None for unlimited)
            **kwargs: Additional renderer-specific options

        Returns:
            The rendered representation of the tree
        """
        pass