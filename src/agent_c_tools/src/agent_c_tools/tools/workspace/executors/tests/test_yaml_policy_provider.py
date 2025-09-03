import pytest
import os
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, MagicMock
from agent_c_tools.tools.workspace.executors.local_storage.yaml_policy_provider import YamlPolicyProvider


class TestYamlPolicyProvider:
    """Comprehensive test suite for YamlPolicyProvider"""

    @pytest.fixture
    def sample_policies(self):
        """Sample policy data for testing"""
        return {
            "git": {
                "description": "Read-only/metadata git operations (no mutations).",
                "subcommands": {
                    "status": {
                        "flags": ["--porcelain", "-s", "-b", "--no-color"],
                        "timeout": 20
                    },
                    "log": {
                        "flags": ["--oneline", "--graph", "--decorate", "-n", "-p", "--no-color"],
                        "timeout": 30
                    }
                },
                "deny_global_flags": ["-c", "--exec-path", "--help", "-P"],
                "safe_env": {"GIT_TERMINAL_PROMPT": "0", "GIT_CONFIG_NOSYSTEM": "1"},
                "env_overrides": {"GIT_PAGER": "cat", "CLICOLOR": "0"},
                "default_timeout": 30
            },
            "npm": {
                "validator": "npm",
                "root_flags": ["-v", "--version", "--help"],
                "subcommands": {
                    "ci": {
                        "enabled": True,
                        "require_no_packages": True,
                        "require_flags": ["--ignore-scripts"],
                        "allowed_flags": ["--ignore-scripts", "--no-audit", "--no-fund", "--prefer-offline", "--cache"]
                    },
                    "install": {
                        "enabled": False
                    },
                    "run": {
                        "allowed_scripts": ["build", "test", "lint", "format", "typecheck", "lint:fix", "test:run"],
                        "deny_args": False
                    },
                    "config": {
                        "get_only": True,
                        "allowed_flags": []
                    }
                },
                "deny_subcommands": ["exec", "publish", "update", "audit", "ci-info", "token", "login"],
                "default_timeout": 120,
                "env_overrides": {
                    "NPM_CONFIG_COLOR": "false",
                    "NPM_CONFIG_PROGRESS": "false",
                    "NO_COLOR": "1",
                    "CI": "1"
                }
            },
            "npx": {
                "validator": "npx",
                "flags": ["--yes", "-y", "--package", "-p", "--call", "-c", "--shell", "-s"],
                "allowed_packages": ["@angular/cli", "create-react-app", "typescript", "eslint", "prettier"],
                "command_aliases": {"typescript": ["tsc"]},
                "default_timeout": 120,
                "env_overrides": {"NO_COLOR": "1", "CI": "1"}
            },
            "pytest": {
                "flags": ["-q", "--maxfail", "--disable-warnings", "--color"],
                "default_timeout": 120,
                "env_overrides": {
                    "PYTHONDONTWRITEBYTECODE": "1",
                    "PYTEST_ADDOPTS": "-q --color=no --maxfail=1",
                    "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"
                }
            }
        }

    @pytest.fixture
    def temp_config_dir(self, sample_policies):
        """Create a temporary configuration directory with policy file"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_dir = Path(temp_dir)
            policy_file = config_dir / "whitelist_commands.yaml"

            with open(policy_file, 'w') as f:
                yaml.dump(sample_policies, f)

            yield config_dir

    @pytest.fixture
    def temp_policy_file(self, sample_policies):
        """Create a temporary policy file"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(sample_policies, f)
            temp_file = Path(f.name)

        yield temp_file
        temp_file.unlink()

    def test_init_with_config_path(self, temp_config_dir):
        """Test initialization with explicit config path"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        assert provider.config_path == str(temp_config_dir)
        assert provider.policy_filename == "whitelist_commands.yaml"
        assert provider.policy_file_path == temp_config_dir / "whitelist_commands.yaml"

    def test_init_with_custom_filename(self, temp_config_dir):
        """Test initialization with custom policy filename"""
        custom_filename = "custom_policies.yaml"

        # Create the custom file
        custom_file = temp_config_dir / custom_filename
        custom_file.write_text("test: {}")

        provider = YamlPolicyProvider(config_path=str(temp_config_dir), policy_filename=custom_filename)

        assert provider.policy_filename == custom_filename
        assert provider.policy_file_path == temp_config_dir / custom_filename

    def test_env_override_policy_path(self, temp_config_dir):
        """Test environment variable override for policy file path"""
        # Create a temporary file to use as the override path
        temp_override_file = temp_config_dir / "override_policies.yaml"
        temp_override_file.write_text("test_override: {}")

        with patch.dict(os.environ, {"AGENTC_POLICIES_FILE": str(temp_override_file)}):
            provider = YamlPolicyProvider()

            # Should use the environment override path
            assert provider.policy_file_path == temp_override_file

    def test_get_policy_success(self, temp_config_dir):
        """Test successful policy retrieval"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        git_policy = provider.get_policy("git")
        assert git_policy is not None
        assert git_policy["description"] == "Read-only/metadata git operations (no mutations)."
        assert "subcommands" in git_policy
        assert git_policy["default_timeout"] == 30

    def test_get_policy_case_insensitive(self, temp_config_dir):
        """Test that policy retrieval is case insensitive"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        git_policy_lower = provider.get_policy("git")
        git_policy_upper = provider.get_policy("GIT")
        git_policy_mixed = provider.get_policy("Git")

        assert git_policy_lower == git_policy_upper == git_policy_mixed

    def test_get_policy_not_found(self, temp_config_dir):
        """Test policy retrieval for non-existent command"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        result = provider.get_policy("nonexistent")
        assert result is None

    def test_get_policy_file_not_found(self):
        """Test behavior when policy file doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            provider = YamlPolicyProvider(config_path=temp_dir)

            result = provider.get_policy("git")
            assert result is None

    def test_has_policy(self, temp_config_dir):
        """Test has_policy method"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        assert provider.has_policy("git") is True
        assert provider.has_policy("npm") is True
        assert provider.has_policy("nonexistent") is False

    def test_get_all_policies(self, temp_config_dir, sample_policies):
        """Test retrieving all policies"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        all_policies = provider.get_all_policies()

        assert len(all_policies) == len(sample_policies)
        assert "git" in all_policies
        assert "npm" in all_policies
        assert "npx" in all_policies
        assert "pytest" in all_policies

    def test_caching_behavior(self, temp_config_dir):
        """Test that policies are cached and not reloaded unnecessarily"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        # First call should load the file
        policy1 = provider.get_policy("git")

        # Mock the file loading to ensure it's not called again
        with patch.object(provider, '_ensure_policy_loaded', return_value=True) as mock_load:
            mock_load.return_value = True
            policy2 = provider.get_policy("git")

            # Should use cached version
            assert policy1 == policy2

    def test_reload_policy(self, temp_config_dir, sample_policies):
        """Test policy reload functionality"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        # Load initial policy
        initial_policy = provider.get_policy("git")
        assert initial_policy is not None

        # Modify the policy file
        modified_policies = sample_policies.copy()
        modified_policies["git"]["description"] = "Modified description"

        policy_file = temp_config_dir / "whitelist_commands.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(modified_policies, f)

        # Reload and verify changes
        success = provider.reload_policy()
        assert success is True

        reloaded_policy = provider.get_policy("git")
        assert reloaded_policy["description"] == "Modified description"

    def test_yaml_error_handling(self, temp_config_dir):
        """Test handling of malformed YAML"""
        # Create malformed YAML file
        policy_file = temp_config_dir / "whitelist_commands.yaml"
        policy_file.write_text("invalid: yaml: content: [")

        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        with pytest.raises(yaml.YAMLError):
            provider.get_policy("git")

    def test_unicode_encoding_handling(self, temp_config_dir):
        """Test handling of different file encodings"""
        policy_file = temp_config_dir / "whitelist_commands.yaml"

        # Write file with UTF-8 BOM
        content = "test:\n  description: 'Test with Unicode: 测试'"
        policy_file.write_bytes(b'\xef\xbb\xbf' + content.encode('utf-8'))

        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        test_policy = provider.get_policy("test")
        assert test_policy is not None
        assert "测试" in test_policy["description"]

    def test_build_command_instructions_git(self, temp_config_dir):
        """Test instruction building for git command"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))
        git_policy = provider.get_policy("git")

        instructions = YamlPolicyProvider.build_command_instructions("git", git_policy)

        assert "Read-only/metadata git operations" in instructions
        assert "Allowed subcommands:" in instructions
        assert "status" in instructions
        assert "log" in instructions
        assert "--porcelain" in instructions
        assert "Examples:" in instructions

    def test_build_command_instructions_npm(self, temp_config_dir):
        """Test instruction building for npm command"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))
        npm_policy = provider.get_policy("npm")

        instructions = YamlPolicyProvider.build_command_instructions("npm", npm_policy)

        assert "Allowed root flags:" in instructions
        assert "--version" in instructions
        assert "Allowed subcommands:" in instructions
        assert "ci:" in instructions
        assert "auto-added: --ignore-scripts" in instructions
        assert "install:" in instructions
        assert "DISABLED" in instructions
        assert "run:" in instructions
        assert "scripts: build, test, lint" in instructions
        assert "config:" in instructions
        assert "only: get" in instructions
        assert "Disallowed subcommands:" in instructions
        assert "exec, publish, update" in instructions

    def test_build_command_instructions_npx(self, temp_config_dir):
        """Test instruction building for npx command (special case)"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))
        npx_policy = provider.get_policy("npx")

        instructions = YamlPolicyProvider.build_command_instructions("npx", npx_policy)

        assert "Allowed packages:" in instructions
        assert "@angular/cli" in instructions
        assert "create-react-app" in instructions
        assert "typescript" in instructions
        assert "Allowed flags:" in instructions
        assert "--yes" in instructions
        assert "--package" in instructions
        assert "npx --yes" in instructions

    def test_build_command_instructions_pytest(self, temp_config_dir):
        """Test instruction building for pytest command (no subcommands)"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))
        pytest_policy = provider.get_policy("pytest")

        instructions = YamlPolicyProvider.build_command_instructions("pytest", pytest_policy)

        assert "Allowed root flags:" in instructions
        assert "-q" in instructions
        assert "--maxfail" in instructions
        assert "--disable-warnings" in instructions
        assert "pytest -q" in instructions

    def test_build_command_instructions_max_chars(self, temp_config_dir):
        """Test instruction building with character limit"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))
        npm_policy = provider.get_policy("npm")

        instructions = YamlPolicyProvider.build_command_instructions("npm", npm_policy, max_chars=200)

        assert len(instructions) <= 200
        assert instructions.endswith("…")

    def test_build_command_instructions_custom_description(self):
        """Test instruction building with custom description"""
        custom_policy = {
            "description": "Custom command description",
            "flags": ["--test"],
            "default_timeout": 30
        }

        instructions = YamlPolicyProvider.build_command_instructions("custom", custom_policy)

        assert "Custom command description" in instructions
        assert "Allowed root flags: --test" in instructions

    def test_build_command_instructions_no_description(self):
        """Test instruction building without description (uses default)"""
        policy_no_desc = {
            "flags": ["--test"],
            "default_timeout": 30
        }

        instructions = YamlPolicyProvider.build_command_instructions("testcmd", policy_no_desc)

        assert "Run safe, policy-constrained testcmd commands" in instructions

    def test_build_command_instructions_complex_require_flags(self):
        """Test instruction building with complex require_flags"""
        complex_policy = {
            "subcommands": {
                "build": {
                    "flags": ["--config", "--verbose"],
                    "require_flags": {
                        "--config": True,
                        "--verbosity": ["quiet", "minimal"],
                        "--logger": "console;verbosity=minimal"
                    }
                }
            }
        }

        instructions = YamlPolicyProvider.build_command_instructions("complex", complex_policy)

        assert "auto-added: --config" in instructions
        assert "--verbosity={{ quiet, minimal }}" in instructions  # Fix: use double braces
        assert "--logger=console;verbosity=minimal" in instructions

    def test_normalization_of_keys(self, temp_config_dir):
        """Test that policy keys are normalized to lowercase"""
        # Create policy file with mixed case keys
        mixed_case_policies = {
            "GIT": {"description": "Git policy"},
            "NPM": {"description": "NPM policy"},
            "PyTest": {"description": "PyTest policy"}
        }

        policy_file = temp_config_dir / "whitelist_commands.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(mixed_case_policies, f)

        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        # Should be able to access with lowercase
        assert provider.get_policy("git") is not None
        assert provider.get_policy("npm") is not None
        assert provider.get_policy("pytest") is not None

        # Should also work with original case
        assert provider.get_policy("GIT") is not None
        assert provider.get_policy("NPM") is not None
        assert provider.get_policy("PyTest") is not None

    @patch('builtins.open')
    def test_file_access_error_handling(self, mock_open):
        """Test handling of file access errors"""
        mock_open.side_effect = OSError("Permission denied")

        with tempfile.TemporaryDirectory() as temp_dir:
            provider = YamlPolicyProvider(config_path=temp_dir)

            result = provider.get_policy("git")
            assert result is None

    def test_empty_policy_file(self, temp_config_dir):
        """Test handling of empty policy file"""
        policy_file = temp_config_dir / "whitelist_commands.yaml"
        policy_file.write_text("")

        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        all_policies = provider.get_all_policies()
        assert all_policies == {}

        result = provider.get_policy("git")
        assert result is None

    def test_policy_file_property(self, temp_config_dir):
        """Test policy_file_path property"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        expected_path = temp_config_dir / "whitelist_commands.yaml"
        assert provider.policy_file_path == expected_path

    @patch.dict(os.environ, {"AGENTC_POLICIES_FILE": ""}, clear=True)
    def test_no_env_override(self, temp_config_dir):
        """Test behavior when no environment override is set"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        expected_path = temp_config_dir / "whitelist_commands.yaml"
        assert provider.policy_file_path == expected_path

    def test_get_policy_with_parts_parameter(self, temp_config_dir):
        """Test get_policy method with parts parameter (compatibility)"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        # The parts parameter should be ignored but method should still work
        policy = provider.get_policy("git", ["status", "--porcelain"])
        assert policy is not None
        assert policy["description"] == "Read-only/metadata git operations (no mutations)."

    def test_mtime_based_cache_invalidation(self, temp_config_dir, sample_policies):
        """Test that cache is invalidated when file modification time changes"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        # Load initial policy
        initial_policy = provider.get_policy("git")
        assert initial_policy is not None

        # Wait a bit and modify the file
        import time
        time.sleep(0.1)

        modified_policies = sample_policies.copy()
        modified_policies["git"]["description"] = "Modified git description"

        policy_file = temp_config_dir / "whitelist_commands.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(modified_policies, f)

        # Should automatically reload due to mtime change
        updated_policy = provider.get_policy("git")
        assert updated_policy["description"] == "Modified git description"

    def test_logger_usage(self, temp_config_dir):
        """Test that logger is used appropriately"""
        provider = YamlPolicyProvider(config_path=str(temp_config_dir))

        # Verify logger exists and is configured
        assert hasattr(provider, 'logger')
        assert provider.logger is not None

        # Test loading logs info message
        with patch.object(provider.logger, 'info') as mock_info:
            provider.get_policy("git")
            mock_info.assert_called()

    def test_build_command_instructions_edge_cases(self):
        """Test instruction building edge cases"""
        # Empty policy
        empty_policy = {}
        instructions = YamlPolicyProvider.build_command_instructions("empty", empty_policy)
        assert "Run safe, policy-constrained empty commands" in instructions

        # Policy with empty lists
        empty_lists_policy = {
            "root_flags": [],
            "subcommands": {},
            "deny_subcommands": []
        }
        instructions = YamlPolicyProvider.build_command_instructions("emptylists", empty_lists_policy)
        assert "Run safe, policy-constrained emptylists commands" in instructions

        # Policy with None values
        none_values_policy = {
            "root_flags": None,
            "subcommands": None,
            "deny_subcommands": None
        }
        instructions = YamlPolicyProvider.build_command_instructions("none", none_values_policy)
        assert "Run safe, policy-constrained none commands" in instructions
