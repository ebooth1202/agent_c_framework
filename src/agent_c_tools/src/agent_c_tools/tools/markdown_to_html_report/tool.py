import json
import logging
import re

from pathlib import Path
from typing import Dict, List, Any, Optional

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from .helpers.path_helper import PathHelper
from .helpers.validation_helper import ValidationHelper
from .helpers.media_helper import MediaEventHelper
from .helpers.markdown_file_collector import MarkdownFileCollector
from .helpers.markdown_to_docx import MarkdownToDocxConverter
from .helpers.html_template_manager import HtmlTemplateManager
from ... import WorkspaceTools

logger = logging.getLogger(__name__)



class MarkdownToHtmlReportTools(Toolset):
    """Toolset for generating interactive HTML viewers from markdown files in a workspace."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, name="markdown_viewer", use_prefix=False)
        # Get workspace tools for file operations
        self.workspace_tool = Optional[WorkspaceTools]
        if not self.workspace_tool:
            logger.warning("Workspace toolset not available. This tool requires workspace tools.")

        self.path_helper = PathHelper()
        self.validation_helper = ValidationHelper(self.workspace_tool)
        self.media_helper = MediaEventHelper()
        self.file_collector = MarkdownFileCollector(self.workspace_tool)
        self.docx_converter = MarkdownToDocxConverter()
        self.template_manager = HtmlTemplateManager()

    async def post_init(self):
        self.workspace_tool = self.tool_chest.active_tools.get("WorkspaceTools")

    async def _safe_operation(self, operation_name, operation_func, *args, **kwargs):
        """Execute operations with standardized error handling."""
        try:
            return await operation_func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {operation_name}: {str(e)}")
            return {"success": False, "error": f"Error in {operation_name}: {str(e)}"}

    async def _get_file_system_path(self, unc_path: str) -> Optional[str]:
        """Get the actual file system path from a UNC path."""
        try:
            _, workspace_obj, rel_path = self.workspace_tool._parse_unc_path(unc_path)
            if workspace_obj and hasattr(workspace_obj, 'full_path'):
                return workspace_obj.full_path(rel_path, mkdirs=False)
            return None
        except Exception as e:
            logger.error(f"Error getting file system path: {e}")
            return None

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
    async def generate_md_viewer(self, **kwargs) -> str:
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
        files_to_ignore = kwargs.get('files_to_ignore', [])

        # Validate required fields
        validation_error = self.validation_helper.validate_required_fields(
            kwargs, ["workspace", "input_path", "output_filename"])
        if validation_error:
            return json.dumps({"success": False, "error": validation_error})

        try:
            # Process input path
            input_path_full = self.path_helper.ensure_unc_path(input_path, workspace)

            # Validate input path
            error, workspace_obj, rel_path = await self.validation_helper.validate_path(input_path_full)
            if error:
                return json.dumps({"success": False, "error": f"Invalid input path: {error}"})

            # Process output filename
            output_filename = self.path_helper.ensure_file_extension(output_filename, 'html')
            if not output_filename.startswith('//'):
                output_filename = Path(output_filename).name
                output_path_full = f"//{workspace}/{output_filename}"
            else:
                output_path_full = output_filename

            # Validate output path
            error, _, _ = await self.validation_helper.validate_path(output_path_full)
            if error:
                return json.dumps({"success": False, "error": f"Output path issue: {error}"})

            # Check if input directory exists
            logger.debug("Checking if input path exists...")
            ls_result = await self.workspace_tool.ls(path=input_path_full)
            ls_data = json.loads(ls_result)

            if 'error' in ls_data:
                return json.dumps({
                    "success": False,
                    "error": f"Input path '{input_path}' is not accessible: {ls_data['error']}"
                })

            # Collect markdown files
            logger.debug("Collecting markdown files...")
            combined_ignore_list = files_to_ignore + ([output_filename] if output_filename else [])
            markdown_files = await self.file_collector.collect_markdown_files(
                root_path=input_path_full, files_to_ignore=combined_ignore_list)

            if not markdown_files:
                logger.debug(f"No markdown files found in {input_path}. Will search subdirectories recursively...")

                # Try to search deeper by examining subdirectories manually
                for item in ls_data.get('items', []):
                    if item['type'] == 'directory':
                        subdir_path = f"{input_path_full}/{item['name']}"
                        subdir_files = await self.file_collector.collect_markdown_files(subdir_path, files_to_ignore=combined_ignore_list)
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
            file_structure = await self.file_collector.build_file_structure(input_path_full, markdown_files)

            if not file_structure:
                return json.dumps({
                    "success": False,
                    "error": "Failed to build file structure"
                })

            # Get the HTML template
            logger.debug("Preparing HTML template...")
            html_template = await self.template_manager.get_html_template()

            # Customize title if provided
            if title:
                html_template = html_template.replace(
                    "<h3 style=\"margin: 0 16px 16px 16px;\">Agent C Output Viewer</h3>",
                    f"<h3 style=\"margin: 0 16px 16px 16px;\">{title}</h3>")

            # Replace placeholder with file structure
            json_structure = json.dumps(file_structure)
            html_content = html_template.replace('$FILE_STRUCTURE', json_structure)

            # Write the generated HTML to the workspace
            logger.debug("Writing HTML viewer to output location...")
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

            # Get file system path and raise a media event
            file_system_path = await self._get_file_system_path(output_path_full)

            # Create output info dictionary
            output_info = {
                "output_filename": output_filename,
                "output_path": output_path_full,
                "file_system_path": file_system_path,
                "file_count": len(markdown_files)
            }

            # Generate and raise HTML content for the result
            try:
                html_content = await self.media_helper.create_result_html(output_info)
                await self._raise_render_media(
                    sent_by_class=self.__class__.__name__,
                    sent_by_function='generate_md_viewer',
                    content_type="text/html",
                    content=html_content
                )
                # markdown_content = await self.media_helper.create_markdown_media(output_info)
                # await self._raise_render_media(
                #     sent_by_class=self.__class__.__name__,
                #     sent_by_function='generate_report',
                #     content_type="text/markdown",  # Use text/markdown content type
                #     content=markdown_content
                # )
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


    @json_schema(
        description="Convert a markdown file to Word (DOCX) format",
        params={
            "workspace": {
                "type": "string",
                "description": "The workspace containing the markdown file",
                "required": True
            },
            "input_path": {
                "type": "string",
                "description": "The path to the markdown file to convert (UNC-style or relative to workspace)",
                "required": True
            },
            "output_filename": {
                "type": "string",
                "description": "filename for the output Word document",
                "required": False
            },
            "style": {
                "type": "string",
                "description": "Style template to use",
                "enum": ["default", "academic", "business", "minimal"],
                "required": False,
                "default": "default"
            },
            "include_toc": {
                "type": "boolean",
                "description": "Whether to include a table of contents",
                "required": False,
                "default": True
            },
            "page_break_level": {
                "type": "integer",
                "description": "Insert page breaks before headings of this level (1-6)",
                "required": False,
                "default": 1
            }
        }
    )
    async def markdown_to_docx(self, **kwargs) -> str:
        """Convert a markdown file to Word (DOCX) format.

        Args:
            kwargs:
                workspace: The workspace containing the markdown file
                input_path: The path to the markdown file to convert (UNC-style or relative to workspace)
                output_path: Output path for the Word document (UNC-style or relative to workspace)
                style: Style template to use (default, academic, business, minimal)
                include_toc: Whether to include a table of contents
                page_break_level: Insert page breaks before headings of this level (1-6)

        Returns:
            A dictionary with success status and information about the operation
        """
        """Convert a markdown file to Word (DOCX) format."""
        if not self.docx_converter.docx_conversion_available:
            return json.dumps({
                "success": False,
                "error": "Required dependencies not available. Please install python-markdown, python-docx, and beautifulsoup4."
            })

        workspace = kwargs.get('workspace')
        input_path = kwargs.get('input_path')
        output_filename = kwargs.get('output_filename')
        style = kwargs.get('style', 'default')
        include_toc = kwargs.get('include_toc', True)
        page_break_level = kwargs.get('page_break_level', 1)

        # Validate required fields
        validation_error = self.validation_helper.validate_required_fields(
            kwargs, ["workspace", "input_path"])
        if validation_error:
            return json.dumps({"success": False, "error": validation_error})

        try:
            # Process paths
            input_path_full = self.path_helper.ensure_unc_path(input_path, workspace)

            # Validate input path
            error, workspace_obj, rel_path = await self.validation_helper.validate_path(input_path_full)
            if error:
                return json.dumps({"success": False, "error": f"Invalid input path: {error}"})

            # Extract the filename using string manipulation
            normalized_path = self.path_helper.normalize_path(input_path_full)
            input_filename = normalized_path.split('/')[-1]

            if not self.path_helper.is_markdown_file(normalized_path):
                return json.dumps({
                    "success": False,
                    "error": f"Input file '{normalized_path}' does not appear to be a markdown file. Expected a .md or .markdown extension."
                })

            # Determine output path
            if not output_filename:
                # Use the same name as the input but with .docx extension
                output_filename = Path(input_filename).stem + ".docx"
                output_path_full = f"//{workspace}/{output_filename}"
            elif not output_filename.startswith('//'):
                # Ensure it has .docx extension
                output_filename = self.path_helper.ensure_file_extension(output_filename, 'docx')
                output_path_full = f"//{workspace}/{output_filename}"
            else:
                output_path_full = output_filename

            # Validate output path
            error, _, _ = await self.validation_helper.validate_path(output_path_full)
            if error:
                return json.dumps({"success": False, "error": f"Output path issue: {error}"})

            # Read and Process the markdown file
            file_content = await self.workspace_tool.read(path=input_path_full)
            if file_content.startswith('{"error":'):
                raise ValueError(f"Error reading file: {file_content}")

            # Convert markdown to Word document
            docx_content_bytes = await self.docx_converter.convert_to_docx(
                file_content, style, include_toc, page_break_level)

            try:
                write_result = await self.workspace_tool.internal_write_bytes(
                    path=output_path_full,
                    data=docx_content_bytes,
                    mode="write",
                )
            except Exception as e:
                logger.error(f"Error writing docx file: {e}")
                return json.dumps({
                    "success": False,
                    "error": f"Failed to write Word document: {str(e)}"
                })

            write_data = json.loads(write_result)
            if 'error' in write_data:
                return json.dumps({
                    "success": False,
                    "error": f"Failed to write Word document: {write_data['error']}"
                })

            # Get file system path
            file_system_path = await self._get_file_system_path(output_path_full)

            # Prepare output summary
            result = {
                "success": True,
                "message": f"Successfully converted markdown to Word document at {output_path_full}",
                "input_file": input_path_full,
                "output_file": output_path_full,
                "workspace": workspace,
                "style": style
            }

            # Create output info dictionary for media event
            output_info = {
                "type": "docx",
                "output_filename": output_filename,
                "output_path": output_path_full,
                "file_system_path": file_system_path,
                "style": style
            }

            # Generate and raise HTML content for the result
            try:
                html_content = await self.media_helper.create_result_html(output_info)
                await self._raise_render_media(
                    sent_by_class=self.__class__.__name__,
                    sent_by_function='markdown_to_docx',
                    content_type="text/html",
                    content=html_content
                )
            except Exception as e:
                logger.error(f"Failed to raise media event: {str(e)}")

            return json.dumps(result)

        except Exception as e:
            logger.exception("Error converting markdown to Word document")
            return json.dumps({
                "success": False,
                "error": f"Error converting markdown to Word document: {str(e)}"
            })


# Register the toolset with the Agent C framework
Toolset.register(MarkdownToHtmlReportTools, required_tools=['WorkspaceTools'])
