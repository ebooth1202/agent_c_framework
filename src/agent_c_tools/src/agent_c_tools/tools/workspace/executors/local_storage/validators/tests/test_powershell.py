#!/usr/bin/env python3
"""
Simple test to verify PowerShell integration works correctly.
This tests the validator, policy loading, and basic security restrictions.
"""

import sys
from pathlib import Path

# Add the source directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from agent_c_tools.tools.workspace.executors.local_storage.validators.powershell_validator import PowershellValidator
from agent_c_tools.tools.workspace.executors.local_storage.yaml_policy_provider import YamlPolicyProvider


def test_yaml_parsing():
    """Test that the YAML configuration is valid using YamlPolicyProvider"""
    print("Testing YAML configuration parsing with YamlPolicyProvider...")

    # Use YamlPolicyProvider with default config path resolution
    provider = YamlPolicyProvider()

    try:
        # Check that PowerShell configurations exist
        ps_policy = provider.get_policy('powershell')
        pwsh_policy = provider.get_policy('pwsh')

        assert ps_policy is not None, "PowerShell configuration missing"
        assert pwsh_policy is not None, "PowerShell Core configuration missing"

        # Check key security settings for PowerShell
        assert ps_policy['validator'] == 'powershell', "Wrong validator specified"
        assert '-Command' in ps_policy['deny_global_flags'], "Command execution not blocked"
        assert '-NoProfile' in ps_policy['require_flags'], "NoProfile not required"
        assert ps_policy['safe_env']['PSExecutionPolicyPreference'] == 'Restricted', "Execution policy not restricted"

        print("✓ YAML configuration is valid and secure")
        print(f"✓ Policy file loaded from: {provider.policy_file_path}")
        return True

    except Exception as e:
        print(f"✗ YAML configuration error: {e}")
        return False


def test_policy_provider_features():
    """Test YamlPolicyProvider specific features"""
    print("Testing YamlPolicyProvider features...")

    # Use default config path resolution
    provider = YamlPolicyProvider()

    try:
        # Test has_policy method
        assert provider.has_policy('powershell'), "PowerShell policy should exist"
        assert provider.has_policy('pwsh'), "PowerShell Core policy should exist"
        assert not provider.has_policy('nonexistent'), "Nonexistent policy should not exist"

        # Test get_all_policies
        all_policies = provider.get_all_policies()
        assert 'powershell' in all_policies, "PowerShell should be in all policies"
        assert 'pwsh' in all_policies, "PowerShell Core should be in all policies"

        # Test reload functionality
        reload_success = provider.reload_policy()
        assert reload_success, "Policy reload should succeed"

        print("✓ YamlPolicyProvider features working correctly")
        return True

    except Exception as e:
        print(f"✗ YamlPolicyProvider feature test error: {e}")
        return False


def test_validator_security():
    """Test that the validator blocks dangerous operations"""
    print("Testing PowerShell validator security...")

    # Use YamlPolicyProvider with default config path resolution
    provider = YamlPolicyProvider()

    # Get the PowerShell policy
    ps_policy = provider.get_policy('powershell')
    if not ps_policy:
        print("✗ Could not load PowerShell policy")
        return False

    validator = PowershellValidator()

    # Test cases that should be BLOCKED
    dangerous_commands = [
        (['powershell.exe', '-Command', 'Get-Process'], "denied flag -Command"),
        (['powershell.exe', '-c', 'Write-Host "Hello"'], "denied flag -c"),
        (['powershell.exe', '-EncodedCommand', 'R2V0LVByb2Nlc3M='], "denied flag -EncodedCommand"),
        (['powershell.exe', '-File', 'script.ps1'], "denied flag -File"),
        (['powershell.exe', '-ExecutionPolicy', 'Bypass'], "flag not allowed"),
        (['powershell.exe', '-NoProfile', '-NonInteractive', 'Invoke-Expression', '"dangerous code"'],
         "dangerous pattern"),
        (['powershell.exe', '-NoProfile', '-NonInteractive', 'Set-Location', 'C:\\'], "dangerous pattern set-"),
        (['powershell.exe', '-NoProfile', '-NonInteractive', 'New-Item', '-Path', 'test.txt'],
         "dangerous pattern new-"),
        (['powershell.exe', '-NoProfile', '-NonInteractive', 'Remove-Item', 'test.txt'], "cmdlet not allowed"),
    ]

    for cmd, expected_reason in dangerous_commands:
        result = validator.validate(cmd, ps_policy)
        if result.allowed:
            print(f"✗ SECURITY FAILURE: Command should be blocked: {' '.join(cmd)}")
            return False
        else:
            print(f"✓ Correctly blocked: {' '.join(cmd[:2])} - {result.reason}")

    # Test cases that should be ALLOWED (with required flags)
    safe_commands = [
        ['powershell.exe', '-NoProfile', '-NonInteractive', '-Help'],
        ['powershell.exe', '-NoProfile', '-NonInteractive', '-NoLogo'],
        ['powershell.exe', '-NoProfile', '-NonInteractive', 'Get-Process'],
        ['powershell.exe', '-NoProfile', '-NonInteractive', 'Get-Service', '|', 'Format-Table'],
    ]

    for cmd in safe_commands:
        result = validator.validate(cmd, ps_policy)
        if not result.allowed:
            print(f"✗ Safe command was blocked: {' '.join(cmd)} - {result.reason}")
            return False
        else:
            print(f"✓ Correctly allowed: {' '.join(cmd)}")

    print("✓ Validator security tests passed")
    return True


def test_environment_security():
    """Test that the validator sets up secure environment"""
    print("Testing PowerShell environment security...")

    validator = PowershellValidator()

    policy = {
        'safe_env': {
            'PSExecutionPolicyPreference': 'Restricted',
            '__PSLockdownPolicy': '1'
        },
        'env_overrides': {
            'NO_COLOR': '1',
            'POWERSHELL_TELEMETRY_OPTOUT': '1'
        }
    }

    base_env = {'PATH': '/usr/bin', 'HOME': '/home/user'}
    parts = ['powershell.exe', '-NoProfile', '-NonInteractive']

    result_env = validator.adjust_environment(base_env, parts, policy)

    # Check critical security settings
    security_checks = [
        ('PSExecutionPolicyPreference', 'Restricted'),
        ('__PSLockdownPolicy', '1'),
        ('NO_COLOR', '1'),
        ('POWERSHELL_TELEMETRY_OPTOUT', '1'),
        ('PSModuleAutoLoadingPreference', 'None'),
    ]

    for key, expected_value in security_checks:
        if result_env.get(key) != expected_value:
            print(f"✗ Security environment not set: {key} should be {expected_value}, got {result_env.get(key)}")
            return False
        else:
            print(f"✓ Security setting: {key} = {expected_value}")

    print("✓ Environment security tests passed")
    return True


def main():
    """Run all tests"""
    print("PowerShell Integration Security Test")
    print("=" * 50)

    tests = [
        test_yaml_parsing,
        test_policy_provider_features,
        test_validator_security,
        test_environment_security,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        print()
        try:
            if test():
                passed += 1
            else:
                print("Test failed!")
        except Exception as e:
            print(f"Test error: {e}")

    print()
    print("=" * 50)
    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All tests passed! PowerShell integration is secure.")
        return 0
    else:
        print("❌ Some tests failed. Review security implementation.")
        return 1


if __name__ == "__main__":
    sys.exit(main())