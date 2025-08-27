from typing import Dict, Any, List, Mapping
import os
from .base_validator import ValidationResult, CommandValidator

class DotnetCommandValidator:
    """
    Allow read-only dotnet queries; block build/run/test/restore.
    Policy (example):
      dotnet:
        subcommands:
          --info:         { flags: [] }
          --list-sdks:    { flags: [] }
          --list-runtimes:{ flags: [] }
          nuget:          { flags: ["list","--help"] }   # read-only metadata
          new:            { flags: ["--list"] }          # list templates only
        deny_subcommands: ["build","run","test","restore","publish","tool"]
        default_timeout: 20
        env_overrides:
          DOTNET_CLI_TELEMETRY_OPTOUT: "1"
    """
    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        name = os.path.splitext(os.path.basename(parts[0]))[0].lower()
        if name != "dotnet":
            return ValidationResult(False, "Not a dotnet command")

        subs: Mapping[str, Any] = policy.get("subcommands", {})
        deny_subs = set(policy.get("deny_subcommands") or [])

        # dotnet supports "dotnet --info" (flag-like subcommands)
        if len(parts) >= 2 and parts[1].startswith("-"):
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

        # regular subcommand (e.g., dotnet nuget ...)
        if len(parts) < 2:
            return ValidationResult(False, "Missing dotnet subcommand")

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