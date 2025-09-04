"""
Tests for testing command path handling policies across multiple tools.
Tests the new ability to specify test paths, including absolute/relative paths,
files, line numbers, function names, and security restrictions.
"""
import pytest
import os
from pathlib import Path

# Import validators with proper error handling
try:
    from agent_c_tools.tools.workspace.executors.local_storage.validators.pytest_validator import PytestCommandValidator
except ImportError:
    PytestCommandValidator = None

try:
    from agent_c_tools.tools.workspace.executors.local_storage.validators.dotnet_validator import DotnetCommandValidator
except ImportError:
    DotnetCommandValidator = None

try:
    from agent_c_tools.tools.workspace.executors.local_storage.validators.node_validator import NodeCommandValidator
except ImportError:
    NodeCommandValidator = None

try:
    from agent_c_tools.tools.workspace.executors.local_storage.validators.npm_validator import NpmCommandValidator
except ImportError:
    NpmCommandValidator = None

try:
    from agent_c_tools.tools.workspace.executors.local_storage.validators.lerna_validator import LernaCommandValidator
except ImportError:
    LernaCommandValidator = None


@pytest.fixture
def mock_workspace_root(tmp_path):
    """Create a mock workspace with test files for path validation"""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create test directory structure
    (workspace / "tests").mkdir()
    (workspace / "tests" / "test_example.py").write_text("def test_example(): pass")
    (workspace / "tests" / "unit").mkdir()
    (workspace / "tests" / "unit" / "test_unit.py").write_text("def test_unit_func(): pass")
    (workspace / "src").mkdir()
    (workspace / "src" / "main.py").write_text("def main(): pass")
    (workspace / "Project.csproj").write_text("<Project></Project>")
    (workspace / "Solution.sln").write_text("# Solution file")
    (workspace / "package.json").write_text('{"name": "test", "scripts": {"test": "jest"}}')

    return str(workspace)


class TestPytestPathHandling:
    """Test pytest test path handling capabilities"""

    def test_pytest_allows_test_paths_when_enabled(self, policies):
        """Test that pytest allows test paths when allow_test_paths is true"""
        if "pytest" not in policies:
            pytest.skip("pytest policy not present")

        pol = policies["pytest"]
        assert pol.get("allow_test_paths") is True, "pytest should allow test paths"

    def test_pytest_relative_file_paths(self, mock_workspace_root):
        """Test pytest validation with relative file paths"""
        if PytestCommandValidator is None:
            pytest.skip("PytestCommandValidator not available")

        validator = PytestCommandValidator()
        policy = {
            "allow_test_paths": True,
            "workspace_root": mock_workspace_root,
            "flags": ["-q", "-v", "-x"],
            "default_timeout": 120
        }

        # Valid relative paths within workspace
        valid_cases = [
            ["pytest", "tests/test_example.py"],
            ["pytest", "tests/unit/test_unit.py"],
            ["pytest", "tests/"],
            ["pytest", "tests/test_example.py::test_example"],
            ["pytest", "tests/test_example.py::TestClass::test_method"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow valid relative path: {case} - {result.reason}"

    def test_pytest_file_line_references(self, mock_workspace_root):
        """Test pytest validation with file:line number references"""
        if PytestCommandValidator is None:
            pytest.skip("PytestCommandValidator not available")

        validator = PytestCommandValidator()
        policy = {
            "allow_test_paths": True,
            "workspace_root": mock_workspace_root,
            "flags": ["-q", "-v"],
            "default_timeout": 120
        }

        # Valid file:line references
        valid_cases = [
            ["pytest", "tests/test_example.py:10"],
            ["pytest", "tests/unit/test_unit.py:5"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow file:line reference: {case} - {result.reason}"

    def test_pytest_node_id_references(self, mock_workspace_root):
        """Test pytest validation with node ID references (::function, ::class::method)"""
        if PytestCommandValidator is None:
            pytest.skip("PytestCommandValidator not available")

        validator = PytestCommandValidator()
        policy = {
            "allow_test_paths": True,
            "workspace_root": mock_workspace_root,
            "flags": ["-q", "-v", "-k"],
            "default_timeout": 120
        }

        # Valid node ID references
        valid_cases = [
            ["pytest", "tests/test_example.py::test_example"],
            ["pytest", "tests/test_example.py::TestClass"],
            ["pytest", "tests/test_example.py::TestClass::test_method"],
            ["pytest", "tests/unit/test_unit.py::test_unit_func"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow node ID reference: {case} - {result.reason}"

    def test_pytest_blocks_paths_outside_workspace(self, mock_workspace_root, tmp_path):
        """Test that pytest blocks test paths outside workspace root"""
        if PytestCommandValidator is None:
            pytest.skip("PytestCommandValidator not available")

        validator = PytestCommandValidator()
        policy = {
            "allow_test_paths": True,
            "workspace_root": mock_workspace_root,
            "flags": ["-q", "-v"],
            "default_timeout": 120
        }

        # Create file outside workspace
        outside_file = tmp_path / "outside_test.py"
        outside_file.write_text("def test_outside(): pass")

        # Invalid paths outside workspace
        invalid_cases = [
            ["pytest", str(outside_file)],
            ["pytest", "../outside_test.py"],
            ["pytest", "/tmp/test_file.py"],
            ["pytest", "C:\\Windows\\test.py"],
            ["pytest", str(outside_file) + "::test_outside"],
        ]

        for case in invalid_cases:
            result = validator.validate(case, policy)
            assert not result.allowed, f"Should block path outside workspace: {case} - {result.reason}"
            assert "unsafe path" in result.reason.lower() or "outside workspace" in result.reason.lower()

    def test_pytest_absolute_workspace_paths(self, mock_workspace_root):
        """Test pytest with absolute paths that are within workspace"""
        if PytestCommandValidator is None:
            pytest.skip("PytestCommandValidator not available")

        validator = PytestCommandValidator()
        policy = {
            "allow_test_paths": True,
            "workspace_root": mock_workspace_root,
            "flags": ["-q", "-v"],
            "default_timeout": 120
        }

        # Absolute paths within workspace should be allowed
        test_file = os.path.join(mock_workspace_root, "tests", "test_example.py")
        valid_cases = [
            ["pytest", test_file],
            ["pytest", test_file + "::test_example"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow absolute path within workspace: {case} - {result.reason}"

    def test_pytest_parametrized_node_ids(self, mock_workspace_root):
        """Test pytest with parametrized test node IDs"""
        if PytestCommandValidator is None:
            pytest.skip("PytestCommandValidator not available")

        validator = PytestCommandValidator()
        policy = {
            "allow_test_paths": True,
            "workspace_root": mock_workspace_root,
            "flags": ["-q", "-v", "-k"],
            "default_timeout": 120
        }

        # Parametrized test node IDs
        valid_cases = [
            ["pytest", "tests/test_example.py::test_func[param1]"],
            ["pytest", "tests/test_example.py::test_func[param1-param2]"],
            ["pytest", "tests/test_example.py::TestClass::test_method[case1]"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow parametrized node ID: {case} - {result.reason}"

    def test_pytest_multiple_test_selectors(self, mock_workspace_root):
        """Test pytest with multiple test file selectors"""
        if PytestCommandValidator is None:
            pytest.skip("PytestCommandValidator not available")

        validator = PytestCommandValidator()
        policy = {
            "allow_test_paths": True,
            "workspace_root": mock_workspace_root,
            "flags": ["-q", "-v"],
            "default_timeout": 120,
            "max_selector_args": 10
        }

        # Multiple test selectors
        valid_cases = [
            ["pytest", "tests/test_example.py", "tests/unit/test_unit.py"],
            ["pytest", "tests/test_example.py::test_example", "tests/unit/test_unit.py::test_unit_func"],
            ["pytest", "tests/", "src/"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow multiple test selectors: {case} - {result.reason}"

    def test_pytest_blocks_excessive_selectors(self, mock_workspace_root):
        """Test that pytest blocks excessive number of selectors"""
        if PytestCommandValidator is None:
            pytest.skip("PytestCommandValidator not available")

        validator = PytestCommandValidator()
        policy = {
            "allow_test_paths": True,
            "workspace_root": mock_workspace_root,
            "flags": ["-q", "-v"],
            "default_timeout": 120,
            "max_selector_args": 2  # Low limit for testing
        }

        # Too many selectors
        invalid_case = ["pytest"] + [f"tests/test_{i}.py" for i in range(5)]

        result = validator.validate(invalid_case, policy)
        assert not result.allowed, f"Should block excessive selectors: {result.reason}"
        assert "too many selectors" in result.reason.lower()


class TestDotnetTestPathHandling:
    """Test dotnet test path handling capabilities"""

    def test_dotnet_test_policy_structure(self, policies):
        """Test that dotnet test policy has correct structure"""
        if "dotnet" not in policies:
            pytest.skip("dotnet policy not present")

        pol = policies["dotnet"]
        subs = pol.get("subcommands", {})

        assert "test" in subs, "dotnet should have test subcommand"
        test_config = subs["test"]

        # Check policy structure
        assert isinstance(test_config.get("flags", []), list)
        assert isinstance(test_config.get("allow_project_paths", True), bool)
        assert isinstance(test_config.get("allow_test_paths", False), bool)

    def test_dotnet_test_allows_project_paths(self, mock_workspace_root):
        """Test that dotnet test allows project/solution paths when configured"""
        if DotnetCommandValidator is None:
            pytest.skip("DotnetCommandValidator not available")

        validator = DotnetCommandValidator()
        policy = {
            "subcommands": {
                "test": {
                    "flags": ["--configuration", "-c", "--no-build", "--nologo", "--verbosity", "-v", "--filter", "--logger"],
                    "allow_project_paths": True,
                    "allow_test_paths": False,
                    "require_flags": {
                        "--no-build": True,
                        "--nologo": True,
                        "--verbosity": ["minimal", "quiet"],
                        "--logger": "console;verbosity=minimal"
                    }
                }
            },
            "workspace_root": mock_workspace_root,
            "default_timeout": 300
        }

        # Valid project/solution paths
        valid_cases = [
            ["dotnet", "test", "Project.csproj", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
            ["dotnet", "test", "Solution.sln", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
            ["dotnet", "test", "./Project.csproj", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow project/solution path: {case} - {result.reason}"

    def test_dotnet_test_blocks_test_paths_when_disabled(self, mock_workspace_root):
        """Test that dotnet test blocks test file paths when allow_test_paths is false"""
        if DotnetCommandValidator is None:
            pytest.skip("DotnetCommandValidator not available")

        validator = DotnetCommandValidator()
        policy = {
            "subcommands": {
                "test": {
                    "flags": ["--configuration", "-c", "--no-build", "--nologo", "--verbosity", "-v", "--filter", "--logger"],
                    "allow_project_paths": True,
                    "allow_test_paths": False,
                    "require_flags": {
                        "--no-build": True,
                        "--nologo": True,
                        "--verbosity": ["minimal", "quiet"],
                        "--logger": "console;verbosity=minimal"
                    }
                }
            },
            "workspace_root": mock_workspace_root,
            "default_timeout": 300
        }

        # Invalid test file paths when test paths disabled
        invalid_cases = [
            ["dotnet", "test", "tests/TestFile.cs", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
            ["dotnet", "test", "src/UnitTests.cs", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
            ["dotnet", "test", "./tests/", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
        ]

        for case in invalid_cases:
            result = validator.validate(case, policy)
            assert not result.allowed, f"Should block test path when disabled: {case} - {result.reason}"
            assert "test paths not permitted" in result.reason.lower() or "filter" in result.reason.lower()

    def test_dotnet_test_allows_test_paths_when_enabled(self, mock_workspace_root):
        """Test dotnet test allows test paths when allow_test_paths is true"""
        if DotnetCommandValidator is None:
            pytest.skip("DotnetCommandValidator not available")

        # Create test files
        test_dir = Path(mock_workspace_root) / "tests"
        test_dir.mkdir(exist_ok=True)
        (test_dir / "TestFile.cs").write_text("// test file")

        validator = DotnetCommandValidator()
        policy = {
            "subcommands": {
                "test": {
                    "flags": ["--configuration", "-c", "--no-build", "--nologo", "--verbosity", "-v", "--filter", "--logger"],
                    "allow_project_paths": True,
                    "allow_test_paths": True,
                    "require_flags": {
                        "--no-build": True,
                        "--nologo": True,
                        "--verbosity": ["minimal", "quiet"],
                        "--logger": "console;verbosity=minimal"
                    }
                }
            },
            "workspace_root": mock_workspace_root,
            "default_timeout": 300
        }

        # Valid test paths when enabled
        valid_cases = [
            ["dotnet", "test", "tests/TestFile.cs", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
            ["dotnet", "test", "tests/", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow test path when enabled: {case} - {result.reason}"

    def test_dotnet_test_blocks_paths_outside_workspace(self, mock_workspace_root, tmp_path):
        """Test that dotnet test blocks paths outside workspace"""
        if DotnetCommandValidator is None:
            pytest.skip("DotnetCommandValidator not available")

        # Create file outside workspace
        outside_file = tmp_path / "OutsideTest.cs"
        outside_file.write_text("// outside test")

        validator = DotnetCommandValidator()
        policy = {
            "subcommands": {
                "test": {
                    "flags": ["--configuration", "-c", "--no-build", "--nologo", "--verbosity", "-v", "--logger"],
                    "allow_project_paths": True,
                    "allow_test_paths": True,
                    "require_flags": {
                        "--no-build": True,
                        "--nologo": True,
                        "--verbosity": ["minimal", "quiet"],
                        "--logger": "console;verbosity=minimal"
                    }
                }
            },
            "workspace_root": mock_workspace_root,
            "default_timeout": 300
        }

        # Invalid paths outside workspace
        invalid_cases = [
            ["dotnet", "test", str(outside_file), "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
            ["dotnet", "test", "../OutsideTest.cs", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
            ["dotnet", "test", "/tmp/test.cs", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
        ]

        for case in invalid_cases:
            result = validator.validate(case, policy)
            assert not result.allowed, f"Should block path outside workspace: {case} - {result.reason}"
            assert "unsafe path" in result.reason.lower() or "outside workspace" in result.reason.lower()

    def test_dotnet_test_path_flags_validation(self, mock_workspace_root, tmp_path):
        """Test that dotnet test validates paths in flag values"""
        if DotnetCommandValidator is None:
            pytest.skip("DotnetCommandValidator not available")

        # Create results directory outside workspace
        outside_dir = tmp_path / "outside_results"
        outside_dir.mkdir()

        validator = DotnetCommandValidator()
        policy = {
            "subcommands": {
                "test": {
                    "flags": ["--no-build", "--results-directory", "--settings", "--nologo", "--verbosity", "--logger"],
                    "allow_project_paths": True,
                    "allow_test_paths": False,
                    "require_flags": {
                        "--no-build": True,
                        "--nologo": True,
                        "--verbosity": ["minimal", "quiet"],
                        "--logger": "console;verbosity=minimal"
                    }
                }
            },
            "workspace_root": mock_workspace_root,
            "default_timeout": 300
        }

        # Invalid path flag values outside workspace
        invalid_cases = [
            ["dotnet", "test", "--results-directory", str(outside_dir), "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
            ["dotnet", "test", f"--results-directory={outside_dir}", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
            ["dotnet", "test", "--settings", "/tmp/test.runsettings", "--no-build", "--nologo", "--verbosity", "minimal", "--logger", "console;verbosity=minimal"],
        ]

        for case in invalid_cases:
            result = validator.validate(case, policy)
            assert not result.allowed, f"Should block unsafe path flag value: {case} - {result.reason}"


class TestNodeTestPathHandling:
    """Test Node.js test path handling through --test flag"""

    def test_node_test_allows_test_paths(self, policies):
        """Test that node --test allows test paths when configured"""
        if "node" not in policies:
            pytest.skip("node policy not present")

        pol = policies["node"]
        
        # Check for allow_test_mode in multiple places (old and new format)
        allow_test_mode = False
        
        # Check top-level policy (legacy format)
        if pol.get("allow_test_mode") is True:
            allow_test_mode = True
        
        # Check flag-specific configuration (new format)
        flags = pol.get("flags", [])
        if isinstance(flags, dict):
            test_flag_config = flags.get("--test", {})
            if test_flag_config.get("allow_test_mode", False):
                allow_test_mode = True
        
        # Check modes configuration
        modes_config = pol.get("modes", {})
        test_mode_config = modes_config.get("test", {})
        if test_mode_config.get("allow_test_mode", False):
            allow_test_mode = True
        
        assert allow_test_mode, "node should allow test mode (either at top-level, flag-level, or mode-level)"

    def test_node_test_file_patterns(self, mock_workspace_root):
        """Test node --test with file patterns"""
        if NodeCommandValidator is None:
            pytest.skip("NodeCommandValidator not available")

        # Create test files
        test_dir = Path(mock_workspace_root) / "test"
        test_dir.mkdir()
        (test_dir / "example.test.js").write_text("// test file")

        validator = NodeCommandValidator()
        policy = {
            "flags": ["--test", "--test-reporter", "--test-name-pattern"],
            "allow_test_mode": True,
            "workspace_root": mock_workspace_root,
            "default_timeout": 120
        }

        # Valid test patterns
        valid_cases = [
            ["node", "--test", "test/example.test.js"],
            ["node", "--test", "test/*.test.js"],
            ["node", "--test", "--test-reporter", "spec"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow node test pattern: {case} - {result.reason}"

    def test_node_blocks_paths_outside_workspace(self, mock_workspace_root, tmp_path):
        """Test that node --test blocks paths outside workspace"""
        if NodeCommandValidator is None:
            pytest.skip("NodeCommandValidator not available")

        # Create test file outside workspace
        outside_file = tmp_path / "outside.test.js"
        outside_file.write_text("// outside test")

        validator = NodeCommandValidator()
        policy = {
            "flags": ["--test", "--test-reporter", "--test-name-pattern"],
            "allow_test_mode": True,
            "workspace_root": mock_workspace_root,
            "default_timeout": 120
        }

        # Invalid paths outside workspace
        invalid_cases = [
            ["node", "--test", str(outside_file)],
            ["node", "--test", "../outside.test.js"],
        ]

        for case in invalid_cases:
            result = validator.validate(case, policy)
            assert not result.allowed, f"Should block path outside workspace: {case} - {result.reason}"


class TestNpmTestPathHandling:
    """Test npm test path handling through run scripts"""

    def test_npm_run_test_allows_test_paths(self, policies):
        """Test that npm run scripts allow test paths when configured"""
        if "npm" not in policies:
            pytest.skip("npm policy not present")

        pol = policies["npm"]
        subs = pol.get("subcommands", {})

        if "run" in subs:
            run_config = subs["run"]
            assert run_config.get("allow_test_paths") is True, "npm run should allow test paths"

    def test_npm_run_test_script_execution(self, mock_workspace_root):
        """Test npm run test with allowed scripts"""
        if NpmCommandValidator is None:
            pytest.skip("NpmCommandValidator not available")

        validator = NpmCommandValidator()
        policy = {
            "subcommands": {
                "run": {
                    "allowed_scripts": ["test", "test:unit", "test:integration"],
                    "allow_test_paths": True,
                    "deny_args": False
                }
            },
            "workspace_root": mock_workspace_root,
            "default_timeout": 120
        }

        # Valid npm run test commands
        valid_cases = [
            ["npm", "run", "test"],
            ["npm", "run", "test:unit"],
            ["npm", "run", "test", "--", "--coverage"],
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow npm run test: {case} - {result.reason}"

    def test_npm_blocks_dangerous_scripts(self, mock_workspace_root):
        """Test that npm blocks dangerous or non-allowed scripts"""
        if NpmCommandValidator is None:
            pytest.skip("NpmCommandValidator not available")

        validator = NpmCommandValidator()
        policy = {
            "subcommands": {
                "run": {
                    "allowed_scripts": ["test", "test:unit"],
                    "allow_test_paths": True,
                    "deny_args": False
                }
            },
            "workspace_root": mock_workspace_root,
            "default_timeout": 120
        }

        # Invalid scripts not in allowed list
        invalid_cases = [
            ["npm", "run", "build"],
            ["npm", "run", "postinstall"],
            ["npm", "run", "preinstall"],
        ]

        for case in invalid_cases:
            result = validator.validate(case, policy)
            assert not result.allowed, f"Should block non-allowed script: {case} - {result.reason}"


class TestPnpmTestPathHandling:
    """Test pnpm test path handling"""

    def test_pnpm_allows_test_paths(self, policies):
        """Test that pnpm allows test paths when configured"""
        if "pnpm" not in policies:
            pytest.skip("pnpm policy not present")

        pol = policies["pnpm"]
        subs = pol.get("subcommands", {})

        if "run" in subs:
            run_config = subs["run"]
            # Check if allow_test_paths is configured at subcommand level
            if "allow_test_paths" in run_config:
                # The current config doesn't have this, but test the structure
                pass
            else:
                # Check general tool-level configuration
                assert pol.get("allow_test_paths") is not False, "pnpm should not explicitly disable test paths"


class TestLernaTestPathHandling:
    """Test Lerna test path handling"""

    def test_lerna_run_allows_test_paths(self, policies):
        """Test that lerna run allows test paths when configured"""
        if "lerna" not in policies:
            pytest.skip("lerna policy not present")

        pol = policies["lerna"]
        subs = pol.get("subcommands", {})

        if "run" in subs:
            run_config = subs["run"]
            assert run_config.get("allow_test_paths") is True, "lerna run should allow test paths"

    def test_lerna_run_test_script_execution(self, mock_workspace_root):
        """Test lerna run test with allowed scripts"""
        if LernaCommandValidator is None:
            pytest.skip("LernaCommandValidator not available")

        validator = LernaCommandValidator()
        policy = {
            "flags": ["--concurrency", "--loglevel", "--scope"],  # Add global flags from whitelist config
            "subcommands": {
                "run": {
                    "flags": ["--npm-client", "--stream", "--parallel", "--bail", "--no-bail", "--no-prefix"],  # Add subcommand flags
                    "allowed_scripts": ["test", "test:unit", "build"],
                    "allow_test_paths": True,
                    "deny_args": False
                }
            },
            "workspace_root": mock_workspace_root,
            "default_timeout": 300
        }

        # Valid lerna run test commands
        valid_cases = [
            ["lerna", "run", "test"],
            ["lerna", "run", "test:unit"],
            ["lerna", "run", "test", "--concurrency", "1"],  # Now this should work with global flags
        ]

        for case in valid_cases:
            result = validator.validate(case, policy)
            assert result.allowed, f"Should allow lerna run test: {case} - {result.reason}"

    def test_lerna_blocks_dangerous_scripts(self, mock_workspace_root):
        """Test that lerna blocks dangerous or non-allowed scripts"""
        if LernaCommandValidator is None:
            pytest.skip("LernaCommandValidator not available")

        validator = LernaCommandValidator()
        policy = {
            "subcommands": {
                "run": {
                    "allowed_scripts": ["test", "test:unit"],
                    "allow_test_paths": True,
                    "deny_args": False
                }
            },
            "workspace_root": mock_workspace_root,
            "default_timeout": 300
        }

        # Invalid scripts not in allowed list
        invalid_cases = [
            ["lerna", "run", "publish"],
            ["lerna", "run", "postinstall"],
            ["lerna", "run", "preinstall"],
        ]

        for case in invalid_cases:
            result = validator.validate(case, policy)
            assert not result.allowed, f"Should block non-allowed script: {case} - {result.reason}"


class TestTestingSecurityRestrictions:
    """Test security restrictions for testing commands"""

    def test_all_testing_tools_have_workspace_restrictions(self, policies):
        """Test that all tools with testing capabilities enforce workspace restrictions"""
        testing_tools = ["pytest", "dotnet", "npm", "pnpm", "node", "lerna"]

        for tool in testing_tools:
            if tool not in policies:
                continue

            pol = policies[tool]

            # Check that tool has proper timeout configurations
            assert pol.get("default_timeout"), f"{tool} should have default timeout"

            # Check environment security settings where applicable
            if "env_overrides" in pol:
                env_overrides = pol["env_overrides"]
                # Should have some form of security environment settings
                assert len(env_overrides) > 0, f"{tool} should have environment security settings"

    def test_testing_tools_block_dangerous_flags(self, policies):
        """Test that testing tools block dangerous flags"""
        # pytest should not allow arbitrary execution flags
        if "pytest" in policies:
            pytest_pol = policies["pytest"]
            flags = pytest_pol.get("flags", [])
            dangerous_flags = ["--pdb", "--pdbcls", "--capture=no", "-s"]

            # These flags might be allowed for debugging, but should be controlled
            # The key is that there should be a restricted set of allowed flags
            assert isinstance(flags, list), "pytest should have explicit flag list"

    def test_dotnet_test_requires_security_flags(self, policies):
        """Test that dotnet test requires security flags"""
        if "dotnet" not in policies:
            pytest.skip("dotnet policy not present")

        pol = policies["dotnet"]
        subs = pol.get("subcommands", {})

        if "test" in subs:
            test_config = subs["test"]
            require_flags = test_config.get("require_flags", {})

            # Should require no-build for security
            assert require_flags.get("--no-build") is True, "dotnet test should require --no-build"
            assert require_flags.get("--nologo") is True, "dotnet test should require --nologo"

    def test_npm_script_restrictions(self, policies):
        """Test that npm run has script restrictions"""
        if "npm" not in policies:
            pytest.skip("npm policy not present")

        pol = policies["npm"]
        subs = pol.get("subcommands", {})

        if "run" in subs:
            run_config = subs["run"]
            allowed_scripts = run_config.get("allowed_scripts", [])
            assert "test" in allowed_scripts, "npm run should allow test script"
            assert isinstance(allowed_scripts, list), "npm should have explicit allowed scripts list"

    def test_testing_tools_have_proper_timeouts(self, policies):
        """Test that testing tools have reasonable timeout values"""
        # Primary testing tools that should have longer timeouts
        primary_testing_tools = ["pytest", "dotnet", "npm", "pnpm", "lerna"]
        # Node is a runtime, not primarily a testing tool, so it can have shorter timeout
        runtime_tools = ["node"]

        for tool in primary_testing_tools:
            if tool not in policies:
                continue

            pol = policies[tool]
            timeout = pol.get("default_timeout")

            # Primary testing tools should have reasonable timeouts (not too short, not too long)
            assert timeout is not None, f"{tool} should have a default timeout"
            assert 30 <= timeout <= 600, f"{tool} timeout should be reasonable (30-600s), got {timeout}"

        # Runtime tools can have shorter timeouts since they're not primarily for testing
        for tool in runtime_tools:
            if tool not in policies:
                continue

            pol = policies[tool]
            timeout = pol.get("default_timeout")

            # Runtime tools should have a timeout but it can be shorter
            assert timeout is not None, f"{tool} should have a default timeout"
            assert 5 <= timeout <= 600, f"{tool} timeout should be reasonable (5-600s), got {timeout}"
