import json
import logging
import xml.etree.ElementTree as ET
from typing import Optional, List, Dict, Any, Union

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from agent_c_tools.tools.workspaces.base import BaseWorkspace
from agent_c_tools.tools.workspaces.prompt import WorkspaceSection
from agent_c_tools.tools.workspaces.xml_navigator import XMLNavigator

class WorkspaceTools(Toolset):
    """
    WorkspaceTools allows the model to read / write data to one or more workspaces.
    This allows us to absract things like S3, Azure Storage and the like.

    This really just a rough outline at this point.
    """

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
        try:
            return next(workspace for workspace in self.workspaces if workspace.name == name)
        except StopIteration:
            # Handle the case where no workspaces with the given name is found
            self.logger.warning(f"No workspaces found with the name: {name}")
            return None


    @json_schema(
        'List the contents of a directory within a workspaces.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the path resides in. Refer to the "available workspaces" list for valid names.',
                'required': True
            },
            'path': {
                'type': 'string',
                'description': 'The path, relative to the workspace root folder, to list.',
                'required': False
            }
        }
    )
    async def ls(self, **kwargs: Any) -> str:
        """Asynchronously lists the contents of a workspaces or a subdirectory in it.

        Args:
            workspace (str): The workspaces to use
            path (str): Relative path within the workspaces to list contents for.

        Returns:
            str: JSON string with the listing or an error message.
        """
        relative_path: str = kwargs.get('path', '')
        if relative_path == '/':
            relative_path = ''

        if relative_path.startswith('/'):
            error_msg = f'The path {relative_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspaces found with the name: {workspace}'

        return await workspace.ls(relative_path)

    @json_schema(
        'Retrieve a string "tree" of the directory structure within a workspace.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the path resides in. Refer to the "available workspaces" list for valid names.',
                'required': True
            },
            'path': {
                'type': 'string',
                'description': 'The path, relative to the workspace root folder, to start the tree from.',
                'required': False
            }
        }
    )
    async def tree(self, **kwargs: Any) -> str:
        """Asynchronously lists the contents of a workspaces or a subdirectory in it.

        Args:
            workspace (str): The workspaces to use
            path (str): Relative path within the workspaces to list contents for.

        Returns:
            str: JSON string with the listing or an error message.
        """
        relative_path: str = kwargs.get('path', '')
        if relative_path == '/':
            relative_path = ''

        if relative_path.startswith('/'):
            error_msg = f'The path {relative_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspaces found with the name: {workspace}'

        return await workspace.tree(relative_path)

    @json_schema(
        'Reads the contents of a text file within the workspaces.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the file_path resides in. Refer to the "available workspaces" list for valid names.',
                'required': True
            },
            'file_path': {
                'type': 'string',
                'description': 'The path to the file, relative to the workspace root folder',
                'required': True
            }
        }
    )
    async def read(self, **kwargs: Any) -> str:
        """Asynchronously reads the content of a text file within the workspaces.

        Args:
            file_path (str): Relative path to the text file within the workspaces.

        Returns:
            str: JSON string with the file content or an error message.
        """
        file_path: str = kwargs['file_path']
        if file_path.startswith('/'):
            error_msg = f'The path {file_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspaces found with the name: {workspace}'

        return await workspace.read(file_path)

    @json_schema(
        'Writes or appends text data to a file within the workspaces.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the file_path resides in. Refer to the "available workspaces" list for valid names.',
                'required': True
            },
            'file_path': {
                'type': 'string',
                'description': 'The path, relative to the workspace root folder, to the file within the workspace.',
                'required': True
            },
            'data': {
                'type': 'string',
                'description': 'The text data to write or append to the file.',
                'required': True
            },
            'mode': {
                'type': 'string',
                'description': 'The writing mode: "write" to overwrite or "append" to add to the file.',
                'required': False
            }
        }
    )
    async def write(self, **kwargs: Any) -> str:
        """Asynchronously writes or appends data to a file within the workspaces.

        Args:
            file_path (str): Relative path to the file within the workspaces.
            data (str): The text data to write or append to the file.
            mode (str): The writing mode, either 'write' to overwrite or 'append'.

        Returns:
            str: JSON string with a success message or an error message.
        """
        file_path: str = kwargs['file_path']
        data: str = kwargs['data']
        mode: str = kwargs.get('mode', 'write')

        if file_path.startswith('/'):
            error_msg = f'The path {file_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspaces found with the name: {workspace}'

        return await workspace.write(file_path, mode, data)

    @json_schema(
        'Copy a file or directory within a workspace.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the paths reside in. Refer to the "available workspaces" list for valid names.',
                'required': True
            },
            'src_path': {
                'type': 'string',
                'description': 'The source path, relative to the workspace root folder.',
                'required': True
            },
            'dest_path': {
                'type': 'string',
                'description': 'The destination path, relative to the workspace root folder.',
                'required': True
            }
        }
    )
    async def cp(self, **kwargs: Any) -> str:
        """Asynchronously copies a file or directory within a workspace.

        Args:
            workspace (str): The workspace to use
            src_path (str): Relative source path within the workspace
            dest_path (str): Relative destination path within the workspace

        Returns:
            str: JSON string with the result or an error message.
        """
        src_path: str = kwargs.get('src_path', '')
        dest_path: str = kwargs.get('dest_path', '')

        # Check for absolute paths
        if src_path.startswith('/'):
            error_msg = f'The source path {src_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        if dest_path.startswith('/'):
            error_msg = f'The destination path {dest_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspace found with the name: {kwargs.get("workspace")}'

        return await workspace.cp(src_path, dest_path)

    @json_schema(
        'Move a file or directory within a workspace.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the paths reside in. Refer to the "available workspaces" list for valid names.',
                'required': True
            },
            'src_path': {
                'type': 'string',
                'description': 'The source path, relative to the workspace root folder.',
                'required': True
            },
            'dest_path': {
                'type': 'string',
                'description': 'The destination path, relative to the workspace root folder.',
                'required': True
            }
        }
    )
    async def mv(self, **kwargs: Any) -> str:
        """Asynchronously moves a file or directory within a workspace.

        Args:
            workspace (str): The workspace to use
            src_path (str): Relative source path within the workspace
            dest_path (str): Relative destination path within the workspace

        Returns:
            str: JSON string with the result or an error message.
        """
        src_path: str = kwargs.get('src_path', '')
        dest_path: str = kwargs.get('dest_path', '')

        # Check for absolute paths
        if src_path.startswith('/'):
            error_msg = f'The source path {src_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        if dest_path.startswith('/'):
            error_msg = f'The destination path {dest_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspace found with the name: {kwargs.get("workspace")}'

        return await workspace.mv(src_path, dest_path)

    @json_schema(
        'Update a text file within the workspace with multiple string replacements or complete rewrite. This functions the same as the Anthropic artifacts update tool does ',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the file resides in.',
                'required': True
            },
            'file_path': {
                'type': 'string',
                'description': 'The path, relative to the workspace root folder, of the file to update.',
                'required': True
            },
            'updates': {
                'type': 'array',
                'description': 'Array of update operations to perform.',
                'items': {
                    'type': 'object',
                    'properties': {
                        'old_string': {
                            'type': 'string',
                            'description': 'The exact string to be replaced. This can be a multiline string.'
                        },
                        'new_string': {
                            'type': 'string',
                            'description': 'The new string that will replace the old string.  This can be a multiline string.'
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
            workspace (str): The name of the workspace the file resides in.
            file_path (str): Relative path to the file within the workspace.
            updates (list): A list of update operations, each containing 'old_string' and 'new_string'.
            rewrite (bool, optional): If True, performs a full rewrite instead of string replacements.

        Returns:
            str: JSON string with a success message or an error message.
        """
        file_path: str = kwargs['file_path']
        updates: list = kwargs['updates']
        rewrite: bool = kwargs.get('rewrite', False)

        if file_path.startswith('/'):
            error_msg = f'The path {file_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspace found with the name: {kwargs.get("workspace")}'

        try:
            if rewrite:
                if not updates or len(updates) == 0:
                    return json.dumps({'error': 'No updates provided for rewrite operation'})

                # Use the new_string from the first update as the complete new content
                new_content = updates[0].get('new_string', '')
                if not new_content:
                    return json.dumps({'error': 'No new content provided for rewrite operation'})

                # Write the new content to the file
                write_response = await workspace.write(file_path, 'write', new_content)

                return write_response
            else:
                file_content_response = await workspace.read(file_path)

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
                write_response = await workspace.write(file_path, 'write', updated_content)

                if 'error' in write_response:
                    return write_response

                return json.dumps({
                    'success': True,
                    'message': f'Successfully updated file {file_path}',
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
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the file resides in.',
                'required': True
            },
            'file_path': {
                'type': 'string',
                'description': 'The path to the XML file, relative to the workspace root folder.',
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
        file_path: str = kwargs['file_path']
        max_depth: int = kwargs.get('max_depth', 3)
        sample_count: int = kwargs.get('sample_count', 5)

        if file_path.startswith('/'):
            error_msg = f'The path {file_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspace found with the name: {kwargs.get("workspace")}'

        navigator = XMLNavigator(workspace)
        return await navigator.get_structure(file_path, max_depth, sample_count)

    @json_schema(
        'Execute an XPath query on an XML file and return matching elements.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the file resides in.',
                'required': True
            },
            'file_path': {
                'type': 'string',
                'description': 'The path to the XML file, relative to the workspace root folder.',
                'required': True
            },
            'xpath': {
                'type': 'string',
                'description': 'XPath query to execute on the XML file.',
                'required': True
            },
            'limit': {
                'type': 'integer',
                'description': 'Maximum number of results to return.',
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
        file_path: str = kwargs['file_path']
        xpath: str = kwargs['xpath']
        limit: int = kwargs.get('limit', 10)

        if file_path.startswith('/'):
            error_msg = f'The path {file_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspace found with the name: {kwargs.get("workspace")}'

        navigator = XMLNavigator(workspace)
        return await navigator.xpath_query(file_path, xpath, limit)

    @json_schema(
        'Extract a subtree from an XML file and optionally save it to a new file.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the file resides in.',
                'required': True
            },
            'file_path': {
                'type': 'string',
                'description': 'The path to the XML file, relative to the workspace root folder.',
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
        file_path: str = kwargs['file_path']
        xpath: str = kwargs['xpath']
        output_path: Optional[str] = kwargs.get('output_path')

        if file_path.startswith('/'):
            error_msg = f'The path {file_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        if output_path and output_path.startswith('/'):
            error_msg = f'The output path {output_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspace found with the name: {kwargs.get("workspace")}'

        navigator = XMLNavigator(workspace)
        return await navigator.extract_subtree(file_path, xpath, output_path)

    @json_schema(
        'Find customizations in a Dynamics customizations.xml file.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the file resides in.',
                'required': True
            },
            'file_path': {
                'type': 'string',
                'description': 'The path to the customizations.xml file, relative to the workspace root folder.',
                'required': True
            }
        }
    )
    async def dynamics_find_customizations(self, **kwargs: Any) -> str:
        """Asynchronously finds customizations in a Dynamics customizations.xml file.

        Args:
            workspace (str): The name of the workspace the file resides in.
            file_path (str): Relative path to the customizations.xml file within the workspace.

        Returns:
            str: JSON string with customization details or an error message.
        """
        file_path: str = kwargs['file_path']

        if file_path.startswith('/'):
            error_msg = f'The path {file_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspace found with the name: {kwargs.get("workspace")}'

        navigator = XMLNavigator(workspace)
        return await navigator.find_customizations(file_path)

    @json_schema(
        'Extract a specific section from a Dynamics customizations.xml file for detailed analysis.',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the file resides in.',
                'required': True
            },
            'file_path': {
                'type': 'string',
                'description': 'The path to the customizations.xml file, relative to the workspace root folder.',
                'required': True
            },
            'section_type': {
                'type': 'string',
                'description': 'Type of section to extract (Entity, Form, Ribbon, SiteMap, SavedQuery, Workflow).',
                'required': True
            },
            'entity_name': {
                'type': 'string',
                'description': 'Optional entity name to filter by.',
                'required': False
            },
            'output_path': {
                'type': 'string',
                'description': 'Optional path to save the extracted section.',
                'required': False
            },
            'metadata_only': {
                'type': 'boolean',
                'description': 'Return only metadata about the sections found, not their content.',
                'required': False
            },
            'limit': {
                'type': 'integer',
                'description': 'Maximum number of sections to return.',
                'required': False
            },
            'attributes_to_include': {
                'type': 'array',
                'description': 'List of specific attributes to include in metadata.',
                'items': {
                    'type': 'string'
                },
                'required': False
            },
            'format': {
                'type': 'string',
                'description': 'Output format (yaml, json, or xml).',
                'required': False
            }
        }
    )
    async def dynamics_extract_section(self, **kwargs: Any) -> str:
        """Asynchronously extracts a specific section from a Dynamics customizations.xml file.

        Args:
            workspace (str): The name of the workspace the file resides in.
            file_path (str): Relative path to the customizations.xml file within the workspace.
            section_type (str): Type of section to extract (Entity, Form, Ribbon, SiteMap, SavedQuery, Workflow).
            entity_name (str, optional): Optional entity name to filter by.
            output_path (str, optional): Optional path to save the extracted section.
            metadata_only (bool, optional): Return only metadata about the sections found, not their content. Defaults to False.
            limit (int, optional): Maximum number of sections to return. Defaults to 10.
            attributes_to_include (list, optional): List of specific attributes to include in metadata.
            format (str, optional): Output format (yaml, json, or xml). Defaults to yaml.

        Returns:
            str: JSON string with the extracted section, metadata, or a status message.
        """
        file_path: str = kwargs['file_path']
        section_type: str = kwargs['section_type']
        entity_name: Optional[str] = kwargs.get('entity_name')
        output_path: Optional[str] = kwargs.get('output_path')
        metadata_only: bool = kwargs.get('metadata_only', False)
        limit: int = kwargs.get('limit', 10)
        attributes_to_include: Optional[List[str]] = kwargs.get('attributes_to_include')
        format: str = kwargs.get('format', 'yaml')  # Default to YAML

        if file_path.startswith('/'):
            error_msg = f'The path {file_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        if output_path and output_path.startswith('/'):
            error_msg = f'The output path {output_path} is absolute. Please provide a relative path.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspace found with the name: {kwargs.get("workspace")}'

        navigator = XMLNavigator(workspace)
        return await navigator.extract_section(file_path, section_type, entity_name, output_path,
                                               metadata_only, limit, attributes_to_include, format)

Toolset.register(WorkspaceTools)