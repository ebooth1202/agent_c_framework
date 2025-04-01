from typing import List, Optional

from agent_c_tools.tools.workspace.util.trees.renderers.base import TreeRenderer
from agent_c_tools.tools.workspace.util.trees.models import DirectoryTree, TreeNode


class MinimalTreeRenderer(TreeRenderer):
    """
    Renderer that outputs a directory tree with minimal formatting.

    This renderer provides a simple view with just two spaces for indentation.
    """

    def render(self,
               tree: DirectoryTree,
               max_depth: Optional[int] = None,
               max_files_depth: Optional[int] = None,
               include_root: bool = True,
               **kwargs) -> List[str]:
        """
        Render a DirectoryTree with minimal formatting.

        Args:
            tree: The DirectoryTree to render
            max_depth: Maximum depth to traverse (None for unlimited)
            max_files_depth: Maximum depth at which to show files (None for unlimited)
            include_root: Whether to include the root node in the output
            **kwargs: Additional rendering options

        Returns:
            List of strings representing the recursive directory structure
        """
        # If max_files_depth is not specified, use the same value as max_depth
        if max_files_depth is None and max_depth is not None:
            max_files_depth = max_depth

        # Start with an empty list for the result
        result = []

        # Add the root node if requested
        if include_root:
            # Add slash to root name if it's a directory
            root_name = f"{tree.root.name}/" if tree.root.is_dir else tree.root.name
            result.append(root_name)
            prefix = ""
        else:
            prefix = ""

        # Render the tree recursively starting from the root's children
        if not tree.is_empty():
            lines = self._render_node_children(
                node=tree.root,
                prefix=prefix,
                current_depth=0,
                max_depth=max_depth,
                max_files_depth=max_files_depth
            )
            result.extend(lines)

        return result

    def _render_node_children(self,
                              node: TreeNode,
                              prefix: str,
                              current_depth: int,
                              max_depth: Optional[int],
                              max_files_depth: Optional[int]) -> List[str]:
        """
        Recursively render the children of a node.

        Args:
            node: The current node whose children to render
            prefix: Current indentation prefix string
            current_depth: Current recursion depth
            max_depth: Maximum depth to display
            max_files_depth: Maximum depth for displaying files

        Returns:
            List of strings representing the minimal tree structure
        """
        if not node.children:
            return []

        # Check if we've reached max depth
        if max_depth is not None and current_depth >= max_depth:
            return [f"{prefix}  ..."]

        result = []

        # Sort the children for consistent display
        sorted_children = node.children.copy()
        sorted_children.sort(key=lambda x: (not x.is_dir, x.name.lower()))

        # Filter out files if we've reached max_files_depth
        visible_children = []
        for child in sorted_children:
            if child.is_dir or max_files_depth is None or current_depth < max_files_depth:
                visible_children.append(child)

        # Process each visible child node
        for child in visible_children:
            # Add slash to directory names
            display_name = f"{child.name}/" if child.is_dir else child.name

            # Add this node to the result with minimal formatting
            result.append(f"{prefix}  {display_name}")

            # Only recurse for directories
            if child.is_dir:
                # Calculate next level's prefix (2 spaces for indentation)
                next_prefix = prefix + "  "

                # Check if we should show children of this directory
                if max_depth is None or current_depth + 1 < max_depth:
                    subtree = self._render_node_children(
                        node=child,
                        prefix=next_prefix,
                        current_depth=current_depth + 1,
                        max_depth=max_depth,
                        max_files_depth=max_files_depth
                    )
                    result.extend(subtree)
                elif max_depth is not None and current_depth + 1 >= max_depth:
                    if child.children:  # Only show ellipsis if there are children
                        result.append(f"{next_prefix}  ...")

        return result
