#!/usr/bin/env python3
"""
Test script to validate that test path support works correctly
"""
import os
import sys
sys.path.insert(0, r'C:\Users\justj\PycharmProjects\agent_c_framework\src\agent_c_tools\src')

from agent_c_tools.tools.workspace.executors.local_storage.validators.pytest_validator import PytestCommandValidator
from agent_c_tools.tools.workspace.executors.local_storage.validators.npm_validator import NpmCommandValidator
from agent_c_tools.tools.workspace.executors.local_storage.validators.dotnet_validator import DotnetCommandValidator

def test_pytest_path_validation():
    validator = PytestCommandValidator()
    workspace_root = r"C:\Users\justj\PycharmProjects\agent_c_framework"

    policy = {
        "allow_test_paths": True,
        "workspace_root": workspace_root,
        "default_timeout": 120
    }

    # Test cases that should be ALLOWED
    allowed_commands = [
        ["pytest", "tests/test_file.py"],
        ["pytest", "tests/test_file.py::test_function"],
        ["pytest", "tests/test_file.py:123"],
        ["pytest", r"src\agent_c_tools\src\agent_c_tools\tools\workspace\executors\tests"],
        ["pytest", "--no-header", "--no-summary", "-q", "tests/"]
    ]

    # Test cases that should be BLOCKED
    blocked_commands = [
        ["pytest", "../dangerous_path"],
        ["pytest", "tests/../../../etc/passwd"],
        ["pytest", r"C:\Windows\System32\test.py"]  # Outside workspace
    ]

    print("Testing ALLOWED commands:")
    for cmd in allowed_commands:
        result = validator.validate(cmd, policy)
        print(f"  {' '.join(cmd)} -> {'�� ALLOWED' if result.allowed else '✗ BLOCKED: ' + result.reason}")

    print("\nTesting BLOCKED commands:")
    for cmd in blocked_commands:
        result = validator.validate(cmd, policy)
        print(f"  {' '.join(cmd)} -> {'✗ BLOCKED: ' + result.reason if not result.allowed else '✓ ALLOWED (unexpected!)'}")

def test_npm_path_validation():
    validator = NpmCommandValidator()
    workspace_root = r"C:\Users\justj\PycharmProjects\agent_c_framework"

    policy = {
        "subcommands": {
            "run": {
                "allowed_scripts": ["test"],
                "deny_args": False,
                "allow_test_paths": True
            }
        },
        "workspace_root": workspace_root,
        "default_timeout": 120
    }

    # Test cases
    allowed_commands = [
        ["npm", "run", "test", "tests/test_file.js"],
        ["npm", "run", "test", "tests/test_file.js:123"]
    ]

    blocked_commands = [
        ["npm", "run", "test", "../dangerous_path"],
        ["npm", "run", "test", r"C:\Windows\System32\test.js"]
    ]

    print("\nTesting NPM ALLOWED commands:")
    for cmd in allowed_commands:
        result = validator.validate(cmd, policy)
        print(f"  {' '.join(cmd)} -> {'✓ ALLOWED' if result.allowed else '✗ BLOCKED: ' + result.reason}")

    print("\nTesting NPM BLOCKED commands:")
    for cmd in blocked_commands:
        result = validator.validate(cmd, policy)
        print(f"  {' '.join(cmd)} -> {'✗ BLOCKED: ' + result.reason if not result.allowed else '✓ ALLOWED (unexpected!)'}")

if __name__ == "__main__":
    test_pytest_path_validation()
    test_npm_path_validation()
    print("\n" + "="*50)
    print("Test validation complete!")
