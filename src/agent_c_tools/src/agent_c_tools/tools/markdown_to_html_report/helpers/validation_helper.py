from typing import Dict, Any, List, Optional, Tuple


class ValidationHelper:
    """Helper class for validation operations."""

    @staticmethod
    def validate_required_fields(kwargs: Dict[str, Any], required_fields: List[str]) -> Optional[str]:
        """Validate required fields exist in kwargs."""
        missing_fields = [field for field in required_fields if kwargs.get(field) is None]
        if missing_fields:
            return f"Required fields cannot be empty: {', '.join(missing_fields)}"
        return None