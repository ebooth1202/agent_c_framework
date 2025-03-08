#!/usr/bin/env python3
"""
Script to scan pyproject.toml files in a repository and generate a requirements.txt file
for non-agent_c dependencies.
"""

import os
import re
import sys
import tomli
from collections import defaultdict


def find_pyproject_toml_files(repo_root, subfolders=None):
    """
    Find all pyproject.toml files in specified subfolders of the repository.

    Args:
        repo_root: Root directory of the repository
        subfolders: List of subfolder names under src/ to scan (e.g., ["agent_c_core", "agent_c_api_ui"])
                   If None, scans all subfolders
    """
    toml_files = []

    if subfolders:
        # Only scan specified subfolders under src/
        src_dir = os.path.join(repo_root, "src")
        if not os.path.isdir(src_dir):
            print(f"Error: src directory not found at {src_dir}", file=sys.stderr)
            return []

        for subfolder in subfolders:
            subfolder_path = os.path.join(src_dir, subfolder)

            if not os.path.isdir(subfolder_path):
                print(f"Warning: Subfolder {subfolder} not found in {src_dir}", file=sys.stderr)
                continue

            # Walk through the subfolder to find pyproject.toml files
            for root, _, files in os.walk(subfolder_path):
                if "pyproject.toml" in files:
                    toml_files.append(os.path.join(root, "pyproject.toml"))
    else:
        # Fallback: scan the entire repository
        for root, _, files in os.walk(repo_root):
            if "pyproject.toml" in files:
                toml_files.append(os.path.join(root, "pyproject.toml"))

    return toml_files


def extract_dependencies(toml_file):
    """Extract dependencies from a pyproject.toml file."""
    try:
        with open(toml_file, "rb") as f:
            data = tomli.load(f)

        dependencies = {}

        # Check for different possible dependency locations in pyproject.toml
        if "project" in data and "dependencies" in data["project"]:
            # PEP 621 format
            for dep in data["project"]["dependencies"]:
                name, version = parse_dependency(dep)
                if name:
                    dependencies[name] = version

        elif "tool" in data and "poetry" in data["tool"] and "dependencies" in data["tool"]["poetry"]:
            # Poetry format
            for name, version_info in data["tool"]["poetry"]["dependencies"].items():
                if name != "python":  # Skip python version constraint
                    if isinstance(version_info, str):
                        dependencies[name] = version_info
                    elif isinstance(version_info, dict) and "version" in version_info:
                        dependencies[name] = version_info["version"]

        # Try to find other formats or additional dependencies
        if "build-system" in data and "requires" in data["build-system"]:
            for dep in data["build-system"]["requires"]:
                name, version = parse_dependency(dep)
                if name:
                    dependencies[name] = version

        return dependencies

    except Exception as e:
        print(f"Error processing {toml_file}: {e}", file=sys.stderr)
        return {}


def parse_dependency(dep_string):
    """Parse a dependency string into name and version."""
    # Handle various dependency formats
    # Simple format: "package_name>=1.0.0"
    match = re.match(r"([a-zA-Z0-9_\-\.]+)\s*(.+)?", dep_string)
    if match:
        name = match.group(1)
        version = match.group(2) if match.group(2) else ""
        return name, version
    return None, None


def is_agent_c_dependency(name):
    """Check if a dependency is an agent_c dependency."""
    return name.startswith("agent_c")


def create_requirements_txt(dependencies, output_file="requirements.txt"):
    """Create a requirements.txt file from the collected dependencies."""
    # Sort dependencies by name
    sorted_deps = sorted(dependencies.items())

    with open(output_file, "w") as f:
        for name, versions in sorted_deps:
            # If we have multiple versions, use the most recent one
            if isinstance(versions, list) and versions:
                # This is a simplistic approach - in reality, you might want to use
                # a more sophisticated version comparison
                versions.sort()  # This might not work for all version formats
                version = versions[-1]
            else:
                version = versions

            if version:
                f.write(f"{name}{version}\n")
            else:
                f.write(f"{name}\n")


def main():
    if len(sys.argv) < 2:
        print("Usage: python dependency_scanner.py <repo_root> [output_file] [subfolder1 subfolder2 ...]")
        print("Example: python dependency_scanner.py /path/to/repo requirements.txt agent_c_core agent_c_api_ui agent_c_tools")
        sys.exit(1)

    repo_root = sys.argv[1]

    # Determine output file (second argument) and subfolders (remaining arguments)
    if len(sys.argv) > 2:
        # If the 2nd arg doesn't end with .txt, assume it's a subfolder
        if sys.argv[2].endswith('.txt'):
            output_file = sys.argv[2]
            subfolders = sys.argv[3:] if len(sys.argv) > 3 else None
        else:
            output_file = "requirements.txt"
            subfolders = sys.argv[2:]
    else:
        output_file = "requirements.txt"
        subfolders = None

    print(f"Scanning repository at {repo_root}...")

    if subfolders:
        print(f"Limiting scan to the following subfolders: {', '.join(subfolders)}")
        toml_files = find_pyproject_toml_files(repo_root, subfolders)
    else:
        print("Scanning all directories for pyproject.toml files")
        toml_files = find_pyproject_toml_files(repo_root)

    print(f"Found {len(toml_files)} pyproject.toml files.")

    # Collect all dependencies, keeping track of different versions
    all_dependencies = defaultdict(list)

    for toml_file in toml_files:
        print(f"Processing {toml_file}...")
        dependencies = extract_dependencies(toml_file)

        for name, version in dependencies.items():
            if not is_agent_c_dependency(name):
                all_dependencies[name].append(version)

    # Create a requirements.txt file
    create_requirements_txt(all_dependencies, output_file)
    print(f"Created {output_file} with {len(all_dependencies)} dependencies.")


if __name__ == "__main__":
    main()