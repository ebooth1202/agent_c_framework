import pytest

from agent_c_tools.tools.workspace.executors.local_storage.validators.powershell_validator import PowershellValidator
from agent_c_tools.tools.workspace.executors.local_storage.yaml_policy_provider import YamlPolicyProvider

# ---------- Fixtures ----------

@pytest.fixture(scope="module")
def provider():
    # Relies on your provider's default resolution of whitelist_commands.yaml
    return YamlPolicyProvider()

@pytest.fixture(params=["powershell", "pwsh"])
def ps_policy(provider, request):
    pol = provider.get_policy(request.param)
    assert pol, f"Missing policy for {request.param}"
    return pol

@pytest.fixture
def validator():
    return PowershellValidator()

# ---------- Policy load sanity ----------

def test_policy_core_security(ps_policy):
    # Validator name and critical flags from YAML
    assert ps_policy["validator"] == "powershell"
    assert "-Command" in ps_policy["deny_global_flags"]
    assert "-NoProfile" in ps_policy["require_flags"]
    assert "-NonInteractive" in ps_policy["require_flags"]

# ---------- Denied global flags ----------

@pytest.mark.parametrize("flag", [
    "-Command", "-c", "-EncodedCommand", "-enc", "-File", "-f",
    "-ExecutionPolicy", "-ep", "-ex"
])
def test_denied_flags_are_blocked(validator, ps_policy, flag):
    parts = ["powershell.exe", flag, "Get-Process"]
    res = validator.validate(parts, ps_policy)
    assert not res.allowed, f"{flag} should be denied; got allowed={res.allowed} reason={res.reason}"

# ---------- Required flags ----------

@pytest.mark.parametrize("missing", [
    ["-NonInteractive"],      # missing -NoProfile
    ["-NoProfile"],           # missing -NonInteractive
    [],                       # missing both
])
def test_required_flags_missing_are_blocked(validator, ps_policy, missing):
    parts = ["powershell.exe", *missing, "Get-Process"]
    res = validator.validate(parts, ps_policy)
    assert not res.allowed
    assert "Required security flag missing" in res.reason

def test_adjust_arguments_injects_required(validator, ps_policy):
    parts = ["powershell.exe", "-NoProfile", "Get-Process"]
    new_parts = validator.adjust_arguments(parts, ps_policy)
    assert "-NoProfile" in new_parts and any(a.lower().startswith("-noninteractive") for a in new_parts[1:])

# ---------- Dangerous patterns & cmdlets ----------

@pytest.mark.parametrize("args", [
    ["Invoke-Expression", '"danger"'],
    ["Set-Location", "C:\\"],
    ["New-Item", "-Path", "test.txt"],
])
def test_dangerous_patterns_blocked(validator, ps_policy, args):
    parts = ["powershell.exe", "-NoProfile", "-NonInteractive", *args]
    res = validator.validate(parts, ps_policy)
    assert not res.allowed

@pytest.mark.parametrize("args", [
    ["Get-Process"],
    ["Get-Service", "|", "Format-Table"],
    ["Get-Command"],
])
def test_safe_cmdlets_allowed(validator, ps_policy, args):
    parts = ["powershell.exe", "-NoProfile", "-NonInteractive", *args]
    res = validator.validate(parts, ps_policy)
    assert res.allowed, res.reason

# ---------- Allowed flags only ----------

@pytest.mark.parametrize("flag", ["-Help", "-NoLogo"])
def test_allowed_flags_pass(validator, ps_policy, flag):
    parts = ["powershell.exe", "-NoProfile", "-NonInteractive", flag]
    res = validator.validate(parts, ps_policy)
    assert res.allowed, res.reason

# ---------- Not a PowerShell command guard ----------

def test_not_powershell_command_is_rejected(validator):
    res = validator.validate(["node", "-e", "1"], {})
    assert not res.allowed
    assert "Not a PowerShell command" in res.reason

# ---------- Environment behavior ----------

def test_adjust_environment_applies_env_overrides_and_defaults(validator):
    base = {"PATH": "/usr/bin"}
    policy = {
        "env_overrides": {
            "NO_COLOR": "1",
            "POWERSHELL_TELEMETRY_OPTOUT": "1",
        }
    }
    env = validator.adjust_environment(base, ["powershell.exe"], policy)
    # from env_overrides
    assert env.get("NO_COLOR") == "1"
    assert env.get("POWERSHELL_TELEMETRY_OPTOUT") == "1"
    # security defaults the validator sets
    assert env.get("PSModuleAutoLoadingPreference") == "None"
    assert env.get("TERM") == "dumb"

def test_adjust_environment_applies_safe_env_if_supported(validator):
    base = {}
    policy = {
        "safe_env": {"PSExecutionPolicyPreference": "Restricted", "__PSLockdownPolicy": "1"}
    }
    env = validator.adjust_environment(base, ["powershell.exe"], policy)
    assert env.get("PSExecutionPolicyPreference") == "Restricted"
    assert env.get("__PSLockdownPolicy") == "1"
