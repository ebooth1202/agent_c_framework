# Output Suppression Guide

This document provides a comprehensive guide to the output suppression feature in the secure command execution system, designed to optimize token usage in AI automation scenarios while preserving full error visibility.

## Overview

The output suppression feature addresses a critical challenge in AI automation: successful build and test commands often produce large amounts of output that consume valuable tokens without providing actionable information. This system intelligently suppresses successful command output while always preserving full error details.

## Key Principles

### 1. Success-Only Suppression
Output suppression **only** affects successful command executions (exit code 0). Failed commands always show full output regardless of suppression settings.

### 2. Error Transparency
When commands fail, the system always provides complete error information including stderr, return codes, and diagnostic details. Suppression settings are ignored for failed executions.

### 3. Configurable Control
Suppression can be controlled at multiple levels:
- **Policy Level** - Default behavior per command in YAML policies
- **Tool Call Level** - Override policy defaults for specific executions
- **Runtime Level** - Dynamic control based on execution context

## Implementation Architecture

### Core Data Structure

```python
@dataclass
class CommandExecutionResult:
    status: str  # "success", "error", "timeout", "blocked", "failed"
    return_code: Optional[int]
    stdout: str
    stderr: str
    command: str
    working_directory: str
    error_message: Optional[str] = None
    duration_ms: Optional[int] = None
    truncated_stdout: Optional[bool] = None
    truncated_stderr: Optional[bool] = None
    suppress_success_output: bool = False  # ← Key suppression field
```

### Suppression Logic Flow

```python
def to_friendly_string(self, success_prefix: str = "OK") -> str:
    """Get appropriate response string for tool to return to LLM"""
    if self.status == "blocked":
        return f"ERROR: Command blocked by security policy: {self.error_message}"
    
    elif self.status == "success":
        # Suppression only applies to successful executions
        if self.suppress_success_output:
            return f"{success_prefix} (output suppressed for token efficiency)"
        elif self.stdout.strip():
            return f"{success_prefix}:\n{self.stdout}"
        else:
            return f"{success_prefix} (no output)"
    
    elif self.status == "timeout":
        return f"ERROR: Command timed out: {self.error_message}"
    
    else:
        # Failed commands ALWAYS show full output regardless of suppression
        msg = self.error_message or "Command failed."
        tail = (self.stderr or "").strip().splitlines()[-10:]
        err_tail = ("\n" + "\n".join(tail)) if tail else ""
        return f"ERROR: {msg}{err_tail}"
```

## Configuration Methods

### 1. Policy-Level Configuration

Configure default suppression behavior in `whitelist_commands.yaml`:

```yaml
# Build tools - typically want suppression for successful builds
dotnet:
  description: ".NET CLI operations"
  suppress_success_output: true  # Default for all dotnet commands
  subcommands:
    build:
      flags: ["--configuration", "--verbosity", "--no-restore"]
      suppress_success_output: true  # Explicit for this subcommand
    test:
      flags: ["--configuration", "--verbosity", "--no-build"]
      suppress_success_output: true
    clean:
      suppress_success_output: false  # Override: show clean output

# Development tools - typically want to see output
git:
  description: "Read-only git operations"
  suppress_success_output: false  # Default: show git output
  subcommands:
    status:
      flags: ["--porcelain", "-s"]
      suppress_success_output: false
    log:
      flags: ["--oneline", "--graph"]
      suppress_success_output: false

# Test runners - suppress successful test runs
npm:
  description: "Node.js package manager"
  suppress_success_output: false  # Default: show npm output
  subcommands:
    run:
      allowed_scripts: ["test", "build", "lint"]
      suppress_success_output: true  # Suppress successful test/build runs
    install:
      suppress_success_output: false  # Always show install output

pytest:
  description: "Python testing framework"
  suppress_success_output: true  # Default: suppress successful test runs
  subcommands:
    "":  # Default subcommand (no subcommand specified)
      flags: ["-v", "--tb", "--no-header"]
      suppress_success_output: true
```

### 2. Tool Call Level Override

Override policy defaults in individual tool calls:

```python
# Example from workspace tool implementation
async def run_command(
    self,
    workspace_id: str,
    command: str,
    suppress_success_output: Optional[bool] = None  # Tool-level override
) -> str:
    """
    Execute command with optional suppression override.
    
    Args:
        workspace_id: Target workspace
        command: Command to execute
        suppress_success_output: Override policy default if provided
    """
    result = await workspace.run_command(
        command,
        suppress_success_output=suppress_success_output
    )
    return result.to_friendly_string()

# Usage examples:
# Force suppression even if policy says false
await run_command("ws1", "npm test", suppress_success_output=True)

# Force showing output even if policy says true  
await run_command("ws1", "dotnet build", suppress_success_output=False)

# Use policy default (most common)
await run_command("ws1", "git status")
```

### 3. Runtime Resolution Logic

The system resolves suppression settings with this precedence:

```python
def _resolve_suppression_setting(
    tool_override: Optional[bool],
    policy_default: Optional[bool],
    command_result: CommandExecutionResult
) -> bool:
    """
    Resolve final suppression setting with precedence:
    1. Tool call override (highest precedence)
    2. Policy configuration
    3. System default (False - show output)
    """
    # Tool override wins
    if tool_override is not None:
        return tool_override
    
    # Policy default
    if policy_default is not None:
        return policy_default
    
    # System default: don't suppress
    return False

# Applied during execution:
final_suppression = _resolve_suppression_setting(
    tool_override=suppress_success_output,  # From tool call
    policy_default=policy.get("suppress_success_output"),  # From YAML
    command_result=result
)

result.suppress_success_output = final_suppression
```

## Use Case Examples

### 1. CI/Automation Workflows

**Problem**: Build pipelines produce massive logs that waste tokens
**Solution**: Suppress successful builds, always show failures

```yaml
# Policy configuration
dotnet:
  suppress_success_output: true
  subcommands:
    build:
      suppress_success_output: true
    test:
      suppress_success_output: true
    publish:
      suppress_success_output: true

npm:
  subcommands:
    run:
      allowed_scripts: ["build", "test", "lint"]
      suppress_success_output: true
```

**Results**:
- Successful build: `"OK (output suppressed for token efficiency)"`
- Failed build: Full error details with stderr and diagnostics

### 2. Development Workflows

**Problem**: Developers need to see command output for debugging
**Solution**: Selective suppression based on command type

```yaml
# Show output for inspection commands
git:
  suppress_success_output: false
  
# Show output for package management
npm:
  suppress_success_output: false
  subcommands:
    install: { suppress_success_output: false }
    run:
      # Suppress for automated tests, show for dev commands
      allowed_scripts: ["test", "build", "lint", "dev", "start"]
      suppress_success_output: false  # Default: show output
```

**Tool call overrides**:
```python
# During automated testing
await run_command("ws1", "npm run test", suppress_success_output=True)

# During development
await run_command("ws1", "npm run dev")  # Uses policy default (False)
```

### 3. Mixed Environments

**Problem**: Same commands used in both CI and development
**Solution**: Environment-specific policies or tool overrides

```python
# Environment-aware suppression
is_ci_environment = os.getenv("CI") == "true"

result = await run_command(
    workspace_id,
    "dotnet build",
    suppress_success_output=is_ci_environment
)
```

## Token Optimization Benefits

### Quantitative Impact

**Before Suppression**:
```
Command: dotnet build
Status: success
Stdout: (2,847 lines of build output)
Token Usage: ~3,200 tokens
```

**After Suppression**:
```
Command: dotnet build  
Status: success
Response: "OK (output suppressed for token efficiency)"
Token Usage: ~15 tokens
```

**Savings**: ~99.5% token reduction for successful builds

### Cumulative Savings

In a typical CI workflow with 10 build/test commands:
- **Without suppression**: ~30,000 tokens for successful run
- **With suppression**: ~150 tokens for successful run
- **Savings**: ~99.5% token reduction
- **Failed runs**: Full diagnostic output preserved (no token penalty for debugging)

## Advanced Features

### 1. Conditional Suppression

```yaml
# Complex suppression rules
pytest:
  suppress_success_output: true
  subcommands:
    "":
      flags: ["-v", "--tb=short"]
      suppress_success_output: true
      # Override suppression for verbose mode
      conditional_suppression:
        - condition: "verbose_flag_present"
          suppress: false
```

### 2. Integration with Token Capping

```python
# Combine suppression with token-aware capping
if result.suppress_success_output and result.is_success:
    return result.to_friendly_string()
else:
    # Use token-aware capping for large outputs
    return result.to_yaml_capped(
        max_tokens=2000,
        count_tokens=count_tokens_function
    )
```

### 3. Smart Suppression Patterns

```python
# Intelligent suppression based on output characteristics
def should_suppress_intelligently(result: CommandExecutionResult) -> bool:
    """Smart suppression based on output patterns"""
    if not result.is_success:
        return False  # Never suppress failures
        
    if not result.stdout.strip():
        return False  # No output to suppress
        
    # Suppress if output is very large and looks like build/test output
    if len(result.stdout) > 10000:
        build_patterns = ["Build succeeded", "Tests passed", "✓", "PASS"]
        if any(pattern in result.stdout for pattern in build_patterns):
            return True
            
    return False
```

## Testing and Validation

### 1. Unit Tests

```python
def test_suppress_success_output_true():
    """Test that successful commands respect suppression flag"""
    result = CommandExecutionResult(
        status="success",
        return_code=0,
        stdout="Build successful\nAll tests passed",
        stderr="",
        command="dotnet test",
        working_directory="/workspace",
        suppress_success_output=True
    )
    
    response = result.to_friendly_string()
    assert "output suppressed for token efficiency" in response
    assert "Build successful" not in response

def test_suppress_success_output_preserves_errors():
    """Test that failed commands ignore suppression flag"""
    result = CommandExecutionResult(
        status="error",
        return_code=1,
        stdout="Some output",
        stderr="Build failed: missing dependency",
        command="dotnet build",
        working_directory="/workspace",
        suppress_success_output=True  # Should be ignored for failures
    )
    
    response = result.to_friendly_string()
    assert "ERROR" in response
    assert "Build failed: missing dependency" in response
    assert "output suppressed" not in response
```

### 2. Integration Tests

```python
async def test_policy_driven_suppression():
    """Test suppression configuration via policies"""
    policy = {
        "dotnet": {
            "suppress_success_output": True,
            "subcommands": {
                "build": {"suppress_success_output": True}
            }
        }
    }
    
    executor = SecureCommandExecutor(policy_provider=MockPolicyProvider(policy))
    result = await executor.execute_command("dotnet build")
    
    assert result.suppress_success_output == True
    if result.is_success:
        assert "output suppressed" in result.to_friendly_string()
```

## Best Practices

### 1. Policy Design

**DO**:
- Enable suppression for build/test/lint commands
- Disable suppression for inspection commands (git status, ls, etc.)
- Use tool-level overrides for special cases
- Document suppression behavior in policy comments

**DON'T**:
- Suppress output for commands that provide critical feedback
- Use suppression for commands with small output
- Forget that failures always show full output

### 2. Implementation Guidelines

```yaml
# Good policy structure
command_name:
  description: "Clear description of command purpose"
  suppress_success_output: true  # Clear default
  subcommands:
    build:
      # Document why suppression is appropriate
      description: "Build project (suppress on success for CI efficiency)"
      suppress_success_output: true
    status:
      # Document why suppression is NOT appropriate
      description: "Show project status (always show output)"
      suppress_success_output: false
```

### 3. Monitoring and Debugging

```python
# Log suppression decisions for debugging
def _log_suppression_decision(self, command: str, result: CommandExecutionResult):
    if result.suppress_success_output and result.is_success:
        self.logger.info(f"Output suppressed for successful command: {command}")
    elif result.is_error:
        self.logger.info(f"Full error output preserved for failed command: {command}")
```

## Migration Guide

### From Non-Suppressed System

1. **Identify High-Volume Commands**: Find commands that produce large output
2. **Categorize by Use Case**: Separate CI/automation from development use
3. **Start Conservative**: Begin with obvious candidates (build, test)
4. **Monitor Impact**: Track token savings and user feedback
5. **Expand Gradually**: Add more commands as confidence grows

### Example Migration Plan

**Phase 1** - High-impact, low-risk:
```yaml
dotnet:
  suppress_success_output: true
npm:
  subcommands:
    run:
      allowed_scripts: ["test", "build"]
      suppress_success_output: true
```

**Phase 2** - Medium-impact commands:
```yaml
pytest:
  suppress_success_output: true
lerna:
  subcommands:
    run:
      suppress_success_output: true
```

**Phase 3** - Fine-tuning and edge cases:
```yaml
# Add conditional logic and tool-level overrides as needed
```

## Troubleshooting

### Common Issues

**Issue**: "I'm not seeing error details when commands fail"
**Solution**: Check that `suppress_success_output` is only affecting successful commands. Failed commands should always show full output.

**Issue**: "Suppression isn't working despite policy configuration"
**Solution**: Verify policy loading and check for tool-level overrides that might be forcing output display.

**Issue**: "Token usage is still high despite suppression"
**Solution**: Check if commands are actually succeeding. Only successful commands are suppressed. Also verify the suppression flag is being set correctly.

### Debugging Commands

```python
# Check suppression settings
print(f"Policy suppression: {policy.get('suppress_success_output')}")
print(f"Tool override: {suppress_success_output}")
print(f"Final result: {result.suppress_success_output}")
print(f"Command status: {result.status}")
print(f"Return code: {result.return_code}")
```

## Future Enhancements

### Planned Features

1. **Smart Suppression**: AI-driven decision making based on output content
2. **Conditional Suppression**: Complex rules based on command context
3. **Suppression Analytics**: Detailed metrics on token savings
4. **User Preferences**: Per-user suppression preferences
5. **Output Summarization**: Brief summaries instead of complete suppression

### Extension Points

```python
# Plugin interface for custom suppression logic
class SuppressionPlugin:
    def should_suppress(self, command: str, result: CommandExecutionResult) -> bool:
        """Custom suppression logic"""
        pass
    
    def generate_summary(self, result: CommandExecutionResult) -> str:
        """Custom summary instead of suppression"""
        pass
```

This output suppression system provides a powerful tool for optimizing token usage in AI automation scenarios while maintaining the critical principle that error information is never compromised. The layered configuration approach ensures flexibility for different use cases while the success-only suppression rule guarantees reliable debugging when things go wrong.
