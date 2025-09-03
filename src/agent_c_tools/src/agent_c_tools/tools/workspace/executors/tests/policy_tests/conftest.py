import os
import importlib
from pathlib import Path
import pytest
from agent_c_tools.tools.workspace.executors.local_storage.yaml_policy_provider import YamlPolicyProvider


def _load_policies():
    # 1) Prefer the project's provider so tests match runtime behavior
    provider = YamlPolicyProvider()
    return provider.get_all_policies()


@pytest.fixture(scope="session")
def policies():
    return _load_policies()

@pytest.fixture(scope="session")
def policy_names(policies):
    # Useful list for parametrization over all policies
    return sorted(policies.keys())

def _load_validator(policy_name: str):
    """Best-effort dynamic loader for validator classes.
    Update the mapping below to point to your project's actual module paths.
    If a validator can't be imported, we return None so validator-specific tests can be skipped.
    """
    # Map policy name -> 'module_path:ClassName'
    mapping = {
        # Testing validators
        "pytest": "agent_c_tools.tools.workspace.executors.local_storage.validators.pytest_validator:PytestCommandValidator",
        "dotnet": "agent_c_tools.tools.workspace.executors.local_storage.validators.dotnet_validator:DotnetCommandValidator",
        "npm": "agent_c_tools.tools.workspace.executors.local_storage.validators.npm_validator:NpmCommandValidator",
        "pnpm": "agent_c_tools.tools.workspace.executors.local_storage.validators.pnpm_validator:PnpmCommandValidator",
        "node": "agent_c_tools.tools.workspace.executors.local_storage.validators.node_validator:NodeCommandValidator",
        "lerna": "agent_c_tools.tools.workspace.executors.local_storage.validators.lerna_validator:LernaCommandValidator",
        # Other validators
        "git": "agent_c_tools.tools.workspace.executors.local_storage.validators.git_validator:GitCommandValidator",
        "powershell": "agent_c_tools.tools.workspace.executors.local_storage.validators.powershell_validator:PowershellValidator",
        "pwsh": "agent_c_tools.tools.workspace.executors.local_storage.validators.powershell_validator:PowershellValidator",
        # Add others here once their modules are available.
        "which": "agent_c_tools.tools.workspace.executors.local_storage.validators.os_validator:OSCommandValidator",
        "where": "agent_c_tools.tools.workspace.executors.local_storage.validators.os_validator:OSCommandValidator",
        "whoami": "agent_c_tools.tools.workspace.executors.local_storage.validators.os_validator:OSCommandValidator",
        "echo": "agent_c_tools.tools.workspace.executors.local_storage.validators.os_validator:OSCommandValidator",
    }
    target = mapping.get(policy_name)
    if not target:
        return None
    mod_name, _, cls_name = target.partition(":")
    try:
        mod = importlib.import_module(mod_name)
        cls = getattr(mod, cls_name)
        return cls
    except Exception:
        return None

@pytest.fixture
def validator_for(request):
    """Returns an instantiated validator for the given policy name (or None if not importable).
    Usage: validator = validator_for('powershell')
    """
    name = request.param
    cls = _load_validator(name)
    return cls() if cls else None

@pytest.fixture
def policy_for(policies, request):
    name = request.param
    if name not in policies:
        pytest.skip(f"No policy named {name}")
    return policies[name]
