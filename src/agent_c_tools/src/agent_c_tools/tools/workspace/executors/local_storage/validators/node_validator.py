from typing import Dict, Any, List, Mapping
import os
from .base_validator import ValidationResult, CommandValidator
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

class NodeCommandValidator:
    """
    Keep node to version/metadata only. Block '-e/--eval' etc.
    Policy (example):
      node:
        flags: ["-v","--version","--help"]
        deny_global_flags: ["-e","--eval","-p","--print"]
        default_timeout: 5
    """

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        import os
        from .path_safety import is_within_workspace, looks_like_path, extract_file_part

        name = os.path.splitext(os.path.basename(parts[0]))[0].lower()
        if name not in ("node", "nodejs"):
            return ValidationResult(False, "Not a node command")

        allowed_flags = set(policy.get("flags") or [])
        deny_global = set(policy.get("deny_global_flags") or [])
        allow_script_paths = bool(policy.get("allow_script_paths", False))
        allow_test_mode = bool(policy.get("allow_test_mode", False))
        allowed_entrypoints = set(policy.get("allowed_entrypoints") or [])

        # Workspace root for fencing
        workspace_root = (
                policy.get("workspace_root")
                or os.environ.get("WORKSPACE_ROOT")
                or os.getcwd()
        )

        args = parts[1:]
        i = 0
        after_dashdash = False
        used_flags: List[str] = []

        def base_flag(tok: str) -> str:
            return tok.split("=", 1)[0]

        # Flags that require a value if allowed
        value_flags = {"--require", "--loader", "--test-reporter", "--test-name-pattern"}

        # 1) Parse flags (stop at first non-flag or `--`)
        while i < len(args):
            a = args[i]
            if a == "--":
                after_dashdash = True
                i += 1
                break
            if a.startswith("-") and not after_dashdash:
                b = base_flag(a)
                # deny list first
                if (b in deny_global) or (a in deny_global):
                    return ValidationResult(False, f"Global flag not allowed: {a}")
                # allow list (if provided)
                if allowed_flags and (b not in allowed_flags) and (a not in allowed_flags):
                    return ValidationResult(False, f"Flag not allowed: {a}")
                used_flags.append(b)
                # consume value for known value-taking flags
                if b in value_flags and "=" not in a:
                    i += 1
                    if i >= len(args) or args[i].startswith("-"):
                        return ValidationResult(False, f"{a} requires a value")
                i += 1
                continue
            break

        # Remaining tokens (could be a script path or, in --test mode, test roots/files)
        positionals = args[i:]

        # Case 0: no positionals ⇒ REPL or flag-only usage
        if not positionals:
            # Allowed: e.g., `node -v` / `node --help` / `node --trace-warnings` (if whitelisted)
            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

        # Detect Node’s built-in test runner mode
        is_test_mode = ("--test" in used_flags)

        # Case 1: node --test <paths...>
        if is_test_mode:
            if not allow_test_mode:
                return ValidationResult(False, "Node --test mode is disabled by policy")
            # Fence every path-like positional to the workspace
            for tok in positionals:
                if looks_like_path(tok) and not is_within_workspace(workspace_root, extract_file_part(tok)):
                    return ValidationResult(False, f"Unsafe path outside workspace in node --test args: {tok}")
            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

        # Case 2: node <script.js> [args...]  (script execution)
        if not allow_script_paths:
            # Your original behavior: disallow running scripts entirely
            return ValidationResult(False, f"Arguments not allowed for node: {' '.join(positionals[:3])}")

        script = positionals[0]

        # Never permit eval/print/STDIN “scripts”
        if script in ("-e", "--eval", "-p", "--print", "-"):
            return ValidationResult(False, "Eval/print/STDIN execution is not allowed")

        # Script must be a path within workspace
        if not looks_like_path(script) or not is_within_workspace(workspace_root, extract_file_part(script)):
            return ValidationResult(False, f"Unsafe script path: {script}")

        # Optional: restrict to explicit entrypoints
        if allowed_entrypoints:
            def norm(p: str) -> str:
                if not os.path.isabs(p):
                    p = os.path.join(workspace_root, p)
                return os.path.normcase(os.path.realpath(p))

            norm_script = norm(script)
            norm_allow = {norm(p) for p in allowed_entrypoints}
            if norm_script not in norm_allow:
                return ValidationResult(False, f"Script not in allowed entrypoints: {script}")

        return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        env = dict(base_env)
        env.update(policy.get("env_overrides") or {})
        
        # Prepend node_modules/.bin to PATH if workspace root is available
        workspace_root = base_env.get("WORKSPACE_ROOT")
        if workspace_root:
            node_modules_bin = os.path.join(workspace_root, "node_modules", ".bin")
            if os.path.exists(node_modules_bin):
                env["PATH_PREPEND"] = node_modules_bin
                
        return env