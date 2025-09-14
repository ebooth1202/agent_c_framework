import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from agent_c_tools.tools.workspace.dynamic_command import DynamicCommandTools
from agent_c_tools.tools.workspace.executors.local_storage.yaml_policy_provider import YamlPolicyProvider


class TestDynamicCommandErrorHandling:
    """Test error handling in DynamicCommandTools initialization"""

    @pytest.fixture
    def valid_policies(self):
        """Valid policy configurations that should work"""
        return {
            "git": {
                "description": "Read-only git operations",
                "flags": ["--version", "--help"],
                "subcommands": {
                    "status": {
                        "flags": ["--porcelain", "-s"]
                    }
                },
                "default_timeout": 30
            },
            "npm": {
                "description": "Safe npm operations",
                "flags": {
                    "--version": {},
                    "--help": {}
                },
                "default_timeout": 60
            }
        }

    @pytest.fixture
    def mixed_policies(self):
        """Mix of valid and invalid policy configurations"""
        return {
            "git": {
                "description": "Valid git policy",
                "flags": ["--version"],
                "default_timeout": 30
            },
            "invalid_cmd": {
                # This will cause build_command_instructions to fail
                "flags": "invalid_format_should_be_list_or_dict",
                "description": "This should fail"
            },
            "npm": {
                "description": "Valid npm policy",
                "flags": ["--version", "--help"],
                "default_timeout": 60
            },
            "another_invalid": {
                # Another invalid config that will cause an exception
                "subcommands": "also_invalid_should_be_dict",
                "description": "This will also fail"
            }
        }

    def test_all_valid_policies_load_successfully(self, valid_policies):
        """Test that all valid policies load without errors"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=valid_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions') as mock_build:
                    # Mock successful instruction building
                    mock_build.side_effect = lambda cmd, spec: f"Instructions for {cmd}"

                    # Mock the post_init and dependencies
                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            # Initialize DynamicCommandTools
                            tools = DynamicCommandTools()

                            # All valid policies should be loaded
                            assert len(tools.whitelisted_commands) == 2
                            assert "git" in tools.whitelisted_commands
                            assert "npm" in tools.whitelisted_commands
                            assert tools.whitelisted_commands["git"]["description"] == "Instructions for git"
                            assert tools.whitelisted_commands["npm"]["description"] == "Instructions for npm"

    def test_mixed_valid_invalid_policies_partial_load(self, mixed_policies):
        """Test that valid policies load while invalid ones are skipped"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=mixed_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions') as mock_build:
                    # Mock: valid commands succeed, invalid ones fail
                    def mock_instruction_builder(cmd, spec):
                        if cmd in ['invalid_cmd', 'another_invalid']:
                            raise ValueError(f"Invalid configuration for {cmd}")
                        return f"Instructions for {cmd}"

                    mock_build.side_effect = mock_instruction_builder

                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            # Initialize DynamicCommandTools
                            tools = DynamicCommandTools()

                            # Only valid policies should be loaded
                            assert len(tools.whitelisted_commands) == 2
                            assert "git" in tools.whitelisted_commands
                            assert "npm" in tools.whitelisted_commands
                            assert "invalid_cmd" not in tools.whitelisted_commands
                            assert "another_invalid" not in tools.whitelisted_commands

    def test_all_invalid_policies_empty_result(self):
        """Test that if all policies are invalid, we get empty whitelisted_commands"""
        invalid_policies = {
            "invalid1": {"flags": "not_a_list_or_dict"},
            "invalid2": {"subcommands": "not_a_dict"}
        }

        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=invalid_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions') as mock_build:
                    # All calls fail
                    mock_build.side_effect = ValueError("All configs are invalid")

                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            # Initialize DynamicCommandTools
                            tools = DynamicCommandTools()

                            # No commands should be loaded
                            assert len(tools.whitelisted_commands) == 0
                            assert tools.whitelisted_commands == {}

    def test_no_policies_available(self):
        """Test behavior when no policies are available"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value={}):
                with patch.object(DynamicCommandTools, 'post_init'):
                    with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                        # Initialize DynamicCommandTools
                        tools = DynamicCommandTools()

                        # Should have empty whitelisted_commands
                        assert len(tools.whitelisted_commands) == 0
                        assert tools.whitelisted_commands == {}

    def test_policy_provider_returns_none(self):
        """Test behavior when policy provider returns None"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=None):
                with patch.object(DynamicCommandTools, 'post_init'):
                    with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                        # Initialize DynamicCommandTools
                        tools = DynamicCommandTools()

                        # Should handle None gracefully and result in empty dict
                        assert len(tools.whitelisted_commands) == 0
                        assert tools.whitelisted_commands == {}

    def test_specific_exception_types_handled_gracefully(self, valid_policies):
        """Test that different exception types are handled gracefully"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=valid_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions') as mock_build:
                    # Different exception types for different commands
                    def mock_instruction_builder(cmd, spec):
                        if cmd == 'git':
                            raise KeyError("Missing required key")
                        elif cmd == 'npm':
                            raise TypeError("Invalid type for flags")
                        return f"Instructions for {cmd}"

                    mock_build.side_effect = mock_instruction_builder

                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            # Initialize DynamicCommandTools
                            tools = DynamicCommandTools()

                            # No commands should be loaded due to exceptions
                            assert len(tools.whitelisted_commands) == 0

    def test_create_dynamic_tools_called_with_valid_commands(self, valid_policies):
        """Test that _create_dynamic_tools is called with the commands that loaded successfully"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=valid_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions') as mock_build:
                    # First command succeeds, second fails
                    call_count = 0
                    def mock_instruction_builder(cmd, spec):
                        nonlocal call_count
                        call_count += 1
                        if call_count == 1:  # git succeeds
                            return f"Instructions for {cmd}"
                        else:  # npm fails
                            raise ValueError("Build failed")

                    mock_build.side_effect = mock_instruction_builder

                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            with patch.object(DynamicCommandTools, '_create_dynamic_tools') as mock_create:
                                # Initialize DynamicCommandTools
                                tools = DynamicCommandTools()

                                # _create_dynamic_tools should still be called
                                mock_create.assert_called_once()
                                
                                # Only one command should be in whitelisted_commands
                                assert len(tools.whitelisted_commands) == 1

    def test_error_handling_preserves_tool_functionality(self, valid_policies):
        """Test that error handling doesn't break the overall tool functionality"""
        # Add one invalid policy to valid ones
        mixed_policies = valid_policies.copy()
        mixed_policies["broken_cmd"] = {"invalid": "config"}

        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=mixed_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions') as mock_build:
                    def mock_instruction_builder(cmd, spec):
                        if cmd == "broken_cmd":
                            raise RuntimeError("Configuration error")
                        return f"Instructions for {cmd}"

                    mock_build.side_effect = mock_instruction_builder

                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            # Initialize DynamicCommandTools
                            tools = DynamicCommandTools()

                            # Valid commands should still be available
                            assert len(tools.whitelisted_commands) == 2
                            assert "git" in tools.whitelisted_commands
                            assert "npm" in tools.whitelisted_commands
                            assert "broken_cmd" not in tools.whitelisted_commands

                            # Tool should still have its basic properties
                            assert hasattr(tools, 'policy_provider')
                            assert hasattr(tools, 'whitelisted_commands')
                            assert tools.name == "commands"
                            assert tools.use_prefix is False

    def test_various_exception_types_handled(self):
        """Test that different types of build_command_instructions errors are handled"""
        policies_with_various_issues = {
            "syntax_error": {"flags": ["--valid"]},
            "type_error": {"flags": ["--also-valid"]},
            "value_error": {"flags": ["--another-valid"]},
        }

        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=policies_with_various_issues):
                with patch.object(YamlPolicyProvider, 'build_command_instructions') as mock_build:
                    # Different exception types for each command
                    def mock_instruction_builder(cmd, spec):
                        if cmd == "syntax_error":
                            raise SyntaxError("Invalid syntax in policy")
                        elif cmd == "type_error":
                            raise TypeError("Wrong type in configuration")
                        elif cmd == "value_error":
                            raise ValueError("Invalid value in policy")
                        return f"Instructions for {cmd}"

                    mock_build.side_effect = mock_instruction_builder

                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            # Initialize DynamicCommandTools
                            tools = DynamicCommandTools()

                            # No commands should be loaded due to all failing
                            assert len(tools.whitelisted_commands) == 0

    def test_build_command_instructions_continues_after_errors(self):
        """Test that build_command_instructions errors don't stop processing other commands"""
        policies = {
            "first_cmd": {"flags": ["--valid"]},
            "failing_cmd": {"flags": ["--also-valid"]},
            "last_cmd": {"flags": ["--another-valid"]},
        }

        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions') as mock_build:
                    # Only middle command fails
                    def mock_instruction_builder(cmd, spec):
                        if cmd == "failing_cmd":
                            raise ValueError("This command fails")
                        return f"Instructions for {cmd}"

                    mock_build.side_effect = mock_instruction_builder

                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            # Initialize DynamicCommandTools
                            tools = DynamicCommandTools()

                            # Two commands should be loaded (first and last)
                            assert len(tools.whitelisted_commands) == 2
                            assert "first_cmd" in tools.whitelisted_commands
                            assert "last_cmd" in tools.whitelisted_commands
                            assert "failing_cmd" not in tools.whitelisted_commands
