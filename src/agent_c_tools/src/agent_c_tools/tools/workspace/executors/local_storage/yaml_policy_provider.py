import os
import yaml
from pathlib import Path
from typing import List, Dict, Optional, Mapping


class YamlPolicyProvider:
    """
    Loads policies from .agentc_policies.yaml
    Resolves a policy file path given as either:
      - absolute path (uses it directly), or
      - anchored suffix (e.g., '/.agentc_policies.yaml'), resolved against anchors.

    Search order (first match wins):
      1) Env override: AGENTC_POLICIES_FILE
      2) <anchors[i]> / <suffix>  (for each anchor in anchors)
      3) Current working directory / <suffix>

    Example schema expected in yaml:
      git:
        subcommands: { status: {...}, log: {...} }
        safe_env: { GIT_TERMINAL_PROMPT: "0" }
        default_timeout: 30
      pytest:
        default_timeout: 120
        env_overrides: { PYTEST_DISABLE_PLUGIN_AUTOLOAD: "1" }
    """
    def __init__(self, policy_path: str | Path = ".agentc_policies.yaml") -> None:
        self._module_dir = Path(__file__).resolve().parent
        self._path = self._resolve_path(policy_path)
        self._cache: Dict[str, Dict] = {}      # keyed by resolved path str
        self._mtimes: Dict[str, float] = {}

    def _resolve_path(self, raw: str | Path | None) -> Path:
        # 1) Env override wins
        envp = os.getenv("AGENTC_POLICIES_FILE")
        if envp:
            return Path(envp).resolve()

        # 2) Default → file next to this provider
        if raw is None:
            return (self._module_dir / ".agentc_policies.yaml").resolve()

        raw_str = str(raw)
        p = Path(raw_str)

        # 3) Absolute → use as-is
        if p.is_absolute():
            return p

        # 4) Anchored suffix (starts with '/' or '\') → relative to provider dir
        if raw_str.startswith(("/", "\\")):
            # keep only suffix (e.g., "/.agentc_policies.yaml" → ".agentc_policies.yaml")
            return (self._module_dir / raw_str.lstrip("/\\")).resolve()

        # 5) Bare filename (no directory separators) → relative to provider dir
        if ("/" not in raw_str) and ("\\" not in raw_str):
            return (self._module_dir / raw_str).resolve()

        # 6) Relative path that already contains directories → treat as CWD-relative
        return Path(raw_str).resolve()

    def _load_if_changed(self) -> bool:
        path = self._path

        if not path.exists():
            # Helpful while testing
            print(f"[policy] not found: {path}")
            return False

        mtime = path.stat().st_mtime
        key = str(path)
        if self._mtimes.get(key) == mtime:
            return True  # cached & unchanged

        print("[policy] resolving from:", Path(__file__).resolve().parent)
        print("[policy] policy path:", self._path, "exists:", self._path.exists())

        last_exc = None
        for enc in ("utf-8", "utf-8-sig", "utf-16"):
            try:
                with open(path, "r", encoding=enc, newline="") as f:
                    content = f.read()
                    data = yaml.safe_load(content) or {}
                # normalize top-level keys to lowercase
                doc = {str(k).lower(): v for k, v in data.items()} if isinstance(data, dict) else {}
                self._cache[key] = doc
                self._mtimes[key] = mtime
                # Optional: print(f"[policy] loaded {path} with {enc}")
                return True
            except UnicodeError as e:
                last_exc = e
                continue
            except yaml.YAMLError as e:
                # YAML is present but malformed; surface this so you can fix the file
                raise

        # If we got here, decoding failed for all tried encodings
        raise UnicodeError(f"Could not decode {path} using utf-8 / utf-8-sig / utf-16") from last_exc

    def get_policy(self, base_cmd: str, parts: list[str]) -> Optional[Mapping]:
        if not self._load_if_changed():
            return None
        doc = self._cache.get(str(self._path), {})
        return doc.get(base_cmd.lower())