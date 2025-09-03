# Command Validators and Security Policies Guide

This document explains how to add validators, configure security policies, and manage command execution in the Agent C Framework workspace system.

## Overview

The secure command execution system uses a three-layer approach:
1. **Policy Provider** - Loads and manages command policies from `whitelist_commands.yaml`
2. **Validators** - Enforce policies with command-specific security logic
3. **Secure Command Executor** - Manages actual execution with security controls

## Policy Configuration Structure

### Standard Policy Schema

All command policies follow the standardized structure defined in [04-WHITELIST_COMMAND_STANDARDS.md](04-WHITELIST_COMMAND_STANDARDS.md):

```yaml
command_name:
  # Core Configuration
  validator: validator_class_name          # Optional: Custom validator (defaults to command_name)
  description: "Human-readable description" # Optional: Purpose and safety rationale
  
  # Global Flags (apply to all subcommands)
  flags: ["-v", "--version", "--help"]     # Allowed global flags
  deny_global_flags: ["-e", "--eval"]     # Explicitly blocked global flags
  require_flags: ["-NoProfile"]           # Flags that must always be present
  
  # Execution Control
  default_timeout: 120                    # Default timeout in seconds
  workspace_root: "/path/to/workspace"    # Optional: Override workspace root
  
  # Environment Security
  env_overrides:                          # Environment variables to set/override
    NO_COLOR: "1"
    TOOL_DISABLE_TELEMETRY: "1"
  safe_env:                              # Required environment variables
    TOOL_SAFE_MODE: "1"
  
  # Subcommands (if applicable)
  subcommands:
    subcommand_name:
      flags: ["--safe-flag"]             # Allowed flags for this subcommand
      allowed_flags: ["--alt-syntax"]    # Alternative syntax (some validators use this)
      deny_flags: ["--dangerous"]       # Explicitly blocked flags
      require_flags:                     # Flags that must be present
        --no-build: true                 # Boolean: flag must be present
        --verbosity: ["minimal", "quiet"] # Array: flag value must be in list
        --logger: "console;verbosity=minimal" # String: flag must have exact value
      
      # Argument Control
      allowed_scripts: ["test", "build"] # For script runners (npm, pnpm, lerna)
      deny_args: false                   # Whether to block additional arguments
      require_no_packages: true         # Block package name arguments
      
      # Path Safety
      allow_test_paths: false            # Allow workspace-relative test file paths
      allow_project_paths: true         # Allow project/solution file paths
      allow_script_paths: false         # Allow script file execution
      
      # Execution Control
      timeout: 300                       # Override default timeout for this subcommand
      enabled: true                      # Whether subcommand is enabled
      
      # Special Behaviors
      get_only: true                     # Special: only allow 'get' operations
  
  # Explicit Denials
  deny_subcommands: ["dangerous_cmd"]    # Blocked subcommands
```

### Policy Categories

#### 1. Simple Commands (OS Utilities)
For basic system commands:

```yaml
which:
  validator: os_basic
  flags: ["-a", "--version"]
  default_timeout: 5

echo:
  validator: os_basic
  flags: ["--help", "-n", "-e"]
  default_timeout: 5
```

#### 2. Development Tools
For tools with moderate complexity:

```yaml
git:
  description: "Read-only/metadata git operations (no mutations)."
  subcommands:
    status: { flags: ["--porcelain", "-s", "-b", "--no-color"], timeout: 20 }
    log: { flags: ["--oneline", "--graph", "--decorate", "-n", "-p", "--no-color"] }
    diff: { flags: ["--name-only", "--stat", "--cached", "-p", "--no-color"] }
  deny_global_flags: ["-c", "--exec-path", "--help", "-P"]
  env_overrides:
    GIT_PAGER: "cat"
    CLICOLOR: "0"
    TERM: "dumb"
  default_timeout: 30
```

#### 3. Package Managers
For script execution tools:

```yaml
npm:
  validator: npm
  root_flags: ["-v", "--version", "--help"]
  subcommands:
    run:
      allowed_scripts: ["build", "test", "lint", "format", "typecheck"]
      deny_args: false
      allow_test_paths: true
    install:
      enabled: false
      require_no_packages: true
      require_flags: ["--ignore-scripts"]
      allowed_flags: ["--ignore-scripts", "--no-audit", "--prefer-offline"]
  deny_subcommands: ["exec", "publish", "update", "audit"]
  default_timeout: 120
```

#### 4. Build Tools
For complex build systems:

```yaml
dotnet:
  validator: dotnet
  subcommands:
    test:
      flags: ["--configuration", "-c", "--no-build", "--nologo", "--verbosity", "--logger"]
      allow_project_paths: true
      allow_test_paths: false
      require_flags:
        --no-build: true
        --nologo: true
        --verbosity: ["minimal", "quiet"]
        --logger: "console;verbosity=minimal"
  deny_subcommands: ["run", "publish", "tool", "pack"]
  default_timeout: 300
```

#### 5. Testing Tools
For test frameworks:

```yaml
pytest:
  flags: ["-q", "--maxfail", "--disable-warnings", "--no-header", "--tb"]
  allow_test_paths: true
  default_timeout: 120
  env_overrides:
    PYTEST_ADDOPTS: "-q --color=no --maxfail=1"
    PYTEST_DISABLE_PLUGIN_AUTOLOAD: "1"
    PYTHONWARNINGS: "ignore"
```

#### 6. High-Risk Tools
For powerful tools requiring maximum security:

```yaml
powershell:
  validator: powershell
  description: "Execute safe, read-only PowerShell cmdlets for information gathering only"
  flags: ["-Help", "-?", "-NoProfile", "-NonInteractive", "-NoLogo"]
  deny_global_flags: ["-Command", "-c", "-EncodedCommand", "-File"]
  require_flags: ["-NoProfile", "-NonInteractive"]
  safe_cmdlets: ["get-process", "get-service", "get-location"]
  dangerous_patterns: ["invoke-expression", "start-process", "new-object"]
  safe_env:
    PSExecutionPolicyPreference: "Restricted"
    __PSLockdownPolicy: "1"
  default_timeout: 30
```

## Creating Custom Validators

### 1. Validator Class Structure

Create a new validator in `executors/local_storage/validators/`:

```python
from typing import Dict, Any, List, Mapping, Optional
import os
from .base_validator import ValidationResult, CommandValidator
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

class MyCommandValidator(CommandValidator):
    """
    Custom validator for 'mycommand' with specific security requirements.
    
    Expected policy shape:
      mycommand:
        subcommands:
          safe_action: { allowed_flags: [...] }
          risky_action: { enabled: false }
        deny_subcommands: [...]
        default_timeout: 60
        env_overrides: {...}
    """

    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        """Validate command against policy."""
        name = os.path.splitext(os.path.basename(parts[0]))[0].lower()
        if name != "mycommand":
            return ValidationResult(False, "Not a mycommand")

        if len(parts) < 2:
            return ValidationResult(False, "Missing subcommand")

        subcommand = parts[1]
        subcommands = policy.get("subcommands", {})
        deny_subcommands = set(policy.get("deny_subcommands", []))

        # Check if subcommand is explicitly denied
        if subcommand in deny_subcommands:
            return ValidationResult(False, f"Subcommand not allowed: {subcommand}")

        # Check if subcommand is configured
        if subcommand not in subcommands:
            return ValidationResult(False, f"Subcommand not configured: {subcommand}")

        subcommand_spec = subcommands[subcommand]
        
        # Check if subcommand is enabled
        if not subcommand_spec.get("enabled", True):
            return ValidationResult(False, f"Subcommand disabled: {subcommand}")

        # Validate flags
        allowed_flags = set(subcommand_spec.get("allowed_flags", []))
        used_flags = [arg for arg in parts[2:] if arg.startswith("-")]
        
        for flag in used_flags:
            base_flag = self._flag_base(flag)
            if base_flag not in allowed_flags and flag not in allowed_flags:
                return ValidationResult(False, f"Flag not allowed: {flag}")

        # Path safety validation if needed
        workspace_root = (
            policy.get("workspace_root")
            or os.environ.get("WORKSPACE_ROOT")
            or os.getcwd()
        )
        
        if subcommand_spec.get("allow_test_paths", False):
            positionals = [arg for arg in parts[2:] if not arg.startswith("-")]
            for arg in positionals:
                if looks_like_path(arg):
                    file_part = extract_file_part(arg)
                    if not is_within_workspace(workspace_root, file_part):
                        return ValidationResult(False, f"Unsafe path: {arg}")

        # Get timeout
        timeout = subcommand_spec.get("timeout") or policy.get("default_timeout")
        
        return ValidationResult(True, "OK", timeout=timeout)

    def _flag_base(self, flag: str) -> str:
        """Handle flags with values like --flag=value."""
        return flag.split("=", 1)[0]

    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        """Configure safe environment for execution."""
        env = dict(base_env)
        
        # Apply safe environment from policy
        safe_env = policy.get("safe_env", {})
        env.update(safe_env)
        
        # Apply environment overrides from policy
        env_overrides = policy.get("env_overrides", {})
        env.update(env_overrides)
        
        return env

    def adjust_arguments(self, parts: List[str], policy: Mapping[str, Any]) -> List[str]:
        """
        Auto-inject required flags for subcommands if missing.
        Called AFTER validate() by the executor.
        """
        if len(parts) < 2:
            return parts

        subcommands = policy.get("subcommands", {})
        subcommand = parts[1].lower()
        subcommand_spec = subcommands.get(subcommand, {})

        required_flags = list(subcommand_spec.get("require_flags", {}))
        if not required_flags:
            return parts

        existing_flags = set()
        for p in parts[2:]:
            if p.startswith("-"):
                existing_flags.add(self._flag_base(p))

        # Insert missing required flags after the subcommand
        insert_at = 2
        for needed in required_flags:
            base = self._flag_base(needed)
            if base not in existing_flags:
                parts.insert(insert_at, needed)
                insert_at += 1

        return parts
```

### 2. Register the Validator

Validators are automatically registered based on the `validator` field in policies, or by command name. Add your validator to `SecureCommandExecutor`:

```python
# In SecureCommandExecutor.__init__()
self.validators: Dict[str, CommandValidator] = {
    "git": GitCommandValidator(),
    "pytest": PytestCommandValidator(),
    "os_basic": OSBasicValidator(),
    "node": NodeCommandValidator(),
    "npm": NpmCommandValidator(),
    "dotnet": DotnetCommandValidator(),
    "powershell": PowershellValidator(),
    "npx": NpxCommandValidator(),
    "pnpm": PnpmCommandValidator(),
    "lerna": LernaCommandValidator(),
    "mycommand": MyCommandValidator(),  # Add your validator here
}
```

### 3. Path Safety Integration

Use the path safety utilities for secure file/directory handling:

```python
from .path_safety import is_within_workspace, looks_like_path, extract_file_part

# Check if a token looks like a path
if looks_like_path(token):
    # Extract the file part (handles test selectors like file.py::test_name)
    file_part = extract_file_part(token)
    
    # Ensure it's within the workspace
    if not is_within_workspace(workspace_root, file_part):
        return ValidationResult(False, f"Unsafe path: {token}")
```

## Policy Provider Configuration

### File Resolution

The `YamlPolicyProvider` resolves the policy file using:

1. Environment override: `AGENTC_POLICIES_FILE` (absolute path)
2. `<config_path>/whitelist_commands.yaml`

### Loading and Caching

Policies are automatically loaded and cached with mtime checking:

```python
provider = YamlPolicyProvider()
policy = provider.get_policy("git")  # Returns policy dict or None
all_policies = provider.get_all_policies()  # Returns all loaded policies
provider.reload_policy()  # Force reload from disk
```

## Security Guidelines

### Flag Management

**Allowed Flags (`flags` / `allowed_flags`)**
- Only include flags that are known to be safe
- Prefer read-only and informational flags
- Always include color-disabling flags where available

**Denied Flags (`deny_flags` / `deny_global_flags`)**
- Explicitly block dangerous flags
- Include execution flags (`-e`, `--eval`, `-c`, `--command`)
- Block file manipulation flags where inappropriate

**Required Flags (`require_flags`)**
- Enforce security-critical flags (e.g., `--no-build`, `--ignore-scripts`)
- Use boolean `true` for flags that must be present
- Use arrays for flags that must have specific values
- Use strings for flags that must have exact values

### Path Safety

**Workspace Boundaries**
- `allow_test_paths`: Only enable for legitimate testing tools
- `allow_project_paths`: Enable for build tools that need project files
- `allow_script_paths`: Very rarely enable; high security risk

**File Access Controls**
- Always validate paths are within workspace boundaries
- Block absolute paths outside workspace
- Use `extract_file_part()` for test selectors

### Environment Security

**Environment Overrides (`env_overrides`)**
- Disable colors: `NO_COLOR: "1"`, `CLICOLOR: "0"`
- Disable telemetry: `TOOL_TELEMETRY_OPTOUT: "1"`
- Enable CI mode: `CI: "1"` (reduces interactivity)
- Set stable output: `TERM: "dumb"`

**Safe Environment (`safe_env`)**
- Use for tools requiring specific security settings
- Example: PowerShell execution policy restrictions

### Timeout Management

**Timeout Guidelines**
- OS utilities: 5-10 seconds
- Development tools: 30-60 seconds
- Package managers: 120-180 seconds
- Build tools: 300-600 seconds
- Testing tools: 120-300 seconds

## Validation Features

### ValidationResult Options

```python
@dataclass
class ValidationResult:
    allowed: bool                              # Required: Allow/block the command
    reason: str = "OK"                        # Error message if blocked
    timeout: Optional[int] = None             # Override default timeout
    env_overrides: Dict[str, str] = field(default_factory=dict)  # Environment changes
```

### Validator Methods

**Required Methods:**
- `validate(parts, policy)` → `ValidationResult`
- `adjust_environment(base_env, parts, policy)` → `Dict[str, str]`

**Optional Methods:**
- `adjust_arguments(parts, policy)` → `List[str]` - Modify command before execution

## Examples

### Complete Policy Example

```yaml
mycommand:
  validator: mycommand
  description: "Execute mycommand operations with security restrictions"
  
  # Global flags allowed for all subcommands
  flags: ["-v", "--version", "--help"]
  
  # Flags denied for all subcommands
  deny_global_flags: ["--unsafe", "--exec"]
  
  # Subcommand definitions
  subcommands:
    info:
      flags: ["--json", "--verbose"]
      timeout: 15
    
    process:
      flags: ["--input", "--output", "--format"]
      allow_test_paths: true
      require_flags:
        --safe-mode: true
        --verbosity: ["quiet", "minimal"]
      timeout: 120
    
    dangerous:
      enabled: false  # Completely disabled
  
  # Explicitly blocked subcommands
  deny_subcommands: ["exec", "eval", "shell"]
  
  # Environment security
  safe_env:
    MYCOMMAND_SAFE_MODE: "1"
    MYCOMMAND_TELEMETRY: "0"
  
  env_overrides:
    NO_COLOR: "1"
    CLICOLOR: "0"
  
  default_timeout: 60
```

### Testing Your Validator

```python
def test_mycommand_validator():
    validator = MyCommandValidator()
    policy = {
        "subcommands": {
            "info": {"flags": ["-v", "--json"]},
            "process": {"flags": ["--input"], "allow_test_paths": True}
        },
        "deny_subcommands": ["dangerous"]
    }
    
    # Should allow
    result = validator.validate(["mycommand", "info", "-v"], policy)
    assert result.allowed
    
    # Should block - dangerous subcommand
    result = validator.validate(["mycommand", "dangerous"], policy)
    assert not result.allowed
    
    # Should block - invalid flag
    result = validator.validate(["mycommand", "info", "--invalid"], policy)
    assert not result.allowed
    
    # Should allow - test path when enabled
    result = validator.validate(["mycommand", "process", "test.py"], policy)
    assert result.allowed
```

## Best Practices

### Validator Design
1. **Fail Secure** - Block anything not explicitly allowed
2. **Clear Error Messages** - Help users understand why commands are blocked
3. **Path Safety First** - Always validate file/directory access
4. **Environment Isolation** - Control dangerous environment variables
5. **Consistent Patterns** - Follow established patterns from existing validators

### Policy Design
1. **Principle of Least Privilege** - Only allow what's necessary
2. **Document Intent** - Use `description` fields to explain security rationale
3. **Reasonable Timeouts** - Balance security with usability
4. **Environment Controls** - Disable dangerous features and telemetry
5. **Test Thoroughly** - Verify both positive and negative cases

### Security Considerations
1. **Whitelist Approach** - Only explicitly allowed commands pass through
2. **Multi-Layer Validation** - Policy + validator + path safety + environment
3. **No Shell Execution** - Always use `shell=False` for subprocess execution
4. **Resource Limits** - Enforce timeouts and output size limits
5. **Audit Trail** - Log all command executions for security review

This system provides strong security guarantees while remaining flexible enough to support a wide variety of development tools and workflows.