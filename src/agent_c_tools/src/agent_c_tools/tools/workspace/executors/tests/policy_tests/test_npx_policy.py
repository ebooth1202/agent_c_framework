import pytest


def test_npx_policy_exists(policies):
    """Test that npx policy exists and has correct validator"""
    if "npx" not in policies:
        pytest.skip("npx policy not present")

    pol = policies["npx"]
    assert pol.get("validator") == "npx", "npx should use npx validator"


def test_npx_core_structure(policies):
    """Test that npx has proper core structure"""
    if "npx" not in policies:
        pytest.skip("npx policy not present")

    pol = policies["npx"]

    # Core structure (npx is different from npm/pnpm)
    assert isinstance(pol.get("packages", {}), dict)
    assert isinstance(pol.get("flags", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)
    assert isinstance(pol.get("env_overrides", {}), dict)


def test_npx_allowed_packages_whitelist(policies):
    """Test npx allowed packages whitelist"""
    if "npx" not in policies:
        pytest.skip("npx policy not present")

    pol = policies["npx"]
    packages = pol.get("packages", {})

    # Test that safe packages are whitelisted
    expected_packages = [
        "@angular/cli", "create-react-app", "create-next-app", "@vue/cli",
        "typescript", "ts-node", "eslint", "prettier", "jest", "mocha",
        "webpack", "vite", "rollup", "parcel", "serve", "http-server"
    ]
    for package in expected_packages:
        assert package in packages, f"Safe package {package} should be allowed"


def test_npx_command_aliases(policies):
    """Test npx command aliases configuration"""
    if "npx" not in policies:
        pytest.skip("npx policy not present")

    pol = policies["npx"]
    command_aliases = pol.get("command_aliases", {})

    # Test typescript aliases
    assert "typescript" in command_aliases, "typescript should have command aliases"
    typescript_aliases = command_aliases["typescript"]
    assert "tsc" in typescript_aliases, "typescript should alias to tsc"


def test_npx_allowed_flags(policies):
    """Test npx allowed flags configuration"""
    if "npx" not in policies:
        pytest.skip("npx policy not present")

    pol = policies["npx"]
    flags = pol.get("flags", [])

    expected_flags = [
        "--yes", "-y", "--package", "-p", "--call", "-c", "--shell", "-s",
        "--shell-auto-fallback", "--ignore-existing", "--quiet", "-q",
        "--npm", "--node-options"
    ]
    for flag in expected_flags:
        assert flag in flags, f"npx should allow {flag} flag"


def test_npx_timeout_configuration(policies):
    """Test npx timeout configuration"""
    if "npx" not in policies:
        pytest.skip("npx policy not present")

    pol = policies["npx"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 120, "npx should have 120 second default timeout"


def test_npx_environment_security(policies):
    """Test npx environment security settings"""
    if "npx" not in policies:
        pytest.skip("npx policy not present")

    pol = policies["npx"]
    env_overrides = pol.get("env_overrides", {})

    # Test output control
    assert env_overrides.get("NPM_CONFIG_COLOR") == "false", "Should disable npm colors"
    assert env_overrides.get("NPM_CONFIG_PROGRESS") == "false", "Should disable progress bars"
    assert env_overrides.get("NO_COLOR") == "1", "Should set NO_COLOR"
    assert env_overrides.get("NODE_DISABLE_COLORS") == "1", "Should disable node colors"
    assert env_overrides.get("CI") == "1", "Should set CI mode"

    # Test security settings
    assert env_overrides.get("NPM_CONFIG_FUND") == "false", "Should disable funding messages"
    assert env_overrides.get("NPM_CONFIG_AUDIT") == "false", "Should disable audit"
    assert env_overrides.get("NPM_CONFIG_UPDATE_NOTIFIER") == "false", "Should disable update notifier"


def test_npx_security_model(policies):
    """Test npx security model - package whitelisting approach"""
    if "npx" not in policies:
        pytest.skip("npx policy not present")

    pol = policies["npx"]

    # npx uses package whitelisting instead of subcommand restrictions
    assert "packages" in pol, "npx should use package whitelisting"
    assert "subcommands" not in pol, "npx should not use subcommand model"
    assert "deny_subcommands" not in pol, "npx should not use deny_subcommands"

    # Ensure the whitelist is not empty
    packages = pol.get("packages", {})
    assert len(packages) > 0, "npx should have at least some allowed packages"
