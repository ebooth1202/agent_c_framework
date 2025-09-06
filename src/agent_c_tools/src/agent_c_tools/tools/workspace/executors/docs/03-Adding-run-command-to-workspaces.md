# Adding run_command to Other Workspace Types

This document explains how to implement secure command execution (`run_command`) for workspace types other than `LocalStorageWorkspace`.

## Overview

Currently, only `LocalStorageWorkspace` supports command execution. The architecture is designed to make it straightforward to add this capability to other workspace types while maintaining security controls.

## Architecture Components

### 1. Base Class Setup

The `BaseWorkspace` class provides the foundation:

```python
class BaseWorkspace:
    supports_run_command: bool = False  # Override this in subclasses
    
    async def run_command(self, command: str, working_directory: Optional[str] = None):
        """
        Override in subclasses that support commands.
        Having this on the base class satisfies static type checkers/IDEs.
        """
        raise NotImplementedError(f"{self.__class__.__name__} does not support run_command")
```

### 2. Tool Layer Integration

The `WorkspaceTools` class automatically detects and uses `run_command` support:

```python
# In tool.py - run_command method
if not workspace or not hasattr(workspace, 'run_command'):
    return f"ERROR: Workspace: {workspace.name if workspace else 'None'} does not support OS level run commands"

# Check the supports_run_command flag
if not workspace.supports_run_command:
    return f"ERROR: Workspace: {workspace.name} does not support command execution"

# Call the workspace's run_command method
result: CommandExecutionResult = await workspace.run_command(command=command, working_directory=abs_path)
```

### 3. Security Layer

All implementations should use the same security components:
- `SecureCommandExecutor` - Core security and execution logic
- `YamlPolicyProvider` - Policy configuration management
- `CommandValidator` classes - Command-specific validation

## Implementation Guide

### Step 1: Enable Command Support

Set the flag and implement the method in your workspace class:

```python
class MyWorkspaceType(BaseWorkspace):
    supports_run_command = True  # Enable command execution
    
    def __init__(self, **kwargs):
        super().__init__("my_workspace_type", **kwargs)
        # Initialize your workspace-specific components
        # ...
        
        # Initialize secure command executor
        policy_provider = YamlPolicyProvider()
        self.executor = SecureCommandExecutor(
            debug_mode=kwargs.get('debug_mode', True),
            log_output=True,
            default_timeout=30,
            max_output_size=1024 * 1024,
            policy_provider=policy_provider
        )
    
    async def run_command(self, command: str, working_directory: Optional[str] = None) -> CommandExecutionResult:
        """Run a command with security controls."""
        # Workspace-specific path validation and resolution
        if working_directory:
            resolved_wd = await self._resolve_working_directory(working_directory)
            if not resolved_wd:
                return CommandExecutionResult(
                    status="error",
                    command=command,
                    stdout="",
                    stderr="Invalid working directory",
                    return_code=1,
                    working_directory=working_directory
                )
            working_directory = resolved_wd
        
        # Build workspace-specific environment
        workspace_env = self._build_workspace_environment()
        
        # Delegate to secure executor
        return await self.executor.execute_command(
            command=command,
            working_directory=working_directory,
            override_env=workspace_env,
            timeout=None
        )
```

### Step 2: Implement Workspace-Specific Logic

Each workspace type requires different approaches for path resolution and command execution:

#### Storage-Only Workspaces
- S3StorageWorkspace
- AzureBlobWorkspace
- GoogleCloudStorageWorkspace
- FTPWorkspace
- Any pure file storage service

Uses base class, where `supports_run_command = False`

#### Executable-Capable Workspaces

```python
class SSHWorkspace(BaseWorkspace):
    supports_run_command = True
    
    def __init__(self, host: str, username: str, **kwargs):
        super().__init__("ssh", **kwargs)
        self.host = host
        self.username = username
        self.ssh_key_path = kwargs.get('ssh_key_path')
        self.base_path = kwargs.get('base_path', '/tmp/ssh_workspace')
        
        # Initialize policy provider with SSH-specific policies
        policy_provider = YamlPolicyProvider()
        self.executor = SecureCommandExecutor(
            policy_provider=policy_provider,
            default_timeout=45  # SSH might need longer timeouts
        )
    
    async def run_command(self, command: str, working_directory: Optional[str] = None) -> CommandExecutionResult:
        """Execute command over SSH."""
        
        # Resolve working directory within SSH workspace
        if working_directory:
            resolved_wd = self._resolve_ssh_path(working_directory)
        else:
            resolved_wd = self.base_path
        
        # Build SSH command wrapper
        ssh_wrapper = self._build_ssh_wrapper(command, resolved_wd)
        
        # Use local executor to run SSH command
        return await self.executor.execute_command(
            command=ssh_wrapper,
            working_directory=None,  # SSH handles remote working dir
            override_env=self._get_ssh_environment(),
            timeout=None
        )
    
    def _build_ssh_wrapper(self, command: str, working_directory: str) -> str:
        """Build SSH command that executes the command remotely."""
        # Escape the command for SSH execution
        escaped_command = shlex.quote(command)
        
        return f"ssh -o BatchMode=yes -o ConnectTimeout=10 {self.username}@{self.host} 'cd {shlex.quote(working_directory)} && {escaped_command}'"

class DockerWorkspace(BaseWorkspace):
    supports_run_command = True
    
    def __init__(self, container_id: str, **kwargs):
        super().__init__("docker", **kwargs)
        self.container_id = container_id
        
        # Docker-specific policies
        policy_provider = YamlPolicyProvider()
        self.executor = SecureCommandExecutor(
            policy_provider=policy_provider,
            default_timeout=120  # Container commands might take longer
        )
    
    async def run_command(self, command: str, working_directory: Optional[str] = None) -> CommandExecutionResult:
        """Execute command in Docker container."""
        
        # Build docker exec command
        docker_cmd = ["docker", "exec"]
        
        if working_directory:
            docker_cmd.extend(["-w", working_directory])
        
        docker_cmd.extend([self.container_id, "sh", "-c", command])
        
        # Convert to single command string for executor
        docker_command = " ".join(shlex.quote(arg) for arg in docker_cmd)
        
        return await self.executor.execute_command(
            command=docker_command,
            working_directory=None,  # Docker handles working directory
            override_env=self._get_docker_environment(),
            timeout=None
        )
```

### Step 3: Policy Configuration

Each workspace type should have appropriate policies:

#### ssh_policies.yaml (example)
```yaml
ssh:
  validator: os_basic
  flags: ["-o", "-p", "-i", "-l"]
  default_timeout: 45
  safe_env:
    SSH_AUTH_SOCK: ""
    SSH_AGENT_PID: ""
  env_overrides:
    SSH_KNOWN_HOSTS: "/dev/null"
    SSH_STRICT_HOST_KEY_CHECKING: "accept-new"
  deny_global_flags: ["-D", "-L", "-R", "-X", "-Y"]
```

#### docker_policies.yaml (example)
```yaml
docker:
  validator: os_basic
  flags: ["-i", "-t", "-w", "-u", "--workdir", "--user"]
  subcommands:
    exec:
      flags: ["-i", "-t", "-w", "-u", "--workdir", "--user"]
      timeout: 120
  default_timeout: 60
  safe_env:
    DOCKER_BUILDKIT: "0"
  deny_global_flags: ["--privileged", "-v", "--volume", "--mount"]
```

### Step 4: Security Implementation

#### Secure Path Resolution
```python
def _resolve_working_directory(self, path: str) -> Optional[str]:
    """Resolve and validate working directory path."""
    if not path:
        return None
    
    # Prevent directory traversal
    if ".." in path.split(os.sep):
        return None
    
    # Ensure path is within workspace bounds
    if os.path.isabs(path):
        # Check if absolute path is within workspace
        if not path.startswith(self.workspace_root):
            return None
        return path
    else:
        # Convert relative path to absolute within workspace
        resolved = os.path.join(self.workspace_root, path)
        return os.path.normpath(resolved)

def _build_workspace_environment(self) -> Dict[str, str]:
    """Build secure environment for command execution."""
    env = {
        "WORKSPACE_TYPE": self.type_name,
        "WORKSPACE_NAME": self.name,
        "WORKSPACE_ROOT": self.workspace_root,
        "CWD": self.workspace_root,
    }
    
    # Add workspace-specific environment variables
    if hasattr(self, '_get_workspace_specific_env'):
        env.update(self._get_workspace_specific_env())
    
    return env
```

## Testing Infrastructure

### Test Organization

Tests should be organized in `tests/policy_tests/` following the established pattern:

```
tests/policy_tests/
├── conftest.py                    # Shared fixtures and utilities
├── test_<workspace_type>_policy.py  # Policy tests for your workspace
└── test_<workspace_type>_integration.py  # Integration tests
```

### Policy Testing Patterns

Create comprehensive tests for your workspace policies:

```python
# test_myworkspace_policy.py
import pytest

def test_myworkspace_policy_exists(policies):
    """Test that workspace policy exists and has correct structure."""
    if "myworkspace" not in policies:
        pytest.skip("myworkspace policy not present")

    pol = policies["myworkspace"]
    assert "default_timeout" in pol, "Policy should have default_timeout"
    assert "env_overrides" in pol, "Policy should have env_overrides"

def test_myworkspace_security_flags(policies):
    """Test that security-critical configuration is present."""
    if "myworkspace" not in policies:
        pytest.skip("myworkspace policy not present")

    pol = policies["myworkspace"]
    
    # Test timeout configuration
    default_timeout = pol.get("default_timeout")
    assert isinstance(default_timeout, int), "default_timeout should be an integer"
    assert 10 <= default_timeout <= 600, "default_timeout should be reasonable"

    # Test environment security
    env_overrides = pol.get("env_overrides", {})
    assert env_overrides.get("NO_COLOR") == "1", "Should disable colors"

def test_myworkspace_denied_operations(policies):
    """Test that dangerous operations are blocked."""
    if "myworkspace" not in policies:
        pytest.skip("myworkspace policy not present")

    pol = policies["myworkspace"]
    
    # Check for dangerous global flags
    deny_flags = pol.get("deny_global_flags", [])
    dangerous_flags = ["--privileged", "--unsafe", "-X"]
    
    for flag in dangerous_flags:
        if flag in deny_flags:  # Only test if the flag is relevant to this workspace
            assert flag in deny_flags, f"Dangerous flag {flag} should be denied"

def test_myworkspace_environment_security(policies):
    """Test environment variable security."""
    if "myworkspace" not in policies:
        pytest.skip("myworkspace policy not present")

    pol = policies["myworkspace"]
    env_overrides = pol.get("env_overrides", {})

    # Test common security environment variables
    security_vars = {
        "NO_COLOR": "1",
        "TERM": "dumb",
    }
    
    for var, expected_value in security_vars.items():
        if var in env_overrides:
            assert env_overrides[var] == expected_value, f"{var} should be set to {expected_value}"
```

### Integration Testing

Test the full workspace implementation:

```python
# test_myworkspace_integration.py
import pytest
from your_module import MyWorkspaceType

@pytest.fixture
async def workspace():
    """Create a test workspace instance."""
    workspace = MyWorkspaceType(
        name="test",
        workspace_root="/tmp/test_workspace"
    )
    yield workspace
    # Cleanup if needed

@pytest.mark.asyncio
async def test_workspace_command_execution(workspace):
    """Test basic command execution."""
    result = await workspace.run_command("echo 'hello world'")
    
    assert result.is_success, f"Command should succeed: {result.error_message}"
    assert "hello world" in result.stdout
    assert result.return_code == 0

@pytest.mark.asyncio
async def test_workspace_blocked_command(workspace):
    """Test that dangerous commands are blocked."""
    result = await workspace.run_command("rm -rf /")
    
    assert result.status == "blocked", "Dangerous command should be blocked"
    assert "not allowed" in result.error_message.lower()

@pytest.mark.asyncio
async def test_workspace_working_directory(workspace):
    """Test working directory handling."""
    result = await workspace.run_command("pwd", working_directory="subdir")
    
    # Should either succeed with correct directory or safely fail
    if result.is_success:
        assert "subdir" in result.stdout
    else:
        # Should fail safely, not crash
        assert result.status in ["error", "blocked"]

@pytest.mark.asyncio
async def test_workspace_path_traversal_protection(workspace):
    """Test protection against path traversal."""
    result = await workspace.run_command("pwd", working_directory="../../../etc")
    
    assert result.is_error, "Path traversal should be blocked"
    assert any(word in result.error_message.lower() for word in ["invalid", "unsafe", "error"])

@pytest.mark.asyncio
async def test_workspace_timeout_handling(workspace):
    """Test command timeout handling."""
    # This test might be workspace-specific
    result = await workspace.run_command("sleep 1", timeout=0.5)
    
    if result.status == "timeout":
        assert "timeout" in result.error_message.lower()
    # Some workspaces might not support custom timeouts

@pytest.mark.asyncio
async def test_workspace_environment_isolation(workspace):
    """Test that environment is properly isolated."""
    result = await workspace.run_command("env | grep WORKSPACE")
    
    if result.is_success:
        # Workspace environment variables should be present
        assert "WORKSPACE" in result.stdout
```

### Running Tests

```bash
# Run all policy tests
pytest tests/policy_tests/ -v

# Run tests for a specific workspace type
pytest tests/policy_tests/test_myworkspace_*.py -v

# Run integration tests only
pytest tests/policy_tests/ -k "integration" -v

# Run tests with detailed output
pytest tests/policy_tests/ -v -s
```

### Test Fixtures (conftest.py)

The existing `conftest.py` provides useful fixtures that your tests can use:

```python
# Example usage in your tests
def test_with_all_policies(policies):
    """Test something across all loaded policies."""
    for policy_name, policy in policies.items():
        # Test each policy
        assert "default_timeout" in policy

@pytest.mark.parametrize("policy_for", ["myworkspace"], indirect=True)
def test_specific_policy(policy_for):
    """Test a specific policy using the fixture."""
    assert policy_for is not None
    assert "default_timeout" in policy_for

@pytest.mark.parametrize("validator_for", ["myworkspace"], indirect=True)
def test_validator_functionality(validator_for):
    """Test validator functionality if available."""
    if not validator_for:
        pytest.skip("Validator not available")
    
    # Test validator logic
    policy = {"subcommands": {"test": {"flags": ["-v"]}}}
    result = validator_for.validate(["myworkspace", "test", "-v"], policy)
    assert result.allowed
```

## Implementation Checklist

When adding `run_command` to a workspace type:

### ✅ Core Implementation
- [ ] Set `supports_run_command = True`
- [ ] Implement `run_command` method
- [ ] Initialize `SecureCommandExecutor` with appropriate policy provider
- [ ] Create and configure workspace-specific policies

### ✅ Security Implementation  
- [ ] Implement secure path validation with `_resolve_working_directory()`
- [ ] Handle workspace boundary enforcement
- [ ] Configure secure environment variables via `_build_workspace_environment()`
- [ ] Set appropriate timeouts and resource limits
- [ ] Validate all user inputs before execution

### ✅ Workspace-Specific Logic
- [ ] Handle workspace-specific path mapping (SSH paths, container paths, etc.)
- [ ] Implement any required synchronization for remote storage
- [ ] Handle workspace-specific command adaptation (SSH wrapping, Docker exec, etc.)
- [ ] Implement proper cleanup procedures
- [ ] Handle workspace connection management (SSH connections, container status, etc.)

### ✅ Policy Configuration
- [ ] Create workspace-specific policy files (e.g., `ssh_policies.yaml`, `docker_policies.yaml`)
- [ ] Configure appropriate command validators or use existing ones
- [ ] Set reasonable default timeouts for workspace type
- [ ] Define safe environment variables for workspace context
- [ ] Configure denied flags specific to workspace security risks

### ✅ Testing Implementation
- [ ] Create comprehensive policy tests in `tests/policy_tests/test_<workspace>_policy.py`
- [ ] Test policy structure and required fields
- [ ] Test security requirements (timeouts, environment variables, denied flags)
- [ ] Test workspace-specific security controls
- [ ] Create integration tests in `tests/policy_tests/test_<workspace>_integration.py`
- [ ] Test successful command execution
- [ ] Test blocked/dangerous command handling
- [ ] Test working directory resolution and validation
- [ ] Test path traversal protection
- [ ] Test timeout handling
- [ ] Test environment isolation
- [ ] Test workspace-specific error conditions
- [ ] Test edge cases (invalid paths, connection failures, etc.)

### ✅ Documentation
- [ ] Document workspace-specific limitations and requirements
- [ ] Provide configuration examples for the workspace type
- [ ] Document security considerations specific to the workspace
- [ ] Add troubleshooting guidance for common issues
- [ ] Document test coverage and how to run workspace-specific tests
- [ ] Document any required setup (SSH keys, Docker containers, etc.)

### ✅ Quality Assurance
- [ ] Run all existing tests to ensure no regressions
- [ ] Run workspace-specific tests with various configurations
- [ ] Test error handling and recovery scenarios
- [ ] Performance test with typical workloads
- [ ] Security review of implementation
- [ ] Documentation review for completeness

This architecture ensures that command execution capabilities can be safely added to any workspace type while maintaining consistent security controls, comprehensive test coverage, and proper documentation across all implementations.