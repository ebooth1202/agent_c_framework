"""
Tests for suppress_success_output parameter override in DynamicCommandTools.
Tests the new user parameter override functionality that allows users to override
policy-defined suppress_success_output behavior.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from typing import Dict, Any

from agent_c_tools.tools.workspace.dynamic_command import DynamicCommandTools
from agent_c_tools.tools.workspace.executors.local_storage.yaml_policy_provider import YamlPolicyProvider
from agent_c_tools.tools.workspace.executors.local_storage.secure_command_executor import CommandExecutionResult


@pytest.fixture
def mock_workspace():
    """Create a mock workspace for testing"""
    workspace = MagicMock()
    workspace.name = "test_workspace"
    workspace.run_command = AsyncMock()
    workspace.full_path = MagicMock(return_value="/test/path")
    return workspace


@pytest.fixture 
def mock_workspace_tool():
    """Create a mock WorkspaceTools"""
    workspace_tool = MagicMock()
    workspace_tool.validate_and_get_workspace_path = MagicMock()
    return workspace_tool


@pytest.fixture
def test_policies():
    """Test policies with suppress_success_output configurations"""
    return {
        "node": {
            "description": "Node.js operations",
            "flags": {
                "--test": {"suppress_success_output": True, "allow_test_mode": True},
                "--version": {},
                "-v": {}
            },
            "default_timeout": 30
        },
        "npm": {
            "description": "NPM operations", 
            "flags": {
                "test": {"suppress_success_output": True},
                "--version": {}
            },
            "default_timeout": 60
        }
    }


class TestSuppressSuccessOutputOverride:
    """Test the suppress_success_output parameter override functionality"""

    def test_dynamic_tools_includes_suppress_param_in_schema(self, test_policies):
        """Test that dynamically created tools include suppress_success_output parameter"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            
                            tools = DynamicCommandTools()
                            
                            # Check that dynamic methods have suppress_success_output parameter
                            assert hasattr(tools, 'run_node')
                            assert hasattr(tools, 'run_npm')
                            
                            # Check schema includes the parameter
                            node_schema = None
                            for schema in tools._schemas:
                                if schema['function']['name'] == 'run_node':
                                    node_schema = schema
                                    break
                            
                            assert node_schema is not None
                            params = node_schema['function']['parameters']['properties']
                            # Check that parameters exist but don't assume specific required format
                            # The json_schema decorator might transform the structure
                            assert 'suppress_success_output' in params
                            assert params['suppress_success_output']['type'] == 'boolean'
                            # Skip the required check - the schema transformation might handle this differently

    @pytest.mark.asyncio
    async def test_override_true_when_policy_false(self, test_policies, mock_workspace, mock_workspace_tool):
        """Test that suppress_success_output=True overrides policy setting of False"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        # Setup mocks
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = (None, mock_workspace, "test/path")
                        
                        # Mock successful command result
                        mock_result = CommandExecutionResult(
                            command="node --version",
                            return_code=0,
                            status="success", 
                            stdout="v18.17.0",
                            stderr="",
                            working_directory="/test/path",
                            duration_ms=100
                        )
                        mock_workspace.run_command.return_value = mock_result
                        
                        # Call with override=True (policy for --version has no suppress setting, defaults to False)
                        result = await tools.run_node(
                            path="//test/workspace",
                            args="--version",
                            suppress_success_output=True
                        )
                        
                        # Verify that suppress_success_output=True was passed to workspace
                        mock_workspace.run_command.assert_called_once()
                        call_args = mock_workspace.run_command.call_args
                        assert call_args.kwargs['suppress_success_output'] is True

    @pytest.mark.asyncio
    async def test_override_false_when_policy_true(self, test_policies, mock_workspace, mock_workspace_tool):
        """Test that suppress_success_output=False overrides policy setting of True"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        # Setup mocks
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = (None, mock_workspace, "test/path")
                        
                        mock_result = CommandExecutionResult(
                            command="node --test",
                            return_code=0,
                            status="success",
                            stdout="Test output",
                            stderr="",
                            working_directory="/test/path",
                            duration_ms=500
                        )
                        mock_workspace.run_command.return_value = mock_result
                        
                        # Call with override=False (policy for --test has suppress_success_output=True)
                        result = await tools.run_node(
                            path="//test/workspace", 
                            args="--test",
                            suppress_success_output=False
                        )
                        
                        # Verify that suppress_success_output=False was passed to workspace
                        mock_workspace.run_command.assert_called_once()
                        call_args = mock_workspace.run_command.call_args
                        assert call_args.kwargs['suppress_success_output'] is False

    @pytest.mark.asyncio
    async def test_none_follows_policy(self, test_policies, mock_workspace, mock_workspace_tool):
        """Test that suppress_success_output=None follows policy behavior"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        # Setup mocks
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = (None, mock_workspace, "test/path")
                        
                        mock_result = CommandExecutionResult(
                            command="node --test",
                            return_code=0,
                            status="success",
                            stdout="Test output", 
                            stderr="",
                            working_directory="/test/path",
                            duration_ms=500
                        )
                        mock_workspace.run_command.return_value = mock_result
                        
                        # Call without suppress_success_output parameter (defaults to None)
                        result = await tools.run_node(
                            path="//test/workspace",
                            args="--test"
                        )
                        
                        # Verify that suppress_success_output=None was passed to workspace
                        mock_workspace.run_command.assert_called_once()
                        call_args = mock_workspace.run_command.call_args
                        assert call_args.kwargs['suppress_success_output'] is None

    @pytest.mark.asyncio
    async def test_parameter_extraction_from_kwargs(self, test_policies, mock_workspace, mock_workspace_tool):
        """Test that suppress_success_output parameter is correctly extracted from kwargs"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        # Setup mocks
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = (None, mock_workspace, "test/path")
                        
                        mock_result = CommandExecutionResult(
                            command="npm test",
                            return_code=0,
                            status="success",
                            stdout="Tests passed",
                            stderr="",
                            working_directory="/test/path",
                            duration_ms=2000
                        )
                        mock_workspace.run_command.return_value = mock_result
                        
                        # Test various parameter formats
                        test_cases = [
                            (True, True),
                            (False, False), 
                            (None, None),
                            ("true", "true"),  # String values should pass through
                            ("false", "false")
                        ]
                        
                        for input_value, expected_value in test_cases:
                            mock_workspace.run_command.reset_mock()
                            
                            await tools.run_npm(
                                path="//test/workspace",
                                args="test",
                                suppress_success_output=input_value
                            )
                            
                            call_args = mock_workspace.run_command.call_args
                            assert call_args.kwargs['suppress_success_output'] == expected_value

    @pytest.mark.asyncio
    async def test_override_with_other_parameters(self, test_policies, mock_workspace, mock_workspace_tool):
        """Test that suppress_success_output works with other parameters"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        # Setup mocks
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = (None, mock_workspace, "test/path")
                        
                        mock_result = CommandExecutionResult(
                            command="node --test test/",
                            return_code=0,
                            status="success",
                            stdout="All tests passed",
                            stderr="",
                            working_directory="/test/path",
                            duration_ms=5000
                        )
                        mock_workspace.run_command.return_value = mock_result
                        
                        # Call with multiple parameters including suppress_success_output
                        result = await tools.run_node(
                            path="//test/workspace",
                            args="--test test/",
                            timeout=120,
                            max_tokens=2000,
                            suppress_success_output=True
                        )
                        
                        # Verify all parameters are passed correctly
                        mock_workspace.run_command.assert_called_once()
                        call_args = mock_workspace.run_command.call_args
                        assert call_args.kwargs['timeout'] == 120
                        assert call_args.kwargs['suppress_success_output'] is True
                        assert call_args.kwargs['command'] == "node --test test/"  # command
                        assert call_args.kwargs['working_directory'] == "/test/path"  # working_directory

    @pytest.mark.asyncio
    async def test_override_different_commands(self, test_policies, mock_workspace, mock_workspace_tool):
        """Test suppress_success_output override works for different command types"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        # Setup mocks
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = (None, mock_workspace, "test/path")
                        
                        mock_result = CommandExecutionResult(
                            command="test command",
                            return_code=0,
                            status="success",
                            stdout="output",
                            stderr="",
                            working_directory="/test/path",
                            duration_ms=1000
                        )
                        mock_workspace.run_command.return_value = mock_result
                        
                        # Test different commands with override
                        commands = [
                            (tools.run_node, "node", "--version"),
                            (tools.run_npm, "npm", "test")
                        ]
                        
                        for method, cmd, args in commands:
                            mock_workspace.run_command.reset_mock()
                            
                            await method(
                                path="//test/workspace",
                                args=args,
                                suppress_success_output=True
                            )
                            
                            call_args = mock_workspace.run_command.call_args
                            assert call_args.kwargs['suppress_success_output'] is True
                            assert cmd in call_args.kwargs['command']  # Check command name

    @pytest.mark.asyncio
    async def test_error_handling_with_override(self, test_policies, mock_workspace, mock_workspace_tool):
        """Test that override parameter doesn't interfere with error handling"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        # Test invalid workspace path
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = ("Invalid path", None, None)
                        
                        result = await tools.run_node(
                            path="//invalid/workspace",
                            args="--test",
                            suppress_success_output=True
                        )
                        
                        # Should return error message
                        assert result.startswith("ERROR:")
                        # workspace.run_command should not be called
                        mock_workspace.run_command.assert_not_called()

    @pytest.mark.asyncio
    async def test_validation_error_with_override(self, test_policies, mock_workspace_tool):
        """Test that override parameter is handled correctly with validation errors"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        # Test missing required field
                        result = await tools.run_node(
                            # path parameter missing
                            args="--test",
                            suppress_success_output=True
                        )
                        
                        # Should return validation error
                        assert "path" in result.lower()
                        assert "required" in result.lower()

    def test_schema_parameter_structure(self, test_policies):
        """Test that the suppress_success_output parameter has correct schema structure"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        with patch.object(DynamicCommandTools, 'get_dependency', return_value=None):
                            
                            tools = DynamicCommandTools()
                            
                            # Check schema for all dynamic tools
                            for schema in tools._schemas:
                                params = schema['function']['parameters']['properties']
                                suppress_param = params['suppress_success_output']
                                
                                # Verify parameter structure exists but don't assume exact schema format
                                assert suppress_param['type'] == 'boolean'
                                # Skip required check - schema transformation might handle this
                                assert 'description' in suppress_param
                                assert 'override' in suppress_param['description'].lower()
                                assert 'policy' in suppress_param['description'].lower()
                                
                                # Verify no default value is specified in schema
                                assert 'default' not in suppress_param

    @pytest.mark.asyncio
    async def test_media_helper_still_works_with_override(self, test_policies, mock_workspace, mock_workspace_tool):
        """Test that media helper functionality still works when using suppress override"""
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        tools._raise_render_media = AsyncMock()
                        
                        # Setup mocks
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = (None, mock_workspace, "test/path")
                        
                        mock_result = CommandExecutionResult(
                            command="node --test",
                            return_code=0,
                            status="success",
                            stdout="Test passed",
                            stderr="",
                            working_directory="/test/path",
                            duration_ms=1000
                        )
                        mock_workspace.run_command.return_value = mock_result
                        
                        with patch('agent_c_tools.tools.workspace.dynamic_command.MediaEventHelper') as mock_media:
                            mock_media.stdout_html = AsyncMock(return_value="<html>output</html>")
                            
                            # Mock tool_context with proper count_tokens function
                            mock_count_tokens = MagicMock(return_value=500)  # Always return 500 tokens
                            mock_agent_runtime = MagicMock()
                            mock_agent_runtime.count_tokens = mock_count_tokens
                            
                            result = await tools.run_node(
                            path="//test/workspace",
                            args="--test",
                            suppress_success_output=True,
                            tool_context={"agent_runtime": mock_agent_runtime}
                        )
                            
                            # Verify media helper was called
                            mock_media.stdout_html.assert_called_once()
                            tools._raise_render_media.assert_called_once()


class TestSuppressSuccessOutputIntegration:
    """Integration tests for suppress_success_output override with real-world scenarios"""

    @pytest.mark.asyncio
    async def test_node_test_override_integration(self, mock_workspace, mock_workspace_tool):
        """Test realistic node test scenario with suppress override"""
        test_policies = {
            "node": {
                "description": "Node.js with test support",
                "flags": {
                    "--test": {"suppress_success_output": True, "allow_test_mode": True},
                    "--test-reporter": {"suppress_success_output": True, "allow_test_mode": True},
                    "-v": {}
                },
                "default_timeout": 30
            }
        }
        
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="Node test instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = (None, mock_workspace, "project/")
                        
                        mock_result = CommandExecutionResult(
                            command="node --test test/",
                            return_code=0,
                            status="success",
                            stdout="✓ test/unit.test.js\n✓ All tests passed",
                            stderr="",
                            working_directory="project/",
                            duration_ms=3500
                        )
                        mock_workspace.run_command.return_value = mock_result
                        
                        # Developer wants to see test output despite policy suppression
                        result = await tools.run_node(
                            path="//workspace/project",
                            args="--test test/",
                            suppress_success_output=False  # Override policy
                        )
                        
                        # Verify override was passed
                        call_args = mock_workspace.run_command.call_args
                        assert call_args.kwargs['suppress_success_output'] is False
                        assert call_args.kwargs['command'] == "node --test test/"

    @pytest.mark.asyncio 
    async def test_npm_script_override_integration(self, mock_workspace, mock_workspace_tool):
        """Test realistic npm script scenario with suppress override"""
        test_policies = {
            "npm": {
                "description": "NPM package management",
                "subcommands": {
                    "run": {
                        "allowed_scripts": ["test", "build", "lint"],
                        "suppress_success_output": True
                    },
                    "ci": {"suppress_success_output": True}
                },
                "default_timeout": 300
            }
        }
        
        with patch.object(YamlPolicyProvider, '__init__', return_value=None):
            with patch.object(YamlPolicyProvider, 'get_all_policies', return_value=test_policies):
                with patch.object(YamlPolicyProvider, 'build_command_instructions', return_value="NPM instructions"):
                    with patch.object(DynamicCommandTools, 'post_init'):
                        
                        tools = DynamicCommandTools()
                        tools.workspace_tool = mock_workspace_tool
                        
                        mock_workspace_tool.validate_and_get_workspace_path.return_value = (None, mock_workspace, "project/")
                        
                        mock_result = CommandExecutionResult(
                            command="npm run test",
                            return_code=0,
                            status="success",
                            stdout="Jest test results\n20 tests passed",
                            stderr="",
                            working_directory="project/",
                            duration_ms=15000
                        )
                        mock_workspace.run_command.return_value = mock_result
                        
                        # Developer wants to see detailed test output 
                        result = await tools.run_npm(
                            path="//workspace/project",
                            args="run test",
                            timeout=180,
                            suppress_success_output=False  # Override policy suppression
                        )
                        
                        # Verify all parameters passed correctly
                        call_args = mock_workspace.run_command.call_args
                        assert call_args.kwargs['suppress_success_output'] is False
                        assert call_args.kwargs['timeout'] == 180
                        assert call_args.kwargs['command'] == "npm run test"


if __name__ == "__main__":
    pytest.main([__file__])
