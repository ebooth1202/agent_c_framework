from typing import Dict, Any, List, Mapping, Optional
import os
from .base_validator import ValidationResult, CommandValidator
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

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

        # NEW: Support both old and new policy formats
        packages_config = policy.get("packages", {})
        allowed_packages = set(policy.get("allowed_packages", []))

        # If using new format, extract allowed packages from config
        if packages_config:
            allowed_packages.update(packages_config.keys())

        allowed_flags = set(policy.get("flags", []))
        cmd_aliases = policy.get("command_aliases") or {}

        workspace_root = (
                policy.get("workspace_root")
                or os.environ.get("WORKSPACE_ROOT")
                or os.getcwd()
        )

        args = parts[1:]
        i = 0
        after_dashdash = False
        preinstall_pkgs: List[str] = []

        def allow_flag(flag: str) -> bool:
            base = self._flag_base(flag)
            return (flag in allowed_flags) or (base in allowed_flags)

        # UNCHANGED: Flag parsing logic
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
                i += 1
                continue
            break

        # UNCHANGED: Extract invoked command
        if i >= len(args):
            return ValidationResult(False, "npx requires a package or command to run")

        invoked = args[i]
        invoked_name = self._split_pkg_name(invoked)
        package_args = args[i + 1:]

        # UNCHANGED: Permission checking
        allowed = False
        resolved_package = None  # NEW: Track which package we resolved to

        if invoked_name in allowed_packages:
            allowed = True
            resolved_package = invoked_name
        else:
            for pkg, aliases in cmd_aliases.items():
                if pkg in allowed_packages or pkg in preinstall_pkgs:
                    if invoked in aliases or invoked_name in aliases:
                        allowed = True
                        resolved_package = pkg
                        break

        if not allowed:
            return ValidationResult(False, f"Command not allowed: {invoked}")

        # UNCHANGED: Path fencing
        bad = next(
            (a for a in package_args
             if looks_like_path(a) and not is_within_workspace(workspace_root, extract_file_part(a))),
            None
        )
        if bad:
            return ValidationResult(False, f"Unsafe path outside workspace in npx package args: {bad}")

        # NEW: Get package-specific configuration for policy_spec
        package_spec = {}
        if packages_config and resolved_package:
            package_spec = packages_config.get(resolved_package, {})

        # CHANGED: Pass package_spec instead of no policy_spec
        return ValidationResult(True, "OK",
                                timeout=policy.get("default_timeout"),
                                policy_spec=package_spec)

    def adjust_environment(self, base_env, parts, policy):
        env = super().adjust_environment(base_env, parts, policy)
        return env