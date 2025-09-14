import os
import logging
from typing import Dict, Any, List, Mapping

from .base_validator import ValidationResult, CommandValidator
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

class PnpmCommandValidator(CommandValidator):
    logger = logging.getLogger("agent_c.validators.pnpm")
    DEBUG = False
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

    @staticmethod
    def _basename_noext(p: str) -> str:
        return os.path.splitext(os.path.basename(p))[0].lower()

    @staticmethod
    def _flag_base(f: str) -> str:
        # treat "--depth=0" as "--depth" when comparing
        return f.split("=", 1)[0]

    @staticmethod
    def _get_allowed_flags_and_presence(spec: Mapping[str, Any]) -> (List[str], bool):
        # Presence matters: empty [] means "no flags allowed"; missing means "unconstrained"
        if "allowed_flags" in spec:
            return list(spec.get("allowed_flags") or []), True
        if "flags" in spec:  # legacy, try not to use it
            return list(spec.get("flags") or []), True
        return [], False

    @staticmethod
    def _split_after_options(tokens: List[str]) -> (List[str], List[str]):
        """
        Split command tail into (flags_region, positionals_region) honoring `--` as end-of-options.
        Everything after `--` is positional, even if it starts with '-'.
        """
        if "--" in tokens:
            idx = tokens.index("--")
            return tokens[:idx], tokens[idx + 1:]
        # No explicit separator; do your existing heuristic
        return [t for t in tokens if t.startswith("-")], [t for t in tokens if not t.startswith("-")]

    def _validate_spec_and_args(
            self,
            spec: Mapping[str, Any],
            after_tokens: List[str],
            sub_name: str,
            policy: Mapping[str, Any],
    ) -> ValidationResult:
        # Honor `--`: everything after is positional
        used_flags, positionals = self._split_after_options(after_tokens)
        has_end_of_opts = ("--" in after_tokens)

        deny_args = spec.get("deny_args", True)
        allow_test_paths = spec.get("allow_test_paths", False)

        # 1) Enforce flags if the list is present (empty list => no flags allowed).
        allowed_flags, flags_present = self._get_allowed_flags_and_presence(spec)
        if flags_present:
            allowed = set(allowed_flags)
            for f in used_flags:
                base = self._flag_base(f)
                if base not in allowed and f not in allowed:
                    return ValidationResult(False, f"Flag not allowed for {sub_name}: {f}")
        # If not present, flags are unconstrained and allowed.

        # 2) Deny positional arguments (and a bare '--') when deny_args is True.
        if deny_args:
            if positionals or has_end_of_opts:
                return ValidationResult(
                    False,
                    f"Arguments not allowed for {sub_name}: "
                    f"{' '.join(positionals[:3]) if positionals else '--'}"
                )

        # 3) If args are allowed and path fencing is requested, fence to workspace.
        if allow_test_paths:
            workspace_root = (
                    policy.get("workspace_root")
                    or os.environ.get("WORKSPACE_ROOT")
                    or os.getcwd()
            )
            bad = next(
                (a for a in positionals
                 if looks_like_path(a)
                 and not is_within_workspace(workspace_root, extract_file_part(a))),
                None
            )
            if bad:
                return ValidationResult(False, f"Unsafe path outside workspace: {bad}")

        return ValidationResult(
            True,
            "OK",
            timeout=spec.get("timeout") or policy.get("default_timeout"),
            policy_spec=spec,
        )

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        name = self._basename_noext(parts[0])
        if name != "pnpm":
            return ValidationResult(False, "Not a pnpm command")

        root_flags = set(policy.get("root_flags") or [])
        if self.DEBUG:
            workspace_root = (
                    policy.get("workspace_root")
                    or os.environ.get("WORKSPACE_ROOT")
                    or os.environ.get("CWD")  # optional fallback you already use elsewhere
                    or os.getcwd()
            )
            cwd = os.environ.get("CWD") or os.getcwd()
            self.logger.debug(
                "pnpm.validate: workspace_root=%s cwd=%s "
                "(policy.workspace_root=%s env.WORKSPACE_ROOT=%s env.CWD=%s)",
                workspace_root,
                cwd,
                policy.get("workspace_root"),
                os.environ.get("WORKSPACE_ROOT"),
                os.environ.get("CWD"),
            )

        subs: Mapping[str, Any] = policy.get("subcommands", {}) or {}
        deny_subs = set((policy.get("deny_subcommands") or []))
        global_before = dict(policy.get("global_flags_before_subcommand") or {})

        # --- Consume allowed global flags that may appear before the subcommand
        i = 1
        consumed_global = False
        while i < len(parts) and parts[i].startswith("-"):
            tok = parts[i]
            base = self._flag_base(tok)  # turns --filter=@x into --filter

            if base in global_before:
                consumed_global = True
                takes_val = bool(global_before[base])

                # equals form: --filter=@scope/pkg (value inline)
                if "=" in tok:
                    i += 1
                    continue

                # space form: --filter @scope/pkg
                i += 1
                if takes_val:
                    if i >= len(parts):
                        return ValidationResult(False, f"Missing value for global flag: {base}")
                    # treat next token as the value even if it looks like a flag
                    i += 1
                continue
            break

        # Root-flags-only mode applies only if the *first* token was a flag and
        # we didn't accept it as an allowed global flag.
        # Root-flags-only usage (e.g., pnpm -v) is only valid if we didn't consume any global-before flags
        if i == 1 and (len(parts) == 1 or parts[1].startswith("-")) and not consumed_global:
            used_flags = [p for p in parts[1:] if p.startswith("-")]
            for f in used_flags:
                base = self._flag_base(f)
                if base not in root_flags and f not in root_flags:
                    return ValidationResult(False, f"Root flag not allowed: {f}")
            non_flags = [p for p in parts[1:] if not p.startswith("-")]
            if non_flags:
                return ValidationResult(False, f"Unexpected args: {' '.join(non_flags[:3])}")
            return ValidationResult(True, "OK", timeout=policy.get("default_timeout"), policy_spec=None)

        # From here, the subcommand is at index i (after any allowed global flags)
        if i >= len(parts):
            return ValidationResult(False, "Missing subcommand")

        sub = parts[i].lower()
        if sub in deny_subs:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        spec = subs.get(sub)
        if spec is None:
            return ValidationResult(False, f"Subcommand not allowed: {sub}")

        after = parts[i + 1:]

        # Special handling: `pnpm run <script> ...`
        # this section should return a ValidationResult.  Regular subcommands are handled after this block.
        if sub == "run":
            scripts = (spec.get("scripts") or {})

            # Find the script name:
            # - Prefer the first non-flag token BEFORE a `--` if present
            # - If no non-flag before `--`, then treat the token AFTER `--` as the script (allows scripts starting with '-')
            script_name = None
            i = 0
            while i < len(after):
                tok = after[i]
                if tok == "--":
                    # No script yet -> script is next token (if any). Else, `--` just ends options; script must have been found.
                    if script_name is None:
                        if i + 1 >= len(after):
                            return ValidationResult(False, "Missing script name for 'pnpm run'")
                        script_name = after[i + 1]
                        i = i + 2
                    else:
                        i += 1
                    break
                if not tok.startswith("-") and script_name is None:
                    script_name = tok
                    i += 1
                    break
                i += 1

            if script_name is None:
                return ValidationResult(False, "Missing script name for 'pnpm run'")

            # Remainder are script arguments; if the first is `--`, drop it so everything after is positional
            script_after = after[i:]

            script_spec = scripts.get(script_name)
            if script_spec is None:
                return ValidationResult(False, f"Script not allowed: {script_name}")

            return self._validate_spec_and_args(script_spec, script_after, f"run:{script_name}", policy)

        # Normal subcommand (build, test, lint, etc.)
        return self._validate_spec_and_args(spec, after, sub, policy)

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