import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Optional

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema

logger = logging.getLogger(__name__)

# Regular expression to match UNC paths
UNC_PATH_PATTERN = r'^(//|\\\\)[^/\\]+(/|\\)[^/\\].*$'


class MarkdownToHtmlReportTools(Toolset):
    """Toolset for generating interactive HTML viewers from markdown files in a workspace."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, name="markdown_viewer")
        # Get workspace tools for file operations
        self.workspace_tool = self.tool_chest.active_tools.get('workspace')
        if not self.workspace_tool:
            logger.warning("Workspace toolset not available. This tool requires workspace tools.")

    @json_schema(
        description="Generate an interactive HTML viewer for markdown files in a workspace directory",
        params={
            "workspace": {
                "type": "string",
                "description": "The workspace containing the markdown files",
                "required": True
            },
            "input_path": {
                "type": "string",
                "description": "The path within the workspace where markdown files are located (or a full UNC path)",
                "required": True
            },
            "output_filename": {
                "type": "string",
                "description": "The name of the output HTML file to generate (can be a simple filename or full UNC path)",
                "required": True
            },
            "title": {
                "type": "string",
                "description": "Optional title for the HTML viewer (displayed in the sidebar)",
                "required": False
            },
            "files_to_ignore": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Optional flat list of filenames to ignore when generating the HTML viewer. Does not support folder level differentiation.",
                "required": False,
                "default": []
            }
        }
    )
    async def generate_report(self, **kwargs) -> str:
        """Generate an interactive HTML viewer for markdown files in a workspace directory.

        Args:
            workspace: The workspace containing the markdown files
            input_path: The path within the workspace where markdown files are located (or a full UNC path)
            output_filename: The name of the output HTML file to generate (can be a simple filename or full UNC path)
            title: Optional title for the HTML viewer

        Returns:
            A dictionary with success status and information about the operation
        """
        workspace = kwargs.get('workspace')
        input_path = kwargs.get('input_path')
        output_filename = kwargs.get('output_filename')
        title = kwargs.get('title', 'output_report.html')
        files_to_ignore = kwargs.get('files_to_ignore')

        # Arg check
        missing_fields = []
        if workspace is None:
            missing_fields.append("workspace")
        if input_path is None:
            missing_fields.append("input_path")
        if output_filename is None:
            missing_fields.append("output_filename")

        if missing_fields:
            return f"Required fields cannot be empty: {', '.join(missing_fields)}"

        combined_ignore_list = (files_to_ignore or []) + ([output_filename] if output_filename else [])

        try:
            # Check if input_path is already a UNC path
            if re.match(UNC_PATH_PATTERN, input_path):
                # Input path is already a UNC path, use it directly
                input_path_full = input_path
                # Extract workspace from UNC path if possible (for later use)
                try:
                    unc_parts = input_path.split('/', 3) if '/' in input_path else input_path.split('\\', 3)
                    if len(unc_parts) >= 3:
                        # Use the extracted workspace name
                        workspace = unc_parts[2]
                except Exception as e:
                    logger.warning(f"Could not extract workspace from UNC path: {e}")
            else:
                # If input_path is just the workspace name, don't append it again
                if input_path.strip('/') == workspace:
                    input_path_full = f"//{workspace}"
                else:
                    # Normalize input path for workspace construction
                    normalized_input_path = input_path.lstrip('/')
                    # Construct workspace UNC path
                    input_path_full = f"//{workspace}/{normalized_input_path}"

            # Ensure the output filename has .html extension
            if not output_filename.lower().endswith('.html'):
                output_filename += '.html'

            # Check if output_filename is already a UNC path
            if re.match(UNC_PATH_PATTERN, output_filename):
                # Output path is already a UNC path, use it directly
                output_path_full = output_filename
            else:
                # Normalize the output filename to remove any path information
                output_filename = Path(output_filename).name
                # Construct the output path in the workspace root
                output_path_full = f"//{workspace}/{output_filename}"

            logger.debug(f"Original input path: {input_path}")
            logger.debug(f"Workspace name: {workspace}")
            logger.debug(f"Processed input path: {input_path_full}")
            logger.debug(f"Output path: {output_path_full}")

            # Check if input directory exists by listing its contents
            logger.debug(f"Checking if input path exists...")
            ls_result = await self.workspace_tool.ls(path=input_path_full)
            ls_data = json.loads(ls_result)

            if 'error' in ls_data:
                return json.dumps({
                    "success": False,
                    "error": f"Input path '{input_path}' is not accessible: {ls_data['error']}"
                })

            # Start generating the viewer
            logger.debug(f"Collecting markdown files...")

            # Collect markdown files
            markdown_files = await self._collect_markdown_files(root_path=input_path_full,
                                                                files_to_ignore=combined_ignore_list)

            if not markdown_files:
                logger.debug(f"No markdown files found in {input_path}. Will search subdirectories recursively...")

                # Try to search deeper by examining subdirectories manually
                for item in ls_data.get('items', []):
                    if item['type'] == 'directory':
                        subdir_path = f"{input_path_full}/{item['name']}"
                        subdir_files = await self._collect_markdown_files(subdir_path)
                        if subdir_files:
                            markdown_files.update(subdir_files)

                # If still no files found
                if not markdown_files:
                    return json.dumps({
                        "success": False,
                        "error": f"No markdown files found in {input_path} or its subdirectories"
                    })

            logger.debug(f"Found {len(markdown_files)} markdown files. Building file structure...")

            # Build file structure for the viewer
            file_structure = await self._build_file_structure(input_path_full, markdown_files)

            if not file_structure:
                return json.dumps({
                    "success": False,
                    "error": "Failed to build file structure"
                })

            # Get the HTML template
            logger.debug("Preparing HTML template...")
            html_template = await self._get_html_template()

            # Customize title if provided
            if title:
                html_template = html_template.replace(
                    "<h3 style=\"margin: 0 16px 16px 16px;\">Agent C Output Viewer</h3>",
                    f"<h3 style=\"margin: 0 16px 16px 16px;\">{title}</h3>")

            # Replace placeholder with file structure
            json_structure = json.dumps(file_structure)
            html_content = html_template.replace('$FILE_STRUCTURE', json_structure)

            # Write the generated HTML to the workspace
            logger.debug(f"Writing HTML viewer to output location...")
            write_result = await self.workspace_tool.write(
                path=output_path_full,
                data=html_content,
                mode="write"
            )

            write_data = json.loads(write_result)
            if 'error' in write_data:
                return json.dumps({
                    "success": False,
                    "error": f"Failed to write HTML file: {write_data['error']}"
                })

            message = f"Successfully generated HTML viewer at {output_filename}."
            logger.debug(message)
            
            # Raise a media event with HTML that provides a link to the generated file
            try:
                # Create a fully resolved file path for browser access
                # This will be a local file URL that should open in the browser
                file_url = f"file://{output_path_full.replace('//','/')}"

                # Get the actual OS-level filepath using the workspace's full_path method

                _, workspace_obj, rel_path = self.workspace_tool._parse_unc_path(output_path_full)
                file_system_path = None
                if workspace_obj and hasattr(workspace_obj, 'full_path'):
                    # The full_path method handles path normalization and joining with workspace root
                    # Set mkdirs=False since we're just getting the path for a URL, not writing
                    file_system_path = workspace_obj.full_path(rel_path, mkdirs=False)

                # Create a file:// URL from the system path
                if file_system_path:
                    # Convert backslashes to forward slashes for URL
                    url_path = file_system_path.replace('\\', '/')

                    # Ensure correct URL format (need 3 slashes for file:// URLs with absolute paths)
                    if url_path.startswith('/'):
                        file_url = f"file://{url_path}"
                    else:
                        file_url = f"file:///{url_path}"
                else:
                    # Fallback if we couldn't get the actual path
                    file_url = f"file:///{output_path_full.replace('//', '').replace('\\', '/')}"

                # Create HTML content with a link that opens in a new window
                # html_content = f"<a href='{file_url}' target='_blank'>Open Report: {output_filename}</a>"

                html_content = f"""
                <div style="padding: 20px; font-family: system-ui, sans-serif; max-width: 800px; margin: 0 auto; border: 1px solid #e2e8f0; border-radius: 8px; background-color: #f8fafc;">
                    <h2 style="color: #334155; margin-top: 0;">Report Generated Successfully</h2>

                    <div style="background-color: #f1f5f9; border-radius: 6px; padding: 16px; margin-bottom: 20px;">
                        <p style="margin: 0 0 8px 0;"><strong>File:</strong> {output_filename}</p>
                        <p style="margin: 0 0 8px 0;"><strong>Contents:</strong> {len(markdown_files)} markdown files</p>
                        <p style="margin: 0;"><strong>Location:</strong> <code style="background: #e2e8f0; padding: 2px 4px; border-radius: 4px;">{output_path_full}</code></p>
                    </div>

                    <div style="background-color: #fff7ed; border-left: 4px solid #f97316; padding: 16px; margin-bottom: 20px;">
                        <p style="margin: 0; font-weight: 500; color: #9a3412;">Browser Security Notice</p>
                        <p style="margin: 8px 0 0 0;">Due to browser security restrictions, you'll need to manually open the file:</p>
                    </div>

                    <div style="margin-bottom: 16px;">
                        <p><strong>File path:</strong> <br/>
                        <code style="background: #e2e8f0; padding: 8px; border-radius: 4px; display: block; margin-top: 8px; word-break: break-all;">{file_system_path}</code>
                        </p>

                        <p><strong>Terminal command:</strong> <br/>
                        <code style="background: #e2e8f0; padding: 8px; border-radius: 4px; display: block; margin-top: 8px; word-break: break-all;">
                            {f'start "" "{file_system_path}"' if ':\\' in file_system_path else f'open "{file_system_path}"'}
                        </code>
                        </p>
                    </div>

                    <ol style="margin-top: 0; padding-left: 20px;">
                        <li style="margin-bottom: 8px;">Copy the file path and paste it into your file explorer address bar</li>
                        <li style="margin-bottom: 8px;">Or copy the command and run it in your terminal/command prompt</li>
                    </ol>

                    <div style="margin-top: 16px;">
                        <a href="{file_url}" target="_blank" style="display: inline-block; background-color: #3b82f6; color: white; text-decoration: none; padding: 10px 16px; border-radius: 6px; font-weight: 500;">Try Direct Link</a>
                        <span style="margin-left: 8px; color: #6b7280;">(may not work due to browser restrictions)</span>
                    </div>
                </div>
                """
                # Raise the media event
                await self._raise_render_media(
                    sent_by_class=self.__class__.__name__,
                    sent_by_function='generate_report',
                    content_type="text/html",
                    content=html_content
                )

                # markdown_content = f"""# Your Report is Ready
                # The report containing **{len(markdown_files)} markdown files** has been generated.
                # ## Details
                # - Filename: `{output_filename}`
                # - Location: `{file_url}`
                #
                # [Click here to open the report]({file_url})"""
                #
                # await self._raise_render_media(
                #     sent_by_class=self.__class__.__name__,
                #     sent_by_function='generate_report',
                #     content_type="text/markdown",  # Use text/markdown content type
                #     content=markdown_content
                # )
                
                # logger.debug(f"Raised media event with link to generated HTML file: {file_url}")
            except Exception as e:
                logger.error(f"Failed to raise media event: {str(e)}")

            return json.dumps({
                "success": True,
                "message": message,
                "output_file": output_filename,
                "output_path": output_path_full,
                "workspace": workspace,
                "file_count": len(markdown_files)
            })

        except Exception as e:
            logger.exception("Error generating markdown viewer")
            return json.dumps({
                "success": False,
                "error": f"Error generating markdown viewer: {str(e)}"
            })

    async def _collect_markdown_files(self, root_path: str, files_to_ignore: List[str] = None) -> Dict[str, str]:
        """Collect all markdown files in the workspace directory structure."""
        markdown_files = {}
        files_to_ignore = [f.lower() for f in (files_to_ignore or [])]
        logger.debug(f"Searching for markdown files in {root_path} and subdirectories...")

        # Process a directory to find markdown files recursively
        async def process_directory(dir_path, rel_path=""):
            # Ensure proper UNC path format for directory listing
            normalized_dir_path = dir_path.replace('\\', '/')
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

                    # Create proper UNC item path - don't add extra slash if dir already ends with /
                    item_path = f"{normalized_dir_path}{item_name}"

                    # First check if it's a markdown file by extension - only process .md and .markdown files
                    if self._is_markdown_file(item_name):
                        # Add markdown file to our collection
                        file_rel_path = f"{rel_path}/{item_name}" if rel_path else item_name
                        # Normalize path separators in keys
                        normalized_file_rel_path = file_rel_path.replace('\\', '/')
                        markdown_files[normalized_file_rel_path] = item_path
                        # logger.debug(f"Found markdown file: {normalized_file_rel_path}")
                    else:
                        # Only check if it's a directory - we don't process non-markdown files
                        is_dir_result = await self.workspace_tool.is_directory(path=item_path)
                        is_dir_data = json.loads(is_dir_result)

                        if 'error' not in is_dir_data and is_dir_data.get('is_directory', False):
                            # Recursively process subdirectory
                            new_rel_path = f"{rel_path}/{item_name}" if rel_path else item_name
                            await process_directory(item_path, new_rel_path)
                        # No else clause here - we don't add non-markdown files
            except Exception as e:
                logger.error(f"Error processing directory {normalized_dir_path}: {e}")

        # Start processing from the root path, ensuring proper UNC format
        normalized_root_path = root_path.replace('\\', '/')
        # Make sure root path doesn't have a trailing slash for initial call
        normalized_root_path = normalized_root_path.rstrip('/')
        await process_directory(normalized_root_path)

        file_count = len(markdown_files)
        logger.info(f"Found {file_count} markdown files in {normalized_root_path}")
        logger.debug(f"Found {file_count} markdown files in total")
        return markdown_files

    def _is_markdown_file(self, filename: str) -> bool:
        """Check if a file is a markdown file."""
        filename_lower = filename.lower()
        return filename_lower.endswith('.md') or filename_lower.endswith('.markdown')

    async def _build_file_structure(self, root_path: str, markdown_files: Dict[str, str]) -> List[Dict[str, Any]]:
        """Build file structure for the HTML viewer."""
        structure = []
        folders = {}

        # Normalize root path for consistent path handling
        normalized_root_path = root_path.replace('\\', '/')

        # Sort paths to ensure proper order (parent folders before children)
        for rel_path, unc_path in sorted(markdown_files.items()):
            # Double-check that it's a markdown file before processing
            if not self._is_markdown_file(Path(rel_path).name):
                logger.debug(f"Skipping non-markdown file: {rel_path}")
                continue

            # Normalize the UNC path for consistent handling
            normalized_unc_path = unc_path.replace('\\', '/')

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
                read_result = await self.workspace_tool.read(path=normalized_unc_path)
                read_data = json.loads(read_result)

                if 'error' in read_data:
                    logger.error(f"Error reading file {normalized_unc_path}: {read_data['error']}")
                    file_content = f"Error reading file: {read_data['error']}"
                else:
                    file_content = read_data.get('contents', '')

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
                if re.match(UNC_PATH_PATTERN, target_file):
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

    async def _get_html_template(self) -> str:
        """Get the HTML template for the markdown viewer."""
        try:
            # To get the template from the workspace
            # We're going to use local file only for now
            # workspace_template_paths = [
            #     "//tools/src/agent_c_tools/tools/markdown_viewer/markdown-viewer-template.html",
            #     "//tools/src/markdown-viewer-template.html",
            #     "//tools/markdown-viewer-template.html"
            # ]
            #
            # # Try reading from workspace first
            # for template_path in workspace_template_paths:
            #     try:
            #         read_result = await self.workspace_tool.read(path=template_path)
            #         read_data = json.loads(read_result)
            #
            #         if 'error' not in read_data:
            #             logger.info(f"Found template in workspace: {template_path}")
            #             return read_data.get('contents', '')
            #     except Exception:
            #         # Continue to the next path if this one fails
            #         pass


            # If no workspace template found, try local file system
            local_template_path = Path(__file__).parent / "markdown-viewer-template.html"

            # Check if the template file exists
            if not local_template_path.exists():
                logger.warning(f"Template file not found: {local_template_path}")
                # Try alternate locations in case __file__ is not working as expected
                alt_paths = [
                    Path.cwd() / "markdown-viewer-template.html",
                    Path.cwd() / "tools" / "markdown_viewer" / "markdown-viewer-template.html",
                ]

                for alt_path in alt_paths:
                    if alt_path.exists():
                        local_template_path = alt_path
                        logger.info(f"Found template at alternate location: {local_template_path}")
                        break
                else:
                    raise FileNotFoundError("Could not find template file in workspace or local paths")

            # Read the template file from local file system
            with open(local_template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading template file: {e}")
            raise RuntimeError(f"Failed to load HTML template: {e}")


# Register the toolset with the Agent C framework
Toolset.register(MarkdownToHtmlReportTools)
