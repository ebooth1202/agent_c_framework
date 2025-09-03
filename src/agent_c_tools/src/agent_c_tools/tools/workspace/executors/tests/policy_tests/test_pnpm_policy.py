import pytest


def test_pnpm_policy_exists(policies):
    """Test that pnpm policy exists and has correct validator"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]
    assert pol.get("validator") == "pnpm", "pnpm should use pnpm validator"


def test_pnpm_core_structure(policies):
    """Test that pnpm has proper core structure"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]

    # Core structure
    assert isinstance(pol.get("root_flags", []), list)
    assert isinstance(pol.get("subcommands", {}), dict)
    assert isinstance(pol.get("deny_subcommands", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)
    assert isinstance(pol.get("env_overrides", {}), dict)


def test_pnpm_root_flags(policies):
    """Test pnpm root flags configuration"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]
    root_flags = pol.get("root_flags", [])

    expected_flags = ["-v", "--version", "--help"]
    for flag in expected_flags:
        assert flag in root_flags, f"pnpm should allow root flag {flag}"


def test_pnpm_safe_subcommands(policies):
    """Test pnpm safe subcommands configuration"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]
    subs = pol.get("subcommands", {})

    # Test safe subcommands (pnpm has more than npm)
    safe_commands = ["view", "list", "ping", "outdated", "test", "type_check", "ls", "build", "why", "licenses", "lint"]
    for cmd in safe_commands:
        assert cmd in subs, f"Safe command {cmd} should be present"
        assert "allowed_flags" in subs[cmd], f"{cmd} should have allowed_flags"


def test_pnpm_config_restrictions(policies):
    """Test pnpm config security restrictions"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]
    subs = pol.get("subcommands", {})

    if "config" in subs:
        config_settings = subs["config"]
        assert config_settings.get("get_only") is True, "pnpm config should only allow get operations"
        assert config_settings.get("allowed_flags") == [], "pnpm config should have no additional flags"


def test_pnpm_script_allowlist(policies):
    """Test pnpm script allowlist configuration"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]
    subs = pol.get("subcommands", {})

    if "run" in subs:
        run_settings = subs["run"]
        allowed_scripts = run_settings.get("allowed_scripts", [])
        expected_scripts = ["build", "test", "lint", "lint:fix", "format", "typecheck", "test:run"]
        for script in expected_scripts:
            assert script in allowed_scripts, f"Safe script {script} should be allowed"
        assert run_settings.get("deny_args") is False, "pnpm run should allow script arguments with path validation"
        assert run_settings.get("allow_test_paths") is True, "pnpm run should enable workspace-relative test paths"


def test_pnpm_install_security(policies):
    """Test pnpm install security restrictions"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]
    subs = pol.get("subcommands", {})

    # Test pnpm install (enabled but restricted)
    if "install" in subs:
        install_settings = subs["install"]
        assert install_settings.get("enabled") is True, "pnpm install should be enabled"
        assert install_settings.get("require_no_packages") is True, "pnpm install should require no package arguments"

        required_flags = install_settings.get("require_flags", [])
        assert "--ignore-scripts" in required_flags, "pnpm install should require --ignore-scripts"

        allowed_flags = install_settings.get("allowed_flags", [])
        expected_flags = ["--ignore-scripts", "--prefer-offline", "--frozen-lockfile", "--reporter", "--dev", "--prod"]
        for flag in expected_flags:
            assert flag in allowed_flags, f"pnpm install should allow {flag}"


def test_pnpm_denied_commands(policies):
    """Test that dangerous pnpm commands are properly denied"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]
    denied_commands = pol.get("deny_subcommands", [])

    dangerous_commands = ["exec", "publish", "update", "audit", "login", "adduser", "whoami", "pack", "link", "unlink", "patch", "patch-commit"]
    for cmd in dangerous_commands:
        assert cmd in denied_commands, f"Dangerous command {cmd} should be denied"


def test_pnpm_timeout_configuration(policies):
    """Test pnpm timeout configuration"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 120, "pnpm should have 120 second default timeout"


def test_pnpm_environment_security(policies):
    """Test pnpm environment security settings"""
    if "pnpm" not in policies:
        pytest.skip("pnpm policy not present")

    pol = policies["pnpm"]
    env_overrides = pol.get("env_overrides", {})

    # Test output control
    assert env_overrides.get("PNPM_CONFIG_COLOR") == "false", "Should disable pnpm colors"
    assert env_overrides.get("PNPM_CONFIG_PROGRESS") == "false", "Should disable progress bars"
    assert env_overrides.get("NO_COLOR") == "1", "Should set NO_COLOR"
    assert env_overrides.get("FORCE_COLOR") == "0", "Should force no color"
    assert env_overrides.get("NODE_DISABLE_COLORS") == "1", "Should disable node colors"
    assert env_overrides.get("CI") == "1", "Should set CI mode"

    # Test security settings
    assert env_overrides.get("PNPM_CONFIG_FUND") == "false", "Should disable funding messages"
    assert env_overrides.get("PNPM_CONFIG_UPDATE_NOTIFIER") == "false", "Should disable update notifier"

    # Test Windows compatibility
    assert env_overrides.get("PATHEXT") == ".COM;.EXE;.BAT;.CMD", "Should set Windows PATHEXT"
