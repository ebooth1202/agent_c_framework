from typing import Optional
from io import StringIO
from unidiff import PatchSet
from tempfile import NamedTemporaryFile

class BaseWorkspace:
    """
    This is a base class for workspace representations.

    Attributes:
        name (str): The name of the workspace, as provided by kwargs.
        description (str): The description of the workspace, if provided.
        type_name (str): The type name of the workspace.
        read_only (bool): A flag indicating whether the workspace is read-only.
        write_status (str): A textual representation of the read/write status.
        max_filename_length (int): The maximum length of filenames in the workspace.
                                  A value of -1 indicates no specific limit.
    """

    def __init__(self, type_name: str, **kwargs):
        """
        The initializer for the BaseWorkspace class.

        Args:
            type_name (str): The type name of the workspace.
            **kwargs: Keyword arguments for the workspace properties.
                      - 'name' (str): The name of the workspace.
                      - 'description' (str): The description of the workspace.
                      - 'read_only' (bool): If the workspace should be read-only.
        """
        self.name: Optional[str] = kwargs.get('name')
        self.description: Optional[str] = kwargs.get('description')
        self.type_name: str = type_name
        self.read_only: bool = kwargs.get('read_only', False)
        self.write_status: str = "read only" if self.read_only else "read write"
        self.max_filename_length: int = -1

    def __str__(self) -> str:
        """
        String representation of the BaseWorkspace instance.

        Returns:
            str: A formatted string summary of the workspace.
        """
        return f"- workspace_name: `{self.name}`, rw_status: ({self.write_status}), workspace_type: \"{self.type_name}\", description: {self.description}"

    async def path_exists(self, file_path: str) -> bool:
        """
        Abstract method to check if a path exists within the workspace.

        Args:
            file_path (str): The path to check for existence.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError

    async def tree(self, relative_path: str) -> str:
        raise NotImplementedError

    async def read_bytes_internal(self, file_path: str) -> bytes:
        """
        Abstract method to read bytes directly from a path within the workspace.

        Args:
            file_path (str): The path from which to read bytes.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError

    async def read_bytes_base64(self, file_path: str) -> str:
        """
        Abstract method to read bytes and encode them base64 from a path within the workspace.

        Args:
            file_path (str): The path from which to read bytes.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError

    async def write_bytes(self, file_path: str, mode: str, data: bytes) -> str:
        """
        Abstract method to write bytes to a path within the workspace.

        Args:
            file_path (str): The path where to write bytes.
            mode (str): The mode in which to write the data, can be "write" or "append".
            data (bytes): The data to write into the file.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError

    def full_path(self, path: str, mkdirs: bool = True) -> Optional[str]:
        """
        Method to generate the full path for a given path in the workspace.

        Args:
            path (str): The directory or file path.
            mkdirs (bool): Whether to create directories along the path if they do not exist.

        Returns:
            Optional[str]: The full path or None if the path is not within the workspace.
        """
        return None

    async def ls(self, path: str) -> str:
        """
        Abstract method to list all files in a directory within the workspace.

        Args:
            path (str): The directory path to list files from.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError

    async def read(self, path: str) -> str:
        """
        Abstract method to read text from a path within the workspace.

        Args:
            path (str): The path from which to read text.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError

    async def write(self, path: str, mode: str, data: str) -> str:
        """
        Abstract method to write text to a path within the workspace.

        Args:
            path (str): The path where to write text.
            mode (str): The mode in which to open the file.
            data (str): The data to write into the file.

        Raises:
            NotImplementedError: This method should be implemented by subclasses.
        """
        raise NotImplementedError

    async def apply_unified_diff(self, file_path: str, diff_content: str) -> str:
        raise NotImplementedError

    async def cp(self, src_path: str, dest_path: str) -> str:
        raise NotImplementedError

    async def mv(self, src_path: str, dest_path: str) -> str:
        raise NotImplementedError

    @staticmethod
    def _create_temp_diff_file(diff_content: str) -> str:
        """Create a temporary file with diff content and return its path."""
        with NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write(diff_content)
            return temp_file.name

    def _apply_patch_manual(self, patch_file_path: str, original_content: str) -> str:
        """Apply a patch to the original content using manual parsing."""
        import re

        # Read the patch file
        with open(patch_file_path, 'r', encoding='utf-8') as f:
            patch_content = f.read()

        # Get original lines
        original_lines = original_content.splitlines()
        result_lines = original_lines.copy()

        # Debug info
        print(f"Manual patch: Original file has {len(original_lines)} lines")

        # Pattern to match hunk headers, ignoring context after @@
        hunk_pattern = re.compile(r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@')

        # Process the patch in chunks
        lines = patch_content.splitlines()
        current_file = None
        changes_made = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Handle file headers (--- and +++ lines)
            if line.startswith('--- '):
                # Start of a new file patch
                source_file = line[4:].split('\t')[0]
                if source_file.startswith('a/'):
                    source_file = source_file[2:]
                current_file = source_file
                i += 1
                continue
            elif line.startswith('+++ '):
                # Target file - just skip
                i += 1
                continue
            elif line.startswith('@@ '):
                # We found a hunk header
                match = hunk_pattern.search(line)
                if not match:
                    print(f"Warning: Could not parse hunk header: {line}")
                    i += 1
                    continue

                # Parse the hunk header
                source_start = int(match.group(1))  # 1-based
                source_length = int(match.group(2))
                target_start = int(match.group(3))  # 1-based
                target_length = int(match.group(4))

                print(f"Processing hunk: @@ -{source_start},{source_length} +{target_start},{target_length} @@")

                # Convert to 0-based indices for Python
                source_start -= 1

                # Collect all lines in the hunk
                hunk_lines = []
                i += 1
                while i < len(lines) and not lines[i].startswith('@@ '):
                    if not lines[i].startswith('\\'):  # Skip "\ No newline at end of file"
                        hunk_lines.append(lines[i])
                    i += 1

                # Apply the hunk
                offset = 0
                hunk_pos = 0

                # Create a list of operations to perform
                operations = []

                # Process the hunk to generate operations
                actual_source_line = source_start
                for hunk_line in hunk_lines:
                    if hunk_line.startswith(' '):  # Context line
                        # Verify context
                        if actual_source_line < len(original_lines):
                            context_line = hunk_line[1:]
                            original_line = original_lines[actual_source_line]
                            if context_line != original_line:
                                print(f"Warning: Context mismatch at line {actual_source_line + 1}:")
                                print(f"Expected: '{context_line}'")
                                print(f"Found:    '{original_line}'")
                        actual_source_line += 1
                    elif hunk_line.startswith('-'):  # Remove line
                        operations.append(('remove', actual_source_line, hunk_line[1:]))
                        actual_source_line += 1
                    elif hunk_line.startswith('+'):  # Add line
                        operations.append(('add', actual_source_line, hunk_line[1:]))
                    else:
                        print(f"Warning: Unexpected line in hunk: {hunk_line}")

                # Apply operations in the correct order - removes first, then adds
                # First sort by line number in reverse order
                remove_operations = sorted([op for op in operations if op[0] == 'remove'],
                                           key=lambda x: x[1], reverse=True)

                # Apply all removes
                for _, line_num, _ in remove_operations:
                    if line_num < len(result_lines):
                        result_lines.pop(line_num)
                        changes_made += 1

                # Now apply all adds in forward order
                add_operations = sorted([op for op in operations if op[0] == 'add'],
                                        key=lambda x: x[1])

                # Apply adds with adjusted positions
                for _, line_num, content in add_operations:
                    result_lines.insert(line_num, content)
                    changes_made += 1

                # Don't increment i here, since the while loop already moved past the hunk
            else:
                # Skip any other lines
                i += 1

        print(f"Manual patch complete. Made {changes_made} changes.")
        return '\n'.join(result_lines)

    def _apply_patch(self, patch_file_path: str, original_content: str) -> str:
        """Apply a patch to the original content."""

        try:
            # Try standard PatchSet parsing first
            patch_set = PatchSet.from_filename(patch_file_path, encoding='utf-8')

            if len(patch_set) != 1:
                raise ValueError("Expected a single file in the patch")

            patched_file = patch_set[0]
            original_lines = original_content.splitlines(True)  # Keep line endings

            # Track how many lines we've added/removed so far
            line_offset = 0
            result_lines = original_lines.copy()  # Start with a copy we can modify

            for hunk in patched_file:
                # Adjust hunk start position based on previous changes
                adjusted_start = hunk.source_start - 1 + line_offset

                # Track position within the hunk
                hunk_line = 0
                lines_added = 0
                lines_removed = 0

                # Process each line in the hunk
                for line in hunk:
                    if line.is_added:
                        # Insert new line at the current position
                        result_lines.insert(adjusted_start + hunk_line + lines_added, line.value)
                        lines_added += 1
                    elif line.is_removed:
                        # Remove the line at the current position (accounting for previous adds)
                        result_lines.pop(adjusted_start + hunk_line)
                        lines_removed += 1
                    else:  # Context line
                        hunk_line += 1

                # Update offset for next hunk
                line_offset += (lines_added - lines_removed)

            return ''.join(result_lines)

        except Exception as e:
            # If standard parsing fails, try manual parsing as fallback
            return self._apply_patch_manual(patch_file_path, original_content)

    def _apply_patch_manual(self, patch_file_path: str, original_content: str) -> str:
        """Apply a patch to the original content using manual parsing."""
        import re

        # Read the patch file
        with open(patch_file_path, 'r', encoding='utf-8') as f:
            patch_content = f.read()

        # Get original lines (without line endings to make processing easier)
        original_lines = original_content.splitlines()
        result_lines = original_lines.copy()

        # Pattern to match hunk headers, ignoring context after @@
        hunk_pattern = re.compile(r'^@@ -(\d+),(\d+) \+(\d+),(\d+) @@')

        lines = patch_content.splitlines()
        i = 0

        # Skip the file header lines (--- and +++ lines)
        while i < len(lines) and not lines[i].startswith('@@ '):
            i += 1

        # Process each hunk
        while i < len(lines):
            if not lines[i].startswith('@@ '):
                i += 1
                continue

            # Parse hunk header
            match = hunk_pattern.match(lines[i])
            if not match:
                i += 1
                continue

            # Get hunk line numbers (line numbers in diff are 1-based, python is 0-based)
            source_start = int(match.group(1)) - 1
            source_count = int(match.group(2))
            target_start = int(match.group(3)) - 1  # Not used but kept for clarity
            target_count = int(match.group(4))  # Not used but kept for clarity

            # Move past hunk header
            i += 1

            # Track current position in source
            current_line = source_start

            # Collect changes for this hunk
            hunk_changes = []  # (position, action, content)
            context_count = 0

            # Process each line in the hunk
            while i < len(lines) and not lines[i].startswith('@@ '):
                line = lines[i]

                if line.startswith('-'):
                    # Line to remove
                    hunk_changes.append((current_line, 'remove', line[1:]))
                    current_line += 1
                elif line.startswith('+'):
                    # Line to add
                    hunk_changes.append((current_line, 'add', line[1:]))
                elif line.startswith('\\'):
                    # No newline at end of file indicator - skip
                    pass
                else:
                    # Context line
                    hunk_changes.append((current_line, 'context', line[1:] if line.startswith(' ') else line))
                    current_line += 1
                    context_count += 1

                i += 1

            # If the hunk had no context lines, it might be malformed or empty
            if context_count == 0 and len(hunk_changes) == 0:
                continue

            # Apply the changes from this hunk
            # We need to process removes first, then adds, to avoid index shifting issues

            # Group changes by position
            positions = {}
            for pos, action, content in hunk_changes:
                if pos not in positions:
                    positions[pos] = {'remove': [], 'add': [], 'context': []}
                positions[pos][action].append(content)

            # Sort positions in reverse order so we can remove lines without affecting indices
            sorted_positions = sorted(positions.keys(), reverse=True)

            # First, verify context lines match (if they don't, the patch won't apply cleanly)
            context_correct = True
            for pos in sorted(positions.keys()):
                for context_line in positions[pos]['context']:
                    if pos >= len(result_lines) or result_lines[pos] != context_line:
                        context_correct = False
                        break
                if not context_correct:
                    break

            if not context_correct:
                raise ValueError(f"Context lines don't match at hunk starting at line {source_start + 1}")

            # First pass: remove lines (in reverse order)
            offset = 0
            for pos in sorted_positions:
                # Remove lines at this position
                for _ in range(len(positions[pos]['remove'])):
                    if pos - offset < len(result_lines):
                        result_lines.pop(pos - offset)
                        offset += 1

            # Second pass: add lines (in normal order)
            offset = 0
            for pos in sorted(positions.keys()):
                # Add lines at this position
                for content in positions[pos]['add']:
                    result_lines.insert(pos + offset, content)
                    offset += 1

        # Restore line endings
        return '\n'.join(result_lines)
