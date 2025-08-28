from typing import Dict, Any, List, Mapping
import os
from .base_validator import ValidationResult, CommandValidator  # adjust import to your layout

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
        name = os.path.splitext(os.path.basename(parts[0]))[0].lower()
        if name not in ("node", "nodejs"):
            return ValidationResult(False, "Not a node command")

        allowed_flags = set(policy.get("flags") or [])
        deny_global = set(policy.get("deny_global_flags") or [])

        used_flags = [p for p in parts[1:] if p.startswith("-")]
        for f in used_flags:
            base = f.split("=", 1)[0]
            if base in deny_global or f in deny_global:
                return ValidationResult(False, f"Global flag not allowed: {f}")
            if (base not in allowed_flags) and (f not in allowed_flags):
                return ValidationResult(False, f"Flag not allowed: {f}")

        # Disallow running scripts: if non-flag arg appears, block
        non_flags = [p for p in parts[1:] if not p.startswith("-")]
        if non_flags:
            return ValidationResult(False, f"Arguments not allowed for node: {' '.join(non_flags[:3])}")

        return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        env = dict(base_env)
        env.update(policy.get("env_overrides") or {})
        return env

