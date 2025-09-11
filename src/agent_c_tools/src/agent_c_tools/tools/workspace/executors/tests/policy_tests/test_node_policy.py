import pytest


def test_node_policy_exists(policies):
    """Test that node policy exists and has correct validator"""
    if "node" not in policies:
        pytest.skip("node policy not present")

    pol = policies["node"]
    assert pol.get("validator") == "node", "node should use node validator"


def test_node_core_structure(policies):
    """Test that node has proper core structure"""
    if "node" not in policies:
        pytest.skip("node policy not present")

    pol = policies["node"]

    # Core structure - flags can be either list or dict
    flags = pol.get("flags", [])
    assert isinstance(flags, (list, dict)), "flags should be list or dict"
    assert isinstance(pol.get("deny_global_flags", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)
    assert isinstance(pol.get("env_overrides", {}), dict)


def test_node_allowed_flags(policies):
    """Test node allowed flags configuration"""
    if "node" not in policies:
        pytest.skip("node policy not present")

    pol = policies["node"]
    flags = pol.get("flags", [])

    # Handle both list and dict formats
    if isinstance(flags, dict):
        flag_names = set(flags.keys())
    else:
        flag_names = set(flags)

    expected_flags = {"-v", "--version", "--help", "-c"}
    for flag in expected_flags:
        assert flag in flag_names, f"node should allow {flag} flag"


def test_node_test_flags(policies):
    """Test node test-related flags configuration"""
    if "node" not in policies:
        pytest.skip("node policy not present")

    pol = policies["node"]
    flags = pol.get("flags", [])

    # Handle both list and dict formats
    if isinstance(flags, dict):
        flag_names = set(flags.keys())
        # Test --test flag has proper configuration
        test_flag_config = flags.get("--test", {})
        assert test_flag_config.get("suppress_success_output", False), "--test should suppress success output"
        assert test_flag_config.get("allow_test_mode", False), "--test should allow test mode"
    else:
        flag_names = set(flags)

    test_flags = {"--test", "--test-reporter", "--test-name-pattern"}
    for flag in test_flags:
        assert flag in flag_names, f"node should allow {flag} flag"


def test_node_suppress_success_output(policies):
    """Test node suppress_success_output flag configuration"""
    if "node" not in policies:
        pytest.skip("node policy not present")

    pol = policies["node"]
    flags = pol.get("flags", [])

    # Only test if flags are in dict format
    if isinstance(flags, dict):
        suppress_flags = [flag for flag, config in flags.items() 
                         if config.get("suppress_success_output", False)]
        
        # Test that some flags have suppress_success_output enabled
        expected_suppress_flags = {"--test", "-c", "--test-reporter", "--test-name-pattern"}
        found_suppress_flags = set(suppress_flags)
        
        for flag in expected_suppress_flags:
            if flag in flags:
                assert flag in found_suppress_flags, f"{flag} should have suppress_success_output enabled"


def test_node_denied_flags(policies):
    """Test that dangerous node flags are properly denied"""
    if "node" not in policies:
        pytest.skip("node policy not present")

    pol = policies["node"]
    denied_flags = pol.get("deny_global_flags", [])

    dangerous_flags = ["-e", "--eval", "-p", "--print"]
    for flag in dangerous_flags:
        assert flag in denied_flags, f"Dangerous flag {flag} should be denied"


def test_node_timeout_configuration(policies):
    """Test node timeout configuration"""
    if "node" not in policies:
        pytest.skip("node policy not present")

    pol = policies["node"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 5, "node should have 5 second default timeout"


def test_node_environment_security(policies):
    """Test node environment security settings"""
    if "node" not in policies:
        pytest.skip("node policy not present")

    pol = policies["node"]
    env_overrides = pol.get("env_overrides", {})

    # Test output control
    assert env_overrides.get("NODE_DISABLE_COLORS") == "1", "Should disable node colors"
    assert env_overrides.get("NO_COLOR") == "1", "Should set NO_COLOR"
    assert env_overrides.get("FORCE_COLOR") == "0", "Should force no color"


def test_nodejs_policy_exists(policies):
    """Test that nodejs policy exists and has correct validator"""
    if "nodejs" not in policies:
        pytest.skip("nodejs policy not present")

    pol = policies["nodejs"]
    assert pol.get("validator") == "node", "nodejs should use node validator"


def test_nodejs_core_structure(policies):
    """Test that nodejs has proper core structure"""
    if "nodejs" not in policies:
        pytest.skip("nodejs policy not present")

    pol = policies["nodejs"]

    # Core structure - flags can be either list or dict
    flags = pol.get("flags", [])
    assert isinstance(flags, (list, dict)), "flags should be list or dict"
    assert isinstance(pol.get("deny_global_flags", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)
    assert isinstance(pol.get("env_overrides", {}), dict)


def test_nodejs_allowed_flags(policies):
    """Test nodejs allowed flags configuration"""
    if "nodejs" not in policies:
        pytest.skip("nodejs policy not present")

    pol = policies["nodejs"]
    flags = pol.get("flags", [])

    # Handle both list and dict formats
    if isinstance(flags, dict):
        flag_names = set(flags.keys())
    else:
        flag_names = set(flags)

    expected_flags = {"-v", "--version", "--help"}
    for flag in expected_flags:
        assert flag in flag_names, f"nodejs should allow {flag} flag"


def test_nodejs_denied_flags(policies):
    """Test that dangerous nodejs flags are properly denied"""
    if "nodejs" not in policies:
        pytest.skip("nodejs policy not present")

    pol = policies["nodejs"]
    denied_flags = pol.get("deny_global_flags", [])

    dangerous_flags = ["-e", "--eval", "-p", "--print"]
    for flag in dangerous_flags:
        assert flag in denied_flags, f"Dangerous flag {flag} should be denied"


def test_nodejs_timeout_configuration(policies):
    """Test nodejs timeout configuration"""
    if "nodejs" not in policies:
        pytest.skip("nodejs policy not present")

    pol = policies["nodejs"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 5, "nodejs should have 5 second default timeout"


def test_nodejs_environment_security(policies):
    """Test nodejs environment security settings"""
    if "nodejs" not in policies:
        pytest.skip("nodejs policy not present")

    pol = policies["nodejs"]
    env_overrides = pol.get("env_overrides", {})

    # Test output control
    assert env_overrides.get("NODE_DISABLE_COLORS") == "1", "Should disable node colors"
    assert env_overrides.get("NO_COLOR") == "1", "Should set NO_COLOR"
    assert env_overrides.get("FORCE_COLOR") == "0", "Should force no color"
