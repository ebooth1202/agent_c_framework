# Secure Command Execution Architecture Overview

This document provides a comprehensive overview of the secure command execution architecture in the Agent C Framework, covering security mechanisms, architectural patterns, and implementation details.

## Executive Summary

The secure command execution system provides a robust, multi-layered security architecture that allows AI agents to execute operating system commands while maintaining strict security controls. The system employs whitelisting, policy-driven validation, path safety controls, and resource management to prevent malicious or accidental system damage.

## Core Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                      Workspace Tool Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  • UNC Path Validation   • Token Limits    • Error Handling    │
│  • Workspace Resolution  • Response Format • Output Capping    │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Workspace Implementations                    │
├─────────────────────────────────────────────────────────────────┤
│  LocalStorage │ S3Storage │ DockerWorkspace │ SSHWorkspace │ ... │
│  ✓ commands   │ ✗ no run  │ ✗ future       │ ✗ future     │     │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Secure Command Executor                        │
├─────────────────────────────────────────────────────────────────┤
│  • Command Parsing    • Policy Enforcement  • Resource Limits  │
│  • Validator Dispatch • Environment Control • Timeout Mgmt     │
│  • Executable Resolution • Path Safety    • Output Streaming  │
└─────────────────────┬──────────────���────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Policy    │ │ Validators  │ │  Execution  │
│  Provider   │ │             │ │   Engine    │
├─────────────┤ ├─────────────┤ ├─────────────┤
│YAML Config  │ │Git, Pytest │ │ subprocess  │
│Hot-reload   │ │npm, pnpm    │ │Async I/O    │
│Path resolve │ │dotnet, node │ │Cross-plat   │
│Multi-encode │ │PowerShell   │ │Stream caps  │
└─────────────┘ └─────────────┘ └─────────────┘
                      │
                      ▼
            ┌─────────────────┐
            │   Path Safety   │
            ├─────────────────┤
            │ Workspace fence │
            │ Path validation │
            │ Selector parse  │
            └─────────────────┘
```

### Security Layers

The architecture implements defense-in-depth through multiple security layers:

#### Layer 1: Tool Layer Security
- **UNC Path Validation** - Ensures commands execute in authorized workspaces
- **Token Limits** - Prevents excessive output from consuming resources via `to_yaml_capped()`
- **Workspace Isolation** - Commands cannot cross workspace boundaries

#### Layer 2: Workspace Security  
- **Path Sandboxing** - All operations constrained to workspace directories
- **Permission Control** - Read-only workspaces block command execution
- **Type Safety** - Only workspace types that explicitly support commands

#### Layer 3: Policy Security
- **Whitelist Enforcement** - Only commands with policies are allowed
- **Subcommand Control** - Granular subcommand and flag restrictions
- **Path Safety Integration** - Workspace boundary enforcement via `path_safety.py`

#### Layer 4: Validator Security
- **Command-Specific Logic** - Each command type has dedicated validation
- **Argument Processing** - Dynamic argument injection via `adjust_arguments()`
- **Environment Control** - Safe environment setup via `adjust_environment()`

#### Layer 5: Execution Security
- **Resource Limits** - Memory, timeout, and output size constraints
- **Process Isolation** - Commands run in controlled subprocess environments
- **Streaming I/O** - Bounded memory usage with early termination

#### Layer 6: Output Control Security
- **Success Output Suppression** - Test/build commands can suppress stdout on success
- **Error Transparency** - Failed commands always show full output regardless of suppression
- **Conditional Behavior** - Suppression only applies to successful executions (exit code 0)
- **CI/Automation Enhancement** - Cleaner automation workflows with preserved error visibility

## Security Mechanisms

### 1. Whitelisting Strategy

The system uses an **explicit whitelist approach** where security is the default state:

```yaml
# Only commands with policies are allowed
git:
  description: "Read-only/metadata git operations (no mutations)."
  subcommands:
    status: { flags: ["--porcelain", "-s", "--no-color"], timeout: 20 }
    log: { flags: ["--oneline", "--graph", "--decorate", "-n", "-p", "--no-color"] }
  deny_global_flags: ["-c", "--exec-path", "--help", "-P"]
  
# Commands without policies are automatically blocked  
# Example: "rm", "sudo", "curl" are blocked by default
```

**Key Principles:**
- **Default Deny** - Unknown commands are blocked
- **Explicit Allow** - Commands must be explicitly permitted with policies
- **Granular Control** - Per-command, per-subcommand, and per-argument control
- **Fail Secure** - Parsing errors or missing policies result in blocking

### 2. Policy-Based Validation

#### Current Policy Structure
```yaml
command_name:
  validator: validator_class_name          # Custom validator (defaults to command_name)
  description: "Human-readable description"
  
  # Global flags (apply to all subcommands)
  flags: ["-v", "--version", "--help"]     # Allowed global flags
  deny_global_flags: ["-e", "--eval"]     # Explicitly blocked global flags
  require_flags: ["-NoProfile"]           # Flags that must always be present
  
  # Subcommands (if applicable)
  subcommands:
    subcommand_name:
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
      require_no_packages: true           # Block package name arguments
      
      # Path Safety
      allow_test_paths: false              # Allow workspace-relative test file paths
      allow_project_paths: true           # Allow project/solution file paths
      allow_script_paths: false           # Allow script file execution
      
      # Execution Control
      timeout: 300                         # Override default timeout
      enabled: true                        # Whether subcommand is enabled
      
      # Special Behaviors
      get_only: true                       # Special: only allow 'get' operations
  
  # Environment Security
  env_overrides:                          # Environment variables to set/override
    NO_COLOR: "1"
    TOOL_DISABLE_TELEMETRY: "1"
  safe_env:                              # Required environment variables
    TOOL_SAFE_MODE: "1"
  
  # Explicit Denials
  deny_subcommands: ["dangerous_cmd"]    # Blocked subcommands
  default_timeout: 120                    # Default timeout in seconds
```

#### Policy Resolution Pipeline
```python
async def execute_command(command, working_directory, env, timeout):
    # 1. Parse command into parts using shlex
    parts = shlex.split(command, posix=not self.is_windows)
    
    # 2. Resolve base command (handles python -m pytest → pytest)
    base = self._resolve_base(parts)
    
    # 3. Policy lookup (must exist or command is blocked)
    policy = self.policy_provider.get_policy(base, parts) if self.policy_provider else None
    if not policy:
        return self._blocked(command, working_directory, f"No policy for '{base}'")
    
    # 4. Validator dispatch (must exist or command is blocked)
    validator_key = (policy.get("validator") or base).lower()
    validator = self.validators.get(validator_key)
    if not validator:
        return self._error(command, working_directory, f"No validator registered for '{base}'")
    
    # 5. Policy validation
    vres = validator.validate(parts, policy)
    if not vres.allowed:
        return self._blocked(command, working_directory, vres.reason)
    
    # 6. Argument adjustment (inject required flags, etc.)
    if hasattr(validator, "adjust_arguments"):
        parts = validator.adjust_arguments(parts, policy)
    
    # 7. Environment setup with validator adjustments
    effective_env = self._build_environment(base_env, validator, parts, policy)
    
    # 8. Executable resolution with PATH handling
    resolved = self._resolve_executable(parts[0], effective_env)
    if not resolved:
        return self._failed(command, working_directory, f"Executable not found: {parts[0]}")
    
    # 9. Secure subprocess execution
    return await self._run_subprocess_async(parts, cwd=working_directory, env=effective_env, timeout=effective_timeout)
```

### 3. Path Safety System

The system includes sophisticated path validation to prevent directory traversal and unauthorized file access:

```python
# path_safety.py utilities
def is_within_workspace(workspace_root: str, candidate: str) -> bool:
    """Ensure candidate path is within workspace boundaries."""
    if not candidate or not workspace_root:
        return False
    
    # Handle relative paths
    if not os.path.isabs(candidate):
        candidate = os.path.join(workspace_root, candidate)
    
    try:
        abs_root = os.path.normcase(os.path.realpath(workspace_root))
        abs_cand = os.path.normcase(os.path.realpath(candidate))
        return os.path.commonpath([abs_root, abs_cand]) == abs_root
    except Exception:
        return False

def looks_like_path(token: str) -> bool:
    """Detect if a token appears to be a file path."""
    if not token or token.startswith("-"):
        return False
    return (
        token.endswith((".py", ".ts", ".tsx", ".js", ".jsx", ".csproj", ".sln"))
        or "::" in token       # pytest node-ids
        or "/" in token or "\\" in token
        or ":" in token        # file:line OR Windows drive
    )

def extract_file_part(token: str) -> str:
    """Extract file path from test selectors like tests/foo.py::TestX::test_y"""
    t = token
    if "::" in t:
        t = t.split("::", 1)[0]  # Strip pytest node-id
    if ":" in t:
        i = t.rfind(":")
        if i > 1 and t[i+1:].isdigit():
            t = t[:i]  # Strip :line_number
    return t
```

#### Path Safety Integration in Validators
```python
# Example from npm_validator.py
if sub == "run":
    # ... validate script name ...
    
    # Determine args destined for the script, respecting `--`
    runner_args = rest[rest.index("--") + 1:] if "--" in rest else rest
    
    if spec.get("allow_test_paths", False):
        # Fence file/node-id selectors to workspace
        bad = next(
            (a for a in runner_args
             if looks_like_path(a)
             and not is_within_workspace(workspace_root, extract_file_part(a))),
            None
        )
        if bad:
            return ValidationResult(False, f"Unsafe path outside workspace in npm run args: {bad}")
```

### 4. Environment Security

The system provides sophisticated environment variable control:

#### Environment Building Pipeline
```python
def _build_environment(self, base_env, validator, parts, policy):
    env = dict(os.environ)
    
    # 1. Apply policy "safe_env" (static, lowest precedence)
    safe_env = policy.get("safe_env", {})
    env.update(safe_env)
    
    # 2. Apply workspace-provided overrides (CWD, WORKSPACE_ROOT)
    if override_env:
        env.update(override_env)
    
    # 3. Let validator adjust environment (may set PATH_PREPEND, etc.)
    if hasattr(validator, "adjust_environment"):
        env = validator.adjust_environment(env, parts, policy)
    
    # 4. Handle PATH_PREPEND for node_modules/.bin, etc.
    path_prepend = env.pop("PATH_PREPEND", None)
    if path_prepend:
        sep = ";" if self.is_windows else ":"
        env["PATH"] = f"{path_prepend}{sep}{env.get('PATH', '')}"
    
    return env
```

#### Standard Environment Controls
```yaml
# Common environment security patterns
git:
  safe_env:
    GIT_TERMINAL_PROMPT: "0"           # Disable interactive prompts
    GIT_CONFIG_NOSYSTEM: "1"           # Ignore system git config
    GIT_CONFIG_GLOBAL: "/dev/null"     # Ignore global git config
  env_overrides:
    GIT_PAGER: "cat"                   # Disable pager
    CLICOLOR: "0"                      # Disable colors
    TERM: "dumb"                       # Non-interactive terminal

npm:
  env_overrides:
    NPM_CONFIG_COLOR: "false"          # Disable npm colors
    NO_COLOR: "1"                      # Universal no-color
    CI: "1"                           # Enable CI mode
    NPM_CONFIG_FUND: "false"          # Disable funding messages
    NPM_CONFIG_AUDIT: "false"         # Disable audit warnings
```

### 5. Advanced Validator Features

#### Dynamic Argument Adjustment
Many validators can modify commands before execution:

```python
# From dotnet_validator.py
def adjust_arguments(self, parts: List[str], policy: Mapping[str, Any]) -> List[str]:
    """Override-or-append required flags and normalize verbosity."""
    if len(parts) < 2:
        return parts
    
    spec = policy.get("subcommands", {}).get(parts[1], {})
    require = spec.get("require_flags", {})
    
    if not require:
        return parts
    
    # Parse and normalize arguments
    normalized = self._parse_and_normalize(parts[2:])
    
    # Apply requirements
    if self._requires_true(require, "--nologo"):
        normalized.add_flag("--nologo")
    
    if "--verbosity" in require:
        want = require["--verbosity"]
        if isinstance(want, list) and want:
            target = self._coerce_verbosity(
                normalized.get_value("--verbosity"), 
                allowed=want, 
                default=want[0]
            )
            normalized.set_flag("--verbosity", target)
    
    # Rebuild command
    return [parts[0], parts[1]] + normalized.to_argv()
```

#### Complex Flag Validation
```python
# From powershell_validator.py
def validate(self, parts: List[str], policy: Mapping[str, Any]) -> ValidationResult:
    # Get security lists from policy
    safe_cmdlets = set(c.lower() for c in (policy.get("safe_cmdlets") or []))
    dangerous_patterns = policy.get("dangerous_patterns") or []
    
    # Extract and validate cmdlets
    non_flag_args = [arg for arg in parts[1:] if not arg.startswith("-")]
    if non_flag_args:
        command_content = " ".join(non_flag_args)
        
        # Check for dangerous patterns
        for pattern in dangerous_patterns:
            if re.search(pattern, command_content, re.IGNORECASE):
                return ValidationResult(False, f"Dangerous pattern detected: {pattern}")
        
        # Validate cmdlets against whitelist
        potential_cmdlets = re.findall(r'\b[a-z]+-[a-z]+\b', command_content, re.IGNORECASE)
        for cmdlet in potential_cmdlets:
            if cmdlet.lower() not in safe_cmdlets:
                return ValidationResult(False, f"Cmdlet not allowed: {cmdlet}")
    
    return ValidationResult(True, "OK", timeout=policy.get("default_timeout"))
```

### 6. Resource Protection

#### Output Size Management
```python
class SecureCommandExecutor:
    def __init__(self, max_output_size=1024*1024):  # 1MB default
        self.max_output_size = max_output_size
        
    async def _read_stream(self, stream, chunks, total_ref):
        """Read stream with memory protection."""
        truncated = False
        while True:
            chunk = await stream.read(65536)  # 64KB chunks
            if not chunk:
                break
                
            if total_ref[0] + len(chunk) > self.max_output_size:
                # Take only what fits
                remain = max(0, self.max_output_size - total_ref[0])
                if remain:
                    chunks.append(chunk[:remain])
                    total_ref[0] += remain
                truncated = True
                
                # Drain remaining data but discard
                while True:
                    more = await stream.read(65536)
                    if not more:
                        break
                break
            else:
                chunks.append(chunk)
                total_ref[0] += len(chunk)
                
        return truncated, b"".join(chunks)
```

#### Token-Aware Output Capping
```python
# From CommandExecutionResult
def to_yaml_capped(self, max_tokens: int, count_tokens: Callable[[str], int], 
                   *, head_lines: int = 200, tail_lines: int = 50) -> str:
    """Serialize to YAML, trimming stdout/stderr to satisfy token budget."""
    
    def trim(lines, h, t):
        if not lines:
            return "", False
        if len(lines) <= h + t:
            return "\n".join(lines), False
        return "\n".join(lines[:h] + ["… <TRUNCATED> …"] + lines[-t:]), True
    
    # Iteratively shrink windows until under budget
    h, t = head_lines, tail_lines
    while True:
        out_text, out_trunc = trim(self.stdout.splitlines(), h, t)
        err_text, err_trunc = trim(self.stderr.splitlines(), h//4, t//5)
        
        result_dict = {
            'status': self.status,
            'stdout': out_text,
            'stderr': err_text,
            # ... other fields
        }
        
        yaml_text = yaml.dump(result_dict)
        if count_tokens(yaml_text) <= max_tokens:
            break
            
        h = max(20, h // 2)
        t = max(10, t // 2)
    
    return yaml_text
```

## Cross-Platform Considerations

### Platform-Specific Execution
```python
class SecureCommandExecutor:
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_windows = platform.system().lower().startswith("win")
        
    async def _run_subprocess_async(self, parts, *, cwd, env, timeout):
        # Windows-specific configuration
        creationflags = 0
        if self.is_windows and not self.show_windows:
            CREATE_NO_WINDOW = 0x08000000
            creationflags |= CREATE_NO_WINDOW
            
        proc = await asyncio.create_subprocess_exec(
            parts[0], *parts[1:],
            cwd=cwd,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            creationflags=creationflags if self.is_windows else 0
        )
```

### Cross-Platform Path Handling
```python
# From base_validator.py
def adjust_environment(self, base_env, parts, policy):
    env = dict(base_env)
    
    # Platform PATH separator
    sep = ";" if os.name == "nt" else ":"
    
    # Windows PATHEXT handling
    if self.is_windows:
        env.setdefault("PATHEXT", ".COM;.EXE;.BAT;.CMD")
    
    # PATH_PREPEND processing with deduplication
    path_prepend = env.pop("PATH_PREPEND", None)
    if path_prepend:
        env["PATH"] = f"{path_prepend}{sep}{env.get('PATH', '')}"
```

### Command Resolution
```python
def _resolve_base(self, parts: List[str]) -> str:
    """Resolve base command, handling platform differences and special cases."""
    base = os.path.basename(parts[0])
    lower = base.lower()
    
    # Remove Windows extensions
    for ext in (".exe", ".cmd", ".bat", ".com"):
        if lower.endswith(ext):
            base = base[:-len(ext)]
            break
    
    # Handle Python module execution: python -m pytest → pytest
    if base in ("python", "python3") and len(parts) >= 3 and parts[1] == "-m":
        module = parts[2]
        if module == "pytest":
            return "pytest"
    
    return base

def _resolve_executable(self, cmd: str, env: Dict[str, str]) -> Optional[str]:
    """Resolve executable using PATH/PATHEXT from environment."""
    exe = shutil.which(cmd, path=env.get("PATH"))
    if exe:
        return exe
        
    # Windows fallback with PATHEXT
    if self.is_windows and not cmd.lower().endswith((".exe", ".cmd", ".bat", ".com")):
        for ext in (".cmd", ".bat", ".exe", ".com"):
            exe = shutil.which(cmd + ext, path=env.get("PATH"))
            if exe:
                return exe
                
    return None
```

## Policy Provider System

### YAML Policy Loading
```python
class YamlPolicyProvider(ConfigLoader):
    def __init__(self, config_path=None, policy_filename="whitelist_commands.yaml"):
        super().__init__(config_path)
        self.policy_filename = policy_filename
        self._policy_file_path = self._resolve_policy_path()
        self._cache = {}
        self._mtimes = {}
    
    def _resolve_policy_path(self):
        # 1. Environment override wins
        env_path = os.getenv("AGENTC_POLICIES_FILE")
        if env_path:
            return Path(env_path).resolve()
        
        # 2. Use ConfigLoader's resolved config path + policy filename
        return Path(self.config_path).joinpath(self.policy_filename)
    
    def _ensure_policy_loaded(self):
        """Load policy file with mtime checking and multi-encoding support."""
        path = self._policy_file_path
        
        if not path.exists():
            return False
        
        mtime = path.stat().st_mtime
        key = str(path)
        
        if self._mtimes.get(key) == mtime:
            return True  # cached and unchanged
        
        # Try multiple encodings
        for enc in ("utf-8", "utf-8-sig", "utf-16"):
            try:
                with open(path, "r", encoding=enc, newline="") as f:
                    content = f.read()
                    data = yaml.safe_load(content) or {}
                
                # Normalize keys to lowercase
                doc = {str(k).lower(): v for k, v in data.items()} if isinstance(data, dict) else {}
                self._cache[key] = doc
                self._mtimes[key] = mtime
                return True
                
            except UnicodeError:
                continue
            except yaml.YAMLError as e:
                self.logger.error(f"YAML parsing error in {path}: {e}")
                raise
        
        raise UnicodeError(f"Could not decode {path}")
```

## Error Handling and Recovery

### Comprehensive Error Classification
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
    
    def to_friendly_string(self, success_prefix: str = "OK") -> str:
        """Convert to user-friendly response string."""
        if self.status == "blocked":
            return f"ERROR: Command blocked by security policy: {self.error_message}"
        elif self.status == "success":
            return f"{success_prefix}:\n{self.stdout}" if self.stdout.strip() else f"{success_prefix} (no output)"
        elif self.status == "timeout":
            return f"ERROR: Command timed out: {self.error_message}"
        else:
            msg = self.error_message or "Command failed."
            stderr_tail = self.stderr.strip().splitlines()[-10:] if self.stderr else []
            err_tail = ("\n" + "\n".join(stderr_tail)) if stderr_tail else ""
            return f"ERROR: {msg}{err_tail}"
```

### Graceful Resource Cleanup
```python
async def _run_subprocess_async(self, parts, *, cwd, env, timeout):
    """Execute with guaranteed cleanup."""
    proc = None
    try:
        proc = await asyncio.create_subprocess_exec(...)
        
        # Read with timeout and resource limits
        truncated_out, out_bytes, truncated_err, err_bytes = await asyncio.wait_for(
            self._gather_both_streams(proc),
            timeout=timeout
        )
        
        return_code = await asyncio.wait_for(proc.wait(), timeout=timeout)
        return out_bytes, err_bytes, return_code, truncated_out, truncated_err
        
    except asyncio.TimeoutError:
        # Ensure process termination
        if proc and proc.returncode is None:
            proc.terminate()
            try:
                await asyncio.wait_for(proc.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                proc.kill()
                await proc.wait()
        raise
```

## Monitoring and Logging

### Structured Security Logging
```python
def _log_command_execution(self, command: str, result: CommandExecutionResult):
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'command': command,
        'status': result.status,
        'return_code': result.return_code,
        'working_directory': result.working_directory,
        'duration_ms': result.duration_ms,
        'truncated_output': result.truncated_stdout or result.truncated_stderr
    }
    
    # Include stdout preview only if small and logging enabled
    if self.log_output and result.stdout and len(result.stdout) < 1024:
        log_entry['stdout_preview'] = result.stdout[:500]
    
    if result.status == "blocked":
        log_entry['security_event'] = True
        log_entry['block_reason'] = result.error_message
    
    self.logger.info(json.dumps(log_entry))
```

## Security Guarantees

### What the System Prevents

1. **Command Injection** - All commands parsed with `shlex` and validated before execution
2. **Path Traversal** - Working directories confined to workspace boundaries with `path_safety.py`
3. **Privilege Escalation** - No sudo, su, or privilege-granting commands allowed by policy
4. **Resource Exhaustion** - Memory limits, timeouts, and output size caps prevent DOS
5. **Information Disclosure** - Dangerous flags blocked, outputs sanitized and capped
6. **Environment Pollution** - Controlled environment variable management with security defaults
7. **Script Injection** - Package managers restricted to allowed scripts and safe arguments
8. **Arbitrary Code Execution** - PowerShell restricted to safe cmdlets with pattern detection

### What the System Allows

1. **Safe Development Commands** - git (read-only), testing frameworks, build tools
2. **Controlled Script Execution** - npm/pnpm/lerna run with script allowlists
3. **Read-Only Operations** - File inspection, status checking, information gathering
4. **Contained Modifications** - Changes within workspace boundaries only
5. **Standard Development Tools** - Common utilities with security controls
6. **Custom Validation** - Extensible validator system for new tools

### Threat Model Coverage

The system protects against:

- **Malicious AI Behavior** - Preventing harmful command execution through whitelisting
- **Prompt Injection Attacks** - Commands disguised as legitimate requests blocked by validation
- **Accidental Damage** - Unintended destructive operations prevented by policy restrictions
- **Resource Abuse** - System resource exhaustion prevented by limits and timeouts
- **Data Exfiltration** - Unauthorized data access blocked by path safety and command restrictions
- **Supply Chain Attacks** - Package installation disabled, script execution restricted to allowlists

## Advanced Features

### Output Suppression for Automation

The system includes sophisticated output suppression capabilities to optimize token usage in CI/automation scenarios while preserving full error visibility:

```python
@dataclass
class CommandExecutionResult:
    # ... existing fields ...
    suppress_success_output: bool = False

    def to_friendly_string(self, success_prefix: str = "OK") -> str:
        """Get appropriate response string for tool to return to LLM"""
        if self.status == "blocked":
            return f"ERROR: Command blocked by security policy: {self.error_message}"
        
        elif self.status == "success":
            # Success output suppression only applies to successful executions
            if self.suppress_success_output:
                return f"{success_prefix} (output suppressed for token efficiency)"
            elif self.stdout.strip():
                return f"{success_prefix}:\n{self.stdout}"
            else:
                return f"{success_prefix} (no output)"
        
        elif self.status == "timeout":
            return f"ERROR: Command timed out: {self.error_message}"
        
        else:
            # Failed commands always show full output regardless of suppression flag
            msg = self.error_message or "Command failed."
            tail = (self.stderr or "").strip().splitlines()[-10:]
            err_tail = ("\n" + "\n".join(tail)) if tail else ""
            return f"ERROR: {msg}{err_tail}"
```

#### Key Suppression Behaviors

1. **Success-Only Suppression** - Only successful commands (exit code 0) have output suppressed
2. **Error Transparency** - Failed commands always show full stderr regardless of suppression setting
3. **Policy-Driven** - Suppression can be configured per command in policies via `suppress_success_output: true`
4. **Tool-Level Override** - Individual tool calls can override policy defaults
5. **Token Optimization** - Dramatically reduces token usage for successful build/test operations

### Enhanced Token Management

```python
def to_yaml_capped(
    self,
    max_tokens: int,
    count_tokens: Callable[[str], int],
    *,
    head_lines: int = 200,
    tail_lines: int = 50,
    min_head: int = 20,
    min_tail: int = 10,
) -> str:
    """
    Serialize to YAML, trimming stdout/stderr to satisfy a token budget.
    
    Features:
    - Intelligent head/tail windowing
    - Progressive shrinking until under budget
    - Separate stderr window sizing (smaller than stdout)
    - Line count annotations for clipped output
    - Last resort: complete omission with summary
    """
    # ... implementation with progressive window shrinking ...
```

## Best Practices for Implementation

### Security-First Development
1. **Default Deny** - Start with everything blocked, add permissions through explicit policies
2. **Minimal Permissions** - Grant only the minimum required access per command
3. **Defense in Depth** - Multiple layers: policy, validation, path safety, environment control
4. **Fail Securely** - All errors result in blocked execution, never bypassed security

### Policy Management
1. **Centralized Configuration** - Single `whitelist_commands.yaml` file with hot-reload
2. **Environment Overrides** - Support for environment-specific policy paths via `AGENTC_POLICIES_FILE`
3. **Multi-encoding Support** - Handle different file encodings gracefully (UTF-8, UTF-8-BOM, UTF-16)
4. **Version Control** - Track policy changes and maintain audit trail

### Performance and Scalability
1. **Async Execution** - Non-blocking command execution with proper resource limits
2. **Memory Efficiency** - Streaming I/O with bounded memory usage (1MB default cap)
3. **Policy Caching** - File-based caching with mtime checking for hot-reload
4. **Output Management** - Token-aware truncation and smart formatting

### Monitoring and Maintenance
1. **Comprehensive Logging** - Log all attempts with security event classification
2. **Resource Monitoring** - Track execution times, memory usage, and truncation events
3. **Security Auditing** - Regular policy reviews and blocked command analysis
4. **Error Analysis** - Monitor validation failures and policy gaps

### Token Optimization Strategies
1. **Strategic Suppression** - Use `suppress_success_output: true` for build/test commands
2. **Smart Capping** - Implement `to_yaml_capped()` for large output scenarios
3. **Error Prioritization** - Always preserve full error output for debugging
4. **Progressive Truncation** - Use head/tail windowing instead of simple truncation

This architecture provides a robust foundation for secure command execution that balances security, functionality, and performance while remaining extensible for future workspace types and command validators. The recent enhancements in output suppression and token management make it particularly well-suited for AI automation scenarios where token efficiency is critical.
