import pytest

REQUIRED_KEYS_BY_POLICY = {
    # Minimal keys we expect per policy (not exhaustive, but catches config regressions)
    "powershell": ["validator", "flags", "deny_global_flags", "require_flags", "safe_cmdlets", "dangerous_patterns"],
    "pwsh":       ["validator", "flags", "deny_global_flags", "require_flags", "safe_cmdlets", "dangerous_patterns"],
    "git":        ["subcommands", "deny_global_flags", "env_overrides"],
    "npm":        ["validator", "root_flags", "subcommands", "default_timeout"],
    "pnpm":       ["validator", "root_flags", "subcommands", "default_timeout"],
    "npx":        ["validator", "flags", "packages", "default_timeout"],  # npx uses flags, not root_flags, and packages not subcommands
    "lerna":      ["flags", "subcommands", "default_timeout"],                   # lerna does NOT have explicit validator
    "dotnet":     ["validator", "subcommands", "default_timeout"],
    "pytest":     ["flags", "default_timeout", "env_overrides"],
    "which":      ["validator", "flags", "default_timeout"],
    "where":      ["validator", "flags", "default_timeout"],
    "whoami":     ["validator", "flags", "default_timeout"],
    "echo":       ["validator", "flags", "default_timeout"],
}

@pytest.mark.parametrize("name", list(REQUIRED_KEYS_BY_POLICY.keys()))
def test_policy_has_expected_keys(policies, name):
    if name not in policies:
        pytest.skip(f"Policy {name} not present in YAML")
    pol = policies[name]
    for key in REQUIRED_KEYS_BY_POLICY[name]:
        assert key in pol, f"Missing key '{key}' in policy '{name}'"

def test_yaml_is_parseable_and_nonempty(policies):
    assert policies, "Loaded policies should not be empty"
    assert isinstance(policies, dict)

def test_all_default_timeouts_reasonable(policies):
    for name, pol in policies.items():
        timeout = pol.get("default_timeout")
        if timeout is not None:
            assert isinstance(timeout, int), f"default_timeout for {name} must be int"
            assert 0 < timeout <= 1800, f"default_timeout for {name} seems unreasonable: {timeout}"
