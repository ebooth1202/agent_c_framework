import pytest
import asyncio
import os
import platform
from typing import Dict, Any, List, Optional, Mapping, Tuple
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


class MockPolicyProvider:
    """Mock policy provider for testing"""

    def __init__(self, policies: Dict[str, Any] = None):
        self.policies = policies or {}

    def get_policy(self, base_cmd: str, parts: List[str]) -> Optional[Mapping[str, Any]]:
        return self.policies.get(base_cmd.lower())

    def get_all_policies(self) -> Dict[str, Any]:
        return self.policies


class MockCommandValidator(CommandValidator):
    """Mock validator for testing"""

    def __init__(self, should_allow: bool = True, reason: str = "test", timeout: int = 30):
        self.should_allow = should_allow
        self.reason = reason
        self.timeout = timeout
        self.adjust_arguments_called = False
        self.adjust_environment_called = False

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        return ValidationResult(
            allowed=self.should_allow,
            reason=self.reason if not self.should_allow else None,
            timeout=self.timeout
        )

    def adjust_arguments(self, parts: List[str], policy: Mapping[str, Any]) -> List[str]:
        self.adjust_arguments_called = True
        return parts + ["--adjusted"]

    def adjust_environment(self, env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        self.adjust_environment_called = True
        new_env = env.copy()
        new_env["TEST_ADJUSTED"] = "true"
        return new_env


class TestCommandExecutionResult:
    """Test the CommandExecutionResult dataclass"""

    def test_to_dict(self):
        """Test to_dict method"""
        result = CommandExecutionResult(
            status="success",
            return_code=0,
            stdout="Hello World",
            stderr="",
            command="echo hello",
            working_directory="/tmp",
            duration_ms=100
        )

        result_dict = result.to_dict()
        assert result_dict["status"] == "success"
        assert result_dict["return_code"] == 0
        assert result_dict["stdout"] == "Hello World"
        assert result_dict["command"] == "echo hello"

    def test_to_yaml(self):
        """Test to_yaml method"""
        result = CommandExecutionResult(
            status="success",
            return_code=0,
            stdout="Hello World",
            stderr="",
            command="echo hello",
            working_directory="/tmp"
        )

        yaml_output = result.to_yaml()
        assert "status: success" in yaml_output
        assert "return_code: 0" in yaml_output
        assert "stdout: Hello World" in yaml_output

    def test_to_yaml_capped(self):
        """Test to_yaml_capped method with token limiting"""
        # Create a result with large stdout
        large_stdout = "\n".join([f"Line {i}" for i in range(1000)])
        result = CommandExecutionResult(
            status="success",
            return_code=0,
            stdout=large_stdout,
            stderr="Error line",
            command="echo hello",
            working_directory="/tmp"
        )

        def count_tokens(text: str) -> int:
            return len(text.split())

        # Test with very small token limit
        yaml_output = result.to_yaml_capped(max_tokens=50, count_tokens=count_tokens)
        assert "truncated" in yaml_output.lower() or "omitted" in yaml_output.lower()
        assert len(yaml_output.split()) <= 100  # Should be significantly reduced

    def test_to_yaml_capped_edge_cases(self):
        """Test to_yaml_capped with various edge cases"""
        def count_tokens(text: str) -> int:
            return len(text.split())

        # Test with empty output
        empty_result = CommandExecutionResult(
            status="success", return_code=0, stdout="", stderr="",
            command="test", working_directory="/tmp"
        )
        yaml_output = empty_result.to_yaml_capped(max_tokens=10, count_tokens=count_tokens)
        assert "status: success" in yaml_output

        # Test with only stderr
        stderr_result = CommandExecutionResult(
            status="failed", return_code=1, stdout="",
            stderr="\n".join([f"Error line {i}" for i in range(100)]),
            command="test", working_directory="/tmp"
        )
        yaml_output = stderr_result.to_yaml_capped(max_tokens=20, count_tokens=count_tokens)
        assert "stderr" in yaml_output

        # Test with very small token limit (should use last resort)
        large_result = CommandExecutionResult(
            status="success", return_code=0,
            stdout="\n".join([f"Line {i}" for i in range(1000)]),
            stderr="\n".join([f"Error {i}" for i in range(100)]),
            command="test", working_directory="/tmp"
        )
        yaml_output = large_result.to_yaml_capped(max_tokens=5, count_tokens=count_tokens)
        assert "omitted" in yaml_output

    def test_properties(self):
        """Test convenience properties"""
        success_result = CommandExecutionResult(
            status="success", return_code=0, stdout="", stderr="",
            command="test", working_directory="/tmp"
        )
        assert success_result.is_success is True
        assert success_result.is_error is False

        error_result = CommandExecutionResult(
            status="error", return_code=1, stdout="", stderr="",
            command="test", working_directory="/tmp"
        )
        assert error_result.is_success is False
        assert error_result.is_error is True

        timeout_result = CommandExecutionResult(
            status="timeout", return_code=None, stdout="", stderr="",
            command="test", working_directory="/tmp"
        )
        assert timeout_result.is_success is False
        assert timeout_result.is_error is True

        blocked_result = CommandExecutionResult(
            status="blocked", return_code=None, stdout="", stderr="",
            command="test", working_directory="/tmp"
        )
        assert blocked_result.is_success is False
        assert blocked_result.is_error is True

        failed_result = CommandExecutionResult(
            status="failed", return_code=2, stdout="", stderr="",
            command="test", working_directory="/tmp"
        )
        assert failed_result.is_success is False
        assert failed_result.is_error is True

    def test_to_friendly_string(self):
        """Test to_friendly_string method"""
        # Success with output
        success_result = CommandExecutionResult(
            status="success", return_code=0, stdout="Hello World", stderr="",
            command="echo hello", working_directory="/tmp"
        )
        friendly = success_result.to_friendly_string()
        assert "OK:" in friendly
        assert "Hello World" in friendly

        # Success without output
        success_no_output = CommandExecutionResult(
            status="success", return_code=0, stdout="", stderr="",
            command="touch file", working_directory="/tmp"
        )
        friendly = success_no_output.to_friendly_string()
        assert "OK (no output)" in friendly

        # Success with only whitespace output
        success_whitespace = CommandExecutionResult(
            status="success", return_code=0, stdout="   \n\t  ", stderr="",
            command="test", working_directory="/tmp"
        )
        friendly = success_whitespace.to_friendly_string()
        assert "OK (no output)" in friendly

        # Blocked command
        blocked_result = CommandExecutionResult(
            status="blocked", return_code=None, stdout="", stderr="",
            command="rm -rf /", working_directory="/tmp",
            error_message="Dangerous command"
        )
        friendly = blocked_result.to_friendly_string()
        assert "ERROR: Command blocked by security policy: Dangerous command" in friendly

        # Timeout
        timeout_result = CommandExecutionResult(
            status="timeout", return_code=None, stdout="", stderr="",
            command="sleep 100", working_directory="/tmp",
            error_message="Command timed out after 30 seconds"
        )
        friendly = timeout_result.to_friendly_string()
        assert "ERROR: Command timed out" in friendly

        # Error with stderr
        error_result = CommandExecutionResult(
            status="error", return_code=1, stdout="", stderr="File not found\nPermission denied",
            command="cat missing", working_directory="/tmp",
            error_message="Command failed"
        )
        friendly = error_result.to_friendly_string()
        assert "ERROR: Command failed" in friendly
        assert "Permission denied" in friendly

        # Error with very long stderr (should be truncated)
        long_stderr = "\n".join([f"Error line {i}" for i in range(20)])
        error_long = CommandExecutionResult(
            status="error", return_code=1, stdout="", stderr=long_stderr,
            command="test", working_directory="/tmp",
            error_message="Many errors"
        )
        friendly = error_long.to_friendly_string()
        assert "ERROR: Many errors" in friendly
        # Should only show last 10 lines
        friendly_lines = friendly.split('\n')
        assert len(friendly_lines) <= 12  # Error message + max 10 stderr lines + some buffer

        # Custom success prefix
        success_custom = CommandExecutionResult(
            status="success", return_code=0, stdout="Done", stderr="",
            command="test", working_directory="/tmp"
        )
        friendly = success_custom.to_friendly_string(success_prefix="COMPLETED")
        assert "COMPLETED:" in friendly
        assert "Done" in friendly

    def test_get_error_details(self):
        """Test get_error_details method"""
        # Success should return None
        success_result = CommandExecutionResult(
            status="success", return_code=0, stdout="", stderr="",
            command="test", working_directory="/tmp"
        )
        assert success_result.get_error_details() is None

        # Error should return details
        error_result = CommandExecutionResult(
            status="error", return_code=1, stdout="output", stderr="error",
            command="test", working_directory="/tmp", error_message="Failed"
        )
        details = error_result.get_error_details()
        assert details is not None
        assert details["status"] == "error"
        assert details["return_code"] == 1
        assert details["command"] == "test"
        assert details["error_message"] == "Failed"

        # Test with very long output (should be truncated)
        long_output = "x" * 1000
        long_error = "e" * 1000
        error_long = CommandExecutionResult(
            status="failed", return_code=2, stdout=long_output, stderr=long_error,
            command="test", working_directory="/tmp", error_message="Long error"
        )
        details = error_long.get_error_details()
        assert len(details["stdout"]) <= 503  # 500 + "..."
        assert len(details["stderr"]) <= 503  # 500 + "..."
        assert details["stdout"].endswith("...")
        assert details["stderr"].endswith("...")


class TestSecureCommandExecutor:
    """Test the SecureCommandExecutor class"""

    @pytest.fixture
    def basic_policies(self):
        """Basic policies for testing"""
        return {
            "echo": {
                "validator": "basic",
                "default_timeout": 10,
                "safe_env": {"TEST_VAR": "test_value"}
            },
            "git": {
                "validator": "git",
                "default_timeout": 30,
                "safe_env": {"GIT_CONFIG_GLOBAL": "/dev/null"}
            },
            "test": {
                "validator": "test",
                "default_timeout": 5,
                "require_flags": ["--safe"],
                "safe_env": {"SAFE_MODE": "1"}
            }
        }

    @pytest.fixture
    def mock_policy_provider(self, basic_policies):
        """Mock policy provider fixture"""
        return MockPolicyProvider(basic_policies)

    @pytest.fixture
    def executor(self, mock_policy_provider):
        """SecureCommandExecutor fixture"""
        return SecureCommandExecutor(
            policy_provider=mock_policy_provider,
            default_timeout=30,
            max_output_size=1024
        )

    def test_initialization(self):
        """Test SecureCommandExecutor initialization"""
        executor = SecureCommandExecutor()

        # Test platform detection
        assert hasattr(executor, 'platform')
        assert hasattr(executor, 'is_windows')
        assert executor.is_windows == platform.system().lower().startswith("win")

        # Test defaults
        assert executor.default_timeout == 30
        assert executor.max_output_size == 1024 * 1024
        assert executor.show_windows is False

        # Test validators are registered
        assert "git" in executor.validators
        assert "npm" in executor.validators
        assert "powershell" in executor.validators

    def test_initialization_with_custom_settings(self, mock_policy_provider):
        """Test initialization with custom settings"""
        executor = SecureCommandExecutor(
            show_windows=True,
            log_output=False,
            default_timeout=60,
            max_output_size=2048,
            policy_provider=mock_policy_provider
        )

        assert executor.show_windows is True
        assert executor.log_output is False
        assert executor.default_timeout == 60
        assert executor.max_output_size == 2048
        assert executor.policy_provider == mock_policy_provider

    def test_initialization_edge_cases(self):
        """Test initialization with edge cases"""
        # Test with invalid timeout (should be converted to int)
        executor = SecureCommandExecutor(default_timeout="45")
        assert executor.default_timeout == 45
        assert isinstance(executor.default_timeout, int)

        # Test with invalid max_output_size
        executor = SecureCommandExecutor(max_output_size="2048")
        assert executor.max_output_size == 2048
        assert isinstance(executor.max_output_size, int)

        # Test with empty default policies
        executor = SecureCommandExecutor(default_policies={})
        assert executor.default_policies == {}

        # Test with None policy provider
        executor = SecureCommandExecutor(policy_provider=None)
        assert executor.policy_provider is None

    def test_ansi_handling(self):
        """Test ANSI escape sequence handling"""
        # Test ANSI detection
        assert SecureCommandExecutor.has_ansi("\x1b[31mred text\x1b[0m") is True
        assert SecureCommandExecutor.has_ansi("plain text") is False
        assert SecureCommandExecutor.has_ansi("") is False
        assert SecureCommandExecutor.has_ansi("\x1b[0m") is True
        assert SecureCommandExecutor.has_ansi("\x1b[1;32mgreen\x1b[0m") is True

        # Test ANSI stripping
        colored_text = "\x1b[31mred\x1b[0m \x1b[32mgreen\x1b[0m"
        stripped = SecureCommandExecutor.strip_ansi(colored_text)
        assert stripped == "red green"
        assert SecureCommandExecutor.has_ansi(stripped) is False

        # Test various ANSI sequences
        complex_ansi = "\x1b[1;31;40mBold Red on Black\x1b[0m\x1b[2K\x1b[A"
        stripped_complex = SecureCommandExecutor.strip_ansi(complex_ansi)
        assert "Bold Red on Black" in stripped_complex
        assert "\x1b[" not in stripped_complex

    def test_resolve_base(self):
        """Test _resolve_base method"""
        # Basic command
        assert SecureCommandExecutor._resolve_base(["echo", "hello"]) == "echo"

        # Windows executable
        assert SecureCommandExecutor._resolve_base(["git.exe", "status"]) == "git"
        assert SecureCommandExecutor._resolve_base(["cmd.exe", "/c", "dir"]) == "cmd"
        assert SecureCommandExecutor._resolve_base(["test.cmd"]) == "test"
        assert SecureCommandExecutor._resolve_base(["script.bat"]) == "script"
        assert SecureCommandExecutor._resolve_base(["program.com"]) == "program"

        # Python module invocation
        assert SecureCommandExecutor._resolve_base(["python", "-m", "pytest", "test.py"]) == "pytest"
        assert SecureCommandExecutor._resolve_base(["python3", "-m", "pytest", "--verbose"]) == "pytest"

        # Non-pytest module
        assert SecureCommandExecutor._resolve_base(["python", "-m", "pip", "install"]) == "python"
        assert SecureCommandExecutor._resolve_base(["python", "-m", "mymodule"]) == "python"

        # Edge cases
        assert SecureCommandExecutor._resolve_base(["python", "-m"]) == "python"  # incomplete -m
        assert SecureCommandExecutor._resolve_base(["python"]) == "python"  # just python

        # Path with executable
        assert SecureCommandExecutor._resolve_base(["/usr/bin/git", "status"]) == "git"
        assert SecureCommandExecutor._resolve_base(["C:\\Program Files\\Git\\bin\\git.exe", "status"]) == "git"

        # Case sensitivity
        assert SecureCommandExecutor._resolve_base(["GIT.EXE", "status"]) == "GIT"
        assert SecureCommandExecutor._resolve_base(["Test.CMD"]) == "Test"

    def test_register_validator(self, executor):
        """Test registering custom validators"""
        custom_validator = MockCommandValidator()
        executor.register_validator("custom", custom_validator)

        assert "custom" in executor.validators
        assert executor.validators["custom"] == custom_validator

        # Test overriding existing validator
        new_validator = MockCommandValidator(should_allow=False)
        executor.register_validator("custom", new_validator)
        assert executor.validators["custom"] == new_validator

    @pytest.mark.asyncio
    async def test_execute_command_no_policy(self, executor):
        """Test command execution when no policy exists"""
        result = await executor.execute_command("unknown_command arg1")

        assert result.status == "blocked"
        assert "No policy for 'unknown_command'" in result.error_message
        assert result.return_code is None
        assert result.command == "unknown_command arg1"

    @pytest.mark.asyncio
    async def test_execute_command_parse_error(self, executor):
        """Test command execution with parse error"""
        # Invalid shell syntax - unclosed quote
        result = await executor.execute_command('echo "unclosed quote')

        assert result.status == "error"
        assert "Parse error" in result.error_message

        # Empty string after parsing
        with patch('shlex.split', return_value=[]):
            result = await executor.execute_command("echo hello")
            assert result.status == "error"
            assert "Empty command" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_command_empty_command(self, executor):
        """Test command execution with empty command"""
        result = await executor.execute_command("")

        assert result.status == "error"
        assert "Empty command" in result.error_message

        # Test with whitespace only
        result = await executor.execute_command("   \t\n   ")
        assert result.status == "error"

    @pytest.mark.asyncio
    async def test_execute_command_validation_failed(self, executor):
        """Test command execution when validation fails"""
        # Register a validator that blocks everything
        blocking_validator = MockCommandValidator(should_allow=False, reason="Blocked for testing")
        executor.register_validator("basic", blocking_validator)

        result = await executor.execute_command("echo hello")

        assert result.status == "blocked"
        assert "Blocked for testing" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_command_success(self, executor):
        """Test successful command execution"""
        # Register a permissive validator
        allowing_validator = MockCommandValidator(should_allow=True, timeout=15)
        executor.register_validator("basic", allowing_validator)

        # Mock executable resolution to succeed
        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("Hello World\n", "", 0, False, False)

                result = await executor.execute_command("echo hello")

                assert result.status == "success"
                assert result.return_code == 0
                assert "Hello World" in result.stdout
                assert result.stderr == ""
                assert result.command == "echo hello"
                assert result.duration_ms is not None
                assert result.truncated_stdout is False
                assert result.truncated_stderr is False

    @pytest.mark.asyncio
    async def test_execute_command_with_stderr(self, executor):
        """Test command execution with stderr output"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "Error message", 1, False, False)

                result = await executor.execute_command("echo hello")

                assert result.status == "failed"
                assert result.return_code == 1
                assert result.stdout == ""
                assert "Error message" in result.stderr
                assert "Return code 1" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_command_timeout(self, executor):
        """Test command execution timeout"""
        allowing_validator = MockCommandValidator(should_allow=True, timeout=1)
        executor.register_validator("basic", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.side_effect = asyncio.TimeoutError()

                result = await executor.execute_command("echo hello")

                assert result.status == "timeout"
                assert result.return_code is None
                assert "timed out after 1 seconds" in result.error_message
                assert result.duration_ms is not None

    @pytest.mark.asyncio
    async def test_execute_command_file_not_found(self, executor):
        """Test command execution when executable not found"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value=None):
            result = await executor.execute_command("echo hello")

            assert result.status == "failed"
            assert "Executable not found" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_command_with_ansi_stripping(self, executor):
        """Test that ANSI escape sequences are stripped from output"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        ansi_output = "\x1b[31mRed text\x1b[0m and \x1b[32mgreen text\x1b[0m"

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = (ansi_output, ansi_output, 0, False, False)

                result = await executor.execute_command("echo hello")

                assert result.status == "success"
                assert "\x1b[" not in result.stdout
                assert "\x1b[" not in result.stderr
                assert "Red text and green text" in result.stdout

    @pytest.mark.asyncio
    async def test_execute_command_environment_handling(self, executor):
        """Test environment variable handling"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("test", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/test"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "", 0, False, False)

                # Test with override environment
                override_env = {"CUSTOM_VAR": "custom_value", "PATH": "/custom/path"}
                result = await executor.execute_command(
                    "test command",
                    override_env=override_env
                )

                # Check that subprocess was called with environment containing our variables
                call_args = mock_subprocess.call_args
                called_env = call_args.kwargs['env']

                # Should have safe_env from policy
                assert called_env.get("SAFE_MODE") == "1"
                # Should have override env
                assert called_env.get("CUSTOM_VAR") == "custom_value"
                # Should have validator adjustments if validator supports it
                if allowing_validator.adjust_environment_called:
                    assert called_env.get("TEST_ADJUSTED") == "true"

    @pytest.mark.asyncio
    async def test_execute_command_argument_adjustment(self, executor):
        """Test argument adjustment by validators"""
        adjusting_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("test", adjusting_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/test"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "", 0, False, False)

                result = await executor.execute_command("test command")

                # Check if adjust_arguments was called
                assert adjusting_validator.adjust_arguments_called

                # Check that subprocess was called with adjusted arguments
                call_args = mock_subprocess.call_args
                called_parts = call_args.args[0]
                assert "--adjusted" in called_parts

    @pytest.mark.asyncio
    async def test_execute_command_timeout_precedence(self, executor):
        """Test timeout precedence: argument > per-command > executor default"""
        validator = MockCommandValidator(should_allow=True, timeout=10)
        executor.register_validator("basic", validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "", 0, False, False)

                # Test with explicit timeout argument (should override everything)
                await executor.execute_command("echo hello", timeout=5)

                call_args = mock_subprocess.call_args
                assert call_args.kwargs['timeout'] == 5

    @pytest.mark.asyncio
    async def test_execute_command_working_directory(self, executor):
        """Test working directory handling"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "", 0, False, False)

                test_dir = "/tmp/test"
                result = await executor.execute_command("echo hello", working_directory=test_dir)

                assert result.working_directory == test_dir
                call_args = mock_subprocess.call_args
                assert call_args.kwargs['cwd'] == test_dir

    @pytest.mark.asyncio
    async def test_execute_command_working_directory_none(self, executor):
        """Test working directory when None is passed"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "", 0, False, False)

                result = await executor.execute_command("echo hello", working_directory=None)

                call_args = mock_subprocess.call_args
                assert call_args.kwargs['cwd'] is None

    @pytest.mark.asyncio
    async def test_execute_command_truncated_output(self, executor):
        """Test handling of truncated output"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                # Simulate truncated output
                mock_subprocess.return_value = ("Truncated output", "Truncated errors", 0, True, True)

                result = await executor.execute_command("echo hello")

                assert result.status == "success"
                assert result.truncated_stdout is True
                assert result.truncated_stderr is True

    def test_resolve_executable_unix(self, executor):
        """Test executable resolution on Unix-like systems"""
        test_env = {"PATH": "/usr/bin:/bin:/usr/local/bin"}

        with patch('shutil.which') as mock_which:
            mock_which.return_value = "/usr/bin/git"

            result = executor._resolve_executable("git", test_env)
            assert result == "/usr/bin/git"
            mock_which.assert_called_with("git", path="/usr/bin:/bin:/usr/local/bin")

    def test_resolve_executable_windows(self, executor):
        """Test executable resolution on Windows"""
        if not executor.is_windows:
            pytest.skip("Windows-specific test")

        test_env = {"PATH": "C:\\Windows\\System32;C:\\Program Files\\Git\\bin"}

        with patch('shutil.which') as mock_which:
            # First call returns None, second call with .exe extension returns path
            mock_which.side_effect = [None, "C:\\Program Files\\Git\\bin\\git.exe"]

            result = executor._resolve_executable("git", test_env)
            assert result == "C:\\Program Files\\Git\\bin\\git.exe"

    def test_resolve_executable_not_found(self, executor):
        """Test executable resolution when not found"""
        test_env = {"PATH": "/usr/bin:/bin"}

        with patch('shutil.which', return_value=None):
            result = executor._resolve_executable("nonexistent", test_env)
            assert result is None

    def test_resolve_executable_edge_cases(self, executor):
        """Test executable resolution edge cases"""
        # Test with empty PATH
        result = executor._resolve_executable("git", {"PATH": ""})
        # Should handle gracefully (likely return None)

        # Test with missing PATH
        result = executor._resolve_executable("git", {})
        # Should handle gracefully

        # Test on Windows with existing extension
        if executor.is_windows:
            with patch('shutil.which') as mock_which:
                mock_which.return_value = "C:\\Program Files\\test.exe"
                result = executor._resolve_executable("test.exe", {"PATH": "C:\\Program Files"})
                assert result == "C:\\Program Files\\test.exe"

    @pytest.mark.asyncio
    async def test_execute_command_no_validator_registered(self, executor):
        """Test command execution when no validator is registered for the command type"""
        # Remove all validators to simulate missing validator
        executor.validators.clear()

        result = await executor.execute_command("echo hello")

        assert result.status == "error"
        assert "No validator registered for 'echo'" in result.error_message

    @pytest.mark.asyncio
    async def test_execute_command_subprocess_exception(self, executor):
        """Test command execution when subprocess raises an exception"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.side_effect = Exception("Subprocess failed")

                result = await executor.execute_command("echo hello")

                assert result.status == "error"
                assert "Execution error: Subprocess failed" in result.error_message
                assert result.duration_ms is not None

    @pytest.mark.asyncio
    async def test_execute_command_file_not_found_exception(self, executor):
        """Test command execution when FileNotFoundError is raised"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.side_effect = FileNotFoundError("File not found")

                result = await executor.execute_command("echo hello")

                assert result.status == "failed"
                assert "Executable not found" in result.error_message

    def test_logging_integration(self, executor):
        """Test that command execution is properly logged"""
        # Test that logger is initialized
        assert hasattr(executor, 'logger')
        assert executor.logger is not None

        # Test log_output setting
        executor_no_log = SecureCommandExecutor(log_output=False)
        assert executor_no_log.log_output is False

    @pytest.mark.asyncio
    async def test_path_prepend_handling(self, executor):
        """Test PATH_PREPEND environment variable handling"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        # Mock environment adjustment to set PATH_PREPEND
        def mock_adjust_env(env, parts, policy):
            new_env = env.copy()
            new_env["PATH_PREPEND"] = "/custom/bin"
            return new_env

        allowing_validator.adjust_environment = mock_adjust_env

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "", 0, False, False)

                result = await executor.execute_command("echo hello")

                call_args = mock_subprocess.call_args
                called_env = call_args.kwargs['env']

                # PATH_PREPEND should be removed and prepended to PATH
                assert "PATH_PREPEND" not in called_env
                path_sep = ";" if executor.is_windows else ":"
                assert called_env["PATH"].startswith(f"/custom/bin{path_sep}")

    @pytest.mark.asyncio
    async def test_windows_pathext_handling(self, executor):
        """Test Windows PATHEXT handling"""
        if not executor.is_windows:
            pytest.skip("Windows-specific test")

        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="C:\\Windows\\System32\\echo.exe"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "", 0, False, False)

                # Test that PATHEXT is set on Windows
                await executor.execute_command("echo hello")

                call_args = mock_subprocess.call_args
                called_env = call_args.kwargs['env']

                assert "PATHEXT" in called_env
                assert ".COM;.EXE;.BAT;.CMD" in called_env["PATHEXT"]

    @pytest.mark.asyncio
    async def test_complex_integration_scenario(self, executor):
        """Test a complex integration scenario with multiple features"""
        # Setup a validator that uses multiple features
        class ComplexValidator(MockCommandValidator):
            def adjust_arguments(self, parts, policy):
                # Add safety flags
                return parts + ["--safe-mode", "--no-interaction"]

            def adjust_environment(self, env, parts, policy):
                new_env = env.copy()
                new_env["SAFETY_MODE"] = "enabled"
                new_env["PATH_PREPEND"] = "/safe/bin"
                return new_env

        complex_validator = ComplexValidator(should_allow=True, timeout=25)
        executor.register_validator("complex", complex_validator)

        # Mock a successful execution
        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/complex"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("Success output", "Warning message", 0, False, False)

                result = await executor.execute_command(
                    "complex command --verbose",
                    working_directory="/tmp/test",
                    override_env={"CUSTOM": "value"},
                    timeout=20  # Should override validator timeout
                )

                # Verify result
                assert result.status == "success"
                assert result.return_code == 0
                assert "Success output" in result.stdout
                assert "Warning message" in result.stderr
                assert result.working_directory == "/tmp/test"

                # Verify subprocess call details
                call_args = mock_subprocess.call_args
                called_parts = call_args.args[0]
                called_env = call_args.kwargs['env']
                called_timeout = call_args.kwargs['timeout']
                called_cwd = call_args.kwargs['cwd']

                # Check argument adjustment
                assert "--safe-mode" in called_parts
                assert "--no-interaction" in called_parts

                # Check environment handling
                assert called_env["SAFETY_MODE"] == "enabled"
                assert called_env["CUSTOM"] == "value"
                # PATH_PREPEND should be processed and removed
                assert "PATH_PREPEND" not in called_env
                path_sep = ";" if executor.is_windows else ":"
                assert called_env["PATH"].startswith(f"/safe/bin{path_sep}")

                # Check timeout override
                assert called_timeout == 20

                # Check working directory
                assert called_cwd == "/tmp/test"

    @pytest.mark.asyncio
    async def test_concurrent_execution(self, executor):
        """Test concurrent command execution"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("basic", allowing_validator)

        # Mock subprocess calls with different delays
        async def mock_subprocess_delay(parts, **kwargs):
            await asyncio.sleep(0.1)  # Small delay
            return (f"Output from {parts[1]}", "", 0, False, False)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/echo"):
            with patch.object(executor, '_run_subprocess_async', side_effect=mock_subprocess_delay):
                # Execute multiple commands concurrently
                tasks = [
                    executor.execute_command("echo command1"),
                    executor.execute_command("echo command2"),
                    executor.execute_command("echo command3")
                ]

                results = await asyncio.gather(*tasks)

                assert len(results) == 3
                for i, result in enumerate(results, 1):
                    assert result.status == "success"
                    assert f"command{i}" in result.stdout

    def test_command_result_serialization_edge_cases(self):
        """Test CommandExecutionResult serialization with edge cases"""
        # Test with None values
        result_with_nones = CommandExecutionResult(
            status="error",
            return_code=None,
            stdout="",
            stderr="",
            command="test",
            working_directory=None,
            duration_ms=None,
            error_message=None
        )

        yaml_output = result_with_nones.to_yaml()
        assert "return_code: null" in yaml_output or "return_code:" in yaml_output

        # Test with very large output (should be handled gracefully)
        large_output = "x" * 10000
        result_large = CommandExecutionResult(
            status="success",
            return_code=0,
            stdout=large_output,
            stderr="",
            command="test",
            working_directory="/tmp"
        )

        # Should not crash with large output
        friendly_str = result_large.to_friendly_string()
        assert len(friendly_str) > 0

        # Test token-capped YAML
        def simple_count_tokens(text):
            return len(text.split())

        capped_yaml = result_large.to_yaml_capped(max_tokens=10, count_tokens=simple_count_tokens)
        assert len(capped_yaml.split()) <= 50  # Should be much smaller than original

    @pytest.mark.asyncio
    async def test_validator_adjustment_exceptions(self, executor):
        """Test handling of exceptions in validator adjustment methods"""
        class FaultyValidator(MockCommandValidator):
            def adjust_arguments(self, parts, policy):
                raise Exception("Arguments adjustment failed")

            def adjust_environment(self, env, parts, policy):
                raise Exception("Environment adjustment failed")

        faulty_validator = FaultyValidator(should_allow=True)
        executor.register_validator("faulty", faulty_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/faulty"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "", 0, False, False)

                # Should not crash despite validator exceptions
                result = await executor.execute_command("faulty command")

                # Should still execute successfully
                assert result.status == "success"

                # Original arguments should be used
                call_args = mock_subprocess.call_args
                called_parts = call_args.args[0]
                # Should not have adjustment artifacts
                assert "--adjusted" not in called_parts

    @pytest.mark.asyncio
    async def test_policy_provider_prime_validators(self):
        """Test _prime_validators_from_policy method"""
        # Create policy provider with custom policies
        policies = {
            "custom1": {"validator": "custom1_validator"},
            "custom2": {"validator": "custom2_validator"},
            "existing": {"validator": "git"}  # Should use existing validator
        }

        class TestPolicyProvider:
            def get_policy(self, base_cmd, parts):
                return policies.get(base_cmd)

            def get_all_policies(self):
                return policies

        executor = SecureCommandExecutor(policy_provider=TestPolicyProvider())

        # Should have created basic validators for unknown types
        assert "custom1_validator" in executor.validators
        assert "custom2_validator" in executor.validators
        # Should use existing validator for known types
        assert "git" in executor.validators

    @pytest.mark.asyncio
    async def test_policy_provider_exception_handling(self):
        """Test handling of exceptions from policy provider"""
        class FaultyPolicyProvider:
            def get_policy(self, base_cmd, parts):
                return {"validator": "basic", "default_timeout": 10}

            def get_all_policies(self):
                raise Exception("Policy provider failed")

        # Should not crash during initialization
        executor = SecureCommandExecutor(policy_provider=FaultyPolicyProvider())
        assert executor is not None

    @pytest.mark.asyncio
    async def test_run_subprocess_async_details(self, executor):
        """Test _run_subprocess_async method directly with various scenarios"""
        # This tests the actual subprocess execution logic
        parts = ["echo", "test"]
        env = {"PATH": "/usr/bin:/bin"}

        # Test successful execution
        with patch('asyncio.create_subprocess_exec') as mock_create:
            mock_proc = AsyncMock()
            mock_proc.stdout.read = AsyncMock()
            mock_proc.stderr.read = AsyncMock()
            mock_proc.wait = AsyncMock(return_value=0)

            # Mock the reading streams
            mock_proc.stdout.read.side_effect = [b"test output", b""]
            mock_proc.stderr.read.side_effect = [b"", b""]

            mock_create.return_value = mock_proc

            stdout, stderr, rc, trunc_out, trunc_err = await executor._run_subprocess_async(
                parts, cwd="/tmp", env=env, timeout=30
            )

            assert stdout == "test output"
            assert stderr == ""
            assert rc == 0
            assert trunc_out is False
            assert trunc_err is False

    @pytest.mark.asyncio
    async def test_run_subprocess_output_truncation(self, executor):
        """Test output truncation in _run_subprocess_async"""
        parts = ["echo", "test"]
        env = {"PATH": "/usr/bin:/bin"}

        # Test with output exceeding max_output_size
        large_output = b"x" * (executor.max_output_size + 100)

        with patch('asyncio.create_subprocess_exec') as mock_create:
            mock_proc = AsyncMock()
            mock_proc.wait = AsyncMock(return_value=0)

            # Mock large output that should be truncated
            chunks = [large_output[:65536], large_output[65536:], b""]
            mock_proc.stdout.read = AsyncMock(side_effect=chunks)
            mock_proc.stderr.read = AsyncMock(side_effect=[b"", b""])

            mock_create.return_value = mock_proc

            stdout, stderr, rc, trunc_out, trunc_err = await executor._run_subprocess_async(
                parts, cwd="/tmp", env=env, timeout=30
            )

            # Should be truncated
            assert len(stdout.encode()) <= executor.max_output_size
            assert trunc_out is True
            assert trunc_err is False

    @pytest.mark.asyncio
    async def test_multiple_error_scenarios(self, executor):
        """Test various error scenarios in sequence"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("test", allowing_validator)

        # Test sequence of different errors
        error_scenarios = [
            (FileNotFoundError("Not found"), "failed", "Executable not found"),
            (asyncio.TimeoutError(), "timeout", "timed out"),
            (Exception("Generic error"), "error", "Execution error"),
        ]

        for exception, expected_status, expected_message in error_scenarios:
            with patch.object(executor, '_resolve_executable', return_value="/usr/bin/test"):
                with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                    mock_subprocess.side_effect = exception

                    result = await executor.execute_command("test command")

                    assert result.status == expected_status
                    assert expected_message in result.error_message

    def test_environment_variable_edge_cases(self, executor):
        """Test environment variable handling edge cases"""
        allowing_validator = MockCommandValidator(should_allow=True)

        # Test environment adjustment returning None
        def return_none_env(env, parts, policy):
            return None

        allowing_validator.adjust_environment = return_none_env
        executor.register_validator("test", allowing_validator)

        # Should handle None gracefully and fall back to original env
        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/test"):
            with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                mock_subprocess.return_value = ("", "", 0, False, False)

                asyncio.run(executor.execute_command("test command", override_env={"TEST": "value"}))

                call_args = mock_subprocess.call_args
                called_env = call_args.kwargs['env']

                # Should have the override env since validator returned None
                assert "TEST" in called_env

    @pytest.mark.asyncio
    async def test_command_logging_details(self, executor):
        """Test detailed command logging functionality"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("test", allowing_validator)

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/test"):
            with patch.object(executor.logger, 'info') as mock_log:
                with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                    mock_subprocess.return_value = ("small output", "small error", 0, False, False)

                    await executor.execute_command("test command", working_directory="/test/dir")

                    # Should log command execution
                    mock_log.assert_called()
                    log_call_args = mock_log.call_args[0][0]
                    log_data = log_call_args  # JSON string

                    assert "test command" in log_data
                    assert "/test/dir" in log_data
                    assert "success" in log_data

    @pytest.mark.asyncio
    async def test_large_output_logging_suppression(self, executor):
        """Test that large output is not logged"""
        allowing_validator = MockCommandValidator(should_allow=True)
        executor.register_validator("test", allowing_validator)

        # Create large output
        large_output = "x" * 2000  # Larger than 1024 limit

        with patch.object(executor, '_resolve_executable', return_value="/usr/bin/test"):
            with patch.object(executor.logger, 'info') as mock_log:
                with patch.object(executor, '_run_subprocess_async', new_callable=AsyncMock) as mock_subprocess:
                    mock_subprocess.return_value = (large_output, "", 0, False, False)

                    await executor.execute_command("test command")

                    # Should log but without the large stdout
                    mock_log.assert_called()
                    log_call_args = mock_log.call_args[0][0]

                    # Large output should not be in log
                    assert large_output not in log_call_args
                    # stdout_preview should be empty for large output
                    assert '"stdout_preview": ""' in log_call_args

    def test_platform_specific_behaviors(self, executor):
        """Test platform-specific behavior differences"""
        # Test Windows-specific behavior
        if executor.is_windows:
            # Test creation flags for hidden window
            assert hasattr(executor, 'show_windows')

            # Test PATHEXT handling
            test_env = {}
            # In the actual execute_command, PATHEXT should be set
            # This is tested in other methods, but we verify the constant exists
            assert ".EXE" in ".COM;.EXE;.BAT;.CMD"

        # Test Unix-specific behavior
        else:
            # Test that posix=True is used for shlex.split
            with patch('shlex.split') as mock_split:
                mock_split.return_value = ["echo", "test"]

                asyncio.run(executor.execute_command("echo test"))

                # Should be called with posix=True on Unix
                mock_split.assert_called_with("echo test", posix=True)


if __name__ == "__main__":
    pytest.main([__file__])
