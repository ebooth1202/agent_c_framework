import os
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


    def build_command_instructions(
            self,
            base_cmd: str,
            spec: Mapping[str, Any],
            *,
            max_examples: int = 6,
            max_chars: int = 1400
    ) -> str:
        import textwrap

        def _fmt_list(items):
            return ", ".join(items) if items else "—"

        def _coerce_flags(entry):
            # Accept either "flags" or "allowed_flags"
            if not isinstance(entry, dict):
                return []
            flags = entry.get("allowed_flags")
            if flags is None:
                flags = entry.get("flags")
            return list(flags or [])

        desc = (spec.get("description") or f"Run safe, policy-constrained {base_cmd} commands.").strip()

        # Handle both dict and list formats for flags
        flags_config = spec.get("root_flags") or spec.get("flags") or []
        if isinstance(flags_config, dict):
            root_flags = list(flags_config.keys())
        else:
            root_flags = flags_config

        sub = spec.get("subcommands") or {}
        deny = spec.get("deny_subcommands") or []
        lines = [desc, "", "Use only the items below. Anything not listed is rejected.", ""]


        if root_flags:
            lines.append("Allowed root flags: " + ", ".join(root_flags))


        # Special-case: npx (no subcommands; allowed_packages + flags)
        if base_cmd == "npx" and spec.get("allowed_packages"):
            lines.append("Allowed packages: " + ", ".join(spec["allowed_packages"]))
            if spec.get("flags"):
                npx_flags = spec["flags"]
                if isinstance(npx_flags, dict):
                    lines.append("Allowed flags: " + ", ".join(npx_flags.keys()))
                else:
                    lines.append("Allowed flags: " + ", ".join(npx_flags))

        if sub:
            lines.append("Allowed subcommands:")
            for name, info in sub.items():
                info = info or {}
                flags = info.get("allowed_flags") or info.get("flags") or []
                bits = []
                if flags:
                    bits.append("flags: " + ", ".join(flags))
                if "allowed_scripts" in info:
                    bits.append("scripts: " + ", ".join(info["allowed_scripts"]))
                if info.get("get_only"):
                    bits.append("only: get")
                if "require_flags" in info:
                    # render auto-required flags succinctly
                    req = info["require_flags"]
                    if isinstance(req, dict):
                        req_list = []
                        for k, v in req.items():
                            if v is True:
                                req_list.append(k)
                            elif isinstance(v, list):
                                req_list.append(f"{k}={{{{ {', '.join(v)} }}}}")
                            else:
                                req_list.append(f"{k}={v}")
                        bits.append("auto-added: " + ", ".join(req_list))
                    elif isinstance(req, list):
                        bits.append("auto-added: " + ", ".join(req))
                if info.get("require_no_packages"):
                    bits.append("no package names allowed")
                if info.get("enabled") is False:
                    bits.append("DISABLED")
                line = f"  • {name}" + (": " + "; ".join(bits) if bits else "")
                lines.append(line)

        if deny:
            lines.append("Disallowed subcommands: " + ", ".join(deny))

        # A few short, safe examples
        examples = []
        try:
            if root_flags:
                examples.append(f"{base_cmd} {root_flags[0]}")


            if sub:
                for s in list(sub)[:3]:
                    if "allowed_scripts" in sub[s]:
                        examples.append(f"{base_cmd} {s} {sub[s]['allowed_scripts'][0]}")
                    elif (sub[s].get("require_flags")):
                        examples.append(f"{base_cmd} {s}  # required flags auto-added")
                    else:
                        examples.append(f"{base_cmd} {s}")

            if base_cmd == "npx" and spec.get("allowed_packages"):
                examples.append(f"npx --yes {spec['allowed_packages'][0]} --version")
        except Exception as e:
            self.logger.exception(f"Failed to build examples for {base_cmd}, {e}")

        if examples:
            lines += ["", "Examples:", *[f"  • {e}" for e in examples]]

        text = "\n".join(lines).strip()
        if max_chars and len(text) > max_chars:
            text = textwrap.shorten(text, width=max_chars, placeholder="…")
        return text
