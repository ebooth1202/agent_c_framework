import json
from typing import Tuple, Optional, Union, Dict, Any


def parse_workspace_result(result: str, operation_name: str = "workspace operation") -> Tuple[bool, Optional[Union[Dict[str, Any], str]], Optional[str]]:
    """Parse workspace tool results that may be JSON, YAML, or error strings.

    Args:
        result: The result string from a workspace tool method
        operation_name: Name of the operation for error reporting

    Returns:
        tuple: (success: bool, data: dict|str, error_msg: str|None)
    """
    if not isinstance(result, str):
        return False, None, f"Expected string result from {operation_name}, got {type(result)}"

    # Check for error responses
    if result.startswith(("Error:", "ERROR:")):
        return False, None, result

    # Try JSON first (most common for write operations)
    try:
        data = json.loads(result)
        if isinstance(data, dict) and 'error' in data:
            return False, data, data['error']
        return True, data, None
    except json.JSONDecodeError:
        pass

    # Try YAML (common for ls operations)
    try:
        import yaml
        data = yaml.safe_load(result)
        if isinstance(data, dict) and 'error' in data:
            return False, data, data['error']
        return True, data, None
    except Exception:
        pass

    # If all parsing fails, treat as raw string (might be success message)
    if "success" in result.lower() or "completed" in result.lower():
        return True, result, None
    else:
        return False, None, f"Could not parse {operation_name} result: {result}"
