import json
from typing import Dict, Any, Optional, List

from agent_c_tools.tools.workspace.util.trees.renderers.base import TreeRenderer
from agent_c_tools.tools.workspace.util.trees.models import DirectoryTree, TreeNode


class JsonTreeRenderer(TreeRenderer):
    """
    Renderer that outputs a directory tree in JSON format.

    This renderer is useful for programmatic access to the tree structure.
    """

    def render(self,
               tree: DirectoryTree,
               max_depth: Optional[int] = None,
               max_files_depth: Optional[int] = None,
               pretty_print: bool = True,
               include_metadata: bool = True,
               **kwargs) -> str:
        """
        Render a DirectoryTree into JSON format.

        Args:
            tree: The DirectoryTree to render
            max_depth: Maximum depth to traverse (None for unlimited)
            max_files_depth: Maximum depth at which to show files (None for unlimited)
            pretty_print: Whether to format the JSON with indentation
            include_metadata: Whether to include tree metadata in the output
            **kwargs: Additional rendering options

        Returns:
            JSON string representation of the tree
        """
        # If max_files_depth is not specified, use the same value as max_depth
        if max_files_depth is None and max_depth is not None:
            max_files_depth = max_depth

        # Create the JSON structure
        result = {}

        # Add tree metadata if requested
        if include_metadata:
            result["metadata"] = tree.metadata

        # Add the root node and its children
        result["tree"] = self._node_to_dict(
            node=tree.root,
            current_depth=0,
            max_depth=max_depth,
            max_files_depth=max_files_depth
        )

        # Convert to JSON string
        indent = 2 if pretty_print else None
        return json.dumps(result, indent=indent)

    def _node_to_dict(self,
                      node: TreeNode,
                      current_depth: int,
                      max_depth: Optional[int],
                      max_files_depth: Optional[int]) -> Dict[str, Any]:
        """
        Convert a TreeNode to a dictionary representation.

        Args:
            node: The node to convert
            current_depth: Current recursion depth
            max_depth: Maximum depth to display
            max_files_depth: Maximum depth for displaying files

        Returns:
            Dictionary representation of the node
        """
        result = {
            "name": node.name,
            "type": "directory" if node.is_dir else "file"
        }

        # Add children if this is a directory
        if node.is_dir:
            # Check depth limits
            if max_depth is not None and current_depth >= max_depth:
                result["truncated"] = True
            else:
                # Process children
                children = []
                for child in node.children:
                    # Skip files if we've reached max_files_depth
                    if not child.is_dir and max_files_depth is not None and current_depth >= max_files_depth:
                        continue

                    # Recursively add the child
                    child_dict = self._node_to_dict(
                        child,
                        current_depth + 1,
                        max_depth,
                        max_files_depth
                    )
                    children.append(child_dict)

                # Add children to the result
                if children:
                    result["children"] = children

                # Indicate if we've omitted files due to max_files_depth
                if max_files_depth is not None and current_depth >= max_files_depth:
                    files_count = sum(1 for c in node.children if not c.is_dir)
                    if files_count > 0:
                        result["files_omitted"] = files_count

        return result
