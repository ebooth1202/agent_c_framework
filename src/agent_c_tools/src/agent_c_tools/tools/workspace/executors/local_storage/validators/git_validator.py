import platform
from typing import Dict, Any, List, Mapping

from .base_validator import ValidationResult

# -------------------------------
# Git-specific validator
# -------------------------------

class GitCommandValidator:
    """
    Safe validator for `git` enforcing:
      - explicit subcommand allowlist
      - per-subcommand flag allowlist
      - deny select global flags (`-c`, `--exec-path`, etc.)
      - no reliance on shell chaining (we use shell=False)

    Expected policy shape (example):
    {
      "subcommands": {
        "status":  {"flags": ["--porcelain", "-s", "-b"], "timeout": 20},
        "log":     {"flags": ["--oneline","--graph","--decorate","-n","-p"]},
        "commit":  {"flags": ["-m","--amend","--no-verify"]},
        ...
      },
      "deny_global_flags": ["-c","--exec-path","--help","-P"],
      "safe_env": {
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",  # (Windows handled below)
        "GIT_ALLOW_PROTOCOL": "https,file"
      },
      "default_timeout": 30
    }
    """

    @staticmethod
    def validate(parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        if not parts or parts[0] != "git":
            return ValidationResult(False, "Not a git command")

        if len(parts) < 2:
            return ValidationResult(False, "Missing git subcommand")

        sub = parts[1]
        subs: Mapping[str, Any] = policy.get("subcommands", {})
        if sub not in subs:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        spec = subs[sub] or {}
        allowed_flags = {f for f in (spec.get("flags") or [])}

        # global denylists (apply to all subcommands)
        deny_global = set(policy.get("deny_global_flags") or [])
        # Collect flags (tokens that *start* with -)
        used_flags = [p for p in parts[2:] if p.startswith("-")]

        # 1) deny any global disallowed flags
        for f in used_flags:
            if f in deny_global:
                return ValidationResult(False, f"Global flag not allowed: {f}")

        # 2) ensure every used flag is allowed for the subcommand
        for f in used_flags:
            # allow "-m" and "-m <msg>" patterns, allow "--long=value" if "--long" is allowed
            base = f.split("=", 1)[0]
            if (base not in allowed_flags) and (f not in allowed_flags):
                return ValidationResult(False, f"Flag not allowed for {sub}: {f}")

        return ValidationResult(
            True,
            "OK",
            timeout=spec.get("timeout") or policy.get("default_timeout")
        )

    @staticmethod
    def adjust_environment(base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        """
        Build the execution environment for `git` with minimal, safe overrides.
        For read-only subcommands (status/diff/log/show/rev-parse/ls-files/branch),
        DO NOT override global/system git config so results match a normal CLI.
        """
        env = dict(base_env)
        safe_env = dict(policy.get("safe_env") or {})

        # Determine subcommand ('' if missing)
        subcmd = parts[1] if len(parts) > 1 else ""
        read_only_subs = {"status", "diff", "log", "show", "rev-parse", "ls-files", "branch"}
        is_read_only = subcmd in read_only_subs

        # For read-only ops, don't hide system/global config
        if is_read_only:
            safe_env.pop("GIT_CONFIG_NOSYSTEM", None)
            safe_env.pop("GIT_CONFIG_GLOBAL", None)

        # Platform tweaks
        import platform
        if platform.system().lower().startswith("win"):
            # Normalize /dev/null → NUL if still present
            if safe_env.get("GIT_CONFIG_GLOBAL") == "/dev/null":
                safe_env["GIT_CONFIG_GLOBAL"] = "NUL"
            # Non-interactive SSH by default (safe)
            safe_env.setdefault("GIT_SSH_COMMAND", "ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new")

        # Apply safe env
        env.update(safe_env)

        # Optional per-policy overrides (kept after safe_env so they win)
        overrides = policy.get("env_overrides") or {}
        env.update(overrides)

        return env