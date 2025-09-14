import os
import textwrap

import yaml
from pathlib import Path
from typing import List, Dict, Optional, Mapping, Any
from agent_c.config.config_loader import ConfigLoader

class YamlPolicyProvider(ConfigLoader):
    """
    Loads policies from whitelist_commands.yaml using ConfigLoader for path resolution.

    Resolves a policy file path using ConfigLoader's configuration directory,
    with optional environment override.

    Search order (first match wins):
      1) Env override: AGENTC_POLICIES_FILE (absolute path)
      2) <config_path>/<policy_filename>

    Example schema expected in yaml:
      git:
        subcommands: { status: {...}, log: {...} }
        safe_env: { GIT_TERMINAL_PROMPT: "0" }
        default_timeout: 30
      pytest:
        default_timeout: 120
        env_overrides: { PYTEST_DISABLE_PLUGIN_AUTOLOAD: "1" }
    """
    def __init__(self, config_path: Optional[str] = None, policy_filename: str = "whitelist_commands.yaml") -> None:
        """
        Initialize the YAML policy provider.

        Args:
            config_path: Optional path to configuration directory (uses ConfigLoader resolution if None)
            policy_filename: Name of the policy file to load (default: .whitelist_commands.yaml)
        """
        super().__init__(config_path)
        self._module_dir = Path(__file__).resolve().parent
        self.policy_filename = policy_filename
        self._policy_file_path = self._resolve_policy_path()
        self._cache: Dict[str, Dict] = {}
        self._mtimes: Dict[str, float] = {}

    def _resolve_policy_path(self) -> Path:
        """
        Resolve the path to the policy file.

        Returns:
            Resolved Path to the policy file
        """
        # 1) Environment override wins
        env_path = os.getenv("AGENTC_POLICIES_FILE")
        if env_path:
            return Path(env_path).resolve()

        # 2) Use ConfigLoader's resolved config path + policy filename
        return Path(self.config_path).joinpath(self.policy_filename)

    def _ensure_policy_loaded(self) -> bool:
        """
        Load the policy file if it has changed since last load.

        Returns:
            True if file was loaded successfully or is in cache
            False if file doesn't exist

        Raises:
            yaml.YAMLError: If YAML is malformed
            UnicodeError: If file cannot be decoded
        """
        path = self._policy_file_path

        if not path.exists():
            self.logger.debug(f"Policy file not found: {path}")
            return False

        try:
            mtime = path.stat().st_mtime
        except OSError as e:
            self.logger.error(f"Error accessing policy file {path}: {e}")
            return False

        key = str(path)
        if self._mtimes.get(key) == mtime:
            return True  # cached & unchanged

        self.logger.info(f"Loading policy from: {path}")

        last_exc = None
        for enc in ("utf-8", "utf-8-sig", "utf-16"):
            try:
                with open(path, "r", encoding=enc, newline="") as f:
                    content = f.read()
                    data = yaml.safe_load(content) or {}

                # Normalize top-level keys to lowercase
                doc = {str(k).lower(): v for k, v in data.items()} if isinstance(data, dict) else {}
                self._cache[key] = doc
                self._mtimes[key] = mtime

                self.logger.debug(f"Successfully loaded policy file with {enc} encoding")
                return True

            except UnicodeError as e:
                last_exc = e
                continue
            except yaml.YAMLError as e:
                # YAML is present but malformed; surface this so you can fix the file
                self.logger.error(f"YAML parsing error in {path}: {e}")
                raise

        # If we got here, decoding failed for all tried encodings
        error_msg = f"Could not decode {path} using utf-8 / utf-8-sig / utf-16"
        self.logger.error(error_msg)
        raise UnicodeError(error_msg) from last_exc

    def get_policy(self, base_cmd: str, parts: Optional[List[str]] = None) -> Optional[Mapping]:
        """
        Get policy for a given command.

        Args:
            base_cmd: Base command to get policy for
            parts: Additional command parts (currently unused but kept for compatibility)

        Returns:
            Policy mapping for the command, or None if not found
        """
        if not self._ensure_policy_loaded():
            return None

        doc = self._cache.get(str(self._policy_file_path), {})
        return doc.get(base_cmd.lower())

    def reload_policy(self) -> bool:
        """
        Force reload of the policy file, bypassing cache.

        Returns:
            True if file was loaded successfully, False if file doesn't exist
        """
        # Clear cache for this file
        key = str(self._policy_file_path)
        if key in self._cache:
            del self._cache[key]
        if key in self._mtimes:
            del self._mtimes[key]

        return self._ensure_policy_loaded()

    def get_all_policies(self) -> Dict[str, Dict]:
        """
        Get all loaded policies.

        Returns:
            Dictionary of all policies keyed by command name
        """
        if not self._ensure_policy_loaded():
            return {}

        return self._cache.get(str(self._policy_file_path), {})

    def has_policy(self, base_cmd: str) -> bool:
        """
        Check if a policy exists for the given command.

        Args:
            base_cmd: Base command to check

        Returns:
            True if policy exists, False otherwise
        """
        return self.get_policy(base_cmd) is not None

    @property
    def policy_file_path(self) -> Path:
        """Get the resolved policy file path."""
        return self._policy_file_path

    # inside class YamlPolicyProvider
    from typing import Mapping, Optional, Any, List
    import textwrap

    @staticmethod
    def build_command_instructions(
            command_name: str,
            policy: Mapping[str, Any],
            *,
            subcommand: str | None = None,  # nice, high-level selector
            spec: Mapping[str, Any] | None = None,  # raw override (advanced)
            max_chars: int | None = None,
            description: str | None = None,
    ) -> str:
        """Build human-readable instructions for a command based on a policy.

        Back-compat: callers may pass only (command_name, policy).
        Enhancement: callers may target a single subcommand via subcommand=...,
        or pass a raw spec=... dict directly.
        """

        def _coerce_list(v) -> List[str]:
            if v is None:
                return []
            if isinstance(v, (list, tuple, set)):
                return [str(x) for x in v]
            if isinstance(v, dict):
                return list(v.keys())
            return [str(v)]

        def _coerce_flags(entry: Mapping[str, Any] | None) -> List[str]:
            if not isinstance(entry, Mapping):
                return []
            flags = entry.get("allowed_flags", entry.get("flags"))
            return _coerce_list(flags)

        def _format_require_flags(entry: Mapping[str, Any] | None) -> List[str]:
            if not isinstance(entry, Mapping):
                return []
            rf = entry.get("require_flags")
            if not rf:
                return []
            out: List[str] = []
            if isinstance(rf, list):
                out.extend(map(str, rf))
            elif isinstance(rf, dict):
                for k, v in rf.items():
                    if v is True:
                        out.append(str(k))
                    elif isinstance(v, (list, tuple, set)):
                        inner = ", ".join(map(str, v))
                        out.append(f"{k}={{{{ {inner} }}}}")
                    else:
                        out.append(f"{k}={v}")
            else:
                out.append(str(rf))
            return out

        def _append_global_flags_before(lines: List[str], gb: Mapping[str, Any]):
            if not gb:
                return
            items = []
            for k, takes_val in gb.items():
                items.append(f"{k}{' <val>' if bool(takes_val) else ''}")
            lines.append("Global flags (pre-subcommand): " + ", ".join(items))

        desc = (description
                or policy.get("description")
                or f"Run safe, policy-constrained {command_name} commands."
                ).strip()

        # Root flags (list or dict accepted)
        root_flags_cfg = policy.get("root_flags", policy.get("flags", []))
        root_flags = _coerce_list(root_flags_cfg)

        subcommands = policy.get("subcommands")
        deny_sub = _coerce_list(policy.get("deny_subcommands"))
        global_before = policy.get("global_flags_before_subcommand") or {}
        default_timeout = policy.get("default_timeout")

        lines: List[str] = [desc, "", "Use only the items below. Anything not listed is rejected.", ""]

        if root_flags:
            lines.append("Allowed root flags: " + ", ".join(root_flags))
        _append_global_flags_before(lines, global_before)
        if deny_sub:
            lines.append("Disallowed subcommands: " + ", ".join(deny_sub))
        if default_timeout is not None:
            lines.append(f"Default timeout: {default_timeout}s")

        # ---------- Resolve target (spec or policy summary) ----------
        target_spec: Optional[Mapping[str, Any]] = None
        target_label: Optional[str] = None

        if spec is not None:
            target_spec = spec
            target_label = subcommand or "<spec>"
        elif subcommand and isinstance(subcommands, dict) and subcommand in subcommands:
            target_spec = subcommands[subcommand] or {}
            target_label = subcommand

        # ---------- Render a single spec (if requested) ----------
        if target_spec is not None:
            lines.append("")
            lines.append(f"Subcommand: {target_label}")

            flags = _coerce_flags(target_spec)
            req_flags = _format_require_flags(target_spec)
            deny_args = target_spec.get("deny_args")
            allow_test_paths = target_spec.get("allow_test_paths")
            get_only = target_spec.get("get_only")
            require_no_packages = target_spec.get("require_no_packages")
            enabled = target_spec.get("enabled")
            timeout = target_spec.get("timeout")

            if flags:
                lines.append("  • Allowed flags: " + ", ".join(flags))
            if req_flags:
                lines.append("  • Auto-added flags: " + ", ".join(req_flags))
            if deny_args is not None:
                lines.append(f"  • deny_args: {bool(deny_args)}")
            if allow_test_paths:
                lines.append("  • path-fencing: enabled")
            if get_only:
                lines.append("  • only: get")
            if require_no_packages:
                lines.append("  • no package names allowed")
            if enabled is False:
                lines.append("  • DISABLED")
            if timeout is not None:
                lines.append(f"  • timeout: {timeout}s")

            # scripts (supports either legacy allowed_scripts or new scripts dict)
            scripts = target_spec.get("allowed_scripts")
            if not scripts and isinstance(target_spec.get("scripts"), Mapping):
                scripts = list((target_spec["scripts"] or {}).keys())
            if scripts:
                lines.append("  • scripts: " + ", ".join(map(str, scripts)))

        # ---------- Otherwise, render a summary of the whole policy ----------
        else:
            # npx special case
            if command_name == "npx" and policy.get("allowed_packages"):
                lines.append("Allowed packages: " + ", ".join(policy["allowed_packages"]))
                flags = _coerce_flags(policy)
                if flags:
                    lines.append("Allowed flags: " + ", ".join(flags))

            # Subcommand listing
            if isinstance(subcommands, dict) and subcommands:
                lines.append("")
                lines.append("Allowed subcommands:")
                for name, info in subcommands.items():
                    info = info or {}
                    flags = _coerce_flags(info)
                    req = _format_require_flags(info)
                    bits: List[str] = []
                    if flags:
                        bits.append("flags: " + ", ".join(flags))
                    if req:
                        bits.append("auto-added: " + ", ".join(req))
                    if info.get("deny_args") is not None:
                        bits.append(f"deny_args: {bool(info.get('deny_args'))}")
                    if info.get("allow_test_paths"):
                        bits.append("path-fencing: enabled")
                    if info.get("get_only"):
                        bits.append("only: get")
                    if info.get("require_no_packages"):
                        bits.append("no package names allowed")
                    if info.get("enabled") is False:
                        bits.append("DISABLED")
                    # scripts: legacy list or new dict under run.scripts
                    scripts = info.get("allowed_scripts")
                    if not scripts and isinstance(info.get("scripts"), Mapping):
                        scripts = list((info["scripts"] or {}).keys())
                    if scripts:
                        bits.append("scripts: " + ", ".join(map(str, scripts)))
                    lines.append("  • " + name + (": " + "; ".join(bits) if bits else ""))

        # ---------- Examples (best-effort, safe) ----------
        examples: List[str] = []
        try:
            if root_flags:
                examples.append(f"{command_name} {root_flags[0]}")

            if target_spec is not None:
                # Single-subcommand example
                if target_label:
                    if target_spec.get("require_flags"):
                        examples.append(f"{command_name} {target_label}  # required flags auto-added")
                    elif target_spec.get("allowed_scripts"):
                        ex_script = target_spec["allowed_scripts"][0]
                        examples.append(f"{command_name} {target_label} {ex_script}")
                    elif isinstance(target_spec.get("scripts"), Mapping):
                        keys = list(target_spec["scripts"].keys())
                        if keys:
                            examples.append(f"{command_name} {target_label} {keys[0]}")
                    else:
                        examples.append(f"{command_name} {target_label}")
            else:
                # Policy-level examples
                if isinstance(subcommands, dict) and subcommands:
                    for sname, sinfo in list(subcommands.items())[:3]:
                        if sinfo and sinfo.get("allowed_scripts"):
                            examples.append(f"{command_name} {sname} {sinfo['allowed_scripts'][0]}")
                        elif sinfo and isinstance(sinfo.get("scripts"), Mapping):
                            skeys = list((sinfo["scripts"] or {}).keys())
                            if skeys:
                                examples.append(f"{command_name} {sname} {skeys[0]}")
                        elif sinfo and sinfo.get("require_flags"):
                            examples.append(f"{command_name} {sname}  # required flags auto-added")
                        else:
                            examples.append(f"{command_name} {sname}")

            if command_name == "npx" and policy.get("allowed_packages"):
                examples.append(f"npx --yes {policy['allowed_packages'][0]} --version")
        except Exception:
            # keep examples best-effort and non-fatal
            pass

        if examples:
            lines += ["", "Examples:", *[f"  • {e}" for e in examples]]

        text = "\n".join(lines).strip()
        if isinstance(max_chars, int) and max_chars > 0 and len(text) > max_chars:
            text = textwrap.shorten(text, width=max_chars, placeholder="…")
        return text

