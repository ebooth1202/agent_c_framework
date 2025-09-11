import pytest


def test_dotnet_core_policy_exists(policies):
    """Test that dotnet policy exists and has correct validator"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]
    assert pol.get("validator") == "dotnet", "dotnet policy should use dotnet validator"


def test_dotnet_information_subcommands(policies):
    """Test that safe information gathering subcommands are present"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]
    subs = pol.get("subcommands", {})

    # Test information gathering commands
    info_commands = ["--info", "--list-sdks", "--list-runtimes"]
    for cmd in info_commands:
        assert cmd in subs, f"Expected read-only subcommand {cmd} to be present"
        # These should have no flags or minimal flags only
        cmd_config = subs[cmd]
        assert isinstance(cmd_config, dict), f"{cmd} should have configuration"
        assert "flags" in cmd_config, f"{cmd} should have flags configuration"


def test_dotnet_restore_security(policies):
    """Test that dotnet restore has proper security restrictions"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]
    subs = pol.get("subcommands", {})

    assert "restore" in subs, "restore subcommand should be present"
    restore_config = subs["restore"]

    # Test allowed flags
    allowed_flags = restore_config.get("flags", [])
    expected_flags = ["--locked-mode", "--configfile", "--source", "--verbosity", "-v", "--nologo"]
    for flag in expected_flags:
        assert flag in allowed_flags, f"restore should allow {flag} flag"

    # Test required flags for security
    require_flags = restore_config.get("require_flags", {})
    assert require_flags.get("--locked-mode") is True, "restore should require --locked-mode for security"
    assert require_flags.get("--nologo") is True, "restore should require --nologo"

    # Test verbosity restrictions
    verbosity_options = require_flags.get("--verbosity", [])
    assert "quiet" in verbosity_options, "restore should support quiet verbosity"
    assert "minimal" in verbosity_options, "restore should support minimal verbosity"


def test_dotnet_build_security(policies):
    """Test that dotnet build has proper security restrictions"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]
    subs = pol.get("subcommands", {})

    assert "build" in subs, "build subcommand should be present"
    build_config = subs["build"]

    # Test allowed flags
    allowed_flags = build_config.get("flags", [])
    expected_flags = ["--configuration", "-c", "--no-restore", "--nologo", "--verbosity", "-v"]
    for flag in expected_flags:
        assert flag in allowed_flags, f"build should allow {flag} flag"

    # Test required flags for security
    require_flags = build_config.get("require_flags", {})
    assert require_flags.get("--nologo") is True, "build should require --nologo"

    # Test verbosity restrictions
    verbosity_options = require_flags.get("--verbosity", [])
    assert "quiet" in verbosity_options, "build should support quiet verbosity"
    assert "minimal" in verbosity_options, "build should support minimal verbosity"


def test_dotnet_test_security(policies):
    """Test that dotnet test has proper security restrictions"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]
    subs = pol.get("subcommands", {})

    assert "test" in subs, "test subcommand should be present"
    test_config = subs["test"]

    # Test allowed flags
    allowed_flags = test_config.get("flags", [])
    expected_flags = ["--configuration", "-c", "--no-build", "--nologo", "--verbosity", "-v", "--filter"]
    for flag in expected_flags:
        assert flag in allowed_flags, f"test should allow {flag} flag"

    # Test required flags for security
    require_flags = test_config.get("require_flags", {})
    assert require_flags.get("--no-build") is True, "test should require --no-build for security"
    assert require_flags.get("--nologo") is True, "test should require --nologo"

    # Test verbosity restrictions
    verbosity_options = require_flags.get("--verbosity", [])
    assert "minimal" in verbosity_options, "test should support minimal verbosity"
    assert "quiet" in verbosity_options, "test should support quiet verbosity"

    # Test logger requirement
    logger_config = require_flags.get("--logger")
    assert logger_config == "console;verbosity=minimal", "test should require minimal console logger"


def test_dotnet_denied_subcommands(policies):
    """Test that dangerous subcommands are properly denied"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]
    denied_subs = pol.get("deny_subcommands", [])

    # Test that dangerous commands are denied
    dangerous_commands = ["run", "publish", "tool", "new", "pack", "clean", "nuget", "workload"]
    for cmd in dangerous_commands:
        assert cmd in denied_subs, f"Dangerous subcommand {cmd} should be denied"


def test_dotnet_timeout_configuration(policies):
    """Test that appropriate timeouts are configured"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]
    default_timeout = pol.get("default_timeout")

    assert default_timeout == 300, "dotnet should have 300 second default timeout for build operations"


def test_dotnet_environment_security(policies):
    """Test that security-focused environment variables are set"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]
    env_overrides = pol.get("env_overrides", {})

    # Test telemetry and privacy settings
    assert env_overrides.get("DOTNET_CLI_TELEMETRY_OPTOUT") == "1", "Should opt out of telemetry"
    assert env_overrides.get("DOTNET_SKIP_FIRST_TIME_EXPERIENCE") == "1", "Should skip first time experience"
    assert env_overrides.get("DOTNET_NOLOGO") == "1", "Should disable logo"

    # Test package management security
    assert env_overrides.get("NUGET_PACKAGES") == ".nuget/packages", "Should use local package cache"

    # Test output formatting for security
    assert env_overrides.get("CLICOLOR") == "0", "Should disable colors"
    assert env_overrides.get("NO_COLOR") == "1", "Should set NO_COLOR"
    assert env_overrides.get("TERM") == "dumb", "Should use dumb terminal"

    # Test language consistency
    assert env_overrides.get("DOTNET_CLI_UI_LANGUAGE") == "en-US", "Should use English for consistent output"


def test_dotnet_policy_structure(policies):
    """Test overall policy structure and required fields"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]

    # Test required top-level fields
    assert "validator" in pol, "dotnet policy should specify validator"
    assert "subcommands" in pol, "dotnet policy should have subcommands"
    assert "deny_subcommands" in pol, "dotnet policy should have deny_subcommands"
    assert "default_timeout" in pol, "dotnet policy should have default_timeout"
    assert "env_overrides" in pol, "dotnet policy should have env_overrides"

    # Test subcommands structure
    subs = pol["subcommands"]
    assert isinstance(subs, dict), "subcommands should be a dictionary"

    # Each subcommand should have proper structure
    for sub_name, sub_config in subs.items():
        assert isinstance(sub_config, dict), f"subcommand {sub_name} should have dict configuration"
        assert "flags" in sub_config, f"subcommand {sub_name} should have flags"


def test_dotnet_security_compliance(policies):
    """Test that the policy meets security requirements"""
    if "dotnet" not in policies:
        pytest.skip("dotnet policy not present")

    pol = policies["dotnet"]

    # Test that no dangerous global flags are allowed at top level
    flags = pol.get("flags", [])
    dangerous_global_flags = ["--interactive", "-i", "--force"]
    for flag in dangerous_global_flags:
        assert flag not in flags, f"Dangerous global flag {flag} should not be allowed"

    # Test that subcommands have appropriate restrictions
    subs = pol.get("subcommands", {})

    # Commands that modify state should have restrictions
    if "restore" in subs:
        restore_flags = subs["restore"].get("require_flags", {})
        assert "--locked-mode" in restore_flags, "restore should require locked mode for security"

    if "build" in subs:
        build_flags = subs["build"].get("require_flags", {})
        assert "--nologo" in build_flags, "build should require nologo for consistent output"

    if "test" in subs:
        test_flags = subs["test"].get("require_flags", {})
        assert "--no-build" in test_flags, "test should require no-build for separation of concerns"
