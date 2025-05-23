from typing import Dict, Any, List, Optional, TypedDict, Tuple


def _is_missing(val: Any) -> bool:
    if val is None:
        return True
    if isinstance(val, str) and not val.strip():  # "", "   "
        return True
    return False

def validate_required_fields(kwargs: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Return (ok, error_message).  A field is considered missing when

    * the key is absent
    * the value is None
    * the value is a blank or whitespace‑only string
    """
    missing_fields = [f for f in required_fields if _is_missing(kwargs.get(f))]
    if missing_fields:
        return False, f"Required fields cannot be empty: {', '.join(missing_fields)}"
    return True, None
