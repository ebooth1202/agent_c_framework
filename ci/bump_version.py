#!/usr/bin/env python3
import sys
import tomli  # For reading TOML (pip install tomli)
import tomli_w  # For writing TOML (pip install tomli-w)


def bump_version(file_path, build_number):
    # Load the TOML file
    with open(file_path, "rb") as f:
        data = tomli.load(f)

    # Attempt to retrieve the current version from common sections.
    # Adjust the keys below based on your project's configuration.
    version = None
    if "tool" in data and "poetry" in data["tool"]:
        version = data["tool"]["poetry"].get("version")
    if not version and "project" in data:
        version = data["project"].get("version")
    if not version:
        print("Version not found in the file.")
        sys.exit(1)

    # Append the build number (you could choose a different format)
    new_version = f"{version}+{build_number}"

    # Update version in the sections if present.
    if "tool" in data and "poetry" in data["tool"] and "version" in data["tool"]["poetry"]:
        data["tool"]["poetry"]["version"] = new_version
    if "project" in data and "version" in data["project"]:
        data["project"]["version"] = new_version

    # Write changes back to the file.
    with open(file_path, "wb") as f:
        tomli_w.dump(data, f)

    print(f"Updated version to {new_version} in {file_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: bump_version.py <path_to_pyproject.toml> <build_number>")
        sys.exit(1)
    bump_version(sys.argv[1], sys.argv[2])