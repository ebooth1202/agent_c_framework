from typing import Dict, Any, List, Mapping, Optional
import os
from .base_validator import ValidationResult, CommandValidator

class LernaCommandValidator(CommandValidator):
    """
    Validator for Lerna monorepo management commands.
    
    Lerna can be powerful and potentially dangerous with commands like 
    'exec' that can run arbitrary scripts. We restrict to safe informational
    and build-related commands.
    
    Expected policy shape:
      lerna:
        subcommands:
          list: { flags: [...] }
          info: { flags: [...] }
          bootstrap: { flags: [...] }
          clean: { flags: [...] }
          # ... other safe subcommands
        deny_subcommands: [...]  # explicitly blocked subcommands
        flags: [...]             # global flags allowed for all subcommands
        default_timeout: 120
        env_overrides: {...}
    """

    def _basename_noext(self, p: str) -> str:
        """Get basename without extension."""
        return os.path.splitext(os.path.basename(p))[0].lower()

    def _flag_base(self, f: str) -> str:
        """Handle flags with values like --scope=value."""
        return f.split("=", 1)[0]

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
        allowed_flags = set(subcommand_spec.get("flags", []))
        
        # Combine global flags with subcommand-specific flags
        all_allowed_flags = global_flags.union(allowed_flags)
        
        # Validate flags used with this subcommand
        args = parts[2:]  # everything after the subcommand
        used_flags = [arg for arg in args if arg.startswith("-")]
        
        for flag in used_flags:
            base_flag = self._flag_base(flag)
            if base_flag not in all_allowed_flags and flag not in all_allowed_flags:
                return ValidationResult(False, f"Flag not allowed for {subcommand}: {flag}")
        
        # Get timeout from subcommand spec or fall back to default
        timeout = subcommand_spec.get("timeout") or policy.get("default_timeout")
        
        return ValidationResult(True, "OK", timeout=timeout)

    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        """Configure safe environment for lerna execution."""
        env = dict(base_env)
        
        # Apply environment overrides from policy
        env_overrides = policy.get("env_overrides", {})
        env.update(env_overrides)
        
        return env