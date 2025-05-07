import logging
from typing import List, Dict, Any
import json
import re
from pathlib import Path

from ....helpers.path_helper import create_unc_path, ensure_file_extension, os_file_system_path, has_file_extension, normalize_path

logger = logging.getLogger(__name__)

class MarkdownFileCollector:
    """Helper class for collecting and processing markdown files."""

    def __init__(self, workspace_tool):
        self.workspace_tool = workspace_tool

    async def collect_markdown_files(self, root_path: str, files_to_ignore: List[str] = None) -> Dict[str, str]:
        """Collect all markdown files in the workspace directory structure."""
        markdown_files = {}
        files_to_ignore = [f.lower() for f in (files_to_ignore or [])]
        logger.debug(f"Searching for markdown files in {root_path} and subdirectories...")

        # Process a directory to find markdown files recursively
        async def process_directory(dir_path, rel_path=""):
            # Ensure proper UNC path format for directory listing
            normalized_dir_path = normalize_path(dir_path)
            # Ensure trailing slash for consistent path handling
            if not normalized_dir_path.endswith('/'):
                normalized_dir_path += '/'

            try:
                ls_result = await self.workspace_tool.ls(path=normalized_dir_path)
                ls_data = json.loads(ls_result)

                if 'error' in ls_data:
                    logger.error(f"Error listing directory '{normalized_dir_path}': {ls_data['error']}")
                    return

                items = ls_data.get('contents', [])
                logger.debug(f"Found {len(items)} items in {normalized_dir_path}")

                for item_name in items:
                    # Skip hidden files and directories
                    if item_name.startswith('.'):
                        continue

                    if item_name.lower() in files_to_ignore:
                        continue

                    # Create proper UNC item path
                    item_path = f"{normalized_dir_path}{item_name}"

                    # First check if it's a markdown file by extension
                    if has_file_extension(item_name, ['md', 'markdown']):
                        # Add markdown file to our collection
                        file_rel_path = f"{rel_path}/{item_name}" if rel_path else item_name
                        # Normalize path separators in keys
                        normalized_file_rel_path = normalize_path(file_rel_path)
                        markdown_files[normalized_file_rel_path] = item_path
                    else:
                        # Only check if it's a directory - we don't process non-markdown files
                        is_dir_result = await self.workspace_tool.is_directory(path=item_path)
                        is_dir_data = json.loads(is_dir_result)

                        if 'error' not in is_dir_data and is_dir_data.get('is_directory', False):
                            # Recursively process subdirectory
                            new_rel_path = f"{rel_path}/{item_name}" if rel_path else item_name
                            await process_directory(item_path, new_rel_path)
            except Exception as e:
                logger.error(f"Error processing directory {normalized_dir_path}: {e}")

        # Start processing from the root path
        normalized_root_path = normalize_path(root_path).rstrip('/')
        await process_directory(normalized_root_path)

        file_count = len(markdown_files)
        logger.info(f"Found {file_count} markdown files in {normalized_root_path}")
        return markdown_files

    async def build_file_structure(self, root_path: str, markdown_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Build file structure for the HTML viewer."""
        structure = []
        folders = {}

        # Normalize root path for consistent path handling
        normalized_root_path = normalize_path(root_path)

        # Sort paths to ensure proper order (parent folders before children)
        for rel_path, unc_path in sorted(markdown_files.items()):
            # Double-check that it's a markdown file before processing
            if not has_file_extension(Path(rel_path).name, ['md', 'markdown']):
                logger.debug(f"Skipping non-markdown file: {rel_path}")
                continue

            # Normalize the UNC path for consistent handling
            normalized_unc_path = normalize_path(unc_path)

            # Get path parts for folder hierarchy construction
            path_parts = rel_path.split('/')
            file_name = path_parts[-1]

            # Create folder hierarchy
            current_folders = structure
            current_path = ""

            # Process all path parts except the last one (which is the file)
            for part in path_parts[:-1]:
                if current_path:
                    current_path += f"/{part}"
                else:
                    current_path = part

                # Check if this folder already exists in our structure
                folder = next((f for f in current_folders if f['type'] == 'folder' and f['name'] == part), None)

                if not folder:
                    # Create new folder
                    folder = {
                        'name': part,
                        'type': 'folder',
                        'path': current_path,
                        'children': []
                    }
                    current_folders.append(folder)
                    folders[current_path] = folder['children']

                # Move to the next level
                current_folders = folder['children']

            try:
                # Read the file content
                file_content = await self.workspace_tool.read(path=normalized_unc_path)
                if file_content.startswith('{"error":'):
                    # Detect a read error
                    raise ValueError(f"Error reading file: {file_content}")

                # Process links in the content
                processed_content = await self._process_markdown_links(file_content, rel_path, normalized_root_path,
                                                                       markdown_files)

                # Add the file to the structure
                current_folders.append({
                    'name': file_name,
                    'type': 'file',
                    'path': rel_path,
                    'content': processed_content
                })
            except Exception as e:
                logger.error(f"Error processing file {normalized_unc_path}: {e}")
                # Add the file with error message
                current_folders.append({
                    'name': file_name,
                    'type': 'file',
                    'path': rel_path,
                    'content': f"Error processing file: {str(e)}"
                })

        return structure

    async def _process_markdown_links(self, content: str, file_rel_path: str, root_path: str,
                                      markdown_files: Dict[str, str]) -> str:
        """Convert markdown links to other markdown files into internal viewer links."""
        # Normalize path separators in file_rel_path
        normalized_file_rel_path = file_rel_path.replace('\\', '/')

        # Get the directory of the current file for resolving relative paths
        file_dir = Path(normalized_file_rel_path).parent.as_posix() if '/' in normalized_file_rel_path else ""

        # Regular expression to find markdown links
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        def replace_link(match):
            link_text = match.group(1)
            link_target = match.group(2)

            # Handle internal document links (just anchors)
            if link_target.startswith('#'):
                anchor_id = link_target.replace("#", "")
                return f'[{link_text}](javascript:void(scrollToAnchor("{anchor_id}")))'

            # Skip already processed javascript links
            if link_target.startswith('javascript:'):
                return match.group(0)

            # Skip external links
            if link_target.startswith(('http://', 'https://')):
                return match.group(0)

            # Split target into file path and anchor if it exists
            parts = link_target.split('#', 1)
            target_file = parts[0]
            anchor = f"#{parts[1]}" if len(parts) > 1 else ""

            try:
                # Normalize target file path separators
                target_file = target_file.replace('\\', '/')

                # Handle UNC paths in links
                if re.match(self.workspace_tool.UNC_PATH_PATTERN, target_file):
                    # If the link target is a UNC path, extract the relative part
                    try:
                        # Extract the part after the workspace
                        unc_parts = target_file.split('/', 3)
                        if len(unc_parts) >= 4:
                            target_path = unc_parts[3]
                        else:
                            # Can't extract relative path, use as is
                            target_path = target_file
                    except Exception:
                        target_path = target_file
                else:
                    # Calculate the full path from the current file's directory
                    if target_file.startswith('/'):
                        # Handle absolute path (relative to root)
                        target_path = target_file[1:]
                    else:
                        # Handle relative path
                        if file_dir:
                            target_path = f"{file_dir}/{target_file}"
                        else:
                            target_path = target_file

                # Normalize path and separators
                target_path = Path(target_path).as_posix()

                # Check if the target is a markdown file in our collection
                if target_path in markdown_files:
                    # Replace with internal link
                    if anchor:
                        return f'[{link_text}](javascript:void(openMarkdownFile("{target_path}", "{anchor}")))'
                    else:
                        return f'[{link_text}](javascript:void(openMarkdownFile("{target_path}")))'

                # If it's potentially a directory link (ending with / or no extension)
                if target_path.endswith('/') or '.' not in target_path.split('/')[-1]:
                    # Ensure path ends with a slash for proper directory prefix matching
                    if not target_path.endswith('/'):
                        target_path = f"{target_path}/"

                    # Check if there are any markdown files in this directory
                    for md_path in markdown_files.keys():
                        if md_path.startswith(target_path):
                            # It's a directory with markdown files, link to the first one
                            return f'[{link_text}](javascript:void(openMarkdownFile("{md_path}")))'
            except Exception as e:
                # If there's an error resolving the path, log it and leave the link unchanged
                logger.error(f"Error processing link '{link_target}' in file '{normalized_file_rel_path}': {e}")

            # If target doesn't exist in our structure or path resolution failed, leave the link unchanged
            return match.group(0)

        # Process all links in the content
        processed_content = re.sub(link_pattern, replace_link, content)
        return processed_content