import pytest


def test_pytest_policy_exists(policies):
    """Test that pytest policy exists and has correct structure"""
    if "pytest" not in policies:
        pytest.skip("pytest policy not present")

    pol = policies["pytest"]

    # pytest does not have an explicit validator in the YAML
    assert "validator" not in pol, "pytest should not have explicit validator (uses default)"


def test_pytest_core_structure(policies):
    """Test that pytest has proper core structure"""
    if "pytest" not in policies:
        pytest.skip("pytest policy not present")

    pol = policies["pytest"]

    # Core structure
    assert isinstance(pol.get("flags", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)
    assert isinstance(pol.get("env_overrides", {}), dict)


def test_pytest_allowed_flags(policies):
    """Test pytest allowed flags configuration"""
    if "pytest" not in policies:
        pytest.skip("pytest policy not present")

    pol = policies["pytest"]
    flags = pol.get("flags", [])

    expected_flags = ["-q", "--maxfail", "--disable-warnings", "--color"]
    for flag in expected_flags:
        assert flag in flags, f"pytest should allow {flag} flag"


def test_pytest_timeout_configuration(policies):
    """Test pytest timeout configuration"""
    if "pytest" not in policies:
        pytest.skip("pytest policy not present")

    pol = policies["pytest"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 120, "pytest should have 120 second default timeout"


def test_pytest_environment_security(policies):
    """Test pytest environment security settings"""
    if "pytest" not in policies:
        pytest.skip("pytest policy not present")

    pol = policies["pytest"]
    env_overrides = pol.get("env_overrides", {})

    # Test Python security settings
    assert env_overrides.get("PYTHONDONTWRITEBYTECODE") == "1", "Should prevent bytecode generation"

    # Test pytest-specific settings
    assert env_overrides.get("PYTEST_ADDOPTS") == "-q --color=no --maxfail=1", "Should set quiet mode with no color"
    assert env_overrides.get("PYTEST_DISABLE_PLUGIN_AUTOLOAD") == "1", "Should disable plugin autoload"

    # Test warning suppression
    assert env_overrides.get("PYTHONWARNINGS") == "ignore", "Should ignore Python warnings"


def test_pytest_security_compliance(policies):
    """Test pytest security compliance"""
    if "pytest" not in policies:
        pytest.skip("pytest policy not present")

    pol = policies["pytest"]

    # pytest should focus on safe test execution
    flags = pol.get("flags", [])

    # Should include safety flags
    assert "-q" in flags, "Should include quiet flag for minimal output"
    assert "--disable-warnings" in flags, "Should allow disabling warnings"
    assert "--maxfail" in flags, "Should allow limiting failure count"

    # Environment should be configured for security
    env_overrides = pol.get("env_overrides", {})
    assert "PYTHONDONTWRITEBYTECODE" in env_overrides, "Should prevent bytecode writing"
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD" in env_overrides, "Should disable automatic plugin loading"
