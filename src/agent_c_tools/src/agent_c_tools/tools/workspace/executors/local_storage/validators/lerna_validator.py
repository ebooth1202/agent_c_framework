from typing import Dict, Any, List, Mapping, Optional
import os
from .base_validator import ValidationResult, CommandValidator
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

class LernaCommandValidator(CommandValidator):
    """
    Validator for Lerna monorepo management commands with enhanced security.
    
    Lerna can be powerful and potentially dangerous with commands like 
    'exec' that can run arbitrary scripts. We restrict to safe informational
    and build-related commands with special handling for the 'run' subcommand.
    
    Expected policy shape:
      lerna:
        flags: [...]             # global flags allowed for all subcommands
        subcommands:
          list: { allowed_flags: [...] }
          info: { allowed_flags: [...] }
          bootstrap: { allowed_flags: [...] }
          clean: { allowed_flags: [...] }
          run:
            allowed_scripts: [...]  # scripts that can be executed
            deny_args: true         # prevent extra arguments after script name
            allowed_flags: [...]
            require_flags: [...]    # flags auto-injected if missing
          # ... other safe subcommands
        deny_subcommands: [...]  # explicitly blocked subcommands
        default_timeout: 120
        env_overrides: {...}
    """

    def _basename_noext(self, p: str) -> str:
        """Get basename without extension."""
        return os.path.splitext(os.path.basename(p))[0].lower()

    def _flag_base(self, f: str) -> str:
        """Handle flags with values like --scope=value."""
        return f.split("=", 1)[0]

    def _get_allowed_flags(self, spec: Mapping[str, Any]) -> List[str]:
        """Support both 'allowed_flags' (new) and 'flags' (legacy)."""
        return list(spec.get("allowed_flags") or spec.get("flags") or [])

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        """Validate lerna command against policy."""
        name = self._basename_noext(parts[0])
        if name != "lerna":
            return ValidationResult(False, "Not a lerna command")

        global_flags = set(policy.get("flags", []))
        subcommands = policy.get("subcommands", {})
        deny_subcommands = set(policy.get("deny_subcommands", []))

        # Handle global flags only (e.g., lerna --version)
        if len(parts) == 1 or parts[1].startswith("-"):
            used_flags = [p for p in parts[1:] if p.startswith("-")]
            for flag in used_flags:
                base_flag = self._flag_base(flag)
                if base_flag not in global_flags and flag not in global_flags:
                    return ValidationResult(False, f"Global flag not allowed: {flag}")
            # Ensure no non-flag arguments in global flag mode
            non_flags = [p for p in parts[1:] if not p.startswith("-")]
            if non_flags:
                return ValidationResult(False, f"Unexpected arguments: {' '.join(non_flags[:3])}")
            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

        # Handle subcommand mode
        subcommand = parts[1].lower()

        # Check if subcommand is explicitly denied
        if subcommand in deny_subcommands:
            return ValidationResult(False, f"Subcommand not allowed: {subcommand}")

        # Check if subcommand is in allowed list
        if subcommand not in subcommands:
            return ValidationResult(False, f"Subcommand not configured: {subcommand}")

        subcommand_spec = subcommands[subcommand]
        allowed_flags = set(self._get_allowed_flags(subcommand_spec))

        # Combine global flags with subcommand-specific flags
        all_allowed_flags = global_flags.union(allowed_flags)

        # Helper views over tokens
        after = parts[2:]  # everything after the subcommand
        used_flags = [arg for arg in after if arg.startswith("-")]
        positionals = [arg for arg in after if not arg.startswith("-")]

        # Validate flags used with this subcommand
        for flag in used_flags:
            base_flag = self._flag_base(flag)
            if base_flag not in all_allowed_flags and flag not in all_allowed_flags:
                return ValidationResult(False, f"Flag not allowed for {subcommand}: {flag}")

        # Special handling for run subcommand
        if subcommand == "run":
            allowed_scripts = set(subcommand_spec.get("allowed_scripts", []))
            if not positionals:
                return ValidationResult(False, "lerna run requires a script name")
            script = positionals[0]
            if allowed_scripts and script not in allowed_scripts:
                return ValidationResult(False, f"Script not allowed: {script}")

            # Workspace root
            workspace_root = (
                    policy.get("workspace_root")
                    or os.environ.get("WORKSPACE_ROOT")
                    or os.environ.get("CWD")
                    or os.getcwd()
            )

            # tokens after the script name
            try:
                script_pos = after.index(script)
            except ValueError:
                script_pos = 0  # defensive; script should be the first positional
            rest = after[script_pos + 1:]

            # only args meant for the package script (after `--`, if present)
            runner_args = rest[rest.index("--") + 1:] if "--" in rest else rest

            if subcommand_spec.get("deny_args"):
                # disallow anything after the script (and also a bare `--`)
                if runner_args or ("--" in rest):
                    return ValidationResult(False, "Extra args not allowed after script")
            elif subcommand_spec.get("allow_test_paths", False):
                bad = next(
                    (a for a in runner_args
                     if looks_like_path(a)
                     and not is_within_workspace(workspace_root, extract_file_part(a))),
                    None
                )
                if bad:
                    return ValidationResult(False, f"Unsafe path outside workspace in lerna run args: {bad}")

            if subcommand_spec.get("deny_args"):
                # forbid anything beyond the script, including '--' passthrough
                extra = after[after.index(script) + 1:] if script in after else after[1:]
                if extra:
                    return ValidationResult(False, f"Extra args not allowed after script: {' '.join(extra[:3])}")

        # Get timeout from subcommand spec or fall back to default
        timeout = subcommand_spec.get("timeout") or policy.get("default_timeout")

        return ValidationResult(True, "OK", timeout=timeout)

    def adjust_arguments(self, parts: List[str], policy: Mapping[str, Any]) -> List[str]:
        """
        Auto-inject required flags for subcommands if they're missing.
        Called AFTER validate() by the executor.
        """
        if len(parts) < 2:
            return parts

        subcommands = policy.get("subcommands", {})
        subcommand = parts[1].lower()
        subcommand_spec = subcommands.get(subcommand, {})

        required_flags = list(subcommand_spec.get("require_flags", []))
        if not required_flags:
            return parts

        existing_flags = set()
        for p in parts[2:]:
            if p.startswith("-"):
                existing_flags.add(self._flag_base(p))

        # Insert missing required flags right after the subcommand token
        insert_at = 2
        for needed in required_flags:
            base = self._flag_base(needed)
            if base not in existing_flags:
                parts.insert(insert_at, needed)
                insert_at += 1

        return parts

    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        """Configure safe environment for lerna execution."""
        env = dict(base_env)
        
        # Apply environment overrides from policy
        env_overrides = policy.get("env_overrides", {})
        env.update(env_overrides)
        
        # Prepend node_modules/.bin to PATH if workspace root is available
        workspace_root = base_env.get("WORKSPACE_ROOT")
        if workspace_root:
            node_modules_bin = os.path.join(workspace_root, "node_modules", ".bin")
            print(f"DEBUG: Lerna validator - workspace_root: {workspace_root}")
            print(f"DEBUG: Lerna validator - node_modules_bin: {node_modules_bin}")
            print(f"DEBUG: Lerna validator - path exists: {os.path.exists(node_modules_bin)}")
            if os.path.exists(node_modules_bin):
                env["PATH_PREPEND"] = node_modules_bin
                print(f"DEBUG: Lerna validator - Set PATH_PREPEND to: {node_modules_bin}")
            else:
                print(f"DEBUG: Lerna validator - node_modules/.bin does not exist")
        
        return env