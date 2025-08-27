from typing import Dict, Any, List, Mapping
import os
from .base_validator import ValidationResult, CommandValidator

class NpmCommandValidator:
    """
    Allow safe npm subcommands only (e.g., -v, view, list). Block install/run/exec/publish.
    Policy (example):
      npm:
        root_flags: ["-v","--version","--help"]
        subcommands:
          view:  { flags: ["--json"] }
          list:  { flags: ["--depth","--json"] }
          ping:  { flags: [] }
          config:{ flags: ["get"] }
        deny_subcommands: ["exec","run","install","i","publish","update","audit","ci"]
        default_timeout: 20
        env_overrides:
          NPM_CONFIG_FUND: "false"
          NPM_CONFIG_AUDIT: "false"
          NPM_CONFIG_UPDATE_NOTIFIER: "false"
    """
    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        name = os.path.splitext(os.path.basename(parts[0]).lower())[0]
        if name != "npm":
            return ValidationResult(False, "Not an npm command")

        root_flags = set(policy.get("root_flags") or [])
        subs: Mapping[str, Any] = policy.get("subcommands", {})
        deny_subs = set(policy.get("deny_subcommands") or [])

        # Case A: flags-only usage (e.g., npm -v)
        if len(parts) == 1 or parts[1].startswith("-"):
            used_flags = [p for p in parts[1:] if p.startswith("-")]
            for f in used_flags:
                base = f.split("=", 1)[0]
                if (base not in root_flags) and (f not in root_flags):
                    return ValidationResult(False, f"Root flag not allowed: {f}")
            # disallow trailing non-flags in flags-only mode
            non_flags = [p for p in parts[1:] if not p.startswith("-")]
            if non_flags:
                return ValidationResult(False, f"Unexpected args: {' '.join(non_flags[:3])}")
            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

        # Case B: subcommand mode (npm <sub> ...)
        sub = parts[1]
        if sub in deny_subs:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")
        spec = subs.get(sub)
        if spec is None:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        allowed_flags = set(spec.get("flags") or [])
        used_flags = [p for p in parts[2:] if p.startswith("-")]
        for f in used_flags:
            base = f.split("=", 1)[0]
            if (base not in allowed_flags) and (f not in allowed_flags):
                return ValidationResult(False, f"Flag not allowed for {sub}: {f}")

        return ValidationResult(True, "OK", timeout=spec.get("timeout") or policy.get("default_timeout"))

    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        env = dict(base_env)
        env.update(policy.get("env_overrides") or {})
        return env