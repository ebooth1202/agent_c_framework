
import pytest

PS_NAMES = ["powershell", "pwsh"]

@pytest.mark.parametrize("policy_name", PS_NAMES)
def test_ps_policy_core(policies, policy_name):
    if policy_name not in policies:
        pytest.skip(f"Policy {policy_name} not defined")
    pol = policies[policy_name]
    assert pol.get("validator") == "powershell", "Both powershell and pwsh should use 'powershell' validator"
    # Required security posture
    assert "-NoProfile" in pol.get("require_flags", [])
    assert "-NonInteractive" in pol.get("require_flags", [])

# --- Validator behavior (runs only if we can import the validator class) ---
@pytest.mark.parametrize("policy_for,validator_for", [(n,n) for n in PS_NAMES], indirect=True)
def test_ps_denied_flags_blocked(policy_for, validator_for):
    if validator_for is None:
        pytest.skip("PowershellValidator not importable in this environment")
    parts_base = ["powershell.exe"]
    for flag in ["-Command", "-c", "-EncodedCommand", "-enc", "-File", "-f", "-ExecutionPolicy", "-ep", "-ex"]:
        res = validator_for.validate(parts_base + [flag, "Get-Process"], policy_for)
        assert not res.allowed, f"{flag} should be denied, got allowed"

@pytest.mark.parametrize("policy_for,validator_for", [(n,n) for n in PS_NAMES], indirect=True)
def test_ps_require_flags_enforced(policy_for, validator_for):
    if validator_for is None:
        pytest.skip("PowershellValidator not importable in this environment")
    parts = ["powershell.exe", "-NoProfile", "Get-Process"]
    res = validator_for.validate(parts, policy_for)
    assert not res.allowed, "Missing -NonInteractive should block"

    parts2 = ["powershell.exe", "-NonInteractive", "Get-Process"]
    res2 = validator_for.validate(parts2, policy_for)
    assert not res2.allowed, "Missing -NoProfile should block"

@pytest.mark.parametrize("policy_for,validator_for", [(n,n) for n in PS_NAMES], indirect=True)
def test_ps_safe_cmdlets_allowed(policy_for, validator_for):
    if validator_for is None:
        pytest.skip("PowershellValidator not importable in this environment")
    parts = ["powershell.exe", "-NoProfile", "-NonInteractive", "Get-Process"]
    res = validator_for.validate(parts, policy_for)
    assert res.allowed, res.reason

@pytest.mark.parametrize("policy_for,validator_for", [(n,n) for n in PS_NAMES], indirect=True)
def test_ps_dangerous_patterns_blocked(policy_for, validator_for):
    if validator_for is None:
        pytest.skip("PowershellValidator not importable in this environment")
    parts = ["powershell.exe", "-NoProfile", "-NonInteractive", "Invoke-Expression", '"danger"']
    res = validator_for.validate(parts, policy_for)
    assert not res.allowed, "Invoke-Expression should be blocked"

@pytest.mark.parametrize("policy_for,validator_for", [(n,n) for n in PS_NAMES], indirect=True)
def test_ps_adjust_environment_defaults(policy_for, validator_for):
    if validator_for is None:
        pytest.skip("PowershellValidator not importable in this environment")
    base = {"PATH": "/usr/bin"}
    env = validator_for.adjust_environment(base, ["powershell.exe"], policy_for)
    assert env.get("TERM") == "dumb"
    assert env.get("PSModuleAutoLoadingPreference") == "None"
