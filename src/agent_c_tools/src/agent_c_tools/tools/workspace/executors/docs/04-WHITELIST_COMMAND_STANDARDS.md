# Whitelist Command Configuration Standards

This document establishes the standardized structure for defining command policies in the `whitelist_commands.yaml` configuration file. These policies control which commands, flags, and operations are permitted within the secure execution environment.

## Overview

The whitelist command system uses a hierarchical YAML structure to define security policies for external tools and commands. Each command definition specifies:

- **Allowed operations**: Which subcommands, flags, and arguments are permitted
- **Security restrictions**: Which operations are explicitly denied or require special handling
- **Execution parameters**: Timeouts, environment variables, and runtime constraints
- **Path safety**: Workspace boundary enforcement and file system access controls

## Standard Structure

### Top-Level Command Definition

```yaml
command_name:
  # Core Configuration
  validator: validator_class_name          # Optional: Custom validator (defaults to command_name)
  description: "Human-readable description. This doubles as a fallback to a tool param description." # Optional: Purpose and safety rationale
  
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
      # ... subcommand-specific configuration
  
  # Explicit Denials
  deny_subcommands: ["dangerous_cmd"]    # Blocked subcommands
```

### Subcommand Configuration

```yaml
subcommands:
  subcommand_name:
    # Flag Control
    flags: ["--safe-flag"]               # Allowed flags for this subcommand
    allowed_flags: ["--alt-syntax"]      # Alternative syntax (some validators use this)
    deny_flags: ["--dangerous"]         # Explicitly blocked flags
    require_flags:                       # Flags that must be present
      --no-build: true                   # Boolean: flag must be present
      --verbosity: ["minimal", "quiet"]  # Array: flag value must be in list
      --logger: "console;verbosity=minimal" # String: flag must have exact value
    
    # Argument Control
    allowed_scripts: ["test", "build"]   # For script runners (npm, pnpm, lerna)
    deny_args: false                     # Whether to block additional arguments
    require_no_packages: true            # Block package name arguments
    
    # Path Safety
    allow_test_paths: false              # Allow workspace-relative test file paths
    allow_project_paths: true           # Allow project/solution file paths
    allow_script_paths: false           # Allow script file execution
    
    # Execution Control
    timeout: 300                         # Override default timeout for this subcommand
    enabled: true                        # Whether subcommand is enabled
    
    # Special Behaviors
    get_only: true                       # Special: only allow 'get' operations
```

## Configuration Categories

### 1. Simple Commands (OS Utilities)

For basic system commands with minimal complexity:

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

**Standards:**
- Use `validator: os_basic` for simple OS utilities
- Keep `flags` list minimal and safe
- Use short timeouts (5-10 seconds)
- No subcommands needed

### 2. Development Tools (Git, Node, etc.)

For development tools with moderate complexity:

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

**Standards:**
- Provide descriptive `description` explaining security rationale
- Use `subcommands` for tools with multiple operations
- Always include `--no-color` type flags where available
- Set `env_overrides` to disable interactive features
- Use `deny_global_flags` to block dangerous global options

### 3. Package Managers (npm, pnpm, lerna)

For package managers with script execution capabilities:

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
  env_overrides:
    NPM_CONFIG_COLOR: "false"
    NO_COLOR: "1"
    CI: "1"
```

**Standards:**
- Use `allowed_scripts` to whitelist safe npm/pnpm scripts
- Set `deny_args: false` cautiously (only for trusted script runners)
- Use `require_flags` to enforce security flags like `--ignore-scripts`
- Block dangerous subcommands with `deny_subcommands`
- Set `CI: "1"` to reduce interactivity

### 4. Build Tools (dotnet, etc.)

For build tools with complex flag requirements:

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
    build:
      flags: ["--configuration", "-c", "--no-restore", "--nologo", "--verbosity"]
      require_flags:
        --nologo: true
        --verbosity: ["quiet", "minimal"]
  deny_subcommands: ["run", "publish", "tool", "pack"]
  default_timeout: 300
```

**Standards:**
- Use `require_flags` extensively to enforce security defaults
- Set `allow_project_paths: true` for build tools that need project files
- Set `allow_test_paths: false` by default (enable cautiously)
- Use longer timeouts (300+ seconds) for build operations
- Block dangerous subcommands that can execute arbitrary code

### 5. Testing Tools (pytest, etc.)

For testing frameworks with path access needs:

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

**Standards:**
- Set `allow_test_paths: true` for testing tools that need file access
- Use `env_overrides` to set safe defaults (no color, quiet mode)
- Disable plugin autoloading for security
- Use moderate timeouts (120-300 seconds)

### 6. High-Risk Tools (PowerShell, etc.)

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

**Standards:**
- Provide detailed `description` and security rationale
- Use extensive `deny_global_flags` lists
- Define `safe_cmdlets` whitelist for allowed operations
- Use `dangerous_patterns` regex list to block risky content
- Set `safe_env` to enforce security policies
- Use short timeouts and minimal permissions

## Security Guidelines

### Flag Management

1. **Allowed Flags (`flags` / `allowed_flags`)**
   - Only include flags that are known to be safe
   - Prefer read-only and informational flags
   - Always include color-disabling flags where available

2. **Denied Flags (`deny_flags` / `deny_global_flags`)**
   - Explicitly block dangerous flags that might slip through
   - Include execution flags (`-e`, `--eval`, `-c`, `--command`)
   - Block file manipulation flags where inappropriate

3. **Required Flags (`require_flags`)**
   - Enforce security-critical flags (e.g., `--no-build`, `--ignore-scripts`)
   - Use boolean `true` for flags that must be present
   - Use arrays for flags that must have specific values
   - Use strings for flags that must have exact values

### Path Safety

1. **Workspace Boundaries**
   - `allow_test_paths`: Only enable for legitimate testing tools
   - `allow_project_paths`: Enable for build tools that need project files
   - `allow_script_paths`: Very rarely enable; high security risk

2. **File Access Controls**
   - Prefer using filters/selectors over direct file paths
   - Always validate paths are within workspace boundaries
   - Block absolute paths outside workspace

### Environment Security

1. **Environment Overrides (`env_overrides`)**
   - Disable colors: `NO_COLOR: "1"`, `CLICOLOR: "0"`
   - Disable telemetry: `TOOL_TELEMETRY_OPTOUT: "1"`
   - Enable CI mode: `CI: "1"` (reduces interactivity)
   - Set stable output: `TERM: "dumb"`

2. **Safe Environment (`safe_env`)**
   - Use for tools requiring specific security settings
   - Example: PowerShell execution policy restrictions

### Timeout Management

1. **Timeout Guidelines**
   - OS utilities: 5-10 seconds
   - Development tools: 30-60 seconds
   - Package managers: 120-180 seconds
   - Build tools: 300-600 seconds
   - Testing tools: 120-300 seconds

2. **Timeout Overrides**
   - Use subcommand-level `timeout` for operations needing different limits
   - Consider complexity and expected runtime of operations

## Validation

### Custom Validators

Tools requiring complex validation logic should implement custom validators:

```yaml
tool_name:
  validator: custom_validator_class  # Maps to CustomValidatorClass
```

Validator classes should be placed in:
- `src/agent_c_tools/tools/workspace/executors/local_storage/validators/`

### Standard Validators

- `os_basic`: Simple OS utilities with basic flag validation
- `git`: Git operations with read-only restrictions
- `npm`/`pnpm`: Package managers with script allowlisting
- `dotnet`: .NET build tools with complex flag requirements
- `node`: Node.js runtime with execution restrictions
- `powershell`: PowerShell with extensive security controls

## Testing Requirements

All whitelist command configurations must include comprehensive tests:

1. **Positive Tests**: Verify allowed operations work correctly
2. **Negative Tests**: Verify blocked operations are rejected
3. **Path Safety Tests**: Verify workspace boundary enforcement
4. **Flag Validation Tests**: Verify required and denied flags work correctly
5. **Security Tests**: Verify dangerous operations are blocked

Test files should be placed in:
- `src/agent_c_tools/tools/workspace/executors/tests/policy_tests/`

## Examples

### Adding a New Simple Command

```yaml
curl:
  validator: os_basic
  flags: ["-s", "--silent", "-L", "--location", "--max-time"]
  deny_global_flags: ["-o", "--output", "-F", "--form"]
  default_timeout: 30
  env_overrides:
    NO_COLOR: "1"
```

### Adding a New Build Tool

```yaml
maven:
  validator: maven
  description: "Maven build tool with restricted operations"
  subcommands:
    compile:
      flags: ["-q", "--quiet", "-B", "--batch-mode"]
      require_flags:
        -B: true  # Batch mode required
    test:
      flags: ["-q", "--quiet", "-B", "--batch-mode", "-Dtest"]
      allow_test_paths: true
      require_flags:
        -B: true
  deny_subcommands: ["exec", "deploy", "release"]
  default_timeout: 300
  env_overrides:
    MAVEN_OPTS: "-Djansi.force=false"
    NO_COLOR: "1"
```

## Version History

- **v1.0**: Initial whitelist command standards
- **v1.1**: Added testing tool path handling standards
- **v1.2**: Enhanced security guidelines and validation requirements

---

This document should be updated whenever new command patterns or security requirements are identified. All changes should be reviewed for security implications before implementation.
