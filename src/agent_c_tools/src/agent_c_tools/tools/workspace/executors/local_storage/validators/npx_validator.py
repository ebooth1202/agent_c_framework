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

    def _split_pkg_name(self, token: str) -> str:
        """Return package name without version suffix, preserving scoped names."""
        # Examples:
        #  'eslint@9' -> 'eslint'
        #  '@scope/cli@latest' -> '@scope/cli'
        #  '@scope/cli' -> '@scope/cli'
        if token.startswith("@"):
            # Scoped: split on the last '@'
            if "@" in token[1:]:
                return token.rsplit("@", 1)[0]
            return token
        # Unscoped: split on the first '@'
        return token.split("@", 1)[0]

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        name = self._basename_noext(parts[0])
        if name != "npx":
            return ValidationResult(False, "Not an npx command")

        if len(parts) < 2:
            return ValidationResult(False, "npx requires a package or command")

        allowed_packages = set(policy.get("allowed_packages", []))
        allowed_flags = set(policy.get("flags", []))
        # Optional: map package -> list of allowed command aliases (e.g., typescript -> ["tsc"])
        cmd_aliases = policy.get("command_aliases") or {}

        args = parts[1:]
        i = 0
        after_dashdash = False
        preinstall_pkgs: List[str] = []

        def allow_flag(flag: str) -> bool:
            base = self._flag_base(flag)
            return (flag in allowed_flags) or (base in allowed_flags)

        # 1) Scan flags (and consume values for -p/--package)
        while i < len(args):
            a = args[i]
            if a == "--":
                after_dashdash = True
                i += 1
                break
            if a.startswith("-") and not after_dashdash:
                if not allow_flag(a):
                    return ValidationResult(False, f"Flag not allowed: {a}")
                base = self._flag_base(a)
                if base in ("-p", "--package"):
                    i += 1
                    if i >= len(args):
                        return ValidationResult(False, f"{a} requires a package name")
                    pkg_token = args[i]
                    if pkg_token.startswith("-"):
                        return ValidationResult(False, f"{a} requires a package name")
                    pkg_name = self._split_pkg_name(pkg_token)
                    if pkg_name not in allowed_packages:
                        return ValidationResult(False, f"Package not allowed: {pkg_token}")
                    preinstall_pkgs.append(pkg_name)
                    i += 1
                    continue
                # other flags (possibly --flag=value) — already vetted
                i += 1
                continue
            break  # first non-flag reached

        # 2) Determine the invoked command/package (first token after flags/-p pairs/--).
        if i >= len(args):
            return ValidationResult(False, "npx requires a package or command to run")

        invoked = args[i]
        invoked_name = self._split_pkg_name(invoked)

        # Accept if the invoked token itself is an allowed package
        if invoked_name in allowed_packages:
            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

        # Or accept if it’s an alias of any allowed (or preinstalled) package
        # e.g., 'tsc' allowed because 'typescript' is allowed/preinstalled
        for pkg, aliases in cmd_aliases.items():
            if pkg in allowed_packages or pkg in preinstall_pkgs:
                if invoked in aliases or invoked_name in aliases:
                    return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

        return ValidationResult(False, f"Command not allowed: {invoked}")

    def adjust_environment(self, base_env, parts, policy):
        env = super().adjust_environment(base_env, parts, policy)
        return env