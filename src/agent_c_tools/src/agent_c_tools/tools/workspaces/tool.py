import json
import logging

from typing import Any, List

from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from agent_c_tools.tools.workspaces.base import BaseWorkspace
from agent_c_tools.tools.workspaces.prompt import WorkspaceSection

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
        'Update a text file within the workspace with a unified diff. **This is the preferred way to update files**',
        {
            'workspace': {
                'type': 'string',
                'description': 'The name of the workspace the path resides in..',
                'required': True
            },
            'path': {
                'type': 'string',
                'description': 'The path, relative to the workspace root folder, of the file you wish to patch..',
                'required': True
            },
            'diff': {
                'type': 'string',
                'description': 'The unified diff to apply to the file.',
                'required': True
            }
        })
    async def apply_unified_diff(self, **kwargs) -> str:
        """Apply a unified diff to a file within the workspaces.

        Args:
            path (str): The relative path to the file within the workspaces.
            diff (str): The unified diff content to apply.

        Returns:
            str: JSON string with a success message or an error message.
        """
        workspace = self.find_workspace_by_name(kwargs.get('workspace'))
        if workspace is None:
            return f'No workspaces found with the name: {workspace}'

        try:
            file_path: str = kwargs['path']
            diff_content: str = kwargs['diff']
            resp = await workspace.apply_unified_diff(file_path, diff_content)
            return resp
        except Exception as e:
            return json.dumps({'error': str(e)})

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


Toolset.register(WorkspaceTools)