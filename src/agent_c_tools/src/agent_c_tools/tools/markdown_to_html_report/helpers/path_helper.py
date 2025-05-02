class PathHelper:
    """Helper class for path operations."""

    @staticmethod
    def normalize_path(path: str) -> str:
        """Normalize path separators and ensure consistency."""
        return path.replace('\\', '/')

    @staticmethod
    def ensure_unc_path(path: str, workspace: str) -> str:
        """Ensure a path is in UNC format."""
        normalized_path = PathHelper.normalize_path(path)
        if not normalized_path.startswith('//'):
            return f"//{workspace}/{normalized_path.lstrip('/')}"
        return normalized_path

    @staticmethod
    def is_markdown_file(filename: str) -> bool:
        """Check if a file is a markdown file."""
        filename_lower = filename.lower()
        return filename_lower.endswith('.md') or filename_lower.endswith('.markdown')

    @staticmethod
    def ensure_file_extension(filename: str, extension: str) -> str:
        """Ensure filename has the specified extension."""
        if not filename.lower().endswith(f'.{extension.lower()}'):
            return f"{filename}.{extension}"
        return filename