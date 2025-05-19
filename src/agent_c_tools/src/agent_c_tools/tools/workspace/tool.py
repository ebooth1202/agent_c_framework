import json
import logging
import re
import yaml
from typing import Any, List, Tuple, Optional, Callable, Awaitable, Union
from ts_tool import api
from yaml import FullLoader

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from agent_c_tools.tools.workspace.base import BaseWorkspace
from agent_c_tools.tools.workspace.prompt import WorkspaceSection
from agent_c_tools.tools.workspace.util import ReplaceStringsHelper

class WorkspaceTools(Toolset):
    """
    WorkspaceTools allows the model to read / write data to one or more workspaces.
    This allows us to abstract things like S3, Azure Storage and the like.

    Uses UNC-style paths (//WORKSPACE/path) to reference files and directories.
    """

    UNC_PATH_PATTERN = r'^//([^/]+)(?:/(.*))?$'

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs, name="workspace")
        self.workspaces: List[BaseWorkspace] = kwargs.get('workspaces', [])
        self._create_section()
        self.logger = logging.getLogger(__name__)
        self.replace_helper = ReplaceStringsHelper()

    def add_workspace(self, workspace: BaseWorkspace) -> None:
        """Add a workspace to the list of workspaces."""
        self.workspaces.append(workspace)
        self._create_section()

    def _create_section(self):
        self.section = WorkspaceSection(tool=self)

    def find_workspace_by_name(self, name):
        """Find a workspace by its name."""
        try:
            norm_name = name.lower()
            return next(workspace for workspace in self.workspaces if workspace.name == norm_name)
        except StopIteration:
            # Handle the case where no workspace with the given name is found
            self.logger.warning(f"No workspace found with the name: {name}")
            return None

    def _parse_unc_path(self, path: str) -> Tuple[Optional[str], Optional[BaseWorkspace], Optional[str]]:
        """
        Parse a UNC path (//WORKSPACE/path) into workspace name and relative path.

        Args:
            path (str): The UNC path to parse

        Returns:
            Tuple[Optional[str], Optional[str], Optional[str]]:
                - Error message (if any)
                - Workspace name (if no error)
                - Relative path (if no error)
        """
        if not path:
            return "Path cannot be empty", None, None

        match = re.match(self.UNC_PATH_PATTERN, path)
        if not match:
            return f"Invalid UNC path format: {path}. Expected format: //WORKSPACE/path", None, None

        workspace_name = match.group(1)
        relative_path = match.group(2) or ''

        workspace = self.find_workspace_by_name(workspace_name)
        if workspace is None:
            return f"No workspace found with the name: {workspace_name}", None, None

        return None, workspace, relative_path

    async def _run_cp_or_mv(self, operation: Callable[[object, str, str], Awaitable[str]], *, src_path: str, dest_path: str) -> str:
        """
        Validate UNC paths, ensure same workspace, then perform the operation.
        """
        # Validate paths
        src_error, src_workspace, src_relative_path = self.validate_and_get_workspace_path(src_path)
        if src_error:
            return json.dumps({'error': src_error})

        dest_error, dest_workspace, dest_relative_path = self.validate_and_get_workspace_path(dest_path)
        if dest_error:
            return json.dumps({'error': dest_error})

        # Same-workspace check
        if src_workspace != dest_workspace:
            error_msg = ("Cross-workspace operations are not supported. "
                         "Source and destination must be in the same workspace.")
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        # Do the copy or move
        return await operation(src_workspace, src_relative_path, dest_relative_path)

    def validate_and_get_workspace_path(self, unc_path: str) -> Tuple[Optional[str], Optional[BaseWorkspace], Optional[str]]:
        """
        Validate a UNC path and return the workspace object and relative path.

        Args:
            unc_path (str): UNC-style path to validate

        Returns:
            Tuple[Optional[str], Optional[BaseWorkspace], Optional[str]]:
                - Error message (if any)
                - Workspace object (if no error)
                - Relative path (if no error)
        """
        error, workspace, relative_path = self._parse_unc_path(unc_path)
        if error:
            self.logger.error(error)
            return error, None, None

        return None, workspace, relative_path

    @json_schema(
        'List the contents of a directory using UNC-style path (//WORKSPACE/path)',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to list contents for',
                'required': True
            }
        }
    )
    async def ls(self, **kwargs: Any) -> str:
        """Asynchronously lists the contents of a workspace directory.

        Args:
            **kwargs: Keyword arguments.
                path (str): UNC-style path (//WORKSPACE/path) to list contents for

        Returns:
            str: JSON string with the listing or an error message.
        """
        unc_path = kwargs.get('path', '')

        error, workspace, relative_path = self.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        return await workspace.ls(relative_path)

    @json_schema(
        'Retrieve a string "tree" of the directory structure using UNC-style path',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to start the tree from',
                'required': True
            },
            'folder_depth': {
                'type': 'integer',
                'description': 'Depth of folders to include in the tree',
                'required': False
            },
            'file_depth': {
                'type': 'integer',
                'description': 'Depth of files to include in the tree',
                'required': False
            }
        }
    )
    async def tree(self, **kwargs: Any) -> str:
        """Asynchronously generates a tree view of a directory.

        Args:
            **kwargs: Keyword arguments.
                path (str): UNC-style path (//WORKSPACE/path) to start the tree from
                folder_depth (int): Depth of folders to include in the tree, default 5
                file_depth (int): Depth of files to include in the tree, default 3

        Returns:
            str: JSON string with the tree view or an error message.
        """
        unc_path = kwargs.get('path', '')
        folder_depth = kwargs.get('folder_depth', 5)
        file_depth = kwargs.get('file_depth', 3)

        error, workspace, relative_path = self.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        return await workspace.tree(relative_path, folder_depth, file_depth)

    @json_schema(
        'Reads the contents of a text file using UNC-style path',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to read',
                'required': True
            }
        }
    )
    async def read(self, **kwargs: Any) -> str:
        """Asynchronously reads the content of a text file.

        Args:
            **kwargs: Keyword arguments.
                path (str): UNC-style path (//WORKSPACE/path) to the file to read

        Returns:
            str: JSON string with the file content or an error message.
        """
        unc_path = kwargs.get('path', '')

        error, workspace, relative_path = self.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        return await workspace.read(relative_path)

    @json_schema(
        'Writes or appends text data to a file using UNC-style path',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to write',
                'required': True
            },
            'data': {
                'type': 'string',
                'description': 'The text data to write or append to the file',
                'required': True
            },
            'mode': {
                'type': 'string',
                'description': 'The writing mode: "write" to overwrite or "append" to add to the file',
                'required': False
            }
        }
    )
    async def write(self, **kwargs: Any) -> str:
        """Asynchronously writes or appends data to a file.

        kwargs:
            path (str): UNC-style path (//WORKSPACE/path) to the file to write
            data (Union[str, bytes]): The text or binary data to write or append to the file
            mode (str): The writing mode, either 'write' to overwrite or 'append'
            data_type (str): Type of data being written, either 'text' for plain text or 'binary' for base64-encoded binary data

        Returns:
            str: JSON string with a success message or an error message.
        """
        unc_path = kwargs.get('path', '')
        data = kwargs['data']
        mode = kwargs.get('mode', 'write')

        error, workspace, relative_path = self.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        return await workspace.write(relative_path, mode, data)

    async def internal_write_bytes(self, path: str, data: Union[str, bytes], mode: str) -> str:
        """Asynchronously writes or appends binary data to a file.  This is an internal workspace function, not available to agents.

        Arguments:
            path (str): UNC-style path (//WORKSPACE/path) to the file to write
            data (Union[str, bytes]): The text or binary data to write or append to the file
            mode (str): The writing mode, either 'write' to overwrite or 'append'

        Returns:
            str: JSON string with a success message or an error message.
        """

        error, workspace, relative_path = self.validate_and_get_workspace_path(path)
        if error:
            return json.dumps({'error': error})

        return await workspace.write_bytes(relative_path, mode, data)

    @json_schema(
        'Copy a file or directory using UNC-style paths',
        {
            'src_path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the source',
                'required': True
            },
            'dest_path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the destination',
                'required': True
            }
        }
    )
    async def cp(self, **kwargs: Any) -> str:
        """Asynchronously copies a file or directory.

        Args:
            src_path (str): UNC-style path (//WORKSPACE/path) to the source
            dest_path (str): UNC-style path (//WORKSPACE/path) to the destination

        Returns:
            str: JSON string with the result or an error message.
        """
        src_unc_path = kwargs.get('src_path', '')
        dest_unc_path = kwargs.get('dest_path', '')

        return await self._run_cp_or_mv(
            operation=lambda workspace, source_path, destination_path: workspace.cp(source_path, destination_path),
            src_path=src_unc_path,
            dest_path=dest_unc_path,
        )

    @json_schema(
        'Check if a path is a directory using UNC-style path',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to check',
                'required': True
            }
        }
    )
    async def is_directory(self, **kwargs: Any) -> str:
        """Asynchronously checks if a path is a directory.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to check

        Returns:
            str: JSON string with the result or an error message.
        """
        unc_path = kwargs.get('path', '')

        error, workspace, relative_path = self.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        try:
            result = await workspace.is_directory(relative_path)
            return json.dumps({'is_directory': result})
        except Exception as e:
            error_msg = f'Error checking if path is a directory: {e}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})
    
    @json_schema(
        'Move a file or directory using UNC-style paths',
        {
            'src_path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the source',
                'required': True
            },
            'dest_path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the destination',
                'required': True
            }
        }
    )
    async def mv(self, **kwargs: Any) -> str:
        """Asynchronously moves a file or directory.

        Args:
            src_path (str): UNC-style path (//WORKSPACE/path) to the source
            dest_path (str): UNC-style path (//WORKSPACE/path) to the destination

        Returns:
            str: JSON string with the result or an error message.
        """
        src_unc_path = kwargs.get('src_path', '')
        dest_unc_path = kwargs.get('dest_path', '')

        return await self._run_cp_or_mv(
            operation=lambda workspace, source_path, destination_path: workspace.mv(source_path, destination_path),
            src_path=src_unc_path,
            dest_path=dest_unc_path,
        )

    @json_schema(
        'Using a UNC-style path, update a text file with multiple string replacements. ',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to update',
                'required': True
            },
            'updates': {
                'type': 'array',
                'description': 'Array of update operations to perform',
                'items': {
                    'type': 'object',
                    'properties': {
                        'old_string': {
                            'type': 'string',
                            'description': 'The exact string to be replaced. This can be a multiline string. UTF8 encoding.'
                        },
                        'new_string': {
                            'type': 'string',
                            'description': 'The new string that will replace the old string. This can be a multiline string. UTF8 encoding'
                        }
                    },
                    'required': ['old_string', 'new_string']
                },
                'required': True
            }
        }
    )
    async def replace_strings(self, **kwargs: Any) -> str:
        """
        Asynchronously updates a file with multiple string replacements

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the file to update
            updates (list): A list of update operations, each containing 'old_string' and 'new_string'

        Returns:
            str: JSON string with a success message or an error message.
        """
        updates = kwargs['updates']

        unc_path = kwargs.get('path', '')
        error, workspace, relative_path = self.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        try:
            # Use utf-8 encoding explicitly when processing string replacements
            result = await self.replace_helper.process_replace_strings(
                read_function=workspace.read_internal, write_function=workspace.write,
                path=relative_path, updates=updates, encoding='utf-8')

            return json.dumps(result)
        except Exception as e:
            error_msg = f'Error in replace_strings operation: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

    @json_schema(
        'Read a subset of lines from a text file using UNC-style path',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to read',
                'required': True
            },
            'start_line': {
                'type': 'integer',
                'description': 'The 0-based index of the first line to read',
                'required': True
            },
            'end_line': {
                'type': 'integer',
                'description': 'The 0-based index of the last line to read (inclusive)',
                'required': True
            },
            'include_line_numbers': {
                'type': 'boolean',
                'description': 'Whether to include line numbers in the output',
                'required': False
            }
        }
    )
    async def read_lines(self, **kwargs: Any) -> str:
        """Asynchronously reads a subset of lines from a text file.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the file to read
            start_line (int): The 0-based index of the first line to read
            end_line (int): The 0-based index of the last line to read (inclusive)
            include_line_numbers (bool, optional): If True, includes line numbers in the output

        Returns:
            str: JSON string containing the requested lines or an error message.
        """
        unc_path = kwargs.get('path', '')
        start_line = kwargs.get('start_line')
        end_line = kwargs.get('end_line')
        include_line_numbers = kwargs.get('include_line_numbers', False)

        error, workspace, relative_path = self.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        try:
            # Validate line indices
            if not isinstance(start_line, int) or start_line < 0:
                return json.dumps({'error': 'Invalid start_line value'})
            if not isinstance(end_line, int) or end_line < start_line:
                return json.dumps({'error': 'Invalid end_line value'})

            try:
                file_content = await workspace.read_internal(relative_path)
            except Exception as e:
                return json.dumps({'error': f'Error reading file: {str(e)}'})

            # Split the content into lines
            lines = file_content.splitlines()

            # Check if end_line is beyond the file length
            if end_line >= len(lines):
                end_line = len(lines) - 1

            # Extract the requested subset of lines
            subset_lines = lines[start_line:end_line + 1]

            if include_line_numbers:
                # Format lines with line numbers
                formatted_lines = [f"{start_line + i}: {line}" for i, line in enumerate(subset_lines)]
                subset_content = '\n'.join(formatted_lines)
            else:
                subset_content = '\n'.join(subset_lines)

            return subset_content

        except Exception as e:
            error_msg = f'Error reading file lines: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

    @json_schema(
        'Inspects a code file and returns details about its contents and usage.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to read',
                'required': True
            }
        }
    )
    async def inspect_code(self, **kwargs: Any) -> str:
        """Uses CodeExplorer to prepare code overviews.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the file to read

        Returns:
            str: A markdown overview of the code
        """
        unc_path = kwargs.get('path', '')

        error, workspace, relative_path = self.validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})


        try:
            file_content = await workspace.read_internal(relative_path)
        except Exception as e:
            error_msg = f'Error fetching {unc_path}: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        try:
            context = api.get_code_context(file_content, format='markdown', filename=unc_path)
        except Exception as e:
            error_msg = f'Error inspecting code {unc_path}: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        return context


    @json_schema(
        description="Find files matching a glob pattern in a workspace. Equivlient to `glob.glob` in Python",
        params={
            "path": {
                "type": "string",
                "description": "UNC-style path (//WORKSPACE/path) with glob pattern to find matching files",
                "required": True
            },
            "recursive": {
                "type": "boolean",
                "description": "Whether to search recursively, matching ** patterns",
                "required": False
            },
            "include_hidden": {
                "type": "boolean",
                "description": "Whether to include hidden files in ** pattern matching",
                "required": False
            }
        }
    )
    async def glob(self, **kwargs: Any) -> str:
        """Find files matching a glob pattern in a workspace.
        
        Args:
            **kwargs: Keyword arguments.
                path (str): UNC-style path (//WORKSPACE/path) with glob pattern to find matching files
                recursive (bool): Whether to search recursively (defaults to False)
                include_hidden (bool): Whether to include hidden files (defaults to False)
                
        Returns:
            str: JSON string with the list of matching files or an error message.
        """
        # Get the path with the glob pattern
        unc_path = kwargs.get('path', '')
        recursive = kwargs.get('recursive', False)
        include_hidden = kwargs.get('include_hidden', False)
        
        if not unc_path:
            return json.dumps({'error': '`path` cannot be empty'})
            
        workspace_name, workspace, relative_pattern = self._parse_unc_path(unc_path)
        
        if not workspace:
            return json.dumps({'error': f'Invalid workspace: {workspace_name}'})
            
        try:
            # Use the workspace's glob method to find matching files
            matching_files = await workspace.glob(relative_pattern, recursive=recursive, include_hidden=include_hidden)
            
            # Convert the files back to UNC paths
            unc_files = [f'//{workspace_name}/{file}' for file in matching_files]
            
            return json.dumps({'files': unc_files})
        except Exception as e:
            return json.dumps({'error': f'Error during glob operation: {str(e)}'})

    @json_schema(
        'Run `grep -n`  over files in workspaces using UNC-style paths',
        {
            'paths': {
                "type": "array",
                "items": {
                    "type": "string"
                },
                'description': 'UNC-style paths (//WORKSPACE/path) to grep, wildcards ARE supported',
                'required': True
            },
            'pattern': {
                'type': 'string',
                'description': 'Grep pattern to search for',
                'required': True
            },
            'ignore_case': {
                'type': 'boolean',
                'description': 'Set to true to ignore case',
                'required': False
            },
            'recursive': {
                'type': 'boolean',
                'description': 'Set to true to recursively search subdirectories',
                'required': False
            }
        }
    )
    async def grep(self, **kwargs: Any) -> str:
        """Run grep over files in workspaces using UNC-style paths.
        
        Args:
            **kwargs: Keyword arguments.
                paths (list): UNC-style paths (//WORKSPACE/path) to grep
                pattern (str): Grep pattern to search for
                recursive (bool): Set to true to recursively search subdirectories
                ignore_case (bool): Set to true to ignore case
                
        Returns:
            str: Output of grep command with line numbers.
        """
        unc_paths = kwargs.get('paths', [])
        pattern = kwargs.get('pattern', '')
        ignore_case = kwargs.get('ignore_case', False)
        recursive = kwargs.get('recursive', False)
        errors = []
        queue = {}
        results = []
        
        if not pattern:
            return json.dumps({'error': '`pattern` cannot be empty'})
        
        if not unc_paths:
            return json.dumps({'error': '`paths` cannot be empty'})

        for punc_path in unc_paths:
            error, workspace, relative_path = self.validate_and_get_workspace_path(punc_path)
            if error:
                errors.append(f"Error processing path {punc_path}: {error}")
                continue
            if workspace not in queue:
                queue[workspace] = []

            queue[workspace].append(relative_path)

        # Now process each workspace's files
        for workspace, paths in queue.items():
            try:
                # Use the workspace's grep method to search for the pattern
                result = await workspace.grep(
                    pattern=pattern,
                    file_paths=paths,
                    ignore_case=ignore_case,
                    recursive=recursive
                )
                results.append(result)

            except Exception as e:
                results.append(f'Error searching files: {str(e)}')
        
        err_str = ""
        if errors:
            err_str = f"Errors:\n{"\n".join(errors)}\n\n"

        return f"{err_str}Results:\n{"\n\n".join(results)}"

    @json_schema(
        description="Read the entire metadata yaml file for a workspace",
        params={
            "workspace": {
                "type": "string",
                "description": "Name of the workspace to read metadata from",
                "required": True
            }
        }
    )
    async def read_meta(self, **kwargs: Any) -> str:
        """
        Asynchronously reads the entire metadata from the workspace's .agent_c.meta.yaml file.

        Args:
            **kwargs: Keyword arguments.
                workspace (str): Name of the workspace to read metadata from

        Returns:
            str: The content of the metadata file as a YAML formatted string or an error message.
        """
        workspace_name = kwargs.get("workspace")
        if not workspace_name:
            return json.dumps({"error": "Workspace name is required"})

        # Find the workspace
        workspace = self.find_workspace_by_name(workspace_name)
        if not workspace:
            return json.dumps({"error": f"Workspace '{workspace_name}' not found"})

        # Read the metadata file
        meta_file_path = ".agent_c.meta.yaml"
        
        try:
            if not await workspace.path_exists(meta_file_path):
                # If the file doesn't exist, return an empty YAML document
                return "{}"
            
            # Read the content of the metadata file
            content = await workspace.read_internal(meta_file_path)
            return content
        except Exception as e:
            return json.dumps({"error": f"Failed to read metadata file: {str(e)}"})

    @json_schema(
        description="Read a specific value from the metadata yaml file for a workspace",
        params={
            "workspace": {
                "type": "string",
                "description": "Name of the workspace to read metadata from",
                "required": True
            },
            "key": {
                "type": "string",
                "description": "The key to read, supports dot notation for nested keys (e.g., 'parent.child')",
                "required": True
            }
        }
    )
    async def read_meta_value(self, **kwargs: Any) -> str:
        """
        Asynchronously reads a specific value from the workspace's metadata file.

        Args:
            **kwargs: Keyword arguments.
                workspace (str): Name of the workspace to read metadata from
                key (str): The key to read, supports dot notation for nested keys (e.g., 'parent.child')

        Returns:
            str: The value for the specified key as a YAML formatted string or an error message.
        """
        workspace_name = kwargs.get("workspace")
        key = kwargs.get("key")
        
        if not workspace_name:
            return json.dumps({"error": "Workspace name is required"})
        if not key:
            return json.dumps({"error": "Key is required"})

        # Find the workspace
        workspace = self.find_workspace_by_name(workspace_name)
        if not workspace:
            return json.dumps({"error": f"Workspace '{workspace_name}' not found"})

        # Read the metadata file
        meta_file_path = ".agent_c.meta.yaml"
        
        try:
            if not await workspace.path_exists(meta_file_path):
                return json.dumps({"error": f"Metadata file does not exist in workspace '{workspace_name}'"})
            
            # Read and parse the metadata
            content = await workspace.read_internal(meta_file_path)
            data = yaml.load(content, FullLoader) or {}
            
            # Navigate to the requested key using dot notation
            key_parts = key.split('.')
            value = data
            for part in key_parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return json.dumps({"error": f"Key '{key}' not found in metadata"})
            
            # Return the value as YAML
            return yaml.dump(value, default_flow_style=False)
        except Exception as e:
            return json.dumps({"error": f"Failed to read metadata value: {str(e)}"})

    @json_schema(
        description="Write the entire metadata yaml file for a workspace",
        params={
            "workspace": {
                "type": "string",
                "description": "Name of the workspace to write metadata to",
                "required": True
            },
            "data": {
                "type": "object",
                "description": "The complete metadata to write as a dictionary",
                "required": True
            }
        }
    )
    async def write_meta(self, **kwargs: Any) -> str:
        """
        Asynchronously writes the entire metadata to the workspace's .agent_c.meta.yaml file.

        Args:
            **kwargs: Keyword arguments.
                workspace (str): Name of the workspace to write metadata to
                data (dict): The complete metadata to write as a dictionary

        Returns:
            str: Success message or an error message.
        """
        workspace_name = kwargs.get("workspace")
        data = kwargs.get("data")
        
        if not workspace_name:
            return json.dumps({"error": "Workspace name is required"})
        if data is None:
            return json.dumps({"error": "Data is required"})

        # Find the workspace
        workspace = self.find_workspace_by_name(workspace_name)
        if not workspace:
            return json.dumps({"error": f"Workspace '{workspace_name}' not found"})

        # Check if workspace is read-only
        if workspace.read_only:
            return json.dumps({"error": f"Workspace '{workspace_name}' is read-only"})

        # Write the metadata file
        meta_file_path = ".agent_c.meta.yaml"
        
        try:
            # Convert data to YAML
            yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            
            # Write the content to the metadata file
            await workspace.write(meta_file_path, "write", yaml_content)
            return json.dumps({"success": f"Metadata successfully written to workspace '{workspace_name}'"})
        except Exception as e:
            return json.dumps({"error": f"Failed to write metadata: {str(e)}"})

    @json_schema(
        description="Write a specific value to the metadata yaml file for a workspace",
        params={
            "workspace": {
                "type": "string",
                "description": "Name of the workspace to write metadata to",
                "required": True
            },
            "key": {
                "type": "string",
                "description": "The key to write, supports dot notation for nested keys (e.g., 'parent.child')",
                "required": True
            },
            "value": {
                "type": "object",
                "description": "The value to write for the specified key",
                "required": True
            }
        }
    )
    async def write_meta_value(self, **kwargs: Any) -> str:
        """
        Asynchronously writes a specific value to the workspace's metadata file.

        Args:
            **kwargs: Keyword arguments.
                workspace (str): Name of the workspace to write metadata to
                key (str): The key to write, supports dot notation for nested keys (e.g., 'parent.child')
                value: The value to write for the specified key

        Returns:
            str: Success message or an error message.
        """
        workspace_name = kwargs.get("workspace")
        key = kwargs.get("key")
        value = kwargs.get("value")
        
        if not workspace_name:
            return json.dumps({"error": "Workspace name is required"})
        if not key:
            return json.dumps({"error": "Key is required"})
        if value is None:
            return json.dumps({"error": "Value is required"})

        # Find the workspace
        workspace = self.find_workspace_by_name(workspace_name)
        if not workspace:
            return json.dumps({"error": f"Workspace '{workspace_name}' not found"})

        # Check if workspace is read-only
        if workspace.read_only:
            return json.dumps({"error": f"Workspace '{workspace_name}' is read-only"})

        # Read the metadata file or initialize an empty dict
        meta_file_path = ".agent_c.meta.yaml"
        data = {}
        
        try:
            if await workspace.path_exists(meta_file_path):
                content = await workspace.read_internal(meta_file_path)
                data = yaml.load(content, FullLoader) or {}
            
            # Update the data with the new value using dot notation
            key_parts = key.split('.')
            current = data
            
            # Navigate to the parent of the final key
            for i, part in enumerate(key_parts[:-1]):
                if part not in current or not isinstance(current[part], dict):
                    current[part] = {}
                current = current[part]
            
            # Set the value at the final key
            current[key_parts[-1]] = value
            
            # Convert updated data to YAML and write it back
            yaml_content = yaml.dump(data, default_flow_style=False, allow_unicode=True)
            await workspace.write(meta_file_path, "write", yaml_content)
            
            return json.dumps({"success": f"Metadata value for key '{key}' successfully written to workspace '{workspace_name}'"})
        except Exception as e:
            return json.dumps({"error": f"Failed to write metadata value: {str(e)}"})


Toolset.register(WorkspaceTools)