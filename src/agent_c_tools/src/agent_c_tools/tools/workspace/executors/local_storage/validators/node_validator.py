from typing import Dict, Any, List, Mapping
import os
from .base_validator import ValidationResult, CommandValidator
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

class NodeCommandValidator:
    """
    Keep node to version/metadata only. Block '-e/--eval' etc.
    Policy (example):
      node:
        flags: 
          "--test": { suppress_success_output: true, allow_test_mode: true }
          "-v": {}
          "--version": {}
        deny_global_flags: ["-e","--eval","-p","--print"]
        default_timeout: 5
    """

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        import os
        from .path_safety import is_within_workspace, looks_like_path, extract_file_part

        name = os.path.splitext(os.path.basename(parts[0]))[0].lower()
        if name not in ("node", "nodejs"):
            return ValidationResult(False, "Not a node command")

        # Handle both old (list) and new (dict) flags format
        flags_config = policy.get("flags")
        flags_configured = flags_config is not None
        
        if isinstance(flags_config, dict):
            allowed_flags = set(flags_config.keys())
            flags_settings = flags_config
        elif isinstance(flags_config, list):
            # Legacy list format
            allowed_flags = set(flags_config)
            flags_settings = {}
        else:
            # No flags configuration
            allowed_flags = set()
            flags_settings = {}
            flags_configured = False
            
        deny_global = set(policy.get("deny_global_flags") or [])
        allow_script_paths = bool(policy.get("allow_script_paths", False))
        allow_test_mode = bool(policy.get("allow_test_mode", False))
        allowed_entrypoints = set(policy.get("allowed_entrypoints") or [])

        # Extract modes configuration
        modes_config = policy.get("modes", {})

        # Workspace root for fencing
        workspace_root = (
                policy.get("workspace_root")
                or os.environ.get("WORKSPACE_ROOT")
                or os.getcwd()
        )

        # All the argument parsing logic
        args = parts[1:]
        i = 0
        after_dashdash = False
        used_flags: List[str] = []
        suppress_success_output = False

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
                # allow list (if flags are configured, enforce strictly)
                if flags_configured and (b not in allowed_flags) and (a not in allowed_flags):
                    return ValidationResult(False, f"Flag not allowed: {a}")
                used_flags.append(b)
                
                # Check for flag-specific settings
                flag_spec = flags_settings.get(b, {}) or flags_settings.get(a, {})
                if flag_spec.get("suppress_success_output", False):
                    suppress_success_output = True
                    
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
            # Use modes config instead of hardcoded policy_spec=None
            mode_spec = modes_config.get("repl", {})
            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"), 
                                  suppress_success_output=suppress_success_output, policy_spec=mode_spec)

        # Detect Node's built-in test runner mode
        is_test_mode = ("--test" in used_flags)

        # Case 1: node --test <paths...>
        if is_test_mode:
            # Use modes config for test mode settings
            mode_spec = modes_config.get("test", {})

            # Check allow_test_mode from flag-specific settings first
            flag_allows_test = any(flags_settings.get(f, {}).get("allow_test_mode", False) for f in used_flags)
            mode_allows_test = mode_spec.get("allow_test_mode", False)
            
            if not (flag_allows_test or mode_allows_test or allow_test_mode):
                return ValidationResult(False, "Node --test mode is disabled by policy")

            # Fence every path-like positional to the workspace
            for tok in positionals:
                if looks_like_path(tok) and not is_within_workspace(workspace_root, extract_file_part(tok)):
                    return ValidationResult(False, f"Unsafe path outside workspace in node --test args: {tok}")

            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"), 
                                  suppress_success_output=suppress_success_output, policy_spec=mode_spec)

        # Case 2: node <script.js> [args...]  (script execution)
        # Use modes config for script mode settings
        mode_spec = modes_config.get("script", {})

        # Check allow_script_paths from mode spec first, fallback to global policy
        if not (mode_spec.get("allow_script_paths", False) or allow_script_paths):
            return ValidationResult(False, f"Arguments not allowed for node: {' '.join(positionals[:3])}")

        script = positionals[0]

        # Never permit eval/print/STDIN "scripts"
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

        return ValidationResult(True, "OK", timeout=policy.get("default_timeout"), 
                              suppress_success_output=suppress_success_output, policy_spec=mode_spec)

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
