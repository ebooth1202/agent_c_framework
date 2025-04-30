from typing import Dict, Any, List, Optional, Tuple


class ValidationHelper:
    """Helper class for validation operations."""

    def __init__(self, workspace_tool):
        self.workspace_tool = workspace_tool

    @staticmethod
    def validate_required_fields(kwargs: Dict[str, Any], required_fields: List[str]) -> Optional[str]:
        """Validate required fields exist in kwargs."""
        missing_fields = [field for field in required_fields if kwargs.get(field) is None]
        if missing_fields:
            return f"Required fields cannot be empty: {', '.join(missing_fields)}"
        return None

    async def validate_path(self, full_path: str) -> Tuple[Optional[str], Any, Any]:
        """Validate a path using workspace tools."""
        return self.workspace_tool.validate_and_get_workspace_path(full_path)