from typing import Dict, Any, List, Mapping, Optional
import os
from .base_validator import ValidationResult, CommandValidator
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

class NpmCommandValidator(CommandValidator):
    """
    Hardened npm validator with support for:
      - root flags only (e.g., -v, --version)
      - per-subcommand allowed flags (allowed_flags or flags)
      - npm run: allowed_scripts + deny_args + safe test paths
      - npm ci/install: enabled, require_no_packages, require_flags_all (auto-injected), allowed_flags
      - npm config: get_only (blocks set/delete)

    Expected policy shape:
      npm:
        root_flags: [...]
        subcommands:
          view:   { allowed_flags: [...] }
          list:   { allowed_flags: [...] }
          ping:   { allowed_flags: [] }
          config: { get_only: true }
          run:
            allowed_scripts: [...]
            deny_args: true  # or false to allow test paths
            allow_test_paths: true  # new: allow test file paths
          ci:
            enabled: true
            require_no_packages: true
            require_flags: ["--ignore-scripts"]
            allowed_flags: [...]
          install:
            enabled: false
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
        if name != "npm":
            return ValidationResult(False, "Not an npm command")

        root_flags = set(policy.get("root_flags") or [])
        subs: Mapping[str, Any] = policy.get("subcommands", {}) or {}
        deny_subs = set(policy.get("deny_subcommands") or [])

        # Case A: root-flags-only usage (e.g., npm -v)
        if len(parts) == 1 or parts[1].startswith("-"):
            used_flags = [p for p in parts[1:] if p.startswith("-")]
            for f in used_flags:
                base = self._flag_base(f)
                if base not in root_flags and f not in root_flags:
                    return ValidationResult(False, f"Root flag not allowed: {f}")
            # Disallow any stray non-flags in flags-only mode
            non_flags = [p for p in parts[1:] if not p.startswith("-")]
            if non_flags:
                return ValidationResult(False, f"Unexpected args: {' '.join(non_flags[:3])}")
            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"), policy_spec=None)

        # Case B: subcommand mode
        raw_sub = parts[1].lower()
        alias_map = {"i": "install"}  # normalize aliases (npm i -> install)
        sub = alias_map.get(raw_sub, raw_sub)

        if sub in deny_subs:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        spec = subs.get(sub)
        if spec is None:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        after = parts[2:]
        used_flags = [p for p in after if p.startswith("-")]
        positionals = [p for p in after if not p.startswith("-")]

        # Common: check allowed flags (if provided)
        allowed_flags = set(self._get_allowed_flags(spec))
        if allowed_flags:
            for f in used_flags:
                base = self._flag_base(f)
                if base not in allowed_flags and f not in allowed_flags:
                    return ValidationResult(False, f"Flag not allowed for {sub}: {f}")

        # Workspace root for path validation
        workspace_root = (
                policy.get("workspace_root")
                or os.environ.get("WORKSPACE_ROOT")
                or os.getcwd()
        )

        if sub == "run":
            allowed_scripts = set(spec.get("allowed_scripts") or [])
            if not positionals:
                return ValidationResult(False, "npm run requires a script name")
            script = positionals[0]
            if script not in allowed_scripts:
                return ValidationResult(False, f"Script not allowed: {script}")

            # Determine args *to the script*, respecting npm's `--` convention.
            # parts: ["npm","run","test", ...]
            # after: parts[2:]  => ["test", <maybe flags/args>]
            try:
                script_pos = after.index(script)
            except ValueError:
                script_pos = 0  # defensive; script should be first positional
            rest = after[script_pos + 1:]  # tokens after the script name
            runner_args = rest[rest.index("--") + 1:] if "--" in rest else rest

            if spec.get("deny_args"):
                # forbid anything beyond the script (also disallow a bare `--`)
                if runner_args or ("--" in rest):
                    return ValidationResult(False, "Extra args not allowed after script")
            elif spec.get("allow_test_paths", False):
                # Fence file/node-id selectors to workspace
                bad = next(
                    (a for a in runner_args
                     if looks_like_path(a)
                     and not is_within_workspace(workspace_root, extract_file_part(a))),
                    None
                )
                if bad:
                    return ValidationResult(False, f"Unsafe path outside workspace in npm run args: {bad}")

        elif sub in ("ci", "install"):
            if not spec.get("enabled", False):
                return ValidationResult(False, f"Subcommand disabled by policy: {sub}")

            if spec.get("require_no_packages"):
                # Any positional arg means they tried to install a package name
                if positionals:
                    return ValidationResult(False, f"{sub} with package names is not allowed")
            # Note: require_flags can be auto-injected elsewhere; don't fail here.

        elif sub == "config":
            # Only allow: npm config get <key>
            if spec.get("get_only"):
                first_nonflag = positionals[0].lower() if positionals else None
                if first_nonflag != "get":
                    return ValidationResult(False, "Only 'npm config get <key>' is allowed")

        # All good
        return ValidationResult(True, "OK", timeout=spec.get("timeout") or policy.get("default_timeout"), policy_spec=spec)

    def adjust_arguments(self, parts: List[str], policy: Mapping[str, Any]) -> List[str]:
        """
        Auto-inject required flags for subcommands like 'ci'/'install'
        (e.g., --ignore-scripts) if they're missing, and ensure npm runs
        with no color for cleaner output. Called AFTER validate() by the executor.
        """
        # Be defensive if someone uses this validator generically
        if self._basename_noext(parts[0]) != "npm":
            return parts

        # ----- 1) Inject required flags for specific subcommands -----
        subs: Mapping[str, Any] = policy.get("subcommands", {}) or {}
        raw_sub = parts[1].lower() if len(parts) > 1 else ""
        alias_map = {"i": "install"}
        sub = alias_map.get(raw_sub, raw_sub)
        spec = subs.get(sub) or {}

        req = list(spec.get("require_flags") or [])
        if req and len(parts) >= 2:
            # Collect existing flag bases after the subcommand token
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

        # ----- 2) Ensure npm itself runs without color -----
        # Insert --no-color BEFORE any "--" so it doesn't get forwarded to the script
        try:
            dashdash_idx = parts.index("--")
        except ValueError:
            dashdash_idx = len(parts)

        head = parts[:dashdash_idx]  # args consumed by npm itself
        # Avoid duplicates and accept either spelling already present
        if ("--no-color" not in head) and ("--color=false" not in head):
            parts.insert(dashdash_idx, "--no-color")

        return parts

    def adjust_environment(self, base_env, parts, policy):
        env = super().adjust_environment(base_env, parts, policy)
        return env