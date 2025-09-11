import pytest


def test_git_policy_exists(policies):
    """Test that git policy exists and has correct structure"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    assert pol.get("description") == "Read-only/metadata git operations (no mutations).", "Git policy should describe read-only operations"
    assert "subcommands" in pol and isinstance(pol["subcommands"], dict)
    assert "deny_global_flags" in pol and isinstance(pol["deny_global_flags"], list)
    assert "safe_env" in pol and isinstance(pol["safe_env"], dict)
    assert "env_overrides" in pol and isinstance(pol["env_overrides"], dict)


def test_git_read_only_subcommands(policies):
    """Test that read-only git subcommands are properly configured"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    subs = pol.get("subcommands", {})

    # Test read-only information gathering commands
    read_only_commands = {
        "status": ["--porcelain", "-s", "-b", "--no-color"],
        "log": ["--oneline", "--graph", "--decorate", "-n", "-p", "--no-color"],
        "show": ["--name-only", "--stat", "-p", "--no-color"],
        "diff": ["--name-only", "--stat", "--cached", "-p", "--no-color"],
        "rev-parse": ["--abbrev-ref", "--short", "HEAD", "--verify"],
        "ls-files": ["--exclude-standard", "--others", "--cached"]
    }

    for cmd, expected_flags in read_only_commands.items():
        assert cmd in subs, f"Read-only command {cmd} should be present"
        cmd_config = subs[cmd]
        assert "flags" in cmd_config, f"{cmd} should have flags configuration"
        cmd_flags = cmd_config["flags"]
        for flag in expected_flags:
            assert flag in cmd_flags, f"{cmd} should allow flag {flag}"


def test_git_state_modifying_subcommands(policies):
    """Test that state-modifying git subcommands are configured with appropriate restrictions"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    subs = pol.get("subcommands", {})

    # Test commands that modify state but are allowed with restrictions
    state_commands = {
        "add": [],
        "restore": ["--staged"],
        "reset": ["--hard", "--soft", "--mixed"],
        "checkout": ["-b", "--"],
        "switch": ["-c", "-"],  # switch -c (create branch), not git -c
        "branch": ["-a", "-vv", "-d", "-D"],
        "stash": ["list", "push", "pop", "apply", "drop", "clear"],
        "commit": ["-m", "--amend", "--no-verify"]
    }

    for cmd, expected_flags in state_commands.items():
        assert cmd in subs, f"State command {cmd} should be present"
        cmd_config = subs[cmd]
        assert "flags" in cmd_config, f"{cmd} should have flags configuration"
        cmd_flags = cmd_config["flags"]
        for flag in expected_flags:
            assert flag in cmd_flags, f"{cmd} should allow flag {flag}"


def test_git_timeout_configuration(policies):
    """Test that git commands have appropriate timeouts"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    subs = pol.get("subcommands", {})
    default_timeout = pol.get("default_timeout")

    assert default_timeout == 30, "Git should have 30 second default timeout"

    # Test specific timeout for status command
    if "status" in subs:
        status_config = subs["status"]
        assert status_config.get("timeout") == 20, "Git status should have 20 second timeout"


def test_git_denied_global_flags(policies):
    """Test that dangerous global flags are properly denied"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    denied_flags = pol.get("deny_global_flags", [])

    # Test that dangerous global flags are denied
    dangerous_flags = ["-c", "--exec-path", "--help", "-P"]
    for flag in dangerous_flags:
        assert flag in denied_flags, f"Dangerous global flag {flag} should be denied"


def test_git_security_environment(policies):
    """Test that git security environment variables are properly configured"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    safe_env = pol.get("safe_env", {})

    # Test critical security settings
    assert safe_env.get("GIT_TERMINAL_PROMPT") == "0", "Should disable git terminal prompts"
    assert safe_env.get("GIT_CONFIG_NOSYSTEM") == "1", "Should disable system git config"
    assert safe_env.get("GIT_CONFIG_GLOBAL") == "/dev/null", "Should disable global git config"
    assert safe_env.get("GIT_ALLOW_PROTOCOL") == "https,file", "Should only allow https and file protocols"


def test_git_output_environment(policies):
    """Test that git output environment variables are configured for security"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    env_overrides = pol.get("env_overrides", {})

    # Test output formatting for security
    assert env_overrides.get("GIT_PAGER") == "cat", "Should use cat as pager to avoid escape codes"
    assert env_overrides.get("CLICOLOR") == "0", "Should disable colorization"
    assert env_overrides.get("TERM") == "dumb", "Should use dumb terminal to discourage color/TTY tricks"


def test_git_no_color_flags(policies):
    """Test that git commands consistently use --no-color flag"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    subs = pol.get("subcommands", {})

    # Commands that support color output should have --no-color flag
    color_commands = ["status", "log", "show", "diff"]

    for cmd in color_commands:
        if cmd in subs:
            cmd_flags = subs[cmd].get("flags", [])
            assert "--no-color" in cmd_flags, f"{cmd} should include --no-color flag for consistent output"


def test_git_policy_security_compliance(policies):
    """Test overall git policy security compliance"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]

    # Test that the policy focuses on read-only and safe operations
    description = pol.get("description", "")
    assert "read-only" in description.lower(), "Policy should emphasize read-only operations"
    assert "no mutations" in description.lower(), "Policy should explicitly mention no mutations"

    # Test that dangerous commands are not present in subcommands
    subs = pol.get("subcommands", {})
    dangerous_commands = ["push", "pull", "fetch", "clone", "remote", "config", "merge", "rebase"]

    for dangerous_cmd in dangerous_commands:
        assert dangerous_cmd not in subs, f"Dangerous command {dangerous_cmd} should not be in allowed subcommands"


def test_git_stash_operations(policies):
    """Test that git stash operations are properly configured"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    subs = pol.get("subcommands", {})

    if "stash" in subs:
        stash_flags = subs["stash"].get("flags", [])
        expected_stash_ops = ["list", "push", "pop", "apply", "drop", "clear"]

        for op in expected_stash_ops:
            assert op in stash_flags, f"Stash should allow {op} operation"


def test_git_branch_operations(policies):
    """Test that git branch operations are properly restricted"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    subs = pol.get("subcommands", {})

    if "branch" in subs:
        branch_flags = subs["branch"].get("flags", [])
        expected_branch_flags = ["-a", "-vv", "-d", "-D"]

        for flag in expected_branch_flags:
            assert flag in branch_flags, f"Branch should allow {flag} flag"

        # Test that dangerous branch operations are not allowed
        dangerous_branch_flags = ["-m", "-M", "--set-upstream-to", "-u"]
        for flag in dangerous_branch_flags:
            assert flag not in branch_flags, f"Branch should not allow dangerous flag {flag}"


def test_git_commit_restrictions(policies):
    """Test that git commit operations have appropriate restrictions"""
    if "git" not in policies:
        pytest.skip("git policy not present")

    pol = policies["git"]
    subs = pol.get("subcommands", {})

    if "commit" in subs:
        commit_flags = subs["commit"].get("flags", [])
        expected_commit_flags = ["-m", "--amend", "--no-verify"]

        for flag in expected_commit_flags:
            assert flag in commit_flags, f"Commit should allow {flag} flag"

        # Test that interactive/dangerous commit operations are not allowed
        dangerous_commit_flags = ["--interactive", "-i", "--patch", "-p", "--all", "-a"]
        for flag in dangerous_commit_flags:
            assert flag not in commit_flags, f"Commit should not allow dangerous flag {flag}"
