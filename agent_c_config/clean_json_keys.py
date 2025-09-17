#!/usr/bin/env python3
"""
clean_json_keys.py

Remove selected keys from JSON (.json) files.

- Works on a single file or any number of files and/or directories (recurses).
- In-place editing with optional .bak backups (default keeps backups).
- Remove keys only at the top level (default) or recursively (--recursive).
- Handles top-level dict OR list-of-dicts JSON.
"""

from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
from typing import Any, Iterable


def remove_keys_top_level(obj: Any, keys: set[str]) -> Any:
    if isinstance(obj, dict):
        for k in keys:
            obj.pop(k, None)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                for k in keys:
                    item.pop(k, None)
    return obj


def remove_keys_recursive(obj: Any, keys: set[str]) -> Any:
    if isinstance(obj, dict):
        # remove then recurse
        for k in list(obj.keys()):
            if k in keys:
                obj.pop(k, None)
        for k, v in list(obj.items()):
            obj[k] = remove_keys_recursive(v, keys)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            obj[i] = remove_keys_recursive(v, keys)
    return obj


def process_json_file(path: Path, keys: set[str], recursive: bool, indent: int | None) -> bool:
    """
    Returns True if the file changed.
    """
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    before = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    cleaner = remove_keys_recursive if recursive else remove_keys_top_level
    cleaned = cleaner(data, keys)
    after = json.dumps(cleaned, ensure_ascii=False, separators=(",", ":"), sort_keys=False)

    if after == before:
        return False

    with path.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=indent)
        if indent is not None:
            f.write("\n")
    return True


def iter_json_files(inputs: Iterable[str]) -> Iterable[Path]:
    for p in inputs:
        path = Path(p)
        if path.is_dir():
            for f in path.rglob("*.json"):
                if f.is_file():
                    yield f
        elif path.is_file():
            # accept even if extension isn't .json, but prefer .json
            yield path
        else:
            print(f"[WARN] Skipping non-existent path: {path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Remove specific keys from JSON files.")
    ap.add_argument("inputs", nargs="+", help="One or more JSON files and/or directories (recurses).")
    ap.add_argument("--keys", nargs="+", default=["vendor", "display_name"],
                    help="Keys to remove. Default: vendor display_name")
    ap.add_argument("--recursive", action="store_true",
                    help="Remove keys at any nesting depth. Default removes only top-level keys (and for lists, each element's top level).")
    ap.add_argument("--in-place", action="store_true",
                    help="Edit files in place. (Default: write to --out-dir)")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="Directory to write cleaned copies (mirrors filenames). If omitted, use --in-place.")
    ap.add_argument("--no-backup", action="store_true",
                    help="When using --in-place, do not keep a .bak backup.")
    ap.add_argument("--backup-suffix", default=".bak",
                    help="Backup suffix for in-place edits. Default: .bak")
    ap.add_argument("--indent", type=int, default=2,
                    help="Pretty-print JSON with this indent. Use 0 for minified (no pretty-print). Default: 2")

    args = ap.parse_args()

    if not args.in_place and args.out_dir is None:
        # default to in-place if neither provided
        args.in_place = True

    if args.out_dir is not None:
        args.out_dir.mkdir(parents=True, exist_ok=True)

    keys = set(args.keys)
    indent = None if args.indent == 0 else args.indent

    total = changed = 0
    for src in iter_json_files(args.inputs):
        total += 1

        if args.in_place:
            # make backup unless suppressed
            if not args.no_backup:
                bak = src.with_name(src.name + args.backup_suffix)
                if bak.exists():
                    bak.unlink()
                src.replace(bak)
                # read from backup, write to original filename
                try:
                    changed_now = process_json_file(bak, keys, args.recursive, indent)
                    # write result to original path
                    with bak.open("r", encoding="utf-8") as f:
                        data = json.load(f)
                    with src.open("w", encoding="utf-8") as f:
                        json.dump(data, f, ensure_ascii=False, indent=indent)
                        if indent is not None:
                            f.write("\n")
                except Exception as e:
                    print(f"[ERROR] {src}: {e}. Restoring original from backup.")
                    if src.exists():
                        src.unlink(missing_ok=True)
                    bak.replace(src)
                    continue
                print(f"[INFO] {src} cleaned{'' if changed_now else ' (no changes)'}; backup: {bak}")
                if changed_now:
                    changed += 1
            else:
                # overwrite without backup (atomic-ish)
                tmp = src.with_suffix(src.suffix + ".tmp-clean")
                try:
                    changed_now = process_json_file(src, keys, args.recursive, indent)
                    # if we got here, src already rewritten; emulate atomic replace by writing to tmp then replacing
                    # (Since we rewrote in-place above, keep it simple and just report)
                except Exception as e:
                    print(f"[ERROR] {src}: {e}")
                    continue
                print(f"[INFO] {src} cleaned{'' if not changed_now else ''} (no backup).")
                if changed_now:
                    changed += 1
        else:
            # write to out_dir
            dst = args.out_dir / src.name
            try:
                # read
                with src.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                before = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
                cleaner = remove_keys_recursive if args.recursive else remove_keys_top_level
                cleaned = cleaner(data, keys)
                after = json.dumps(cleaned, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
                with dst.open("w", encoding="utf-8") as f:
                    json.dump(cleaned, f, ensure_ascii=False, indent=indent)
                    if indent is not None:
                        f.write("\n")
                if after != before:
                    changed += 1
                print(f"[INFO] {src} -> {dst}{' (changed)' if after != before else ' (no changes)'}")
            except Exception as e:
                print(f"[ERROR] {src}: {e}")
                continue

    print(f"[SUMMARY] files={total}, changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
