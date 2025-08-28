# doc_registry.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
import os
import re
import unicodedata
from urllib.parse import unquote

# Treat these as markdown documents
MARKDOWN_EXTS = (".md", ".markdown", ".mdx")


def _posix(path: str) -> str:
    """Normalize path separators to POSIX style for consistent keys."""
    return path.replace("\\", "/")


def _has_md_ext(path: str) -> bool:
    return path.lower().endswith(MARKDOWN_EXTS)


# ---------- Alias Normalization ----------

_WS = re.compile(r"[\s_\-]+")
_LEADING_NUM = re.compile(r"^\d+[\s._-]*")


def normalize_display_alias(s: str) -> str:
    """
    Normalize a human label (or filename stem) into a stable alias:
    - NFKD normalize + strip accents
    - lower-case
    - drop leading numeric prefixes like '01 ', '02_', '03-'
    - strip punctuation/emoji (keep word chars, space, underscore, hyphen)
    - collapse spaces/underscores/hyphens to single space
    """
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = s.encode("ascii", "ignore").decode("ascii")
    s = s.strip().lower()
    s = _LEADING_NUM.sub("", s)
    s = re.sub(r"[^\w\s_-]+", "", s)
    s = _WS.sub(" ", s).strip()
    return s


# ---------- Data Models ----------

@dataclass
class DocMeta:
    path: str                # canonical POSIX path, e.g., "dir2/02 meeting-notes.md"
    display_name: str        # e.g., "02 Meeting-Notes" or custom label
    content: str             # raw (already safety-processed) markdown
    anchors: Set[str] = field(default_factory=set)


@dataclass
class DocRegistry:
    by_path: Dict[str, DocMeta] = field(default_factory=dict)
    by_display: Dict[str, List[str]] = field(default_factory=dict)
    by_alias: Dict[str, List[str]] = field(default_factory=dict)

    # ---- Registry population ----

    def add_document(self, doc: DocMeta) -> None:
        """Register a document and build display/alias indices."""
        # Canonicalize path to POSIX
        doc.path = _posix(doc.path)
        self.by_path[doc.path] = doc

        # Exact display-name index
        self.by_display.setdefault(doc.display_name, []).append(doc.path)

        # Alias keys: normalized display name + filename stem
        aliases: Set[str] = set()
        aliases.add(normalize_display_alias(doc.display_name))
        stem = os.path.splitext(os.path.basename(doc.path))[0]
        aliases.add(normalize_display_alias(stem))

        for a in aliases:
            if not a:
                continue
            self.by_alias.setdefault(a, []).append(doc.path)

    # ---- Link resolution ----

    def resolve_link_target(self, target: str, source_path: str) -> Optional[str]:
        """
        Resolve a link target referenced from source_path to a canonical doc path.

        Rules:
          - '#anchor' -> return None (same-doc anchor; caller handles)
          - Path-like (contains '/' OR has md extension) -> resolve relative to source,
            check exact file; if folder path, choose first file under that folder (sorted)
          - Otherwise treat as a display-name alias; must resolve to a unique doc
        """
        if target is None:
            return None

        # Decode %20, %28, etc. before any path operations
        target = unquote(str(target)).strip()
        src = _posix(source_path)

        # split off any fragment so path matching uses the real filename
        if "#" in target:
            target, _frag = target.split("#", 1)

        # Same-document anchor
        if target.startswith("#"):
            return None

        pathlike = ("/" in target) or _has_md_ext(target)
        if pathlike:
            base_dir = _posix(os.path.dirname(src))
            joined = os.path.normpath(os.path.join(base_dir, target))
            candidate = _posix(joined)
            candidate = os.path.normpath(candidate).replace("\\", "/")

            # Exact file
            if candidate in self.by_path:
                return candidate

            # also try stripping a leading "./"
            if candidate.startswith("./"):
                alt = candidate[2:]
                if alt in self.by_path:
                    return alt

            # Folder link (no extension or trailing slash): pick first file beneath
            _, ext = os.path.splitext(candidate)
            if not ext or candidate.endswith("/"):
                prefix = candidate if candidate.endswith("/") else candidate + "/"
                for p in sorted(self.by_path.keys()):
                    if p.startswith(prefix):
                        return p

            return None

        # Display-name / bare reference via aliases
        alias = normalize_display_alias(target)
        matches = self.by_alias.get(alias, [])
        if len(matches) == 1:
            return matches[0]
        # multiple or none -> unresolved
        return None

    # ---- Diagnostics ----

    def stats(self) -> Dict[str, int]:
        total_docs = len(self.by_path)
        unique_display = len(self.by_display)
        display_collisions = sum(1 for _, v in self.by_display.items() if len(v) > 1)
        total_colliding_docs = sum(len(v) for v in self.by_display.values() if len(v) > 1)
        return {
            "total_documents": total_docs,
            "unique_display_names": unique_display,
            "display_name_collisions": display_collisions,
            "total_colliding_docs": total_colliding_docs,
        }


# ---------- UI Tree Builder ----------

def build_ui_tree_from_registry(registry: DocRegistry) -> List[dict]:
    """
    Build the sidebar tree structure expected by the viewer template:
      [
        { "type": "folder", "name": "dir2", "children": [ ... ] },
        { "type": "file",   "name": "01 Index", "path": "dir2/01 index.md", "content": "..."},
        ...
      ]
    """
    # Use a nested dict keyed by folder/file keys, then convert to arrays
    root: dict = {"type": "folder", "name": "Root", "children": {}}

    for path, meta in registry.by_path.items():
        parts = path.split("/")
        node = root
        # descend through folder components
        for folder in parts[:-1]:
            children = node["children"]
            if folder not in children:
                children[folder] = {"type": "folder", "name": folder, "children": {}}
            node = children[folder]
        # leaf file
        node["children"][path] = {
            "type": "file",
            "name": meta.display_name,  # display label in the UI
            "path": path,               # canonical path
            "content": meta.content,    # pre-render markdown string
        }

    def to_list(folder_node: dict) -> List[dict]:
        items: List[dict] = []
        # split into folder children vs file children
        folders = [v for v in folder_node["children"].values() if v["type"] == "folder"]
        files = [v for v in folder_node["children"].values() if v["type"] == "file"]

        # Folders: sort by folder name (case-insensitive)
        folders.sort(key=lambda n: n["name"].lower())
        # Files: sort by full path so numeric prefixes keep natural order
        files.sort(key=lambda n: n["path"].lower())

        for f in folders:
            items.append({
                "type": "folder",
                "name": f["name"],
                "children": to_list(f),
            })
        items.extend(files)
        return items

    # Top-level children as a list
    return to_list(root)


__all__ = [
    "DocMeta",
    "DocRegistry",
    "normalize_display_alias",
    "build_ui_tree_from_registry",
]
