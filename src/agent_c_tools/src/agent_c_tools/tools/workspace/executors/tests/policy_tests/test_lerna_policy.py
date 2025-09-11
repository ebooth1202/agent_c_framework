import pytest


def test_lerna_policy_exists(policies):
    """Test that lerna policy exists and has correct structure"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]

    # Lerna has an explicit validator in the YAML (different from what the old test assumed)
    assert pol.get("validator") == "lerna", "lerna should use lerna validator"


def test_lerna_core_structure(policies):
    """Test that lerna has proper core structure"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]

    # Lerna-specific structure
    assert isinstance(pol.get("flags", []), list)
    assert isinstance(pol.get("subcommands", {}), dict)
    assert isinstance(pol.get("deny_subcommands", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)
    assert isinstance(pol.get("env_overrides", {}), dict)


def test_lerna_global_flags(policies):
    """Test lerna global flags configuration"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]
    flags = pol.get("flags", [])

    expected_flags = [
        "--version", "-v", "--help", "-h", "--loglevel", "--concurrency",
        "--scope", "--ignore", "--include-dependencies", "--include-dependents", "--since"
    ]
    for flag in expected_flags:
        assert flag in flags, f"lerna should allow global flag {flag}"


def test_lerna_information_subcommands(policies):
    """Test lerna information gathering subcommands"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]
    subs = pol.get("subcommands", {})

    # Test safe information commands
    info_commands = ["list", "info", "ls", "changed", "diff"]
    for cmd in info_commands:
        assert cmd in subs, f"Info command {cmd} should be present"
        assert "flags" in subs[cmd], f"{cmd} should have flags configuration"
        assert "timeout" in subs[cmd], f"{cmd} should have timeout configuration"


def test_lerna_build_maintenance_subcommands(policies):
    """Test lerna build and maintenance subcommands"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]
    subs = pol.get("subcommands", {})

    # Test build/maintenance commands
    build_commands = ["bootstrap", "clean", "run", "version"]
    for cmd in build_commands:
        assert cmd in subs, f"Build command {cmd} should be present"
        assert "flags" in subs[cmd], f"{cmd} should have flags configuration"
        assert "timeout" in subs[cmd], f"{cmd} should have timeout configuration"


def test_lerna_specific_subcommand_configs(policies):
    """Test specific lerna subcommand configurations"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]
    subs = pol.get("subcommands", {})

    # Test bootstrap command
    if "bootstrap" in subs:
        bootstrap_config = subs["bootstrap"]
        expected_flags = ["--hoist", "--strict", "--nohoist", "--ignore-scripts", "--ignore-prepublish", "--ignore-engines", "--npm-client", "--use-workspaces"]
        bootstrap_flags = bootstrap_config.get("flags", [])
        for flag in expected_flags:
            assert flag in bootstrap_flags, f"bootstrap should allow {flag} flag"
        assert bootstrap_config.get("timeout") == 300, "bootstrap should have 300 second timeout"

    # Test version command
    if "version" in subs:
        version_config = subs["version"]
        version_flags = version_config.get("flags", [])
        assert "--conventional-commits" in version_flags, "version should allow --conventional-commits"
        assert "--dry-run" in version_flags, "version should allow --dry-run"
        assert version_config.get("timeout") == 120, "version should have 120 second timeout"


def test_lerna_script_allowlist(policies):
    """Test lerna script allowlist configuration"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]
    subs = pol.get("subcommands", {})

    if "run" in subs:
        run_settings = subs["run"]
        allowed_scripts = run_settings.get("allowed_scripts", [])
        expected_scripts = ["build", "test", "lint", "format", "typecheck", "lint:fix", "test:run"]
        for script in expected_scripts:
            assert script in allowed_scripts, f"Safe script {script} should be allowed"
        assert run_settings.get("deny_args") is False, "lerna run should allow script arguments"
        assert run_settings.get("timeout") == 300, "lerna run should have 300 second timeout"


def test_lerna_denied_commands(policies):
    """Test that dangerous lerna commands are properly denied"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]
    denied_commands = pol.get("deny_subcommands", [])

    dangerous_commands = ["publish", "exec", "import", "create", "add", "link"]
    for cmd in dangerous_commands:
        assert cmd in denied_commands, f"Dangerous command {cmd} should be denied"


def test_lerna_timeout_configuration(policies):
    """Test lerna timeout configuration"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 180, "lerna should have 180 second default timeout"


def test_lerna_environment_security(policies):
    """Test lerna environment security settings"""
    if "lerna" not in policies:
        pytest.skip("lerna policy not present")

    pol = policies["lerna"]
    env_overrides = pol.get("env_overrides", {})

    # Lerna-specific environment settings
    assert env_overrides.get("LERNA_DISABLE_PROGRESS") == "1", "lerna should disable progress"
    assert env_overrides.get("NPM_CONFIG_COLOR") == "false", "lerna should disable npm colors"
    assert env_overrides.get("NPM_CONFIG_PROGRESS") == "false", "lerna should disable npm progress"
    assert env_overrides.get("NO_COLOR") == "1", "lerna should set NO_COLOR"
    assert env_overrides.get("FORCE_COLOR") == "0", "lerna should force no color"
    assert env_overrides.get("NODE_DISABLE_COLORS") == "1", "lerna should disable node colors"
    assert env_overrides.get("CI") == "1", "lerna should set CI mode"
