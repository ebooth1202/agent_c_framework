from typing import Dict, Any, List, Optional, Protocol, Mapping
from dataclasses import dataclass, field

@dataclass
class ValidationResult:
    allowed: bool
    reason: str = "OK"
    # Optional per-command overrides:
    timeout: Optional[int] = None
    env_overrides: Dict[str, str] = field(default_factory=dict)

class CommandValidator(Protocol):
    """
    Interface for per-command validators.
    Implementations must be stateless or side-effect free.
    """
    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult: ...
    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]: ...



class BasicCommandValidator:
    """
    Generic validator for commands without a custom handler.

    Policy examples supported:
    - Simple flags allowlist:
      {
        "flags": ["-l","-a","--help"],
        "default_timeout": 10
      }

    - Subcommand + flags:
      {
        "subcommands": {
           "run": {"flags": ["-q","--dry-run"]},
           "exec": {"flags": ["--safe"]},
        },
        "default_timeout": 10
      }
    """
    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        if not parts:
            return ValidationResult(False, "Empty command")

        # If subcommands policy provided, enforce subcommand presence
        subs = policy.get("subcommands")
        if subs:
            if len(parts) < 2:
                return ValidationResult(False, "Missing subcommand")
            sub = parts[1]
            spec = subs.get(sub)
            if spec is None:
                return ValidationResult(False, f"Subcommand not allowed: {sub}")
            allowed_flags = set(spec.get("flags") or [])
        else:
            allowed_flags = set(policy.get("flags") or [])

        used_flags = [p for p in parts[1:] if p.startswith("-")]
        for f in used_flags:
            base = f.split("=", 1)[0]
            if (base not in allowed_flags) and (f not in allowed_flags):
                return ValidationResult(False, f"Flag not allowed: {f}")

        return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

    def adjust_environment(
            self,
            base_env: Dict[str, str],
            parts: List[str],
            policy: Mapping[str, Any]
    ) -> Dict[str, str]:
        import os

        # Start from caller/env + policy overrides
        env = dict(base_env)
        env.update(policy.get("env_overrides") or {})

        # Platform PATH separator
        sep = ";" if os.name == "nt" else ":"

        # For de-duplication across both PATH and any existing PATH_PREPEND
        existing_path = env.get("PATH", "")
        prior_prepend = env.get("PATH_PREPEND")
        already = set(filter(None, existing_path.split(sep))) | (
            set(filter(None, prior_prepend.split(sep))) if prior_prepend else set()
        )

        candidates: list[str] = []

        # Optional, default-on: project-local node binaries
        # Disable by setting prepend_node_modules_bin: false in policy for a command
        if policy.get("prepend_node_modules_bin", True):
            cwd = env.get("CWD")
            if cwd:
                candidates.append(os.path.join(cwd, "node_modules", ".bin"))
            ws = env.get("WORKSPACE_ROOT")
            if ws and ws != cwd:
                candidates.append(os.path.join(ws, "node_modules", ".bin"))

        # Optional: allow policies to specify additional dirs to prepend
        # Relative paths are resolved against CWD (or WORKSPACE_ROOT if no CWD)
        extra = policy.get("extra_path_prepend") or []
        base_dir = env.get("CWD") or env.get("WORKSPACE_ROOT") or ""
        for p in extra:
            p = str(p)
            if not os.path.isabs(p) and base_dir:
                p = os.path.join(base_dir, p)
            candidates.append(p)

        # Build new PATH_PREPEND in order, skipping non-existent dirs and duplicates
        prepend_parts: list[str] = []
        for p in candidates:
            try:
                if os.path.isdir(p) and p not in already:
                    prepend_parts.append(p)
            except Exception:
                # Be defensive: bad path/permissions shouldn't break env setup
                pass

        if prepend_parts:
            env["PATH_PREPEND"] = sep.join(prepend_parts) + (sep + prior_prepend if prior_prepend else "")

        return env
