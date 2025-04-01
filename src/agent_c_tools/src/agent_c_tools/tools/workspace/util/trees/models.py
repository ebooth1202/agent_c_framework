from typing import List, Optional, Dict, Any, Union
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class TreeNode:
    """
    Simple node in a directory tree.
    Represents a file or directory in the file system.
    """
    name: str
    is_dir: bool
    children: List['TreeNode'] = field(default_factory=list)

    def add_child(self, node: 'TreeNode') -> None:
        """Add a child node to this node."""
        self.children.append(node)

    def sort_children(self) -> None:
        """Sort children of this node with directories first."""
        self.children.sort(key=lambda x: (not x.is_dir, x.name.lower()))
        for child in self.children:
            if child.is_dir:
                child.sort_children()


@dataclass
class DirectoryTree:
    """
    Represents a complete directory tree structure.
    Contains the root node and additional metadata.
    """
    root: TreeNode
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_empty(self) -> bool:
        """Check if the tree is empty."""
        return self.root is None or not self.root.children