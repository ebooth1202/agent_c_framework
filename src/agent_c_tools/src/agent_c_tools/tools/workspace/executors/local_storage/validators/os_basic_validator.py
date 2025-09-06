# os_validator.py
from typing import Dict, Any, List, Mapping
import os
from .base_validator import ValidationResult, CommandValidator  # adjust import to your layout

class OSBasicValidator:
    """
    Single validator reused by multiple simple OS commands:
      - which / where
      - whoami
      - echo
      - find (very restricted; no -exec/-delete/-ok etc.)

    Policy shape per *command entry* (not shared):
      which:
        validator: os_basic
        flags: ["-a", "--version"]      # allowed flags for *this* base command
        default_timeout: 5
        deny_tokens: []                 # optional hard denylists, exact match

      find:
        validator: os_basic
        flags: ["-name","-maxdepth","-type","-mtime","-not","-path"]
        default_timeout: 10
        deny_tokens: ["-exec","-ok","-delete","-fdelete","-execdir","-prune"]
    """

    # --- CommandValidator protocol ---
    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        if not parts:
            return ValidationResult(False, "Empty command")

        base = os.path.basename(parts[0]).lower()
        allowed_flags = set(policy.get("flags") or [])
        deny_tokens = set(policy.get("deny_tokens") or [])

        # Collect tokens that look like flags (start with - or / on Windows)
        used_flags = [p for p in parts[1:] if p.startswith("-") or p.startswith("/")]

        # 1) hard-token deny (covers dangerous find actions like -exec/-delete)
        for tok in parts[1:]:
            # normalize "--long=value" to "--long" for deny checks
            tok_base = tok.split("=", 1)[0]
            if tok_base in deny_tokens:
                return ValidationResult(False, f"Token not allowed: {tok_base}")

        # 2) flags allowlist
        for f in used_flags:
            basef = f.split("=", 1)[0]
            if (basef not in allowed_flags) and (f not in allowed_flags):
                return ValidationResult(False, f"Flag not allowed: {f}")

        return ValidationResult(True, "OK", timeout=policy.get("default_timeout"), policy_spec=policy)

    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        # Allow per-command env tweaks via policy.env_overrides
        env = dict(base_env)
        env.update(policy.get("env_overrides") or {})
        return env
