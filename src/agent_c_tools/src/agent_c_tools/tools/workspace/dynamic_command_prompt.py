from typing import Any, Optional

from agent_c.prompting.prompt_section import PromptSection

class DynamicCommandPromptSection(PromptSection):
    def __init__(self, **data: Any):
        TEMPLATE = """This toolset provides secure command execution in workspaces with strict allowlists for safety.

## Available Commands

### Git Commands (`run_git`)
**Allowed subcommands:**
- `status` - flags: `--porcelain`, `-s`, `-b`, `--no-color`
- `log` - flags: `--oneline`, `--graph`, `--decorate`, `-n`, `-p`, `--no-color`
- `show` - flags: `--name-only`, `--stat`, `-p`, `--no-color`
- `diff` - flags: `--name-only`, `--stat`, `--cached`, `-p`, `--no-color`
- `add`, `restore` (with `--staged`), `reset` (with `--hard/--soft/--mixed`)
- `checkout`, `switch`, `branch`, `stash`, `commit`, `rev-parse`, `ls-files`

**Examples:** `git status -s`, `git log --oneline -n 10`, `git diff --name-only`

### Node.js Package Managers

#### NPM Commands (`run_npm`)
**Root flags:** `-v`, `--version`, `--help`
**Allowed subcommands:**
- `view`, `list`, `ping`, `outdated`, `test` - basic info commands
- `config get <key>` - read-only config access
- `run <script>` - allowed scripts: `build`, `test`, `lint`, `format`, `typecheck`, `lint:fix`
- `ci` - lockfile install with `--ignore-scripts` (automatically added)

**Examples:** `npm run build`, `npm list --depth=0`, `npm config get registry`

#### PNPM Commands (`run_pnpm`)
**Root flags:** `-v`, `--version`, `--help`
**Allowed subcommands:**
- `view`, `list`, `ping`, `outdated`, `test`, `why`, `licenses`
- `config get <key>` - read-only config access
- `run <script>` - allowed scripts: `build`, `test`, `lint`, `lint:fix`, `format`, `typecheck`
- `install` - lockfile install with `--ignore-scripts` (automatically added)

**Examples:** `pnpm run test`, `pnpm list --long`, `pnpm why typescript`

#### NPX Commands (`run_npx`)
**Allowed packages:** `@angular/cli`, `create-react-app`, `typescript`, `eslint`, `prettier`, `jest`, etc.
**Flags:** `--yes`, `-y`, `--package`, `-p`, `--quiet`, `-q`

**Examples:** `npx typescript --version`, `npx eslint --help`

#### Lerna Commands (`run_lerna`)
**Global flags:** `--version`, `--help`, `--loglevel`, `--concurrency`, `--scope`
**Allowed subcommands:**
- `list/ls` - list packages with `--json`, `--long`, `--all`
- `info` - package info with `--json`
- `bootstrap` - install dependencies with `--hoist`, `--ignore-scripts`
- `clean` - clean node_modules with `--yes`
- `changed` - show changed packages
- `diff` - show package diffs
- `run` - run scripts with `--parallel`, `--stream`

**Examples:** `lerna list --json`, `lerna run build --parallel`

### .NET Commands (`run_dotnet`)
**Info commands:** `--info`, `--list-sdks`, `--list-runtimes`
**Build commands:**
- `restore` - with `--locked-mode` (automatically added)
- `build` - with `--nologo`, `--verbosity minimal` (automatically added)
- `test` - with `--no-build`, `--nologo` (automatically added)

**Examples:** `dotnet build -c Release`, `dotnet test --filter TestCategory=Unit`

### Python Testing (`run_pytest`)
**Flags:** `-q`, `--maxfail`, `--disable-warnings`, `--color`

**Examples:** `pytest -q`, `pytest --maxfail=1`

### Node.js Runtime (`run_node`)
**Flags:** `-v`, `--version`, `--help` (script execution blocked)

### System Commands
- `run_which` - find executables with `-a`, `--version`
- `run_where` - Windows equivalent with `/r`
- `run_whoami` - current user info
- `run_echo` - simple text output with `--help`, `-n`, `-e`

## Important Notes
- **No shell features**: No pipes, redirection, wildcards, or command chaining
- **Security first**: All commands are validated against strict policies
- **Auto-flags**: Some commands automatically add required security flags
- **Timeouts**: Commands have reasonable timeout limits
- **Clean output**: Color and progress indicators are disabled for token efficiency
- **Local packages**: Node.js commands automatically find locally installed packages

## Usage Tips
- Use concise flags like `-s` for git status, `--oneline` for git log
- Prefer `git ls-files "*.ext"` over platform-specific find commands
- Use `--json` flags when available for structured output
- Check package existence with `list`/`ls` commands before running scripts
"""

        super().__init__(template=TEMPLATE, required=True, name="DynamicCommands", render_section_header=True, **data)
