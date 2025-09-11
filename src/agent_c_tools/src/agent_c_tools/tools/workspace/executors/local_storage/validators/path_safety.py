# validators/path_safety.py
import os

def is_within_workspace(workspace_root: str, candidate: str) -> bool:
    """
    True if `candidate` (abs or rel) lives under `workspace_root`, after resolving
    symlinks and normalizing case (Windows).
    """
    if not candidate or not workspace_root:
        return False

    # If relative, treat as relative to workspace_root
    if not os.path.isabs(candidate):
        candidate = os.path.join(workspace_root, candidate)
    try:
        abs_root = os.path.normcase(os.path.realpath(workspace_root))
        abs_cand = os.path.normcase(os.path.realpath(candidate))
        return os.path.commonpath([abs_root, abs_cand]) == abs_root
    except Exception:
        return False


def looks_like_path(token: str) -> bool:
    if not token or token.startswith("-"):
        return False
    return (
        # Need to consider adding others when we add other validators
        token.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".csproj", ".sln"))
        or "::" in token       # pytest node-ids
        or "/" in token or "\\" in token
        or ":" in token        # file:line OR Windows drive; fenced by is_within_workspace
    )

def extract_file_part(token: str) -> str:
    """
    Pull the filesystem-looking part from a test selector.
    Works for:
      - pytest: tests/foo.py::TestX::test_y, tests/foo.py:123
      - generic runners: just returns token
    Leaves Windows drive letters intact (e.g., 'C:\\...').
    """
    t = token
    if "::" in t:
        t = t.split("::", 1)[0]
    if ":" in t:
        i = t.rfind(":")
        if i > 1 and t[i+1:].isdigit():
            t = t[:i]  # strip :<line>
    return t