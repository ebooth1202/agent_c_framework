import pytest


def test_npm_policy_exists(policies):
    """Test that npm policy exists and has correct validator"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]
    assert pol.get("validator") == "npm", "npm should use npm validator"


def test_npm_core_structure(policies):
    """Test that npm has proper core structure"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]

    # Core structure
    assert isinstance(pol.get("root_flags", []), list)
    assert isinstance(pol.get("subcommands", {}), dict)
    assert isinstance(pol.get("deny_subcommands", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)
    assert isinstance(pol.get("env_overrides", {}), dict)


def test_npm_root_flags(policies):
    """Test npm root flags configuration"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]
    root_flags = pol.get("root_flags", [])

    expected_flags = ["-v", "--version", "--help"]
    for flag in expected_flags:
        assert flag in root_flags, f"npm should allow root flag {flag}"


def test_npm_safe_subcommands(policies):
    """Test npm safe subcommands configuration"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]
    subs = pol.get("subcommands", {})

    # Test safe subcommands
    safe_commands = ["view", "list", "ping", "outdated", "test", "ls"]
    for cmd in safe_commands:
        assert cmd in subs, f"Safe command {cmd} should be present"
        assert "allowed_flags" in subs[cmd], f"{cmd} should have allowed_flags"


def test_npm_config_restrictions(policies):
    """Test npm config security restrictions"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]
    subs = pol.get("subcommands", {})

    if "config" in subs:
        config_settings = subs["config"]
        assert config_settings.get("get_only") is True, "npm config should only allow get operations"
        assert config_settings.get("allowed_flags") == [], "npm config should have no additional flags"


def test_npm_script_allowlist(policies):
    """Test npm script allowlist configuration"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]
    subs = pol.get("subcommands", {})

    if "run" in subs:
        run_settings = subs["run"]
        allowed_scripts = run_settings.get("allowed_scripts", [])
        
        # Check that allowed_scripts is properly configured as a list
        assert isinstance(allowed_scripts, list), "allowed_scripts should be a list"
        
        # If allowed_scripts is configured (non-empty), check that safe scripts are included
        if allowed_scripts:
            safe_scripts = ["test", "lint", "build"]  # Core safe scripts
            found_safe_scripts = [script for script in safe_scripts if script in allowed_scripts]
            assert len(found_safe_scripts) > 0, f"At least one safe script should be allowed. Found: {allowed_scripts}"
        
        # If deny_args is configured, it should be False to allow script arguments
        if "deny_args" in run_settings:
            assert run_settings.get("deny_args") is False, "npm run should allow script arguments when configured"


def test_npm_ci_install_security(policies):
    """Test npm ci and install security restrictions"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]
    subs = pol.get("subcommands", {})

    # Test npm ci (secure install)
    if "ci" in subs:
        ci_settings = subs["ci"]
        assert ci_settings.get("enabled") is True, "npm ci should be enabled"
        assert ci_settings.get("require_no_packages") is True, "npm ci should require no package arguments"

        required_flags = ci_settings.get("require_flags", [])
        assert "--ignore-scripts" in required_flags, "npm ci should require --ignore-scripts for security"

        allowed_flags = ci_settings.get("allowed_flags", [])
        expected_flags = ["--ignore-scripts", "--no-audit", "--no-fund", "--prefer-offline", "--cache"]
        for flag in expected_flags:
            assert flag in allowed_flags, f"npm ci should allow {flag}"

    # Test npm install (should be disabled)
    if "install" in subs:
        install_settings = subs["install"]
        assert install_settings.get("enabled") is False, "npm install should be disabled for security"


def test_npm_denied_commands(policies):
    """Test that dangerous npm commands are properly denied"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]
    denied_commands = pol.get("deny_subcommands", [])

    dangerous_commands = ["exec", "publish", "update", "audit", "ci-info", "token", "login", "adduser", "whoami", "pack", "link", "unlink"]
    for cmd in dangerous_commands:
        assert cmd in denied_commands, f"Dangerous command {cmd} should be denied"


def test_npm_timeout_configuration(policies):
    """Test npm timeout configuration"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 120, "npm should have 120 second default timeout"


def test_npm_environment_security(policies):
    """Test npm environment security settings"""
    if "npm" not in policies:
        pytest.skip("npm policy not present")

    pol = policies["npm"]
    env_overrides = pol.get("env_overrides", {})

    # Test output control
    assert env_overrides.get("NPM_CONFIG_COLOR") == "false", "Should disable npm colors"
    assert env_overrides.get("NPM_CONFIG_PROGRESS") == "false", "Should disable progress bars"
    assert env_overrides.get("NO_COLOR") == "1", "Should set NO_COLOR"
    assert env_overrides.get("FORCE_COLOR") == "0", "Should force no color"
    assert env_overrides.get("NODE_DISABLE_COLORS") == "1", "Should disable node colors"
    assert env_overrides.get("CI") == "1", "Should set CI mode"

    # Test security settings
    assert env_overrides.get("NPM_CONFIG_FUND") == "false", "Should disable funding messages"
    assert env_overrides.get("NPM_CONFIG_AUDIT") == "false", "Should disable audit"
    assert env_overrides.get("NPM_CONFIG_UPDATE_NOTIFIER") == "false", "Should disable update notifier"

    # Test local cache settings
    assert env_overrides.get("NPM_CONFIG_PREFIX") == ".npm-prefix", "Should use local prefix"
    assert env_overrides.get("NPM_CONFIG_CACHE") == ".npm-cache", "Should use local cache"

    # Test Windows compatibility
    assert env_overrides.get("PATHEXT") == ".COM;.EXE;.BAT;.CMD", "Should set Windows PATHEXT"
