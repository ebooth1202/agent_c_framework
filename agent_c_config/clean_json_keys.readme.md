# clean\_json\_keys — README

A tiny CLI to strip specific keys (e.g., `vendor`, `display_name`) from plain **.json** files. Works on single files or whole directories (recursively), supports in-place edits with backups, or writing cleaned copies elsewhere. Can remove keys only at the top level (default) or **recursively**.

## Features

* Files **or** directories (recurses `*.json`)
* **In-place** editing with optional `.bak` backups
* Or write to an **output directory**
* **Top-level** or **recursive** key removal
* Handles JSON that’s a dict or a list (of dicts)

## Installation

No package install needed—just save the script as `clean_json_keys.py` somewhere on your PATH (or call it with `python`).

```bash
python --version  # Python 3.9+ recommended
```

## Usage

```bash
python clean_json_keys.py [FILES_OR_DIRS ...] [options]
```

**Common options**

* `--keys KEY [KEY ...]` — Keys to remove (default: `vendor display_name`)
* `--recursive` — Remove keys at any nesting depth
* `--in-place` — Edit files directly (default behavior if no `--out-dir`)
* `--out-dir DIR` — Write cleaned copies to DIR (keeps originals untouched)
* `--no-backup` — When using `--in-place`, don’t keep `.bak` backups
* `--backup-suffix SFX` — Backup suffix (default: `.bak`)
* `--indent N` — Pretty-print indent (default: `2`, use `0` for compact)

## Examples

**1) Clean a single file in place (creates `file.json.bak`)**

```bash
python clean_json_keys.py path/to/file.json --in-place
```

**2) Clean an entire directory recursively, in place, no backups**

```bash
python clean_json_keys.py agent_c_config/saved_sessions --in-place --no-backup
```

**3) Write cleaned copies to a new folder**

```bash
python clean_json_keys.py agent_c_config/saved_sessions --out-dir cleaned_sessions
```

**4) Remove keys at any nesting depth**

```bash
python clean_json_keys.py saved_sessions --in-place --recursive
```

**5) Customize keys**

```bash
python clean_json_keys.py saved_sessions --in-place --keys vendor display_name foo bar
```

**Windows path examples**

```powershell
python .\clean_json_keys.py C:\path\to\session.json --in-place
python .\clean_json_keys.py C:\path\to\saved_sessions --in-place --no-backup
```

## Notes & Tips

* If a file’s JSON is a **list**, the tool applies top-level removal to **each element**.
* With `--recursive`, keys are removed anywhere in the structure.
* If no `--out-dir` is given, the tool defaults to **in-place** editing.
* Backups are named `filename.json.bak` by default. Keep them until you’ve validated results.

## Exit & Logging

* Prints a summary: total files processed and how many changed.
* Errors (e.g., unreadable JSON) are reported per file; the script continues with the rest.

## Why this exists

Useful when migrating legacy session JSONs that include fields your Pydantic models forbid (e.g., `vendor`, `display_name`) so validation stops throwing `extra_forbidden`.
