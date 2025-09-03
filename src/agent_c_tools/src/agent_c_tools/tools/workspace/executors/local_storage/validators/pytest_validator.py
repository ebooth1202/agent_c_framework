import os
from typing import List, Mapping, Any, Dict
from .base_validator import ValidationResult
from .path_safety import is_within_workspace, looks_like_path, extract_file_part


class PytestCommandValidator:
    SAFE_FLAGS = {
        "-q", "-k", "-x", "-s", "-vv", "-v",
        "--maxfail", "--disable-warnings", "--maxfail=1",
        "--maxfail=2", "--maxfail=3", "--tb=short", "--tb=long",
        "--no-header", "--no-summary", "--tb=no", "--tb=line"
    }

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        # parts[0] is 'pytest'
        if not parts:
            return ValidationResult(False, "empty argv")

        def stem(p: str) -> str:
            return os.path.splitext(os.path.basename(p))[0].lower()

        # Support `pytest …` and `python -m pytest …`
        start = None
        s0 = stem(parts[0])
        if s0 == "pytest":
            start = 1
        elif s0 in ("python", "python3", "py") and len(parts) >= 3 and parts[1] == "-m" and parts[
            2].lower() == "pytest":
            start = 3
        if start is None:
            return ValidationResult(False, "not a pytest invocation")


        used_flags = [p for p in parts[1:] if p.startswith("-")]
        for f in used_flags:
            base = f.split("=", 1)[0]
            if (base not in self.SAFE_FLAGS) and (f not in self.SAFE_FLAGS):
                return ValidationResult(False, f"Flag not allowed: {f}")

        argv = parts[start:]

        # --- Policy knobs & defaults
        allowed_flags = set(policy.get("allowed_flags") or policy.get("flags") or list(self.SAFE_FLAGS))
        # flags that *take* a value (either via "=…" or as the next token)
        value_flags = {"-k", "-m", "--maxfail", "-n", "--max-workers", "--tb", "--durations"}
        workspace_root = policy.get("workspace_root") or os.getcwd()
        max_selectors = int(policy.get("max_selector_args", 50))
        max_argv_len = int(policy.get("max_argv_len", 4096))

        # --- Helpers
        def _flag_base(tok: str) -> str:
            return tok.split("=", 1)[0]

        def _next_is_value(tokens, idx: int) -> bool:
            return idx + 1 < len(tokens) and not tokens[idx + 1].startswith("-")

        def _looks_like_path_or_nodeid(tok: str) -> bool:
            if not tok or tok.startswith("-"):
                return False
            return (
                    tok.endswith(".py")
                    or "::" in tok
                    or "/" in tok
                    or "\\" in tok
                    or (":" in tok)  # file:line or Windows drive; validated by fence below
            )

        # --- Scan argv: validate flags & collect positionals safely
        positionals: List[str] = []
        i = 0
        total_len = sum(len(t) + 1 for t in argv)
        if total_len > max_argv_len:
            return ValidationResult(False, f"argv too long ({total_len} > {max_argv_len})")

        while i < len(argv):
            t = argv[i]
            if t.startswith("-"):
                base = _flag_base(t)
                if base not in allowed_flags:
                    return ValidationResult(False, f"flag not permitted: {t}")
                if base in value_flags and "=" not in t:
                    if not _next_is_value(argv, i):
                        return ValidationResult(False, f"flag expects a value: {base}")
                    # consume value token
                    i += 2
                    continue
                i += 1
                continue

            # Positional token; treat as potential file/nodeid and fence it
            if _looks_like_path_or_nodeid(t):
                file_part = extract_file_part(t)
                if not is_within_workspace(workspace_root, file_part):
                    return ValidationResult(False, f"unsafe path outside workspace: {t}")
                positionals.append(t)
            else:
                # Non-path positional (rare with pytest, but allow)
                positionals.append(t)
            i += 1

        if len(positionals) > max_selectors:
            return ValidationResult(False, f"too many selectors ({len(positionals)} > {max_selectors})")

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