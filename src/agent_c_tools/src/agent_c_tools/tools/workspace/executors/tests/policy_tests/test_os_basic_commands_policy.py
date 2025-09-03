import pytest


def test_which_policy_exists(policies):
    """Test that which policy exists and has correct validator"""
    if "which" not in policies:
        pytest.skip("which policy not present")

    pol = policies["which"]
    assert pol.get("validator") == "os_basic", "which should use os_basic validator"


def test_which_core_structure(policies):
    """Test that which has proper core structure"""
    if "which" not in policies:
        pytest.skip("which policy not present")

    pol = policies["which"]

    # Core structure
    assert isinstance(pol.get("flags", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)


def test_which_allowed_flags(policies):
    """Test which allowed flags configuration"""
    if "which" not in policies:
        pytest.skip("which policy not present")

    pol = policies["which"]
    flags = pol.get("flags", [])

    expected_flags = ["-a", "--version"]
    for flag in expected_flags:
        assert flag in flags, f"which should allow {flag} flag"


def test_which_timeout_configuration(policies):
    """Test which timeout configuration"""
    if "which" not in policies:
        pytest.skip("which policy not present")

    pol = policies["which"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 5, "which should have 5 second default timeout"


def test_where_policy_exists(policies):
    """Test that where policy exists and has correct validator"""
    if "where" not in policies:
        pytest.skip("where policy not present")

    pol = policies["where"]
    assert pol.get("validator") == "os_basic", "where should use os_basic validator"


def test_where_core_structure(policies):
    """Test that where has proper core structure"""
    if "where" not in policies:
        pytest.skip("where policy not present")

    pol = policies["where"]

    # Core structure
    assert isinstance(pol.get("flags", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)


def test_where_allowed_flags(policies):
    """Test where allowed flags configuration"""
    if "where" not in policies:
        pytest.skip("where policy not present")

    pol = policies["where"]
    flags = pol.get("flags", [])

    expected_flags = ["/r"]
    for flag in expected_flags:
        assert flag in flags, f"where should allow {flag} flag"


def test_where_timeout_configuration(policies):
    """Test where timeout configuration"""
    if "where" not in policies:
        pytest.skip("where policy not present")

    pol = policies["where"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 5, "where should have 5 second default timeout"


def test_whoami_policy_exists(policies):
    """Test that whoami policy exists and has correct validator"""
    if "whoami" not in policies:
        pytest.skip("whoami policy not present")

    pol = policies["whoami"]
    assert pol.get("validator") == "os_basic", "whoami should use os_basic validator"


def test_whoami_core_structure(policies):
    """Test that whoami has proper core structure"""
    if "whoami" not in policies:
        pytest.skip("whoami policy not present")

    pol = policies["whoami"]

    # Core structure
    assert isinstance(pol.get("flags", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)


def test_whoami_allowed_flags(policies):
    """Test whoami allowed flags configuration"""
    if "whoami" not in policies:
        pytest.skip("whoami policy not present")

    pol = policies["whoami"]
    flags = pol.get("flags", [])

    # whoami has empty flags list according to YAML
    assert flags == [], "whoami should have empty flags list"


def test_whoami_timeout_configuration(policies):
    """Test whoami timeout configuration"""
    if "whoami" not in policies:
        pytest.skip("whoami policy not present")

    pol = policies["whoami"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 5, "whoami should have 5 second default timeout"


def test_echo_policy_exists(policies):
    """Test that echo policy exists and has correct validator"""
    if "echo" not in policies:
        pytest.skip("echo policy not present")

    pol = policies["echo"]
    assert pol.get("validator") == "os_basic", "echo should use os_basic validator"


def test_echo_core_structure(policies):
    """Test that echo has proper core structure"""
    if "echo" not in policies:
        pytest.skip("echo policy not present")

    pol = policies["echo"]

    # Core structure
    assert isinstance(pol.get("flags", []), list)
    assert isinstance(pol.get("default_timeout", 0), int)


def test_echo_allowed_flags(policies):
    """Test echo allowed flags configuration"""
    if "echo" not in policies:
        pytest.skip("echo policy not present")

    pol = policies["echo"]
    flags = pol.get("flags", [])

    expected_flags = ["--help", "-n", "-e"]
    for flag in expected_flags:
        assert flag in flags, f"echo should allow {flag} flag"


def test_echo_timeout_configuration(policies):
    """Test echo timeout configuration"""
    if "echo" not in policies:
        pytest.skip("echo policy not present")

    pol = policies["echo"]
    default_timeout = pol.get("default_timeout")
    assert default_timeout == 5, "echo should have 5 second default timeout"


def test_os_basic_commands_security(policies):
    """Test that OS basic commands follow security principles"""
    os_basic_commands = ["which", "where", "whoami", "echo"]

    for cmd in os_basic_commands:
        if cmd not in policies:
            continue

        pol = policies[cmd]

        # All OS basic commands should have short timeouts
        timeout = pol.get("default_timeout", 0)
        assert timeout <= 5, f"{cmd} should have short timeout (<=5s) for safety"

        # Should use os_basic validator
        assert pol.get("validator") == "os_basic", f"{cmd} should use os_basic validator"

        # Should have minimal flags
        flags = pol.get("flags", [])
        assert len(flags) <= 5, f"{cmd} should have minimal flags for security"
