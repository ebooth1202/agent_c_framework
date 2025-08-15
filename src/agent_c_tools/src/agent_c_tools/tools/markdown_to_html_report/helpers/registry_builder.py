"""
Registry Builder - Integration module that ties together the new architecture.

This module provides a clean API for building document registries and UI trees
from both directory crawling and custom structure inputs.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, NamedTuple

from .doc_registry import DocRegistry, DocMeta
from .link_rewriter import rewrite_all_documents

logger = logging.getLogger(__name__)


class RegistryResult(NamedTuple):
    """Result of registry building with warnings."""
    registry: DocRegistry
    ui_tree: List[Dict]
    warnings: List[str]


class RegistryBuilder:
    """
    Builds unified document registries from various input sources.

    Handles both directory crawling and custom structure inputs,
    normalizing them into a consistent DocRegistry + UI tree format.
    """

    def __init__(self, workspace_tool):
        self.workspace_tool = workspace_tool

    # -----------------------
    # Public build functions
    # -----------------------

    async def build_from_directory(
        self,
        root_path: str,
        files_to_ignore: Optional[List[str]] = None,
        tool_context: Optional[Dict] = None
    ) -> RegistryResult:
        """
        Build registry from directory crawling.

        Args:
            root_path: Root directory to crawl (UNC path)
            files_to_ignore: List of filenames to skip
            tool_context: Tool context for workspace operations

        Returns:
            RegistryResult with registry, UI tree, and warnings
        """
        logger.debug(f"Building registry from directory: {root_path}")
        warnings: List[str] = []

        # Collect markdown files using workspace_tool
        markdown_files = await self._collect_directory_files(root_path, files_to_ignore, tool_context)

        # Build registry
        registry = DocRegistry()
        for rel_path, unc_path in markdown_files.items():
            doc = await self._create_doc_from_file(unc_path, rel_path, rel_path)
            registry.add_document(doc)

        # Compute display-name collisions (local helper)
        collisions = self._get_display_name_collisions(registry)
        for display_name, paths in collisions.items():
            warnings.append(
                f"Display name collision for '{display_name}': {paths}. "
                "Use explicit paths for cross-document links."
            )

        # Build UI tree (includes 'content' on file nodes)
        ui_tree = self._build_hierarchical_tree(registry)

        logger.info(f"Built directory registry: {registry.stats()}")
        if warnings:
            logger.warning(f"Generated {len(warnings)} warnings during registry build")

        return RegistryResult(registry, ui_tree, warnings)

    async def build_from_custom_structure(
        self,
        custom_structure: Dict[str, Any],
        base_path: str
    ) -> RegistryResult:
        """
        Build registry from custom user-provided structure.

        Args:
            custom_structure: User-defined structure with items array
            base_path: Base UNC path for resolving file paths

        Returns:
            RegistryResult with registry, UI tree, and warnings
        """
        logger.debug("Building registry from custom structure")
        warnings: List[str] = []

        registry = DocRegistry()
        ui_tree: List[Dict] = []

        # Process the custom structure
        await self._process_custom_items(custom_structure.get("items", []), registry, ui_tree, base_path)

        # Compute display-name collisions
        collisions = self._get_display_name_collisions(registry)
        for display_name, paths in collisions.items():
            warnings.append(
                f"Display name collision for '{display_name}': {paths}. "
                "Use explicit paths for cross-document links."
            )

        logger.info(f"Built custom registry: {registry.stats()}")
        if warnings:
            logger.warning(f"Generated {len(warnings)} warnings during custom registry build")

        return RegistryResult(registry, ui_tree, warnings)

    def apply_link_rewriting(self, registry: DocRegistry) -> Tuple[DocRegistry, List[str]]:
        """
        Apply link rewriting to all documents in the registry.

        Args:
            registry: Registry with documents to process

        Returns:
            Tuple of (new registry with rewritten links, warnings)
        """
        logger.debug("Applying link rewriting to registry")
        warnings: List[str] = []

        result = rewrite_all_documents(registry)
        if isinstance(result, tuple) and len(result) == 2:
            rewritten_registry, rewriter_warnings = result
            if rewriter_warnings:
                warnings.extend(rewriter_warnings)
        else:
            rewritten_registry = result

        # Stats & collisions for logging only
        stats = rewritten_registry.stats()
        collisions = self._get_display_name_collisions(rewritten_registry)
        if collisions:
            for display_name, paths in collisions.items():
                warnings.append(
                    f"Display name collision remains after rewriting: '{display_name}': {paths}"
                )

        logger.info(f"Link rewriting complete: {stats}")
        return rewritten_registry, warnings

    # -----------------------
    # Helpers (directory)
    # -----------------------

    async def _collect_directory_files(
        self,
        root_path: str,
        files_to_ignore: Optional[List[str]],
        tool_context: Optional[Dict]
    ) -> Dict[str, str]:
        """Collect markdown files from directory traversal using workspace_tool."""
        from ....helpers.path_helper import normalize_path, has_file_extension
        from ....helpers.workspace_result_parser import parse_workspace_result

        markdown_files: Dict[str, str] = {}
        files_to_ignore = [f.lower() for f in (files_to_ignore or [])]
        logger.debug(f"Searching for markdown files in {root_path} and subdirectories...")

        async def process_directory(dir_path: str, rel_path: str = "") -> None:
            normalized_dir_path = normalize_path(dir_path)
            if not normalized_dir_path.endswith('/'):
                normalized_dir_path += '/'

            try:
                ls_result = await self.workspace_tool.ls(
                    path=normalized_dir_path, tools='ls', tool_context=tool_context
                )
                success, ls_data, error_msg = parse_workspace_result(ls_result, "directory listing")
                if not success:
                    logger.error(f"Error listing directory '{normalized_dir_path}': {error_msg}")
                    return

                if isinstance(ls_data, list):
                    items = ls_data
                elif isinstance(ls_data, dict):
                    items = ls_data.get('contents', ls_data.get('items', []))
                else:
                    logger.warning(f"Unexpected ls data format for {normalized_dir_path}: {type(ls_data)}")
                    items = []

                logger.debug(f"Found {len(items)} items in {normalized_dir_path}")

                for item_name in items:
                    # Skip hidden files and directories
                    if item_name.startswith('.'):
                        continue
                    if item_name.lower() in files_to_ignore:
                        continue

                    item_path = f"{normalized_dir_path}{item_name}"

                    # Check markdown extensions first
                    if has_file_extension(item_name, ['md', 'markdown', 'mdx']):
                        file_rel_path = f"{rel_path}/{item_name}" if rel_path else item_name
                        normalized_file_rel_path = normalize_path(file_rel_path)
                        markdown_files[normalized_file_rel_path] = item_path
                        continue

                    # Otherwise, recurse into directories only
                    is_dir_result = await self.workspace_tool.is_directory(path=item_path)
                    success, is_dir_data, error_msg = parse_workspace_result(is_dir_result, "directory check")

                    is_directory = False
                    if success:
                        if isinstance(is_dir_data, dict):
                            is_directory = is_dir_data.get('is_directory', False)
                        elif isinstance(is_dir_data, bool):
                            is_directory = is_dir_data
                        elif isinstance(is_dir_data, str):
                            is_directory = is_dir_data.lower() in ('true', '1', 'yes')
                    else:
                        logger.warning(f"Could not determine if {item_path} is a directory: {error_msg}")

                    if is_directory:
                        new_rel_path = f"{rel_path}/{item_name}" if rel_path else item_name
                        await process_directory(item_path, new_rel_path)

            except Exception as e:
                logger.error(f"Error processing directory {normalized_dir_path}: {e}")

        normalized_root_path = normalize_path(root_path).rstrip('/')
        await process_directory(normalized_root_path)

        file_count = len(markdown_files)
        logger.info(f"Found {file_count} markdown files in {normalized_root_path}")
        return markdown_files

    async def _create_doc_from_file(
        self,
        unc_path: str,
        canonical_path: str,
        display_name_base: str
    ) -> DocMeta:
        """Create a DocMeta instance from a file."""
        try:
            error, workspace, relative_path = self.workspace_tool.validate_and_get_workspace_path(unc_path)
            if error:
                raise ValueError(f"Error reading file: {error}")

            content = await workspace.read_internal(relative_path)
            if isinstance(content, str) and content.startswith('{"error":'):
                raise ValueError(f"Error reading file: {content}")

            # Display name: filename stem → title-cased with underscores to spaces
            display_name = Path(display_name_base).stem.replace('_', ' ').title()

            return DocMeta(
                display_name=display_name,
                path=canonical_path,
                anchors=set(),        # (optional) you can pre-extract headings later if desired
                content=content if isinstance(content, str) else str(content)
            )

        except Exception as e:
            logger.error(f"Error creating doc from file {unc_path}: {e}")
            return DocMeta(
                display_name=f"Error: {Path(unc_path).name}",
                path=canonical_path,
                anchors=set(),
                content=f"Error loading file: {str(e)}"
            )

    # -----------------------
    # Helpers (custom input)
    # -----------------------

    async def _process_custom_items(
        self,
        items: List[Dict],
        registry: DocRegistry,
        ui_tree: List[Dict],
        base_path: str,
        current_path: str = ""
    ) -> None:
        """Process custom structure items recursively."""
        for item in items:
            item_type = item.get('type')
            item_name = item.get('name')

            if item_type == 'file':
                file_path = item['path']
                # UNC / on-disk path for reading:
                resolved_path = self._resolve_custom_file_path(file_path, base_path)

                # Canonical *registry* path used for link resolution & viewer:// URLs:
                # - strip leading slash
                # - normalize separators
                registry_path = file_path.lstrip('/').replace('\\', '/')

                # Display label shown in the tree:
                display_name = item.get('name') or Path(registry_path).stem

                # Read & register using the canonical registry path
                doc = await self._create_doc_from_file(
                    resolved_path,
                    registry_path,  # <-- IMPORTANT: use canonical registry path, not a "pretty" one
                    display_name
                )
                registry.add_document(doc)

                # UI node: show the custom name, but the clickable path must be the canonical one
                ui_tree.append({
                    'name': display_name,
                    'type': 'file',
                    'path': registry_path,  # <-- MUST match registry.by_path key
                    'content': doc.content,
                })

            elif item_type == 'folder':
                folder_path = f"{current_path}/{item_name}".strip('/') if current_path else item_name
                folder_children: List[Dict] = []

                await self._process_custom_items(
                    item.get('children', []),
                    registry,
                    folder_children,
                    base_path,
                    folder_path
                )

                ui_tree.append({
                    'name': item_name,
                    'type': 'folder',
                    'path': folder_path,
                    'children': folder_children
                })

    def _resolve_custom_file_path(self, file_path: str, base_path: str) -> str:
        """Resolve custom file path to UNC format."""
        if file_path.startswith('//'):
            return file_path

        if file_path.startswith('/'):
            # Absolute path - extract workspace from base_path if present
            if base_path.startswith('//'):
                workspace = base_path.split('/')[2]
                return f"//{workspace}{file_path}"
            return file_path

        # Relative path
        return f"{base_path.rstrip('/')}/{file_path}"

    # -----------------------
    # UI tree builder
    # -----------------------

    def _build_hierarchical_tree(self, registry: DocRegistry) -> List[Dict]:
        """
        Build hierarchical UI tree from the registry.
        Includes 'content' in file nodes so the viewer can render without extra lookups.
        """
        tree: List[Dict] = []

        # Sort paths for consistent ordering (folders then files naturally by path)
        sorted_paths = sorted(registry.by_path.keys(), key=str.lower)

        for path in sorted_paths:
            doc = registry.by_path[path]
            parts = path.split('/')

            current_level = tree
            current_path = ""

            # Create folder structure
            for part in parts[:-1]:
                current_path = f"{current_path}/{part}" if current_path else part
                # find or create folder
                folder = next(
                    (n for n in current_level if n.get('type') == 'folder' and n.get('name') == part),
                    None
                )
                if not folder:
                    folder = {
                        'name': part,
                        'type': 'folder',
                        'path': current_path,
                        'children': []
                    }
                    current_level.append(folder)
                current_level = folder['children']

            # Add file node with content
            current_level.append({
                'name': doc.display_name,
                'type': 'file',
                'path': doc.path,
                'content': doc.content
            })

        return tree

    # -----------------------
    # Diagnostics
    # -----------------------

    def _get_display_name_collisions(self, registry: DocRegistry) -> Dict[str, List[str]]:
        """
        Build a mapping of display-name -> [paths] only for names that collide.
        Works regardless of whether DocRegistry provides a helper.
        """
        collisions: Dict[str, List[str]] = {}
        # If DocRegistry has by_display, prefer it; else derive it.
        by_display = getattr(registry, "by_display", None)
        if by_display is None:
            temp: Dict[str, List[str]] = {}
            for p, meta in registry.by_path.items():
                temp.setdefault(meta.display_name, []).append(p)
            by_display = temp

        for name, paths in by_display.items():
            if len(paths) > 1:
                collisions[name] = list(paths)
        return collisions


# -----------------------
# Module-level API
# -----------------------

async def build_registry_and_tree(
    workspace_tool,
    mode: str,
    **kwargs
) -> Tuple[DocRegistry, List[Dict], List[str]]:
    """
    Main entry point for building registry and UI tree.

    Args:
        workspace_tool: Workspace tool instance
        mode: 'directory' or 'custom'
        **kwargs: Mode-specific arguments

    Returns:
        Tuple of (DocRegistry with rewritten links, UI tree, warnings)
    """
    builder = RegistryBuilder(workspace_tool)
    all_warnings: List[str] = []

    if mode == 'directory':
        result = await builder.build_from_directory(
            root_path=kwargs['root_path'],
            files_to_ignore=kwargs.get('files_to_ignore', []),
            tool_context=kwargs.get('tool_context', {})
        )
    elif mode == 'custom':
        result = await builder.build_from_custom_structure(
            custom_structure=kwargs['custom_structure'],
            base_path=kwargs['base_path']
        )
    else:
        raise ValueError(f"Unknown mode: {mode}")

    # Collect warnings from registry building
    all_warnings.extend(result.warnings)

    # Apply link rewriting (updates doc.content and link targets)
    final_registry, rewrite_warnings = builder.apply_link_rewriting(result.registry)
    all_warnings.extend(rewrite_warnings)

    # IMPORTANT: Rebuild the UI tree AFTER rewriting so 'content' reflects rewritten links
    final_ui_tree = builder._build_hierarchical_tree(final_registry)

    return final_registry, final_ui_tree, all_warnings


def create_content_map(registry: DocRegistry) -> Dict[str, str]:
    """
    Create a path -> content mapping for template injection.

    (Kept for compatibility; the current template reads content directly from the tree.)
    """
    return {path: doc.content for path, doc in registry.by_path.items()}


def validate_registry_integrity(registry: DocRegistry) -> List[str]:
    """
    Validate registry integrity and return list of issues.

    Returns:
        List of validation error messages (empty if no issues)
    """
    issues: List[str] = []

    # Empty registry
    if not registry.by_path:
        issues.append("Registry is empty - no documents found")

    # Display name collisions
    builder = RegistryBuilder(workspace_tool=None)  # only using the helper
    collisions = builder._get_display_name_collisions(registry)
    for display_name, paths in collisions.items():
        issues.append(f"Display name collision '{display_name}': {paths}")

    # Empty content
    empty_docs = [path for path, doc in registry.by_path.items() if not (doc.content or "").strip()]
    if empty_docs:
        issues.append(f"Documents with empty content: {empty_docs}")

    return issues
