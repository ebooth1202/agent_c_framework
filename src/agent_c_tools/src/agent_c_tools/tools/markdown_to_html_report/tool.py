import json
import logging
from pathlib import Path
from typing import Optional
import re

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from .helpers.markdown_file_collector import MarkdownFileCollector
from .helpers.markdown_to_docx import MarkdownToDocxConverter
from ... import WorkspaceTools
from ...helpers.path_helper import create_unc_path, ensure_file_extension, os_file_system_path, has_file_extension, normalize_path
from ...helpers.validate_kwargs import validate_required_fields

logger = logging.getLogger(__name__)

# Constants for magic values
class Constants:
    """Configuration constants for the markdown tools."""
    DEFAULT_TITLE = "Agent C Output Viewer"
    DEFAULT_TITLE_PLACEHOLDER = "<h3 style=\"margin: 0 16px 16px 16px;\">Agent C Output Viewer</h3>"
    MARKDOWN_EXTENSIONS = ['md', 'markdown']
    DOCX_EXTENSIONS = ['.md', '.markdown']

    # JavaScript safety escape patterns
    JS_ESCAPE_PATTERNS = [
        (r'\$"', '&#36;"'),           # C# interpolated strings
        (r'\$\{', '&#36;&#123;'),     # Template literal expressions
        (r'\}', '&#125;'),            # Closing braces
        (r'`', '&#96;'),              # Backticks
        (r'</script>', '&#60;/script&#62;'),  # Script tags
        (r'<script>', '&#60;script&#62;'),
    ]


class MarkdownToHtmlReportTools(Toolset):
    """Toolset for generating interactive HTML viewers from markdown files in a workspace."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs, name="markdown_viewer", use_prefix=False)
        # Get workspace tools for file operations
        self.workspace_tool: Optional[WorkspaceTools] = None
        self.file_collector = None
        self.docx_converter = MarkdownToDocxConverter()

    async def post_init(self):
        self.workspace_tool = self.tool_chest.available_tools.get("WorkspaceTools")
        self.file_collector = MarkdownFileCollector(self.workspace_tool)

    @staticmethod
    async def _safe_operation(operation_name, operation_func, *args, **kwargs):
        """Execute operations with standardized error handling."""
        try:
            return await operation_func(*args, **kwargs)
        except Exception as e:
            logger.exception(f"Error in {operation_name}: {str(e)}")
            return {"success": False, "error": f"Error in {operation_name}: {str(e)}"}

    @staticmethod
    def _parse_workspace_result(result: str, operation_name: str = "workspace operation"):
        """Parse workspace tool results that may be JSON, YAML, or error strings.
        
        Args:
            result: The result string from a workspace tool method
            operation_name: Name of the operation for error reporting
            
        Returns:
            tuple: (success: bool, data: dict|str, error_msg: str|None)
        """
        if not isinstance(result, str):
            return False, None, f"Expected string result from {operation_name}, got {type(result)}"
            
        # Check for error responses
        if result.startswith(("Error:", "ERROR:")):
            return False, None, result
            
        # Try JSON first (most common for write operations)
        try:
            data = json.loads(result)
            if isinstance(data, dict) and 'error' in data:
                return False, data, data['error']
            return True, data, None
        except json.JSONDecodeError:
            pass
            
        # Try YAML (common for ls operations)
        try:
            import yaml
            data = yaml.safe_load(result)
            if isinstance(data, dict) and 'error' in data:
                return False, data, data['error']
            return True, data, None
        except Exception:
            pass
            
        # If all parsing fails, treat as raw string (might be success message)
        if "success" in result.lower() or "completed" in result.lower():
            return True, result, None
        else:
            return False, None, f"Could not parse {operation_name} result: {result}"

    @json_schema(
        description="Generate an interactive HTML viewer for markdown files in a workspace directory",
        params={
            "workspace": {
                "type": "string",
                "description": "The workspace containing the markdown files",
                "required": True
            },
            "file_path": {
                "type": "string",
                "description": "The relative path within the workspace where markdown file(s) are located",
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
            },
            "javascript_safe": {
                "type": "boolean",
                "description": "Whether to apply JavaScript safety processing to handle problematic patterns like C# interpolated strings (recommended: true)",
                "required": False,
                "default": True
            }
        }
    )
    async def generate_md_viewer(self, **kwargs) -> str:
        """Generate an interactive HTML viewer for markdown files in a workspace directory."""
        # Validate required fields
        success, validation_error = validate_required_fields(
            kwargs, ["workspace", "file_path", "output_filename"])
        if not success:
            return self._create_error_response(validation_error)

        # Extract parameters
        workspace = kwargs.get('workspace')
        input_path = kwargs.get('file_path')
        output_filename = kwargs.get('output_filename')
        title = kwargs.get('title', 'output_report.html')
        files_to_ignore = kwargs.get('files_to_ignore', [])
        javascript_safe = kwargs.get('javascript_safe', True)
        tool_context = kwargs.get('tool_context', {})

        try:
            # Validate and process paths
            input_path_full, output_path_full, path_error = await self._validate_and_process_paths(
                workspace, input_path, output_filename)
            if path_error:
                return self._create_error_response(path_error)

            # Determine if input is a file or directory and process accordingly
            file_structure = None
            file_count = 0

            # Check if input is a single markdown file
            if has_file_extension(input_path, Constants.MARKDOWN_EXTENSIONS):
                file_structure, file_count, error = await self._handle_single_file_conversion(
                    input_path_full, input_path, javascript_safe)

                # If single file processing failed, treat as directory
                if error:
                    file_structure, file_count, error = await self._handle_directory_conversion(
                        input_path_full, input_path, files_to_ignore, output_filename, javascript_safe, tool_context)
            else:
                # Treat as directory
                file_structure, file_count, error = await self._handle_directory_conversion(
                    input_path_full, input_path, files_to_ignore, output_filename, javascript_safe, tool_context)

            if error:
                return self._create_error_response(error)

            if not file_structure:
                return self._create_error_response("Failed to build file structure")

            # Generate HTML output
            html_content, html_error = await self._generate_html_output(file_structure, title, output_path_full)
            if html_error:
                return self._create_error_response(html_error)

            # Raise media event
            await self._raise_media_event(output_filename, output_path_full, file_count, tool_context)

            # Return success response
            message = f"Successfully generated HTML viewer at {output_filename}."
            logger.debug(message)

            return self._create_success_response(
                message,
                output_file=output_filename,
                output_path=output_path_full,
                workspace=workspace,
                file_count=file_count
            )

        except Exception as e:
            logger.exception("Error generating markdown viewer")
            return self._create_error_response(f"Error generating markdown viewer: {str(e)}")

    @json_schema(
        description="Generate an interactive HTML viewer with custom file hierarchy structure",
        params={
            "workspace": {
                "type": "string",
                "description": "The workspace containing the markdown files",
                "required": True
            },
            "output_filename": {
                "type": "string",
                "description": "The name of the output HTML file to generate (can be a simple filename or full UNC path)",
                "required": True
            },
            "custom_structure": {
                "type": "string",
                "description": "JSON string defining custom hierarchy. Example: '{\"items\": [{\"type\": \"folder\", \"name\": \"Getting Started\", \"children\": [{\"type\": \"file\", \"name\": \"Introduction\", \"path\": \"intro.md\"}]}, {\"type\": \"file\", \"name\": \"API Reference\", \"path\": \"api.md\"}]}'",
                "required": True
            },
            "title": {
                "type": "string",
                "description": "Optional title for the HTML viewer (displayed in the sidebar)",
                "required": False
            }
        }
    )
    async def generate_custom_md_viewer(self, **kwargs) -> str:
        """Generate an interactive HTML viewer with custom file hierarchy structure."""
        success, validation_error = validate_required_fields(
            kwargs, ["workspace", "output_filename", "custom_structure"])

        # Validate required fields
        if not success:
            return self._create_error_response(validation_error)

        workspace = kwargs.get('workspace')
        output_filename = kwargs.get('output_filename')
        custom_structure_json = kwargs.get('custom_structure')
        title = kwargs.get('title', 'Custom Markdown Viewer')

        try:
            # Parse the custom structure JSON
            try:
                custom_structure = json.loads(custom_structure_json)
            except json.JSONDecodeError as e:
                return self._create_error_response(f"Invalid JSON in custom_structure: {str(e)}")

            # Create base path for file resolution
            base_path = f"//{workspace}"

            # Initialize the file collector
            file_collector = MarkdownFileCollector(self.workspace_tool)

            # Validate the custom structure and collect files
            logger.debug("Validating custom structure and collecting markdown files...")
            try:
                # Use enhanced validation from MarkdownFileCollector
                is_valid, error_msg = await file_collector.validate_custom_structure(custom_structure, base_path)
                if not is_valid:
                    return self._create_error_response(f"Invalid custom structure: {error_msg}")

                # Build the structure using enhanced MarkdownFileCollector
                structure = await file_collector.build_custom_structure(custom_structure, base_path)
                
                if not structure:
                    return self._create_error_response("No valid markdown files found in the custom structure")

            except ValueError as e:
                return self._create_error_response(str(e))

            # Count files in the structure
            file_count = self._count_files_in_structure(structure)
            logger.debug(f"Found {file_count} markdown files. Preparing HTML template...")

            # Create UNC output filename
            output_filename = ensure_file_extension(output_filename, 'html')
            if not output_filename.startswith('//'):
                output_path_full = create_unc_path(workspace, output_filename)
            else:
                output_path_full = output_filename

            # Get the HTML template
            html_template = await self._get_html_template()

            # Customize title
            html_template = html_template.replace(
                Constants.DEFAULT_TITLE_PLACEHOLDER,
                f"<h3 style=\"margin: 0 16px 16px 16px;\">{title}</h3>")

            # Replace placeholder with the processed structure
            json_structure = json.dumps(structure, ensure_ascii=False)
            html_content = html_template.replace('$FILE_STRUCTURE', json_structure)

            # Write the generated HTML to the workspace
            logger.debug("Writing HTML viewer to output location...")
            write_result = await self.workspace_tool.write(
                path=output_path_full,
                data=html_content,
                mode="write"
            )

            # Handle potential empty or invalid JSON response
            try:
                if not write_result or write_result.strip() == "":
                    # If write_result is empty, assume success (some workspace tools return empty on success)
                    write_data = {"success": True}
                else:
                    write_data = json.loads(write_result)
            except json.JSONDecodeError as e:
                # Check if it's a plain text success message
                if write_result and ("successfully written" in write_result.lower() or
                                   "success" in write_result.lower() or
                                   "data written" in write_result.lower() or
                                   "file created" in write_result.lower()):
                    logger.debug(f"Received plain text success message: {write_result}")
                    write_data = {"success": True}
                else:
                    logger.error(f"Failed to parse workspace write response: {write_result}")
                    return self._create_error_response(f"Invalid response from workspace write operation: {str(e)}")

            if 'error' in write_data:
                return self._create_error_response(f"Failed to write HTML file: {write_data['error']}")

            message = f"Successfully generated custom HTML viewer at {output_filename}."
            logger.debug(message)

            # Get file system path and raise a media event
            file_system_path = os_file_system_path(self.workspace_tool, output_path_full)

            # Create output info dictionary
            output_info = {
                "output_filename": output_filename,
                "output_path": output_path_full,
                "file_system_path": file_system_path,
                "file_count": file_count,
                "custom_structure": True
            }

            # Generate and raise HTML content for the result
            try:
                html_content = await self._create_result_html(output_info)
                await self._raise_render_media(
                    sent_by_class=self.__class__.__name__,
                    sent_by_function='generate_custom_md_viewer',
                    content_type="text/html",
                    content=html_content
                )
            except Exception as e:
                logger.error(f"Failed to raise media event: {str(e)}")

            return self._create_success_response(
                message,
                output_file=output_filename,
                output_path=output_path_full,
                workspace=workspace,
                file_count=file_count,
                structure_type="custom"
            )

        except Exception as e:
            logger.exception("Error generating custom markdown viewer")
            return self._create_error_response(f"Error generating custom markdown viewer: {str(e)}")

    def _count_files_in_structure(self, structure):
        """Count the number of files in a processed structure.
        
        Args:
            structure: The processed structure from MarkdownFileCollector
            
        Returns:
            Number of files found
        """
        file_count = 0
        
        for item in structure:
            if item.get('type') == 'file':
                file_count += 1
            elif item.get('type') == 'folder' and 'children' in item:
                file_count += self._count_files_in_structure(item['children'])
                
        return file_count


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
                "description": "The relative path to the markdown file to convert",
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
        """Convert a markdown file to Word (DOCX) format."""
        if not self.docx_converter.docx_conversion_available:
            return self._create_error_response("Required dependencies not available. Please install python-markdown, python-docx, and beautifulsoup4.")

        # Validate required fields
        success, validation_error = validate_required_fields(
            kwargs, ["workspace", "input_path"])
        if not success:
            return self._create_error_response(validation_error)

        workspace = kwargs.get('workspace')
        input_path = kwargs.get('input_path')
        output_filename = kwargs.get('output_filename')
        style = kwargs.get('style', 'default')
        include_toc = kwargs.get('include_toc', True)
        page_break_level = kwargs.get('page_break_level', 1)

        try:
            # Process paths
            input_path_full = create_unc_path(workspace, input_path)

            if not has_file_extension(input_path_full, Constants.DOCX_EXTENSIONS):
                return self._create_error_response(f"Input file '{input_path_full}' is not a markdown file.")

            input_filename = normalize_path(input_path_full).split('/')[-1]

            # Determine output path
            if not output_filename:
                # Use the same name as the input but with .docx extension
                output_filename = Path(input_filename).stem + ".docx"
                output_path_full = f"//{workspace}/{output_filename}"
            elif not output_filename.startswith('//'):
                # Ensure it has .docx extension
                output_filename = ensure_file_extension(output_filename, 'docx')
                output_path_full = f"//{workspace}/{output_filename}"
            else:
                output_path_full = output_filename

            # Read and Process the markdown file
            error, workspace_obj, relative_path = self.workspace_tool.validate_and_get_workspace_path(input_path_full)
            if error:
                raise ValueError(f"Error reading file: {error}")
            file_content = await workspace_obj.read_internal(relative_path)

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
                return self._create_error_response(f"Failed to write Word document: {str(e)}")

            # Parse the write result using the helper function
            success, write_data, error_msg = self._parse_workspace_result(write_result, "write operation")
            if not success:
                return self._create_error_response(f"Failed to write Word document: {error_msg}")

            # Get file system path
            file_system_path = os_file_system_path(self.workspace_tool, output_path_full)

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
                html_content = await self._create_result_html(output_info)
                await self._raise_render_media(
                    sent_by_class=self.__class__.__name__,
                    sent_by_function='markdown_to_docx',
                    content_type="text/html",
                    content=html_content,
                    tool_context=kwargs.get('tool_context', {})
                )
            except Exception as e:
                logger.error(f"Failed to raise media event: {str(e)}")

            return self._create_success_response(
                f"Successfully converted markdown to Word document at {output_path_full}",
                input_file=input_path_full,
                output_file=output_path_full,
                workspace=workspace,
                style=style
            )

        except Exception as e:
            logger.exception("Error converting markdown to Word document")
            return self._create_error_response(f"Error converting markdown to Word document: {str(e)}")

    def _create_error_response(self, error_message: str) -> str:
        """Create a standardized error response."""
        return json.dumps({"success": False, "error": error_message})

    def _create_success_response(self, message: str, **additional_data) -> str:
        """Create a standardized success response."""
        response = {
            "success": True,
            "message": message,
            **additional_data
        }
        return json.dumps(response)

    async def _validate_and_process_paths(self, workspace: str, input_path: str, output_filename: str) -> tuple:
        """
        Validate and process input/output paths.

        Returns:
            tuple: (input_path_full, output_path_full, error_message)
            If error_message is not None, the operation failed.
        """
        try:
            # Create UNC input path
            input_path_full = create_unc_path(workspace, input_path)

            # Create UNC output filename
            output_filename = ensure_file_extension(output_filename, 'html')
            if not output_filename.startswith('//'):
                output_path_full = create_unc_path(workspace, output_filename)
            else:
                output_path_full = output_filename

            return input_path_full, output_path_full, None
        except Exception as e:
            return None, None, f"Error processing paths: {str(e)}"

    async def _handle_single_file_conversion(self, input_path_full: str, input_path: str, javascript_safe: bool) -> tuple:
        """
        Handle conversion of a single markdown file.

        Returns:
            tuple: (file_structure, file_count, error_message)
            If error_message is not None, the operation failed.
        """
        try:
            error, workspace_obj, relative_path = self.workspace_tool.validate_and_get_workspace_path(input_path_full)
            if error:
                return None, 0, f"Input path '{input_path}' is not accessible: {error}"

            # Read file content
            file_content = await workspace_obj.read_internal(relative_path)
            if file_content.startswith('{"error":'):
                return None, 0, f"Error reading file at {input_path}: {file_content}"

            # Process content for JavaScript safety if needed
            if javascript_safe:
                file_content = self._process_javascript_safe_content(file_content)

            # Create file structure
            file_name = Path(input_path).name
            file_structure = [{
                'name': file_name,
                'type': 'file',
                'path': file_name,
                'content': file_content
            }]

            logger.debug(f"Converting single markdown file: {input_path}")
            return file_structure, 1, None

        except Exception as e:
            return None, 0, f"Error processing single file: {str(e)}"

    async def _handle_directory_conversion(self, input_path_full: str, input_path: str, files_to_ignore: list,
                                         output_filename: str, javascript_safe: bool, tool_context: dict) -> tuple:
        """
        Handle conversion of a directory containing markdown files.

        Returns:
            tuple: (file_structure, file_count, error_message)
            If error_message is not None, the operation failed.
        """
        try:
            # Use the file collector to gather markdown files first
            logger.debug(f"Converting directory: {input_path}")

            # Step 1: Collect all markdown files in the directory
            markdown_files = await self.file_collector.collect_markdown_files(
                root_path=input_path_full,
                tool_context=tool_context,
                files_to_ignore=files_to_ignore
            )

            if not markdown_files:
                return None, 0, f"No markdown files found in directory: {input_path}"

            # Step 2: Build the hierarchical structure from the collected files
            structure = await self.file_collector.build_file_structure(
                root_path=input_path_full,
                markdown_files=markdown_files,
                safe_processing=javascript_safe
            )

            if not structure:
                return None, 0, f"Failed to build file structure for directory: {input_path}"

            file_count = self._count_files_in_structure(structure)
            logger.debug(f"Found {file_count} markdown files in directory")

            return structure, file_count, None

        except Exception as e:
            logger.exception("Error processing directory")
            return None, 0, f"Error processing directory: {str(e)}"

    async def _generate_html_output(self, file_structure: list, title: str, output_path_full: str) -> tuple:
        """
        Generate HTML output from file structure.

        Returns:
            tuple: (html_content, error_message)
            If error_message is not None, the operation failed.
        """
        try:
            # Get the HTML template
            html_template = await self._get_html_template()

            # Customize title
            html_template = html_template.replace(
                Constants.DEFAULT_TITLE_PLACEHOLDER,
                f"<h3 style=\"margin: 0 16px 16px 16px;\">{title}</h3>")

            # Replace placeholder with the processed structure
            json_structure = json.dumps(file_structure, ensure_ascii=False)
            html_content = html_template.replace('$FILE_STRUCTURE', json_structure)

            # Write the generated HTML to the workspace
            logger.debug("Writing HTML viewer to output location...")
            write_result = await self.workspace_tool.write(
                path=output_path_full,
                data=html_content,
                mode="write"
            )

            # Handle potential empty or invalid JSON response
            try:
                if not write_result or write_result.strip() == "":
                    # If write_result is empty, assume success (some workspace tools return empty on success)
                    write_data = {"success": True}
                else:
                    write_data = json.loads(write_result)
            except json.JSONDecodeError as e:
                # Check if it's a plain text success message
                if write_result and ("successfully written" in write_result.lower() or
                                   "success" in write_result.lower() or
                                   "data written" in write_result.lower() or
                                   "file created" in write_result.lower()):
                    logger.debug(f"Received plain text success message: {write_result}")
                    write_data = {"success": True}
                else:
                    logger.error(f"Failed to parse workspace write response: {write_result}")
                    return self._create_error_response(f"Invalid response from workspace write operation: {str(e)}")

            if 'error' in write_data:
                return None, f"Failed to write HTML file: {write_data['error']}"

            return html_content, None

        except Exception as e:
            logger.exception("Error generating HTML output")
            return None, f"Error generating HTML output: {str(e)}"

    async def _raise_media_event(self, output_filename: str, output_path_full: str, file_count: int, tool_context: dict):
        """Generate and raise media event for the result."""
        try:
            # Get file system path and raise a media event
            file_system_path = os_file_system_path(self.workspace_tool, output_path_full)

            # Create output info dictionary
            output_info = {
                "output_filename": output_filename,
                "output_path": output_path_full,
                "file_system_path": file_system_path,
                "file_count": file_count
            }

            # Generate and raise HTML content for the result
            html_content = await self._create_result_html(output_info)
            await self._raise_render_media(
                sent_by_class=self.__class__.__name__,
                sent_by_function='generate_md_viewer',
                content_type="text/html",
                content=html_content,
                tool_context=tool_context
            )
        except Exception as e:
            logger.error(f"Failed to raise media event: {str(e)}")

    async def _get_html_template(self) -> str:
        """Get the HTML template for the viewer."""
        try:
            from .helpers.html_template_manager import HtmlTemplateManager
            template_manager = HtmlTemplateManager()
            return await template_manager.get_html_template()
        except Exception as e:
            logger.error(f"Failed to get HTML template: {str(e)}")
            raise

    def _process_javascript_safe_content(self, content: str) -> str:
        """Process content to make it JavaScript-safe by escaping problematic patterns."""
        try:
            from .helpers.javascript_safe_content_processor import JavaScriptSafeContentProcessor
            processor = JavaScriptSafeContentProcessor()
            return processor.process_content(content)
        except Exception as e:
            logger.error(f"Failed to process JavaScript-safe content: {str(e)}")
            return content  # Return original content if processing fails

    async def _create_result_html(self, output_info: dict) -> str:
        """Create HTML content for result media events."""
        try:
            from .helpers.media_helper import MediaEventHelper
            media_helper = MediaEventHelper()
            return await media_helper.create_result_html(output_info)
        except Exception as e:
            logger.error(f"Failed to create result HTML: {str(e)}")
            # Return basic HTML as fallback
            return f"""
            <div style="padding: 16px; background: #f8f9fa; border-radius: 8px; margin: 8px 0;">
                <h4 style="margin: 0 0 8px 0; color: #28a745;">✅ File Generated Successfully</h4>
                <p style="margin: 4px 0;"><strong>Output:</strong> {output_info.get('output_filename', 'Unknown')}</p>
                <p style="margin: 4px 0;"><strong>Files Processed:</strong> {output_info.get('file_count', 0)}</p>
            </div>
            """

    async def _raise_render_media(self, sent_by_class: str, sent_by_function: str,
                                content_type: str, content: str, tool_context: dict = None):
        """Raise a render media event."""
        try:
            if tool_context and hasattr(self.tool_chest, '_raise_render_media'):
                await self.tool_chest._raise_render_media(
                    sent_by_class=sent_by_class,
                    sent_by_function=sent_by_function,
                    content_type=content_type,
                    content=content,
                    tool_context=tool_context
                )
        except Exception as e:
            logger.error(f"Failed to raise render media event: {str(e)}")


# Register the toolset
Toolset.register(MarkdownToHtmlReportTools, required_tools=['WorkspaceTools'])
