from typing import Dict, Any, List, Mapping, Optional
import os
from .base_validator import ValidationResult, CommandValidator
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

class DotnetCommandValidator:
    """
    Allow read-only dotnet queries; block build/run/test/restore.
    Policy (example):
      dotnet:
        subcommands:
          --info:         { flags: [] }
          --list-sdks:    { flags: [] }
          --list-runtimes:{ flags: [] }
          test:           { flags: ["--filter", "--no-build"], allow_test_paths: true }
          nuget:          { flags: ["list","--help"] }   # read-only metadata
          new:            { flags: ["--list"] }          # list templates only
        deny_subcommands: ["build","run","restore","publish","tool"]
        default_timeout: 20
        env_overrides:
          DOTNET_CLI_TELEMETRY_OPTOUT: "1"
    """

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        import os
        from .path_safety import is_within_workspace, looks_like_path, extract_file_part

        name = os.path.splitext(os.path.basename(parts[0]))[0].lower()
        if name != "dotnet":
            return ValidationResult(False, "Not a dotnet command")

        subs: Mapping[str, Any] = policy.get("subcommands", {})
        deny_subs = set(policy.get("deny_subcommands") or [])

        if len(parts) < 2:
            return ValidationResult(False, "Missing dotnet subcommand")

        sub = parts[1]

        # flag-like subcommands (e.g., --info)
        if sub.startswith("-"):
            if sub in deny_subs:
                return ValidationResult(False, f"Subcommand not allowed: {sub}")
            spec = subs.get(sub)
            if spec is None:
                return ValidationResult(False, f"Subcommand not allowed: {sub}")
            allowed_flags = _collect_allowed_flags(spec)
            used_flags = _collect_used_flags(parts[2:])
            for raw in used_flags:
                if not _is_flag_allowed(raw, allowed_flags):
                    return ValidationResult(False, f"Flag not allowed for {sub}: {raw}")
            return ValidationResult(True, "OK", timeout=spec.get("timeout") or policy.get("default_timeout"))

        # regular subcommands
        if sub in deny_subs:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        spec = subs.get(sub)
        if spec is None:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        allowed_flags = _collect_allowed_flags(spec)
        argv = parts[2:]
        used_flags = _collect_used_flags(argv)
        for raw in used_flags:
            if not _is_flag_allowed(raw, allowed_flags):
                return ValidationResult(False, f"Flag not allowed for {sub}: {raw}")

        # --- path-safety integration for `dotnet test`
        if sub == "test":
            workspace_root = (
                    policy.get("workspace_root")
                    or os.environ.get("WORKSPACE_ROOT")
                    or os.environ.get("CWD")
                    or os.getcwd()
            )

            # Split argv around `--` (adapter receives everything after)
            if "--" in argv:
                ddx = argv.index("--")
                before_dd = argv[:ddx]
                after_dd = argv[ddx + 1:]
            else:
                before_dd = argv
                after_dd = []

            # Positionals BEFORE `--` (project/solution/dir paths)
            positionals = [t for t in before_dd if not t.startswith("-")]

            allow_test_paths = bool(spec.get("allow_test_paths", False))
            # Optional: allow typical project/solution path even when test paths disabled
            allow_proj_paths = bool(spec.get("allow_project_paths", True))

            def is_proj_or_sln(tok: str) -> bool:
                tl = tok.lower()
                return tl.endswith(".sln") or tl.endswith(".csproj")

            # If test paths are not allowed, block path-like positionals except csproj/sln (if allowed)
            if not allow_test_paths:
                bad = next(
                    (p for p in positionals
                     if looks_like_path(p)
                     and not (allow_proj_paths and is_proj_or_sln(p))),
                    None
                )
                if bad:
                    return ValidationResult(False, "Test paths not permitted; use --filter")

            # If allowed, fence all path-like positionals to workspace
            else:
                bad = next(
                    (p for p in positionals
                     if looks_like_path(p)
                     and not is_within_workspace(workspace_root, extract_file_part(p))),
                    None
                )
                if bad:
                    return ValidationResult(False, f"Unsafe path outside workspace in dotnet test args: {bad}")

            # Also fence adapter args after `--` (e.g., framework-specific selectors)
            if after_dd:
                bad = next(
                    (p for p in after_dd
                     if looks_like_path(p)
                     and not is_within_workspace(workspace_root, extract_file_part(p))),
                    None
                )
                if bad:
                    return ValidationResult(False, f"Unsafe path outside workspace after --: {bad}")

            # (Optional) fence values of known path flags (inline or next token)
            path_flags = {"--settings", "--results-directory", "--test-adapter-path", "--artifacts", "--output",
                          "--diag"}
            i = 0
            while i < len(before_dd):
                t = before_dd[i]
                if t.startswith("-"):
                    base = t.split("=", 1)[0]
                    val = None
                    if "=" in t:
                        val = t.split("=", 1)[1]
                    elif base in path_flags and (i + 1) < len(before_dd) and not before_dd[i + 1].startswith("-"):
                        val = before_dd[i + 1]
                        i += 1
                    if base in path_flags and val:
                        if looks_like_path(val) and not is_within_workspace(workspace_root, extract_file_part(val)):
                            return ValidationResult(False, f"Unsafe path for {base}: {val}")
                i += 1

        return ValidationResult(True, "OK", timeout=spec.get("timeout") or policy.get("default_timeout"))

    @staticmethod
    def adjust_environment(base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[
        str, str]:
        env = dict(base_env)
        env.update(policy.get("env_overrides") or {})
        return env

    @staticmethod
    def adjust_arguments(parts: List[str], policy: Mapping[str, Any]) -> List[str]:
        """
        Override-or-append required flags as per `require_flags`, and normalize verbosity flags.
        - Canonicalizes -v / --verbosity forms to `--verbosity <value>`.
        - For require_flags:
            * true          → ensure flag present (no value)
            * "string"      → ensure flag == that value
            * ["a","b",..]  → ensure flag value ∈ list; default to first when missing/invalid
        If both -v and --verbosity are present, the validator collapses them to one canonical --verbosity <value> and enforces your required value set.
        If a required flag isn’t present, it’s appended; if present with the wrong value, it’s overridden.
        """
        if len(parts) < 2:
            return parts

        subs: Mapping[str, Any] = policy.get("subcommands", {}) or {}
        sub = parts[1]
        # If sub is not in policy or is a flag-like sub with no spec, nothing to do
        spec = subs.get(sub)
        if spec is None:
            return parts

        require: Mapping[str, Any] = spec.get("require_flags") or {}
        if not require:
            # Still normalize -v/--verbosity if present for consistency
            return _normalize_verbosity_only(parts, sub)

        # Parse the tail (after program+sub) into flags/values & positional args
        arg_start = 2
        normalized = _parse_and_normalize(parts[arg_start:])

        # Apply requirement rules
        # --nologo (boolean)
        if _requires_true(require, "--nologo") and not normalized.has_flag("--nologo"):
            normalized.add_flag("--nologo")

        # --verbosity (enum list or exact string)
        if "--verbosity" in require:
            want = require["--verbosity"]
            if isinstance(want, list) and want:
                # Accept any of the allowed values; default to the first
                target = _coerce_verbosity(normalized.get_value("--verbosity"), allowed=want, default=want[0])
                normalized.set_flag("--verbosity", target)
            elif isinstance(want, str):
                normalized.set_flag("--verbosity", _expand_verbosity_alias(want))
            elif want is True:
                # Require presence but keep existing or default to 'quiet'
                val = normalized.get_value("--verbosity") or "quiet"
                normalized.set_flag("--verbosity", _expand_verbosity_alias(val))

        # --logger (exact string)
        if "--logger" in require:
            want = require["--logger"]
            if isinstance(want, str):
                normalized.set_flag("--logger", want)

        # --no-build (boolean)
        if _requires_true(require, "--no-build") and not normalized.has_flag("--no-build"):
            normalized.add_flag("--no-build")

        # --locked-mode (boolean)
        if _requires_true(require, "--locked-mode") and not normalized.has_flag("--locked-mode"):
            normalized.add_flag("--locked-mode")

        # Rebuild argv: program, sub, normalized flags/values (canonical), then positional args
        rebuilt = [parts[0], sub] + normalized.to_argv()
        return rebuilt


# ---------- Helpers ----------

def _collect_allowed_flags(spec: Mapping[str, Any]) -> set:
    # Support either `flags` (current) or `allowed_flags` (alt spelling)
    allowed = set(spec.get("flags") or spec.get("allowed_flags") or [])
    # Accept both long and short verbosity names if either is present
    if "--verbosity" in allowed:
        allowed.add("-v")
    if "-v" in allowed:
        allowed.add("--verbosity")
    return allowed


def _is_flag_allowed(raw_flag: str, allowed: set) -> bool:
    """
    raw_flag: the flag token stem (before = or :) such as "--verbosity", "-v", "--nologo"
    Allowed if either the raw stem is in allowlist OR its canonical name is (for -v).
    """
    stem = _flag_stem(raw_flag)
    if stem in allowed:
        return True
    if stem == "-v" and "--verbosity" in allowed:
        return True
    if stem == "--verbosity" and "-v" in allowed:
        return True
    return False


def _collect_used_flags(tokens: List[str]) -> List[str]:
    """
    Collect stems of all flag tokens from argv tail (before = or :)
    e.g., ["--verbosity=quiet","-v:q","--nologo"] → ["--verbosity","-v","--nologo"]
    """
    used = []
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]
        if t.startswith("-"):
            used.append(_flag_stem(t))
            # If this is a two-token form for verbosity (-v quiet / --verbosity quiet), skip the value token
            if _is_verbosity_flag(t) and _next_is_value(tokens, i):
                i += 1
        i += 1
    return used


def _flag_stem(token: str) -> str:
    # Return the flag part before '=' or ':' (e.g., "--verbosity=quiet" -> "--verbosity")
    for sep in ("=", ":"):
        if sep in token:
            return token.split(sep, 1)[0]
    return token


def _is_verbosity_flag(token: str) -> bool:
    stem = _flag_stem(token)
    return stem in ("--verbosity", "-v")


def _next_is_value(tokens: List[str], i: int) -> bool:
    return (i + 1) < len(tokens) and not tokens[i + 1].startswith("-")


def _requires_true(require: Mapping[str, Any], key: str) -> bool:
    v = require.get(key)
    return v is True


def _expand_verbosity_alias(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    v = v.strip().lower()
    alias = {"q": "quiet", "m": "minimal", "n": "normal", "d": "detailed", "diag": "diagnostic"}
    return alias.get(v, v)


def _coerce_verbosity(current: Optional[str], allowed: List[str], default: str) -> str:
    if current:
        cur = _expand_verbosity_alias(current)
        if cur in [a.lower() for a in allowed]:
            return cur
    return _expand_verbosity_alias(default) or default


def _normalize_verbosity_only(parts: List[str], sub: str) -> List[str]:
    """If -v/--verbosity present, rewrite it to canonical '--verbosity <value>'."""
    arg_start = 2
    tail = parts[arg_start:]
    norm = _parse_and_normalize(tail)
    if norm.has_flag("--verbosity"):
        rebuilt = [parts[0], sub] + norm.to_argv()
        return rebuilt
    return parts


# ---------- Parsed argv model ----------

class _ArgState:
    """
    Minimal normalized view over dotnet argv tail:
      - flags: dict of flag -> Optional[value] (canonical long names where we care: --verbosity)
      - order is preserved for non-overridden flags; overridden/required flags are appended at the end.
    """

    def __init__(self) -> None:
        self._pairs: Dict[str, Optional[str]] = {}
        self._kept_tokens: List[str] = []  # untouched flags/values or positional args (in order)
        self._positional: List[str] = []  # non-flag tokens not consumed as flag values

    def has_flag(self, name: str) -> bool:
        return name in self._pairs

    def get_value(self, name: str) -> Optional[str]:
        return self._pairs.get(name)

    def add_flag(self, name: str, value: Optional[str] = None) -> None:
        # Required flags appended at the end; use canonical spacing form
        self._pairs[name] = value

    def set_flag(self, name: str, value: Optional[str]) -> None:
        self._pairs[name] = value

    def keep_token(self, token: str) -> None:
        self._kept_tokens.append(token)

    def add_positional(self, token: str) -> None:
        self._positional.append(token)

    def to_argv(self) -> List[str]:
        argv: List[str] = []
        # First, emit kept tokens (original order)
        argv.extend(self._kept_tokens)
        # Then, emit normalized/required flags (canonical long form, if any)
        for k, v in self._pairs.items():
            if v is None:
                argv.append(k)
            else:
                argv.extend([k, v])
        # Finally, positional args
        argv.extend(self._positional)
        return argv


def _parse_and_normalize(tokens: List[str]) -> _ArgState:
    """
    Parse argv tail into:
      - kept tokens (all flags except verbosity/logger that we override; plus their values, conservatively),
      - normalized flag pairs for the ones we manipulate (--verbosity, --logger, --nologo, --no-build, --locked-mode).
    Rewrites any -v/--verbosity variants into canonical `--verbosity <value>` and consumes the value.
    """
    st = _ArgState()
    i = 0
    n = len(tokens)
    while i < n:
        t = tokens[i]

        if not t.startswith("-"):
            st.add_positional(t)
            i += 1
            continue

        stem = _flag_stem(t)

        # ---- Verbosity handling (normalize all forms) ----
        if stem in ("--verbosity", "-v"):
            # Extract value from same token (--verbosity=quiet / -v:q) or next token
            val: Optional[str] = None
            if "=" in t:
                val = t.split("=", 1)[1]
            elif ":" in t:
                val = t.split(":", 1)[1]
            elif _next_is_value(tokens, i):
                val = tokens[i + 1]
                i += 1  # consume the value token
            st.set_flag("--verbosity", _expand_verbosity_alias(val) or "quiet")
            i += 1
            continue

        # ---- Logger handling (we may need to override it) ----
        if stem == "--logger":
            val: Optional[str] = None
            if "=" in t:
                val = t.split("=", 1)[1]
            elif ":" in t:
                val = t.split(":", 1)[1]
            elif _next_is_value(tokens, i):
                val = tokens[i + 1]
                i += 1
            st.set_flag("--logger", val or "")
            i += 1
            continue

        # ---- Flags we may need to ensure presence (booleans) ----
        if stem in ("--nologo", "--no-build", "--locked-mode"):
            st.set_flag(stem, None)
            i += 1
            continue

        # ---- Other flags: keep as-is (and conservatively keep a following value token if present) ----
        st.keep_token(t)
        if _next_is_value(tokens, i):
            st.keep_token(tokens[i + 1])
            i += 1
        i += 1

    return st