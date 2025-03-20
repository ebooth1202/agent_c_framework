import base64
import os
import json
import logging

from pathlib import Path
from typing import Optional, Union

from agent_c.util import generate_path_tree
from agent_c.util.token_counter import TokenCounter
from agent_c_tools.tools.workspaces.base import BaseWorkspace


class LocalStorageWorkspace(BaseWorkspace):
    def __init__(self, **kwargs):
        super().__init__("local_storage", **kwargs)
        workspace_path: Optional[str] = kwargs.get('workspace_path')
        self.max_token_size: int = kwargs.get('max_size', 50000)
        self.valid: bool = isinstance(workspace_path, str)
        if self.valid:
            self.workspace_root: Path = Path(workspace_path).resolve()

        # Check environment for development/local mode
        env = os.environ.get('ENVIRONMENT', '').lower()
        self.allow_symlinks: bool = kwargs.get('allow_symlinks', 'local' in env or 'dev' in env)
        self.logger: logging.Logger = logging.getLogger(__name__)

        if self.allow_symlinks:
            self.logger.info("Symlink paths are allowed in workspace")

        self.max_filename_length = 200

    def _is_path_within_workspace(self, path: str) -> bool:
        """Check if the provided path is within the workspace.

        With symlink allowance enabled, this checks the path string itself rather than
        resolving to physical paths, which would break in Docker environments.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path is valid within the workspace context, else False.
        """
        # Normalize the path (but don't resolve symlinks)
        norm_path = os.path.normpath(path)

        # Prevent path traversal attacks with .. regardless of symlink settings
        if ".." in norm_path.split(os.sep):
            return False

        # If symlinks are allowed and no path traversal, simply allow the path
        if self.allow_symlinks:
            return True

        # If symlinks not allowed, use the traditional path resolution check
        resolved_path = self.workspace_root.joinpath(path).resolve()
        return self.workspace_root in resolved_path.parents or resolved_path == self.workspace_root

    async def tree(self, relative_path: str) -> str:
        if not self._is_path_within_workspace(relative_path):
            error_msg = f'The path {relative_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(relative_path)

        return  '\n'.join(generate_path_tree(str(full_path)))

    async def ls(self, relative_path: str) -> str:
        if not self._is_path_within_workspace(relative_path) or relative_path == '':
            error_msg = f'The path {relative_path} is not within the workspace.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(relative_path)
        try:
            contents = os.listdir(full_path)
            return json.dumps({'contents': contents})
        except Exception as e:
            error_msg = str(e)
            self.logger.exception("Failed to list directory contents.")
            return json.dumps({'error': error_msg})

    async def read(self, file_path: str) -> str:
        if not self._is_path_within_workspace(file_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(file_path)
        try:
            if full_path.is_file():
                # TODO: Direct model to use a dedicated large file tool when complete
                with open(full_path, 'r', encoding='utf-8') as file:
                    contents = file.read()
                    file_tokens = TokenCounter.count(contents)

                    if file_tokens > self.max_token_size:
                        error_msg = f'The file {file_path} exceeds the token limit of {self.max_token_size}.  Actual size is {file_tokens}.'
                        self.logger.error(error_msg)
                        return json.dumps({'error': error_msg})

                    return json.dumps({'contents': contents})
            else:
                error_msg = f'The path {file_path} is not a file.'
                self.logger.error(error_msg)
                return json.dumps({'error': error_msg})
        except Exception as e:
            error_msg = f'An error occurred while reading the file: {e}'
            self.logger.exception("Failed to read the file.")
            return json.dumps({'error': error_msg})

    async def read_bytes_internal(self, file_path: str) -> bytes:
        if not self._is_path_within_workspace(file_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        full_path: Path = self.workspace_root.joinpath(file_path)
        try:
            if full_path.is_file():
                with open(full_path, 'rb') as file:
                    contents = file.read()
                return contents
            else:
                error_msg = f'The path {full_path} is not a file.'
                self.logger.error(error_msg)
                raise ValueError(error_msg)
        except Exception as e:
            error_msg = f'An error occurred while reading the file: {e}'
            self.logger.exception("Failed to read the file.")
            raise RuntimeError(error_msg)

    async def read_bytes_base64(self, file_path: str) -> str:
        return base64.b64encode(await self.read_bytes_internal(file_path)).decode('utf-8')

    def full_path(self, file_path: str, mkdirs: bool = True) -> Union[str, None]:
        if not self._is_path_within_workspace(file_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return None

        full_path: Path = self.workspace_root.joinpath(file_path)
        if mkdirs:
            full_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists in case they're going to write.

        return str(full_path)

    async def path_exists(self, file_path: str) -> bool:
        return self.workspace_root.joinpath(file_path).exists()

    async def write(self, file_path: str, mode: str, data: str) -> str:
        if self.read_only:
            return json.dumps({'error': 'This workspace is read-only.'})

        if not self._is_path_within_workspace(file_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(file_path)
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

            write_mode = 'w' if (mode == 'write' or mode == 'w') else 'a'
            with open(full_path, write_mode, encoding='utf-8') as file:
                file.write(data)

            action = 'written to' if write_mode == 'w' else 'appended in'
            return json.dumps({'message': f'Data successfully {action} {file_path}.'})
        except Exception as e:
            error_msg = f'An error occurred while writing to the file: {e}'
            self.logger.exception(f"Failed to write to the file: {file_path}")
            return json.dumps({'error': error_msg})

    async def write_bytes(self, file_path: str, mode: str, data: bytes) -> str:
        if self.read_only:
            return json.dumps({'error': 'This workspace is read-only.'})

        if not self._is_path_within_workspace(file_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(file_path)
        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

            write_mode = 'wb' if (mode == 'write' or mode == 'wb') else 'ab'
            with open(full_path, write_mode) as file:
                file.write(data)

            action = 'written to' if write_mode == 'wb' else 'appended in'
            return json.dumps({'message': f'Data successfully {action} {file_path}.'})
        except Exception as e:
            error_msg = f'An error occurred while writing to the file: {e}'
            self.logger.exception(f"Failed to write to the file: {file_path}")
            return json.dumps({'error': error_msg})


class LocalProjectWorkspace(LocalStorageWorkspace):
    """
    A workspace that automatically determines the project path using a fallback strategy:
    1. Uses PROJECT_WORKSPACE_PATH environment variable if available
    2. Uses 'app/workspaces/project' path if it exists
    3. Defaults to current working directory

    The description can be overridden via PROJECT_WORKSPACE_DESCRIPTION environment variable.
    """

    def __init__(self, name="project", default_description="A workspace holding the `Agent C` source code in Python."):
        # Use a specific logger name that matches your logging configuration
        self.logger = logging.getLogger("agent_c_tools.tools.workspaces.local_project_workspace")
        self.logger.info("Initializing LocalProjectWorkspace")  # Add this to verify logger works

        # Determine workspace path using fallback strategy
        workspace_path = self._determine_workspace_path()

        # Get description from environment variable or use default
        description = os.environ.get("PROJECT_WORKSPACE_DESCRIPTION", default_description)

        # Initialize the parent class with the determined parameters
        super().__init__(
            name=name,
            workspace_path=workspace_path,
            description=description
        )

    def _determine_workspace_path(self) -> str:
        """
        Determine the workspace path using the fallback strategy:
        1. Environment variable
        2. app/workspaces/project directory
        3. Current working directory
        """
        # Check for environment variable
        if "PROJECT_WORKSPACE_PATH" in os.environ:
            self.logger.info(f"Found PROJECT_WORKSPACE_PATH environment variable: {os.environ['PROJECT_WORKSPACE_PATH']}")
            return os.environ["PROJECT_WORKSPACE_PATH"]

        # Check if /app/workspaces/project exists
        app_workspace_path = Path("/app/workspaces/project")
        if app_workspace_path.exists():
            self.logger.info(f"Found /app/workspaces/project directory: {str(app_workspace_path.absolute())}")
            return str(app_workspace_path.absolute())

        # Default to current working directory
        self.logger.info(f"Using current working directory as the project workspace: {os.getcwd()}")
        return os.getcwd()
