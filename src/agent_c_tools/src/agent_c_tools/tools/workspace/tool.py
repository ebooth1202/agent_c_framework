import json
import logging
import re
from typing import Any, List, Tuple, Optional

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from agent_c_tools.tools.workspace.base import BaseWorkspace
from agent_c_tools.tools.workspace.prompt import WorkspaceSection
from agent_c_tools.tools.workspace.util.xml_navigator import XMLNavigator


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

    def add_workspace(self, workspace: BaseWorkspace) -> None:
        """Add a workspace to the list of workspaces."""
        self.workspaces.append(workspace)
        self._create_section()

    def _create_section(self):
        spaces: str = "\n".join([str(space) for space in self.workspaces])
        self.section = WorkspaceSection(workspaces=spaces)

    def find_workspace_by_name(self, name):
        """Find a workspace by its name."""
        try:
            return next(workspace for workspace in self.workspaces if workspace.name == name)
        except StopIteration:
            # Handle the case where no workspace with the given name is found
            self.logger.warning(f"No workspace found with the name: {name}")
            return None

    def _parse_unc_path(self, path: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
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

    def _validate_and_get_workspace_path(self, unc_path: str) -> Tuple[Optional[str], Optional[BaseWorkspace], Optional[str]]:
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
            path (str): UNC-style path (//WORKSPACE/path) to list contents for

        Returns:
            str: JSON string with the listing or an error message.
        """
        unc_path = kwargs.get('path', '')

        error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
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
            }
        }
    )
    async def tree(self, **kwargs: Any) -> str:
        """Asynchronously generates a tree view of a directory.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to start the tree from

        Returns:
            str: JSON string with the tree view or an error message.
        """
        unc_path = kwargs.get('path', '')

        error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        return await workspace.tree(relative_path)

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
            path (str): UNC-style path (//WORKSPACE/path) to the file to read

        Returns:
            str: JSON string with the file content or an error message.
        """
        unc_path = kwargs.get('path', '')

        error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
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

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the file to write
            data (str): The text data to write or append to the file
            mode (str): The writing mode, either 'write' to overwrite or 'append'

        Returns:
            str: JSON string with a success message or an error message.
        """
        unc_path = kwargs.get('path', '')
        data = kwargs['data']
        mode = kwargs.get('mode', 'write')

        error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        return await workspace.write(relative_path, mode, data)

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

        # Validate source path
        src_error, src_workspace, src_relative_path = self._validate_and_get_workspace_path(src_unc_path)
        if src_error:
            return json.dumps({'error': src_error})

        # Validate destination path
        dest_error, dest_workspace, dest_relative_path = self._validate_and_get_workspace_path(dest_unc_path)
        if dest_error:
            return json.dumps({'error': dest_error})

        # Check if both paths are in the same workspace
        if src_workspace != dest_workspace:
            error_msg = f"Cross-workspace operations are not supported. Source and destination must be in the same workspace."
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        return await src_workspace.cp(src_relative_path, dest_relative_path)

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

        error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
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

        # Validate source path
        src_error, src_workspace, src_relative_path = self._validate_and_get_workspace_path(src_unc_path)
        if src_error:
            return json.dumps({'error': src_error})

        # Validate destination path
        dest_error, dest_workspace, dest_relative_path = self._validate_and_get_workspace_path(dest_unc_path)
        if dest_error:
            return json.dumps({'error': dest_error})

        # Check if both paths are in the same workspace
        if src_workspace != dest_workspace:
            error_msg = f"Cross-workspace operations are not supported. Source and destination must be in the same workspace."
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        return await src_workspace.mv(src_relative_path, dest_relative_path)

    @json_schema(
        'Update a text file with multiple string replacements or complete rewrite using UNC-style path',
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
                            'description': 'The exact string to be replaced. This can be a multiline string.'
                        },
                        'new_string': {
                            'type': 'string',
                            'description': 'The new string that will replace the old string. This can be a multiline string.'
                        }
                    },
                    'required': ['old_string', 'new_string']
                },
                'required': True
            },
            'rewrite': {
                'type': 'boolean',
                'description': 'Whether to completely rewrite the file. If true, the first update is treated as the complete new content.',
                'required': False
            }
        }
    )
    async def update(self, **kwargs: Any) -> str:
        """Asynchronously updates a file with multiple string replacements or a full rewrite.

        Args:
            path (str): UNC-style path (//WORKSPACE/path) to the file to update
            updates (list): A list of update operations, each containing 'old_string' and 'new_string'
            rewrite (bool, optional): If True, performs a full rewrite instead of string replacements

        Returns:
            str: JSON string with a success message or an error message.
        """
        updates = kwargs['updates']
        rewrite = kwargs.get('rewrite', False)

        unc_path = kwargs.get('path', '')
        error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        try:
            if rewrite:
                if not updates or len(updates) == 0:
                    return json.dumps({'error': 'No updates provided for rewrite operation'})

                # Use the new_string from the first update as the complete new content
                new_content = updates[0].get('new_string', '')
                if not new_content:
                    return json.dumps({'error': 'No new content provided for rewrite operation'})

                # Write the new content to the file
                write_response = await workspace.write(relative_path, 'write', new_content)
                return write_response
            else:
                file_content_response = await workspace.read(relative_path)

                # Parse the response to get the actual content
                try:
                    file_content_json = json.loads(file_content_response)
                    if 'error' in file_content_json:
                        return file_content_response  # Return the error from read operation
                    file_content = file_content_json.get('contents', '')
                except json.JSONDecodeError:
                    file_content = file_content_response

                replacement_stats = []
                updated_content = file_content

                for i, update_op in enumerate(updates):
                    old_string = update_op.get('old_string')
                    new_string = update_op.get('new_string')

                    # Validate the update operation
                    if not old_string or not isinstance(old_string, str):
                        return json.dumps({'error': f'Invalid old_string in update operation {i}'})
                    if not isinstance(new_string, str):
                        return json.dumps({'error': f'Invalid new_string in update operation {i}'})

                    # Check if old_string exists in the current content
                    if old_string not in updated_content:
                        replacement_stats.append({
                            'operation': i,
                            'status': 'skipped',
                            'reason': 'Old string not found'
                        })
                        continue

                    # Replace the old string with the new string
                    occurrences = updated_content.count(old_string)
                    updated_content = updated_content.replace(old_string, new_string)

                    replacement_stats.append({
                        'operation': i,
                        'status': 'success',
                        'replacements': occurrences
                    })

                # Write the updated content back to the file
                write_response = await workspace.write(relative_path, 'write', updated_content)

                if 'error' in write_response:
                    return write_response

                return json.dumps({
                    'success': True,
                    'message': f'Successfully updated file {relative_path}',
                    'operation': 'update',
                    'replacement_stats': replacement_stats
                })
        except Exception as e:
            error_msg = f'Error updating file: {str(e)}'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

    @json_schema(
        'Get structure information about a large XML file without loading the entire file.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to update',
                'required': True
            },
            'max_depth': {
                'type': 'integer',
                'description': 'Maximum depth to traverse in the XML structure.',
                'required': False
            },
            'sample_count': {
                'type': 'integer',
                'description': 'Number of sample elements to include at each level.',
                'required': False
            }
        }
    )
    async def xml_structure(self, **kwargs: Any) -> str:
        """Asynchronously retrieves structure information about a large XML file.

        Args:
            workspace (str): The name of the workspace the file resides in.
            file_path (str): Relative path to the XML file within the workspace.
            max_depth (int, optional): Maximum depth to traverse in the XML structure. Defaults to 3.
            sample_count (int, optional): Number of sample elements to include at each level. Defaults to 5.

        Returns:
            str: JSON string with structure information or an error message.
        """
        max_depth: int = kwargs.get('max_depth', 3)
        sample_count: int = kwargs.get('sample_count', 5)
        unc_path = kwargs.get('path', '')
        error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        navigator = XMLNavigator(workspace)
        return await navigator.get_structure(relative_path, max_depth, sample_count)

    @json_schema(
        'Execute an XPath query on an XML file and return matching elements.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to update',
                'required': True
            },
            'xpath': {
                'type': 'string',
                'description': 'XPath query to execute',
                'required': True
            },
            'limit': {
                'type': 'integer',
                'description': 'Max results to return.',
                'required': False
            }
        }
    )
    async def xml_query(self, **kwargs: Any) -> str:
        """Asynchronously executes an XPath query on an XML file.

        Args:
            workspace (str): The name of the workspace the file resides in.
            file_path (str): Relative path to the XML file within the workspace.
            xpath (str): XPath query to execute on the XML file.
            limit (int, optional): Maximum number of results to return. Defaults to 10.

        Returns:
            str: JSON string with query results or an error message.
        """
        xpath: str = kwargs['xpath']
        limit: int = kwargs.get('limit', 10)
        unc_path = kwargs.get('path', '')
        error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        navigator = XMLNavigator(workspace)
        return await navigator.xpath_query(relative_path, xpath, limit)

    @json_schema(
        'Extract a subtree from an XML file and optionally save it to a new file.',
        {
            'path': {
                'type': 'string',
                'description': 'UNC-style path (//WORKSPACE/path) to the file to update',
                'required': True
            },
            'xpath': {
                'type': 'string',
                'description': 'XPath to the root element of the subtree to extract.',
                'required': True
            },
            'output_path': {
                'type': 'string',
                'description': 'Optional path to save the extracted subtree.',
                'required': False
            }
        }
    )
    async def xml_extract(self, **kwargs: Any) -> str:
        """Asynchronously extracts a subtree from an XML file.

        Args:
            workspace (str): The name of the workspace the file resides in.
            file_path (str): Relative path to the XML file within the workspace.
            xpath (str): XPath to the root element of the subtree to extract.
            output_path (str, optional): Path to save the extracted subtree.

        Returns:
            str: JSON string with the extracted subtree or a status message.
        """
        xpath: str = kwargs['xpath']
        output_path: Optional[str] = kwargs.get('output_path')
        unc_path = kwargs.get('path', '')
        error, workspace, relative_path = self._validate_and_get_workspace_path(unc_path)
        if error:
            return json.dumps({'error': error})

        # TODO: this needs to support writing to  unc workspcae path
        if output_path and output_path.startswith('/'):
            error_msg = f'The output path {output_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspace found with the name: {kwargs.get("workspace")}'

        navigator = XMLNavigator(workspace)
        return await navigator.extract_subtree(relative_path, xpath, output_path)


Toolset.register(WorkspaceTools)