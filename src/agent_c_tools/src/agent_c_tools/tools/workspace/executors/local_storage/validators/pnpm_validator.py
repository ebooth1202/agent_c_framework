from typing import Dict, Any, List, Mapping
import os
from .base_validator import ValidationResult, CommandValidator
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

class PnpmCommandValidator(CommandValidator):
    """
    Hardened pnpm validator with support for:
      - root flags only (e.g., -v, --version)
      - per-subcommand allowed flags (allowed_flags or flags)
      - pnpm run: allowed_scripts + deny_args
      - pnpm install: enabled, require_no_packages, require_flags_all (auto-injected), allowed_flags
      - pnpm config: get_only (blocks set/delete)

    Expected policy shape:
      pnpm:
        root_flags: [...]
        subcommands:
          view:   { allowed_flags: [...] }
          list:   { allowed_flags: [...] }
          ping:   { allowed_flags: [] }
          config: { get_only: true }
          run:
            allowed_scripts: [...]
            deny_args: true
          install:
            enabled: true
            require_no_packages: true
            require_flags: ["--ignore-scripts"]
            allowed_flags: [...]
        deny_subcommands: [ ... ]
        default_timeout: 120
        env_overrides: { ... }
    """

    def _basename_noext(self, p: str) -> str:
        return os.path.splitext(os.path.basename(p))[0].lower()

    def _get_allowed_flags(self, spec: Mapping[str, Any]) -> List[str]:
        # support both "allowed_flags" (new) and "flags" (legacy)
        return list(spec.get("allowed_flags") or spec.get("flags") or [])

    def _flag_base(self, f: str) -> str:
        # treat "--depth=0" as "--depth" when comparing
        return f.split("=", 1)[0]

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        name = self._basename_noext(parts[0])
        if name != "pnpm":
            return ValidationResult(False, "Not a pnpm command")

        root_flags = set(policy.get("root_flags") or [])
        subs: Mapping[str, Any] = policy.get("subcommands", {}) or {}
        deny_subs = set((policy.get("deny_subcommands") or []))

        # Case A: root-flags-only usage (e.g., pnpm -v)
        if len(parts) == 1 or parts[1].startswith("-"):
            used_flags = [p for p in parts[1:] if p.startswith("-")]
            for f in used_flags:
                base = self._flag_base(f)
                if base not in root_flags and f not in root_flags:
                    return ValidationResult(False, f"Root flag not allowed: {f}")
            non_flags = [p for p in parts[1:] if not p.startswith("-")]
            if non_flags:
                return ValidationResult(False, f"Unexpected args: {' '.join(non_flags[:3])}")
            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))

        # Case B: subcommand mode
        raw_sub = parts[1].lower()
        alias_map = {"i": "install", "add": "install"}  # pnpm i/add -> install
        sub = alias_map.get(raw_sub, raw_sub)

        if sub in deny_subs:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        spec = subs.get(sub)
        if spec is None:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        after = parts[2:]
        used_flags = [p for p in after if p.startswith("-")]
        positionals = [p for p in after if not p.startswith("-")]

        allowed_flags = set(self._get_allowed_flags(spec))
        if allowed_flags:
            for f in used_flags:
                base = self._flag_base(f)
                if base not in allowed_flags and f not in allowed_flags:
                    return ValidationResult(False, f"Flag not allowed for {sub}: {f}")

        # NEW: workspace root for path fencing
        workspace_root = (
                policy.get("workspace_root")
                or os.environ.get("WORKSPACE_ROOT")
                or os.getcwd()
        )

        if sub == "run":
            allowed_scripts = set(spec.get("allowed_scripts") or [])
            if not positionals:
                return ValidationResult(False, "pnpm run requires a script name")
            script = positionals[0]
            if script not in allowed_scripts:
                return ValidationResult(False, f"Script not allowed: {script}")

            # Determine args destined for the script, respecting `--`
            # parts: ["pnpm","run","test", ...]
            # after: ["test", <maybe flags/args>]
            try:
                script_pos = after.index(script)
            except ValueError:
                script_pos = 0  # defensive; script should be first positional
            rest = after[script_pos + 1:]  # tokens after script name
            runner_args = rest[rest.index("--") + 1:] if "--" in rest else rest

            if spec.get("deny_args"):
                # disallow anything after the script (and also a bare `--`)
                if runner_args or ("--" in rest):
                    return ValidationResult(False, "Extra args not allowed after script")
            elif spec.get("allow_test_paths", False):
                # Fence file/node-id selectors to the workspace
                bad = next(
                    (a for a in runner_args
                     if looks_like_path(a)
                     and not is_within_workspace(workspace_root, extract_file_part(a))),
                    None
                )
                if bad:
                    return ValidationResult(False, f"Unsafe path outside workspace in pnpm run args: {bad}")

        elif sub == "install":
            if not spec.get("enabled", False):
                return ValidationResult(False, f"Subcommand disabled by policy: {sub}")
            if spec.get("require_no_packages"):
                if positionals:
                    return ValidationResult(False, f"{sub} with package names is not allowed")

        elif sub == "config":
            if spec.get("get_only"):
                first_nonflag = positionals[0].lower() if positionals else None
                if first_nonflag != "get":
                    return ValidationResult(False, "Only 'pnpm config get <key>' is allowed")

        return ValidationResult(True, "OK", timeout=spec.get("timeout") or policy.get("default_timeout"))

    def adjust_arguments(self, parts: List[str], policy: Mapping[str, Any]) -> List[str]:
        """
        Auto-inject required flags for subcommands like 'install'
        (e.g., --ignore-scripts) if they're missing.
        Called AFTER validate() by the executor.
        """
        if len(parts) < 2:
            return parts

        subs: Mapping[str, Any] = policy.get("subcommands", {}) or {}
        raw_sub = parts[1].lower()
        alias_map = {"i": "install", "add": "install"}
        sub = alias_map.get(raw_sub, raw_sub)
        spec = subs.get(sub) or {}

        req = list(spec.get("require_flags") or [])
        if not req:
            return parts

        existing = set()
        for p in parts[2:]:
            if p.startswith("-"):
                existing.add(self._flag_base(p))

        # Insert missing required flags right after the subcommand token
        insert_at = 2
        for needed in req:
            base = self._flag_base(needed)
            if base not in existing:
                parts.insert(insert_at, needed)
                insert_at += 1

        return parts

    def adjust_environment(self, base_env, parts, policy):
        env = super().adjust_environment(base_env, parts, policy)
        return env