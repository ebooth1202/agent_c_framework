"""
Additional tests for suppress_success_output in policy configurations.
Tests that policies are correctly configured with suppress_success_output settings.
"""
import pytest
import os
from agent_c_tools.tools.workspace.executors.local_storage.yaml_policy_provider import YamlPolicyProvider


@pytest.fixture(scope="session")
def policies():
    """Load policies using the same method as policy_tests"""
    provider = YamlPolicyProvider()
    return provider.get_all_policies()


class TestSuppressSuccessOutputPolicyConfiguration:
    """Test that policies are correctly configured with suppress_success_output"""

    def test_node_policy_has_suppress_flags(self, policies):
        """Test that node policy has flags configured with suppress_success_output"""
        if "node" not in policies:
            pytest.skip("node policy not present")

        pol = policies["node"]
        flags = pol.get("flags", {})

        # Should be dict format for new configuration
        if isinstance(flags, dict):
            # Test that test-related flags have suppress_success_output
            test_related_flags = ["--test", "-c", "--test-reporter", "--test-name-pattern"]
            
            for flag in test_related_flags:
                if flag in flags:
                    flag_config = flags[flag]
                    assert flag_config.get("suppress_success_output", False), \
                        f"Flag {flag} should have suppress_success_output enabled"

    def test_npx_policy_has_suppress_packages(self, policies):
        """Test that npx policy has packages configured with suppress_success_output"""
        if "npx" not in policies:
            pytest.skip("npx policy not present")

        pol = policies["npx"]
        packages = pol.get("packages", {})

        # Test that testing/build-related packages have suppress_success_output
        test_packages = ["jest", "mocha", "typescript", "webpack", "vite", "rollup", "parcel"]
        build_packages = ["@angular/cli", "ts-node"]
        
        suppress_packages = test_packages + build_packages
        
        for package in suppress_packages:
            if package in packages:
                package_config = packages[package]
                assert package_config.get("suppress_success_output", False), \
                    f"Package {package} should have suppress_success_output enabled"

    def test_npm_policy_test_scripts_configuration(self, policies):
        """Test npm policy configuration for test script suppression"""
        if "npm" not in policies:
            pytest.skip("npm policy not present")

        pol = policies["npm"]
        subs = pol.get("subcommands", {})

        if "run" in subs:
            run_config = subs["run"]
            # If allow_test_paths is configured, verify structure supports suppression
            if "allow_test_paths" in run_config:
                assert isinstance(run_config.get("allow_test_paths"), bool), \
                    "allow_test_paths should be boolean"

    def test_dotnet_test_policy_configuration(self, policies):
        """Test that dotnet test policy can support output suppression"""
        if "dotnet" not in policies:
            pytest.skip("dotnet policy not present")

        pol = policies["dotnet"]
        subs = pol.get("subcommands", {})

        if "test" in subs:
            test_config = subs["test"]
            # Dotnet test should have configuration that could support suppression
            assert isinstance(test_config.get("flags", []), list), \
                "dotnet test should have flags configuration"
            assert isinstance(test_config.get("require_flags", {}), dict), \
                "dotnet test should have require_flags configuration"

    def test_pytest_policy_configuration(self, policies):
        """Test that pytest policy can support output suppression"""
        if "pytest" not in policies:
            pytest.skip("pytest policy not present")

        pol = policies["pytest"]
        # pytest should have basic structure that could support suppression
        assert isinstance(pol.get("flags", []), list), \
            "pytest should have flags configuration"
        assert isinstance(pol.get("env_overrides", {}), dict), \
            "pytest should have env_overrides configuration"


class TestSuppressSuccessOutputValidatorBehavior:
    """Test specific validator behaviors for suppress_success_output"""

    def test_validator_precedence_rules(self):
        """Test that ValidationResult suppress_success_output takes precedence"""
        from agent_c_tools.tools.workspace.executors.local_storage.validators.base_validator import ValidationResult
        
        # Test that ValidationResult with suppress_success_output=True overrides policy_spec
        policy_spec = {"suppress_success_output": False}
        result = ValidationResult(
            allowed=True,
            reason="OK",
            suppress_success_output=True,  # This should take precedence
            policy_spec=policy_spec
        )
        
        assert result.suppress_success_output is True
        assert result.policy_spec["suppress_success_output"] is False

    def test_validation_result_default_behavior(self):
        """Test ValidationResult default behavior for suppress_success_output"""
        from agent_c_tools.tools.workspace.executors.local_storage.validators.base_validator import ValidationResult
        
        # Test default value
        result = ValidationResult(allowed=True, reason="OK")
        assert result.suppress_success_output is False
        
        # Test explicit False
        result = ValidationResult(allowed=True, reason="OK", suppress_success_output=False)
        assert result.suppress_success_output is False
        
        # Test explicit True
        result = ValidationResult(allowed=True, reason="OK", suppress_success_output=True)
        assert result.suppress_success_output is True

    def test_policy_spec_fallback_behavior(self):
        """Test that policy_spec suppress_success_output works as fallback"""
        from agent_c_tools.tools.workspace.executors.local_storage.validators.base_validator import ValidationResult
        
        # When ValidationResult doesn't specify suppress_success_output, policy_spec could be used
        policy_spec = {"suppress_success_output": True}
        result = ValidationResult(
            allowed=True,
            reason="OK",
            # suppress_success_output not specified, defaults to False
            policy_spec=policy_spec
        )
        
        # ValidationResult level takes precedence (defaults to False)
        assert result.suppress_success_output is False
        # But policy_spec is available for executor to check
        assert result.policy_spec["suppress_success_output"] is True


class TestSuppressSuccessOutputToolSpecificBehavior:
    """Test tool-specific behaviors for suppress_success_output"""

    def test_node_test_runner_scenarios(self):
        """Test various node test runner scenarios"""
        from agent_c_tools.tools.workspace.executors.local_storage.validators.node_validator import NodeCommandValidator
        
        validator = NodeCommandValidator()
        
        # Policy with comprehensive test configuration
        policy = {
            "flags": {
                "--test": {"suppress_success_output": True, "allow_test_mode": True},
                "--test-reporter": {"suppress_success_output": True, "allow_test_mode": True},
                "--test-name-pattern": {"suppress_success_output": True, "allow_test_mode": True},
                "-c": {"suppress_success_output": True, "allow_test_mode": True},
                "-v": {},
                "--version": {}
            },
            "deny_global_flags": ["-e", "--eval", "-p", "--print"],
            "default_timeout": 5
        }
        
        # Test various test command combinations
        test_commands = [
            ["node", "--test"],
            ["node", "--test", "test/"],
            ["node", "--test", "--test-reporter", "json"],
            ["node", "--test", "--test-name-pattern", "unit"],
        ]
        
        for cmd in test_commands:
            result = validator.validate(cmd, policy)
            assert result.allowed, f"Command should be allowed: {cmd}"
            assert result.suppress_success_output, f"Command should suppress output: {cmd}"
        
        # Test non-suppress commands
        non_suppress_commands = [
            ["node", "-v"],
            ["node", "--version"],
        ]
        
        for cmd in non_suppress_commands:
            result = validator.validate(cmd, policy)
            assert result.allowed, f"Command should be allowed: {cmd}"
            assert not result.suppress_success_output, f"Command should NOT suppress output: {cmd}"

    def test_mixed_suppress_and_non_suppress_flags(self):
        """Test commands with mixed suppress and non-suppress flags"""
        from agent_c_tools.tools.workspace.executors.local_storage.validators.node_validator import NodeCommandValidator
        
        validator = NodeCommandValidator()
        policy = {
            "flags": {
                "--test": {"suppress_success_output": True, "allow_test_mode": True},
                "-v": {},  # No suppress_success_output
                "--version": {}  # No suppress_success_output
            },
            "deny_global_flags": ["-e", "--eval"],
            "default_timeout": 5
        }
        
        # If ANY flag has suppress_success_output=True, the result should be True
        result = validator.validate(["node", "--test", "-v"], policy)
        assert result.allowed
        assert result.suppress_success_output  # Should be True because --test has it

    def test_legacy_list_format_no_suppression(self):
        """Test that legacy list format doesn't support suppression"""
        from agent_c_tools.tools.workspace.executors.local_storage.validators.node_validator import NodeCommandValidator
        
        validator = NodeCommandValidator()
        policy = {
            "flags": ["-v", "--version", "--test"],  # Legacy list format
            "deny_global_flags": ["-e", "--eval"],
            "default_timeout": 5,
            "allow_test_mode": True
        }
        
        # Legacy format should never suppress output
        result = validator.validate(["node", "--test"], policy)
        assert result.allowed
        assert not result.suppress_success_output  # Should be False with legacy format


if __name__ == "__main__":
    pytest.main([__file__])
