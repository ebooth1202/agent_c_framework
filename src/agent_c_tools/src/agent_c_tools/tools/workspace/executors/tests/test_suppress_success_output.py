"""
Comprehensive tests for suppress_success_output functionality.
Tests cover validator level, executor level, and integration scenarios.
"""
import pytest
import asyncio
import os
from typing import Dict, Any, List, Optional, Mapping
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from dataclasses import asdict

from agent_c_tools.tools.workspace.executors.local_storage.secure_command_executor import (
    SecureCommandExecutor,
    CommandExecutionResult,
    PolicyProvider
)
from agent_c_tools.tools.workspace.executors.local_storage.validators.base_validator import (
    CommandValidator,
    ValidationResult
)
from agent_c_tools.tools.workspace.executors.local_storage.validators.node_validator import NodeCommandValidator


class MockPolicyProvider:
    """Mock policy provider for testing suppress_success_output"""

    def __init__(self, policies: Dict[str, Any] = None):
        self.policies = policies or {}

    def get_policy(self, base_cmd: str, parts: List[str]) -> Optional[Mapping[str, Any]]:
        return self.policies.get(base_cmd.lower())

    def get_all_policies(self) -> Dict[str, Any]:
        return self.policies


class MockValidatorWithSuppression(CommandValidator):
    """Mock validator that can return suppress_success_output"""

    def __init__(self, should_allow: bool = True, suppress_success_output: bool = False, 
                 timeout: int = 30, policy_spec: Optional[Dict[str, Any]] = None):
        self.should_allow = should_allow
        self.suppress_success_output = suppress_success_output
        self.timeout = timeout
        self.policy_spec = policy_spec or {}

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        return ValidationResult(
            allowed=self.should_allow,
            reason="OK" if self.should_allow else "Not allowed",
            timeout=self.timeout,
            suppress_success_output=self.suppress_success_output,
            policy_spec=self.policy_spec
        )

    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], 
                          policy: Mapping[str, Any]) -> Dict[str, str]:
        return base_env


@pytest.fixture
def executor():
    """Create a SecureCommandExecutor for testing"""
    policy_provider = MockPolicyProvider()
    return SecureCommandExecutor(policy_provider=policy_provider)


class TestValidatorLevelSuppression:
    """Test that validators correctly handle suppress_success_output"""

    def test_mock_validator_returns_suppress_false(self):
        """Test that mock validator can return suppress_success_output=False"""
        validator = MockValidatorWithSuppression(suppress_success_output=False)
        result = validator.validate(["echo", "test"], {})
        
        assert result.allowed is True
        assert result.suppress_success_output is False

    def test_mock_validator_returns_suppress_true(self):
        """Test that mock validator can return suppress_success_output=True"""
        validator = MockValidatorWithSuppression(suppress_success_output=True)
        result = validator.validate(["jest", "--test"], {})
        
        assert result.allowed is True
        assert result.suppress_success_output is True

    def test_node_validator_suppress_success_output_with_test_flag(self):
        """Test that NodeCommandValidator sets suppress_success_output for --test flag"""
        validator = NodeCommandValidator()
        policy = {
            "flags": {
                "--test": {"suppress_success_output": True, "allow_test_mode": True},
                "-v": {}
            },
            "deny_global_flags": ["-e", "--eval"],
            "default_timeout": 5
        }
        
        result = validator.validate(["node", "--test"], policy)
        
        assert result.allowed is True
        assert result.suppress_success_output is True

    def test_node_validator_no_suppress_with_regular_flag(self):
        """Test that NodeCommandValidator doesn't suppress for regular flags"""
        validator = NodeCommandValidator()
        policy = {
            "flags": {
                "--test": {"suppress_success_output": True, "allow_test_mode": True},
                "-v": {}
            },
            "deny_global_flags": ["-e", "--eval"],
            "default_timeout": 5
        }
        
        result = validator.validate(["node", "-v"], policy)
        
        assert result.allowed is True
        assert result.suppress_success_output is False

    def test_node_validator_suppress_with_multiple_flags(self):
        """Test suppress_success_output when multiple flags are used"""
        validator = NodeCommandValidator()
        policy = {
            "flags": {
                "--test": {"suppress_success_output": True, "allow_test_mode": True},
                "-c": {"suppress_success_output": True, "allow_test_mode": True},
                "-v": {}
            },
            "deny_global_flags": ["-e", "--eval"],
            "default_timeout": 5
        }
        
        # Test with one suppress flag
        result = validator.validate(["node", "--test", "-v"], policy)
        assert result.allowed is True
        assert result.suppress_success_output is True
        
        # Test with multiple suppress flags
        result = validator.validate(["node", "--test", "-c"], policy)
        assert result.allowed is True
        assert result.suppress_success_output is True


class TestExecutorLevelSuppression:
    """Test that executor respects suppress_success_output from ValidationResult"""

    @pytest.mark.asyncio
    async def test_executor_suppresses_output_when_flag_set(self, executor):
        """Test that executor suppresses stdout when suppress_success_output=True"""
        # Register validator that returns suppress_success_output=True
        suppressing_validator = MockValidatorWithSuppression(
            should_allow=True, 
            suppress_success_output=True
        )
        executor.register_validator("jest", suppressing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/jest"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Mock successful command with output
                mock_subprocess.return_value = ("Test output\\nAll tests passed", "", 0, False, False)

                result = await executor.execute_command("jest --test")

                assert result.status == "success"
                assert result.return_code == 0
                # Output should be suppressed for successful commands
                assert result.stdout == "Command executed successfully."
                assert result.stderr == ""

    @pytest.mark.asyncio
    async def test_executor_shows_output_when_flag_false(self, executor):
        """Test that executor shows stdout when suppress_success_output=False"""
        # Register validator that returns suppress_success_output=False
        non_suppressing_validator = MockValidatorWithSuppression(
            should_allow=True, 
            suppress_success_output=False
        )
        executor.register_validator("echo", non_suppressing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Mock successful command with output
                mock_subprocess.return_value = ("Hello World", "", 0, False, False)

                result = await executor.execute_command("echo 'Hello World'")

                assert result.status == "success"
                assert result.return_code == 0
                # Output should NOT be suppressed
                assert result.stdout == "Hello World"
                assert result.stderr == ""

    @pytest.mark.asyncio
    async def test_executor_always_shows_error_output(self, executor):
        """Test that executor always shows stderr even when suppress_success_output=True"""
        # Register validator that returns suppress_success_output=True
        suppressing_validator = MockValidatorWithSuppression(
            should_allow=True, 
            suppress_success_output=True
        )
        executor.register_validator("failing", suppressing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/failing"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Mock failed command with error output
                mock_subprocess.return_value = ("", "Error: Test failed", 1, False, False)

                result = await executor.execute_command("failing --test")

                assert result.status == "failed"
                assert result.return_code == 1
                # Error output should ALWAYS be shown, even with suppress flag
                assert result.stdout == ""
                assert result.stderr == "Error: Test failed"

    @pytest.mark.asyncio
    async def test_executor_suppresses_only_on_success(self, executor):
        """Test that suppression only applies to successful commands"""
        # Register validator that returns suppress_success_output=True
        suppressing_validator = MockValidatorWithSuppression(
            should_allow=True, 
            suppress_success_output=True
        )
        executor.register_validator("test", suppressing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/test"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Mock failed command with both stdout and stderr
                mock_subprocess.return_value = ("Some output", "Error occurred", 1, False, False)

                result = await executor.execute_command("test --run")

                assert result.status == "failed"
                assert result.return_code == 1
                # Both stdout and stderr should be shown when command fails
                assert result.stdout == "Some output"
                assert result.stderr == "Error occurred"


class TestPolicySpecSuppression:
    """Test suppress_success_output from policy_spec (mode-specific configuration)"""

    @pytest.mark.asyncio
    async def test_policy_spec_suppress_success_output(self, executor):
        """Test that policy_spec can also control suppress_success_output"""
        # Mock validator with policy_spec that has suppress_success_output
        policy_spec = {"suppress_success_output": True}
        validator_with_policy_spec = MockValidatorWithSuppression(
            should_allow=True,
            suppress_success_output=False,  # Validator level is False
            policy_spec=policy_spec
        )
        executor.register_validator("npm", validator_with_policy_spec)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/npm"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("npm test output", "", 0, False, False)

                result = await executor.execute_command("npm test")

                assert result.status == "success"
                assert result.return_code == 0
                # Should be suppressed due to policy_spec
                assert result.stdout == "Command executed successfully."

    @pytest.mark.asyncio
    async def test_validation_result_overrides_policy_spec(self, executor):
        """Test that ValidationResult suppress_success_output takes precedence over policy_spec"""
        # Mock validator where ValidationResult has suppress=True and policy_spec has suppress=False
        policy_spec = {"suppress_success_output": False}
        validator_override = MockValidatorWithSuppression(
            should_allow=True,
            suppress_success_output=True,  # ValidationResult level is True
            policy_spec=policy_spec
        )
        executor.register_validator("jest", validator_override)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/jest"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("Jest test results", "", 0, False, False)

                result = await executor.execute_command("jest --coverage")

                assert result.status == "success"
                assert result.return_code == 0
                # Should be suppressed due to ValidationResult taking precedence
                assert result.stdout == "Command executed successfully."


class TestIntegrationSuppression:
    """Integration tests for suppress_success_output through the full stack"""

    @pytest.mark.asyncio
    async def test_node_test_integration_suppression(self):
        """Test full integration of node --test with suppress_success_output"""
        policy = {
            "node": {
                "validator": "node",
                "flags": {
                    "--test": {"suppress_success_output": True, "allow_test_mode": True},
                    "-v": {}
                },
                "deny_global_flags": ["-e", "--eval"],
                "default_timeout": 5,
                "env_overrides": {"NODE_DISABLE_COLORS": "1"}
            }
        }
        
        policy_provider = MockPolicyProvider(policy)
        executor = SecureCommandExecutor(policy_provider=policy_provider)
        
        # Register the real node validator
        node_validator = NodeCommandValidator()
        executor.register_validator("node", node_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/node"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Mock successful test run
                mock_subprocess.return_value = (
                    "✓ test/example.test.js\\n✓ All tests passed (5 tests)", 
                    "", 
                    0, 
                    False, 
                    False
                )

                result = await executor.execute_command("node --test test/example.test.js")

                assert result.status == "success"
                assert result.return_code == 0
                # Output should be suppressed for successful test runs
                assert result.stdout == "Command executed successfully."
                assert result.stderr == ""

    @pytest.mark.asyncio
    async def test_node_test_integration_shows_failures(self):
        """Test that node --test shows output when tests fail"""
        policy = {
            "node": {
                "validator": "node",
                "flags": {
                    "--test": {"suppress_success_output": True, "allow_test_mode": True},
                    "-v": {}
                },
                "deny_global_flags": ["-e", "--eval"],
                "default_timeout": 5,
                "env_overrides": {"NODE_DISABLE_COLORS": "1"}
            }
        }
        
        policy_provider = MockPolicyProvider(policy)
        executor = SecureCommandExecutor(policy_provider=policy_provider)
        
        node_validator = NodeCommandValidator()
        executor.register_validator("node", node_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/node"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Mock failed test run
                mock_subprocess.return_value = (
                    "✗ test/example.test.js\\n  × expect(true).toBe(false)", 
                    "Error: 1 test failed", 
                    1, 
                    False, 
                    False
                )

                result = await executor.execute_command("node --test test/example.test.js")

                assert result.status == "failed"
                assert result.return_code == 1
                # Output should be shown for failed test runs
                assert "test failed" in result.stderr
                assert "expect(true).toBe(false)" in result.stdout

    @pytest.mark.asyncio
    async def test_node_version_no_suppression(self):
        """Test that node -v doesn't suppress output (no suppress_success_output flag)"""
        policy = {
            "node": {
                "validator": "node",
                "flags": {
                    "--test": {"suppress_success_output": True, "allow_test_mode": True},
                    "-v": {}  # No suppress_success_output for -v
                },
                "deny_global_flags": ["-e", "--eval"],
                "default_timeout": 5
            }
        }
        
        policy_provider = MockPolicyProvider(policy)
        executor = SecureCommandExecutor(policy_provider=policy_provider)
        
        node_validator = NodeCommandValidator()
        executor.register_validator("node", node_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/node"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("v18.17.0", "", 0, False, False)

                result = await executor.execute_command("node -v")

                assert result.status == "success"
                assert result.return_code == 0
                # Output should NOT be suppressed for node -v
                assert result.stdout == "v18.17.0"
                assert result.stderr == ""


class TestEdgeCasesSuppression:
    """Test edge cases for suppress_success_output"""

    @pytest.mark.asyncio
    async def test_empty_output_with_suppression(self, executor):
        """Test that suppression works correctly with empty output"""
        suppressing_validator = MockValidatorWithSuppression(
            should_allow=True, 
            suppress_success_output=True
        )
        executor.register_validator("silent", suppressing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/silent"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Mock command with no output
                mock_subprocess.return_value = ("", "", 0, False, False)

                result = await executor.execute_command("silent --run")

                assert result.status == "success"
                assert result.return_code == 0
                assert result.stdout == "Command executed successfully."
                assert result.stderr == ""

    @pytest.mark.asyncio
    async def test_whitespace_only_output_with_suppression(self, executor):
        """Test suppression with whitespace-only output"""
        suppressing_validator = MockValidatorWithSuppression(
            should_allow=True, 
            suppress_success_output=True
        )
        executor.register_validator("whitespace", suppressing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/whitespace"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Mock command with whitespace-only output
                mock_subprocess.return_value = ("   \\n\\t  \\n", "", 0, False, False)

                result = await executor.execute_command("whitespace --test")

                assert result.status == "success"
                assert result.return_code == 0
                # Whitespace output should be suppressed
                assert result.stdout == "Command executed successfully."
                assert result.stderr == ""

    @pytest.mark.asyncio
    async def test_large_output_with_suppression(self, executor):
        """Test suppression with large output"""
        suppressing_validator = MockValidatorWithSuppression(
            should_allow=True, 
            suppress_success_output=True
        )
        executor.register_validator("large", suppressing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/large"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Mock command with large output
                large_output = "line\\n" * 1000  # 1000 lines
                mock_subprocess.return_value = (large_output, "", 0, False, False)

                result = await executor.execute_command("large --generate")

                assert result.status == "success"
                assert result.return_code == 0
                # Large output should be suppressed
                assert result.stdout == "Command executed successfully."
                assert result.stderr == ""


if __name__ == "__main__":
    pytest.main([__file__])
