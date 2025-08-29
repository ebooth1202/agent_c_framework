from typing import Dict, Any, List, Mapping, Optional
import os
from .base_validator import ValidationResult, CommandValidator

class NpxCommandValidator(CommandValidator):
    """
    Validator for npx commands with security restrictions.
    
    npx is powerful as it can execute any package from npm registry,
    so we need to be very restrictive about what packages and flags are allowed.
    
    Expected policy shape:
      npx:
        allowed_packages: [...]  # explicit allowlist of packages that can be executed
        flags: [...]             # allowed flags
        default_timeout: 60
        env_overrides: {...}
    """

    def _basename_noext(self, p: str) -> str:
        """Get basename without extension."""
        return os.path.splitext(os.path.basename(p))[0].lower()

    def _flag_base(self, f: str) -> str:
        """Handle flags with values like --package=value."""
        return f.split("=", 1)[0]

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        """Validate npx command against policy."""
        name = self._basename_noext(parts[0])
        if name != "npx":
            return ValidationResult(False, "Not an npx command")

        if len(parts) < 2:
            return ValidationResult(False, "npx requires a package or command")

        allowed_packages = set(policy.get("allowed_packages", []))
        allowed_flags = set(policy.get("flags", []))
        
        # Parse command parts after npx
        args = parts[1:]
        flags = [arg for arg in args if arg.startswith("-")]
        non_flags = [arg for arg in args if not arg.startswith("-")]
        
        # Validate flags
        for flag in flags:
            base_flag = self._flag_base(flag)
            if base_flag not in allowed_flags and flag not in allowed_flags:
                return ValidationResult(False, f"Flag not allowed: {flag}")
        
        # Must have at least one non-flag argument (the package/command to run)
        if not non_flags:
            return ValidationResult(False, "npx requires a package name or command")
        
        # The first non-flag argument should be the package name
        package = non_flags[0]
        
        # Check if package is in allowlist
        if package not in allowed_packages:
            return ValidationResult(False, f"Package not allowed: {package}")
        
        return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        """Configure safe environment for npx execution."""
        env = dict(base_env)
        
        # Apply environment overrides from policy
        env_overrides = policy.get("env_overrides", {})
        env.update(env_overrides)
        
        return env