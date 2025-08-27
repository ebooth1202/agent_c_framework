import os
from typing import List, Mapping, Any, Dict
from .base_validator import ValidationResult


class PytestCommandValidator:
    SAFE_FLAGS = {
        "-q", "-k", "-x", "-s", "-vv", "-v",
        "--maxfail", "--disable-warnings", "--maxfail=1",
        "--maxfail=2", "--maxfail=3", "--tb=short", "--tb=long",
    }

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        # parts[0] is 'pytest'
        if len(parts) == 0 or not parts[0].endswith("pytest"):
            from ..validators.base_validator import ValidationResult
            return ValidationResult(False, "Not a pytest command")

        from ..validators.base_validator import ValidationResult
        used_flags = [p for p in parts[1:] if p.startswith("-")]
        for f in used_flags:
            base = f.split("=", 1)[0]
            if (base not in self.SAFE_FLAGS) and (f not in self.SAFE_FLAGS):
                return ValidationResult(False, f"Flag not allowed: {f}")

        # crude non-flag arg sanity (prevent absolute paths or '..')
        for p in parts[1:]:
            if p.startswith("-"):
                continue
            if os.path.isabs(p) or ".." in p.split(os.sep):
                return ValidationResult(False, f"Unsafe path: {p}")

        timeout = policy.get("default_timeout")
        return ValidationResult(True, "OK", timeout=timeout)

    @staticmethod
    def adjust_environment(base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        env = dict(base_env)
        # Disable plugin autoload for safety unless explicitly overridden
        env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
        overrides = policy.get("env_overrides") or {}
        env.update(overrides)
        return env