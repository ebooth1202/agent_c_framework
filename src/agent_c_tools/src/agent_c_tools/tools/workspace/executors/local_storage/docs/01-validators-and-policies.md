# Command Validators and Security Policies Guide

This document explains how to add validators, configure security policies, and manage command execution entries in the Agent C Framework workspace system.

## Overview

The secure command execution system uses a three-layer approach:
1. **Policy Provider** - Defines what commands and arguments are allowed (YAML configuration)
2. **Validators** - Enforce the policies and provide command-specific logic
3. **Secure Command Executor** - Manages actual execution with security controls

## Adding New Validators

### 1. Create a Validator Class

Create a new validator in `executors/local_storage/validators/` by inheriting from the `CommandValidator` protocol:

```python
from typing import Dict, Any, List, Mapping
from .base_validator import ValidationResult

class MyCommandValidator:
    """
    Custom validator for 'mycommand' with specific security requirements.
    """
    
    def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
        """
        Validate command parts against policy.
        
        Args:
            parts: Command split into parts (e.g., ['git', 'status', '--porcelain'])
            policy: Policy configuration from YAML
            
        Returns:
            ValidationResult with allowed status and optional timeout/env overrides
        """
        if not parts or parts[0] != "mycommand":
            return ValidationResult(False, "Not a mycommand")
            
        # Example: Require subcommand
        if len(parts) < 2:
            return ValidationResult(False, "Missing subcommand")
            
        subcommand = parts[1]
        allowed_subs = policy.get("subcommands", {})
        
        if subcommand not in allowed_subs:
            return ValidationResult(False, f"Subcommand not allowed: {subcommand}")
            
        # Validate flags for this subcommand
        sub_policy = allowed_subs[subcommand]
        allowed_flags = set(sub_policy.get("flags", []))
        used_flags = [p for p in parts[2:] if p.startswith("-")]
        
        for flag in used_flags:
            base_flag = flag.split("=", 1)[0]  # Handle --flag=value
            if base_flag not in allowed_flags and flag not in allowed_flags:
                return ValidationResult(False, f"Flag not allowed: {flag}")
        
        # Custom timeout from policy
        timeout = sub_policy.get("timeout") or policy.get("default_timeout")
        
        return ValidationResult(True, "OK", timeout=timeout)
    
    def adjust_environment(self, base_env: Dict[str, str], parts: List[str], policy: Mapping[str, Any]) -> Dict[str, str]:
        """
        Modify environment variables for secure execution.
        
        Args:
            base_env: Current environment
            parts: Command parts
            policy: Policy configuration
            
        Returns:
            Modified environment dictionary
        """
        env = dict(base_env)
        
        # Apply safe environment from policy
        safe_env = policy.get("safe_env", {})
        env.update(safe_env)
        
        # Apply command-specific overrides
        env_overrides = policy.get("env_overrides", {})
        env.update(env_overrides)
        
        return env
```

### 2. Register the Validator

Add your validator to the `SecureCommandExecutor` in `secure_command_executor.py`:

```python
# In SecureCommandExecutor.__init__()
self.validators: Dict[str, CommandValidator] = {
    "git": GitCommandValidator(),
    "pytest": PytestCommandValidator(),
    "mycommand": MyCommandValidator(),  # Add your validator here
}
```

### 3. What Validators Should Do

Validators are responsible for:

- **Command Authorization** - Verify the command is allowed
- **Argument Validation** - Check flags, subcommands, and parameters
- **Path Security** - Prevent directory traversal and unsafe paths
- **Environment Setup** - Configure safe environment variables
- **Timeout Configuration** - Set appropriate execution timeouts

Key principles:
- **Fail Secure** - Block anything not explicitly allowed
- **Stateless** - No side effects between validations
- **Clear Error Messages** - Help users understand why commands are blocked

## Policy Configuration in YAML

### Basic Structure

The `.agentc_policies.yaml` file defines allowed commands:

```yaml
# Command name (matches validator key)
mycommand:
  # Simple flag allowlist (for basic commands)
  flags: ["-v", "--verbose", "-q", "--quiet"]
  
  # OR subcommand-based structure (more complex commands)
  subcommands:
    run:
      flags: ["-v", "--dry-run", "--config"]
      timeout: 60
    test:
      flags: ["-q", "--parallel"]
      timeout: 120
  
  # Global settings
  default_timeout: 30
  
  # Safe environment variables (applied to all subcommands)
  safe_env:
    MYCOMMAND_SAFE_MODE: "1"
    MYCOMMAND_CONFIG: "/path/to/safe/config"
  
  # Environment overrides (higher priority than safe_env)
  env_overrides:
    MYCOMMAND_DEBUG: "0"
  
  # Global flag denials (blocked for all subcommands)
  deny_global_flags: ["--unsafe", "--exec"]
```

### Policy Examples

#### Simple Command (Basic Validator)
```yaml
curl:
  flags: ["-s", "-L", "--fail", "-o", "--max-time"]
  default_timeout: 30
  safe_env:
    HTTP_PROXY: ""
    HTTPS_PROXY: ""
```

#### Complex Command (Custom Validator)
```yaml
docker:
  subcommands:
    ps:
      flags: ["-a", "--format", "--filter"]
      timeout: 10
    images:
      flags: ["-a", "--format", "--filter"]
      timeout: 15
    inspect:
      flags: ["--format"]
      timeout: 20
  
  deny_global_flags: ["--privileged", "-v", "--volume"]
  
  safe_env:
    DOCKER_CONFIG: "/tmp/docker-readonly"
  
  default_timeout: 30
```

#### Environment-Specific Policies
```yaml
npm:
  subcommands:
    list:
      flags: ["--depth", "--json", "--global"]
      timeout: 30
    audit:
      flags: ["--json", "--audit-level"]
      timeout: 60
  
  # Secure npm execution
  safe_env:
    NPM_CONFIG_FUND: "false"
    NPM_CONFIG_AUDIT: "false"
    npm_config_yes: "false"
    npm_config_audit: "false"
  
  default_timeout: 45
```

## Adding Policy Entries

### 1. Identify Command Requirements

Before adding a policy entry:
- What subcommands need to be supported?
- Which flags are safe to allow?
- What environment variables should be controlled?
- What are appropriate timeout values?
- Are there any dangerous flags to explicitly deny?

### 2. Policy Entry Template

```yaml
command_name:
  # Choose ONE structure:
  
  # Option A: Simple flag-based (for commands without subcommands)
  flags: ["--safe-flag1", "--safe-flag2"]
  default_timeout: 30
  
  # Option B: Subcommand-based (for complex commands)
  subcommands:
    subcommand1:
      flags: ["--flag1", "--flag2"]
      timeout: 60  # Override default for this subcommand
    subcommand2:
      flags: ["--different-flags"]
      # Uses default_timeout
  
  # Common settings (optional)
  default_timeout: 30
  
  # Environment security (optional)
  safe_env:
    SAFE_VAR: "safe_value"
    
  env_overrides:
    OVERRIDE_VAR: "override_value"
  
  # Global restrictions (optional)
  deny_global_flags: ["--dangerous", "--exec"]
  
  # Custom validator (optional, defaults to command name)
  validator: "custom_validator_name"
```

### 3. Testing Policy Entries

Test your policies by:

1. **Positive Tests** - Verify allowed commands work
2. **Negative Tests** - Verify blocked commands are rejected
3. **Edge Cases** - Test flag combinations, empty commands, etc.

```python
# Example test in your validator
def test_policy():
    validator = MyCommandValidator()
    policy = {
        "subcommands": {
            "test": {"flags": ["-v", "--quiet"]}
        }
    }
    
    # Should allow
    result = validator.validate(["mycommand", "test", "-v"], policy)
    assert result.allowed
    
    # Should block
    result = validator.validate(["mycommand", "test", "--dangerous"], policy)
    assert not result.allowed
```

## Security Considerations

### Whitelisting Strategy

The system uses a **whitelist approach** - only explicitly allowed commands pass through:

1. **Command must have a policy** - No policy = blocked
2. **Command must have a validator** - No validator = blocked  
3. **Arguments must be explicitly allowed** - Unknown flags = blocked
4. **Paths are validated** - Directory traversal attempts = blocked

### Common Security Patterns

#### Flag Validation
```python
# Handle flag variations
allowed_flags = {"-v", "--verbose", "--output"}
used_flags = [p for p in parts if p.startswith("-")]

for flag in used_flags:
    base_flag = flag.split("=", 1)[0]  # Handle --flag=value
    if base_flag not in allowed_flags:
        return ValidationResult(False, f"Flag not allowed: {flag}")
```

#### Path Security
```python
# Prevent directory traversal
for arg in non_flag_args:
    if ".." in arg.split(os.sep):
        return ValidationResult(False, f"Unsafe path: {arg}")
    if os.path.isabs(arg) and not allow_absolute_paths:
        return ValidationResult(False, f"Absolute path not allowed: {arg}")
```

#### Environment Isolation
```python
def adjust_environment(self, base_env, parts, policy):
    env = dict(base_env)
    
    # Clear potentially dangerous variables
    dangerous_vars = ["LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH"]
    for var in dangerous_vars:
        env.pop(var, None)
    
    # Set safe defaults
    safe_env = policy.get("safe_env", {})
    env.update(safe_env)
    
    return env
```

## Validation Result Options

The `ValidationResult` class supports several configuration options:

```python
@dataclass
class ValidationResult:
    allowed: bool                              # Required: Allow/block the command
    reason: str = "OK"                        # Error message if blocked
    timeout: Optional[int] = None             # Override default timeout
    env_overrides: Dict[str, str] = field(default_factory=dict)  # Environment changes
```

Usage examples:

```python
# Simple allow/block
return ValidationResult(True, "OK")
return ValidationResult(False, "Command not allowed")

# With custom timeout
return ValidationResult(True, "OK", timeout=120)

# With environment overrides
return ValidationResult(
    True, 
    "OK", 
    timeout=60,
    env_overrides={"DEBUG_MODE": "1"}
)
```

## Best Practices

### Validator Design
1. **Minimize Complexity** - Keep validation logic simple and clear
2. **Consistent Patterns** - Follow established patterns from git/pytest validators
3. **Good Error Messages** - Help users understand what went wrong
4. **Document Assumptions** - Explain what the validator expects

### Policy Design
1. **Principle of Least Privilege** - Only allow what's necessary
2. **Clear Organization** - Group related commands and use consistent naming
3. **Reasonable Timeouts** - Balance security with usability
4. **Environment Safety** - Control variables that could affect security

### Testing
1. **Test All Paths** - Cover both allowed and blocked scenarios
2. **Test Flag Combinations** - Verify complex flag interactions
3. **Test Environment Changes** - Ensure environment modifications work correctly
4. **Test Edge Cases** - Empty commands, malformed input, etc.

This system provides strong security guarantees while remaining flexible enough to support a wide variety of development tools and workflows.
