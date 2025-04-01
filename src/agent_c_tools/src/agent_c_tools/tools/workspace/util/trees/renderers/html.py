import html
from typing import Optional

from agent_c_tools.tools.workspace.util.trees.renderers.base import TreeRenderer
from agent_c_tools.tools.workspace.util.trees.models import DirectoryTree, TreeNode


class HtmlTreeRenderer(TreeRenderer):
    """
    Renderer that outputs a directory tree in HTML format.

    This renderer produces an HTML representation with collapsible sections.
    """

    def render(self,
               tree: DirectoryTree,
               max_depth: Optional[int] = None,
               max_files_depth: Optional[int] = None,
               title: str = "Directory Tree",
               include_css: bool = True,
               **kwargs) -> str:
        """
        Render a DirectoryTree into HTML format.

        Args:
            tree: The DirectoryTree to render
            max_depth: Maximum depth to traverse (None for unlimited)
            max_files_depth: Maximum depth at which to show files (None for unlimited)
            title: Title for the HTML page
            include_css: Whether to include CSS styles in the output
            **kwargs: Additional rendering options

        Returns:
            HTML string representation of the tree
        """
        # If max_files_depth is not specified, use the same value as max_depth
        if max_files_depth is None and max_depth is not None:
            max_files_depth = max_depth

        # Start building the HTML
        html_parts = [
            "<!DOCTYPE html>",
            "<html>",
            "<head>",
            f"<title>{html.escape(title)}</title>"
        ]

        # Add CSS if requested
        if include_css:
            css = self._get_css()
            html_parts.append(f"<style>{css}</style>")

        html_parts.extend([
            "</head>",
            "<body>",
            f"<h1>{html.escape(title)}</h1>",
            "<div class='tree-container'>"
        ])

        # Add the tree structure
        html_parts.append(self._render_node(
            node=tree.root,
            current_depth=0,
            max_depth=max_depth,
            max_files_depth=max_files_depth
        ))

        # Close the HTML
        html_parts.extend([
            "</div>",
            "<script>",
            "document.addEventListener('DOMContentLoaded', function() {",
            "  const folders = document.querySelectorAll('.folder-label');",
            "  folders.forEach(folder => {",
            "    folder.addEventListener('click', function() {",
            "      this.parentNode.classList.toggle('open');",
            "    });",
            "  });",
            "});",
            "</script>",
            "</body>",
            "</html>"
        ])

        return "\n".join(html_parts)

    def _render_node(self,
                     node: TreeNode,
                     current_depth: int,
                     max_depth: Optional[int],
                     max_files_depth: Optional[int]) -> str:
        """
        Render a node and its children into HTML.

        Args:
            node: The node to render
            current_depth: Current recursion depth
            max_depth: Maximum depth to display
            max_files_depth: Maximum depth for displaying files

        Returns:
            HTML string representation of the node
        """
        html_parts = []

        # Create the node representation
        if node.is_dir:
            # Directory node
            is_root = current_depth == 0
            folder_class = "folder root-folder" if is_root else "folder"
            html_parts.append(f"<div class='{folder_class}'>")
            html_parts.append(f"<div class='folder-label'>{html.escape(node.name)}</div>")

            # Check depth limits
            if max_depth is not None and current_depth >= max_depth:
                html_parts.append("<div class='truncated'>...</div>")
            else:
                # Process children
                html_parts.append("<div class='folder-contents'>")

                # Sort children with directories first
                sorted_children = node.children.copy()
                sorted_children.sort(key=lambda x: (not x.is_dir, x.name.lower()))

                for child in sorted_children:
                    # Skip files if we've reached max_files_depth
                    if not child.is_dir and max_files_depth is not None and current_depth >= max_files_depth:
                        continue

                    # Recursively render the child
                    html_parts.append(self._render_node(
                        child,
                        current_depth + 1,
                        max_depth,
                        max_files_depth
                    ))

                # Indicate if we've omitted files due to max_files_depth
                if max_files_depth is not None and current_depth >= max_files_depth:
                    files_count = sum(1 for c in node.children if not c.is_dir)
                    if files_count > 0:
                        html_parts.append(f"<div class='omitted-files'>{files_count} file(s) omitted</div>")

                html_parts.append("</div>")  # folder-contents

            html_parts.append("</div>")  # folder
        else:
            # File node
            html_parts.append(f"<div class='file'>{html.escape(node.name)}</div>")

        return "".join(html_parts)

    def _get_css(self) -> str:
        """
        Get the CSS styles for the HTML tree.

        Returns:
            CSS string
        """
        return """
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .tree-container {
                margin-top: 20px;
            }
            .folder {
                margin-bottom: 5px;
            }
            .folder-label {
                background-color: #f0f0f0;
                padding: 5px 10px;
                cursor: pointer;
                border-radius: 3px;
                display: inline-block;
            }
            .folder-label:hover {
                background-color: #e0e0e0;
            }
            .root-folder > .folder-label {
                background-color: #d0d0d0;
                font-weight: bold;
            }
            .folder-contents {
                padding-left: 20px;
                display: none;
            }
            .folder.open > .folder-contents {
                display: block;
            }
            .file {
                padding: 5px 10px 5px 30px;
                position: relative;
            }
            .file::before {
                content: "📄";
                position: absolute;
                left: 10px;
            }
            .folder-label::before {
                content: "📁";
                margin-right: 5px;
            }
            .folder.open > .folder-label::before {
                content: "📂";
            }
            .truncated, .omitted-files {
                color: #888;
                font-style: italic;
                padding: 5px 10px;
            }
            """
