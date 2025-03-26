import os
import json
import base64
import shutil
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

    def _normalize_input_path(self, path: str) -> str:
        """
        Normalize the input path so it uses the correct OS-specific separator.

        This method first converts all backslashes to forward slashes, and then,
        if the OS separator isn’t '/', it replaces them with the proper one.
        Finally, it normalizes the path.
        """
        # Unify slashes by replacing backslashes with forward slashes
        normalized = path.replace("\\", "/")
        # If the OS separator isn't '/', replace forward slashes accordingly
        if os.sep != "/":
            normalized = normalized.replace("/", os.sep)
        return os.path.normpath(normalized)

    def _is_path_within_workspace(self, path: str) -> bool:
        """Check if the provided path is within the workspace.

        With symlink allowance enabled, this checks the path string itself rather than
        resolving to physical paths, which would break in Docker environments.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path is valid within the workspace context, else False.
        """
        norm_path = self._normalize_input_path(path)
        # Prevent path traversal attacks with ".." regardless of symlink settings
        if ".." in norm_path.split(os.sep):
            return False

        if self.allow_symlinks:
            return True

        resolved_path = self.workspace_root.joinpath(norm_path).resolve()
        return self.workspace_root in resolved_path.parents or resolved_path == self.workspace_root

    async def tree(self, relative_path: str) -> str:
        norm_path = self._normalize_input_path(relative_path)
        if not self._is_path_within_workspace(norm_path):
            error_msg = f'The path {relative_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(norm_path)
        return '\n'.join(generate_path_tree(str(full_path)))

    async def ls(self, relative_path: str) -> str:
        norm_path = self._normalize_input_path(relative_path)
        if not self._is_path_within_workspace(norm_path) or norm_path == '':
            error_msg = f'The path {relative_path} is not within the workspace.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(norm_path)
        try:
            contents = os.listdir(full_path)
            return json.dumps({'contents': contents})
        except Exception as e:
            error_msg = str(e)
            self.logger.exception("Failed to list directory contents.")
            return json.dumps({'error': error_msg})

    async def read(self, file_path: str) -> str:
        norm_path = self._normalize_input_path(file_path)
        if not self._is_path_within_workspace(norm_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(norm_path)
        try:
            if full_path.is_file():
                with open(full_path, 'r', encoding='utf-8') as file:
                    contents = file.read()
                    file_tokens = TokenCounter.count(contents)
                    if file_tokens > self.max_token_size:
                        error_msg = (
                            f'The file {file_path} exceeds the token limit of '
                            f'{self.max_token_size}.  Actual size is {file_tokens}.'
                        )
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
        norm_path = self._normalize_input_path(file_path)
        if not self._is_path_within_workspace(norm_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        full_path: Path = self.workspace_root.joinpath(norm_path)
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
        norm_path = self._normalize_input_path(file_path)
        if not self._is_path_within_workspace(norm_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return None

        full_path: Path = self.workspace_root.joinpath(norm_path)
        if mkdirs:
            full_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists in case they're going to write.
        return str(full_path)

    async def path_exists(self, file_path: str) -> bool:
        norm_path = self._normalize_input_path(file_path)
        return self.workspace_root.joinpath(norm_path).exists()

    async def write(self, file_path: str, mode: str, data: str) -> str:
        if self.read_only:
            return json.dumps({'error': 'This workspace is read-only.'})

        norm_path = self._normalize_input_path(file_path)
        if not self._is_path_within_workspace(norm_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(norm_path)
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

        norm_path = self._normalize_input_path(file_path)
        if not self._is_path_within_workspace(norm_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path: Path = self.workspace_root.joinpath(norm_path)
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

    async def apply_unified_diff(self, file_path: str, diff_content: str) -> str:
        """
        Apply a simple diff to a file in the workspace.

        Args:
            file_path (str): The path to the file to be modified
            diff_content (str): The unified diff content to apply

        Returns:
            str: JSON response with success message or error
        """
        # Handle read-only check
        if self.read_only:
            return json.dumps({'error': 'This workspace is read-only.'})

        # Validate and normalize path
        norm_path = self._normalize_input_path(file_path)
        if not self._is_path_within_workspace(norm_path):
            error_msg = f'The file {file_path} is not within the workspaces.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_path = self.workspace_root.joinpath(norm_path)

        # Check if file exists
        if not full_path.is_file():
            error_msg = f'The file {file_path} does not exist.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        try:
            # Read the original file content
            original_content = self._read_file(full_path)

            # Create a temporary file with the diff content
            temp_file_path = self._create_temp_diff_file(diff_content)

            try:
                # Apply the patch and write the result
                new_content = self._apply_patch(temp_file_path, original_content)
                self._write_file(full_path, new_content)

                return json.dumps({'message': f'Diff successfully applied to {file_path}.'})
            finally:
                # Clean up the temporary file
                os.unlink(temp_file_path)

        except Exception as e:
            error_msg = f'An error occurred while applying the diff: {e}'
            self.logger.exception("Failed to apply diff to the file.")
            return json.dumps({'error': error_msg})

    async def cp(self, src_path: str, dest_path: str) -> str:
        """
        Copy a file or directory from src_path to dest_path within the workspace.

        Args:
            src_path (str): Source path relative to workspace
            dest_path (str): Destination path relative to workspace

        Returns:
            str: JSON response with success message or error
        """
        if self.read_only:
            return json.dumps({'error': 'This workspace is read-only.'})

        # Normalize and validate paths
        norm_src = self._normalize_input_path(src_path)
        norm_dest = self._normalize_input_path(dest_path)

        if not self._is_path_within_workspace(norm_src):
            error_msg = f'The source path {src_path} is not within the workspace.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        if not self._is_path_within_workspace(norm_dest):
            error_msg = f'The destination path {dest_path} is not within the workspace.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_src_path = self.workspace_root.joinpath(norm_src)
        full_dest_path = self.workspace_root.joinpath(norm_dest)

        # Check if source exists
        if not full_src_path.exists():
            error_msg = f'The source path {src_path} does not exist.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        try:
            # Create parent directories for destination if they don't exist
            full_dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Perform copy operation based on whether source is file or directory
            if full_src_path.is_file():
                import shutil
                shutil.copy2(full_src_path, full_dest_path)
                return json.dumps({'message': f'File {src_path} successfully copied to {dest_path}.'})
            elif full_src_path.is_dir():
                import shutil
                # If destination exists and is a directory, copy into it
                if full_dest_path.exists() and full_dest_path.is_dir():
                    # Copy content into the existing directory
                    dest_dir = full_dest_path / full_src_path.name
                    shutil.copytree(full_src_path, dest_dir)
                    return json.dumps({'message': f'Directory {src_path} successfully copied to {dest_path}/{full_src_path.name}.'})
                else:
                    # Copy to the specified destination
                    shutil.copytree(full_src_path, full_dest_path)
                    return json.dumps({'message': f'Directory {src_path} successfully copied to {dest_path}.'})
            else:
                error_msg = f'The source path {src_path} is neither a file nor a directory.'
                self.logger.error(error_msg)
                return json.dumps({'error': error_msg})
        except Exception as e:
            error_msg = f'An error occurred while copying: {e}'
            self.logger.exception("Failed to copy.")
            return json.dumps({'error': error_msg})

    async def mv(self, src_path: str, dest_path: str) -> str:
        """
        Move a file or directory from src_path to dest_path within the workspace.

        Args:
            src_path (str): Source path relative to workspace
            dest_path (str): Destination path relative to workspace

        Returns:
            str: JSON response with success message or error
        """
        if self.read_only:
            return json.dumps({'error': 'This workspace is read-only.'})

        # Normalize and validate paths
        norm_src = self._normalize_input_path(src_path)
        norm_dest = self._normalize_input_path(dest_path)

        if not self._is_path_within_workspace(norm_src):
            error_msg = f'The source path {src_path} is not within the workspace.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        if not self._is_path_within_workspace(norm_dest):
            error_msg = f'The destination path {dest_path} is not within the workspace.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        full_src_path = self.workspace_root.joinpath(norm_src)
        full_dest_path = self.workspace_root.joinpath(norm_dest)

        # Check if source exists
        if not full_src_path.exists():
            error_msg = f'The source path {src_path} does not exist.'
            self.logger.error(error_msg)
            return json.dumps({'error': error_msg})

        try:
            # Create parent directories for destination if they don't exist
            full_dest_path.parent.mkdir(parents=True, exist_ok=True)

            # If destination is an existing directory, move into it
            if full_dest_path.exists() and full_dest_path.is_dir():
                dest = full_dest_path / full_src_path.name
                shutil.move(str(full_src_path), str(dest))
                return json.dumps({'message': f'{src_path} successfully moved to {dest_path}/{full_src_path.name}.'})
            else:
                # Move to the specified destination
                shutil.move(str(full_src_path), str(full_dest_path))
                return json.dumps({'message': f'{src_path} successfully moved to {dest_path}.'})
        except Exception as e:
            error_msg = f'An error occurred while moving: {e}'
            self.logger.exception("Failed to move.")
            return json.dumps({'error': error_msg})

    def _read_file(self, path: Path) -> str:
        """Read file content with UTF-8 encoding."""
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()

    def _write_file(self, path: Path, content: str) -> None:
        """Write content to file with UTF-8 encoding."""
        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)



from agent_c_tools.tools.workspaces.local_project import LocalProjectWorkspace

if __name__ == "__main__":
    import asyncio
    import sys
    import os


    async def main():
        # Initialize workspace with the specified desktop path
        workspace = LocalStorageWorkspace(
            workspace_path="C:\\Users\\donav\\Desktop",
            max_size=50000,
            read_only=False,
            allow_symlinks=True
        )

        # Check if the correct number of arguments is provided
        if len(sys.argv) != 3:
            print("Usage: python local_storage.py <file_to_patch> <diff_file>")
            return

        # Get the file to patch and the diff file paths from command line arguments
        file_to_patch = sys.argv[1]
        full_diff_path = sys.argv[2]

        # Check if both files exist
        if not await workspace.path_exists(file_to_patch):
            print(f"Error: File to patch '{file_to_patch}' does not exist.")
            return

        # Read the diff content
        try:
            with open(full_diff_path, 'r', encoding='utf-8') as f:
                diff_content = f.read()
        except Exception as e:
            print(f"Error reading diff file: {e}")
            return

        print(f"Applying diff from '{full_diff_path}' to '{file_to_patch}'...")

        # Apply the unified diff
        result = await workspace.apply_unified_diff(file_to_patch, diff_content)
        print(result)

        # Display the modified file content if successful
        if '"error":' not in result:
            content_result = await workspace.read(file_to_patch)
            try:
                import json
                content = json.loads(content_result).get('contents', '')
                print("\nModified file content:")
                print(content)
            except:
                print("\nCould not display file content.")


    # Run the async main function
    asyncio.run(main())

