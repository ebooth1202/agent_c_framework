from __future__ import annotations

import shlex
from typing import Optional, Dict, Any, List
from agent_c.toolsets.tool_set import Toolset
from agent_c.toolsets.json_schema import json_schema
from .executor.secure_command_executor import SecureCommandExecutor, CommandExecutionResult

from ...helpers.validate_kwargs import validate_required_fields
from ..workspace.tool import WorkspaceTools
from ...helpers.path_helper import create_unc_path, ensure_file_extension, os_file_system_path, has_file_extension, \
    normalize_path, os_path

from .media_event_helper.media_helper import MediaEventHelper



class GitTools(Toolset):
    """Git operations toolset with secure command execution"""
    MAX_TOKENS = 1000  # Max tokens to return from git command results - trying to avoid blowing out context windows

    def __init__(self, **kwargs):
        super().__init__(**kwargs, name='git_tools', use_prefix=False)

        # Instantiate executor
        self.executor = SecureCommandExecutor(
            debug_mode=True,
            log_output=True,  # keep your logging
            default_timeout=30,
            max_output_size=1024 * 1024, # byte size limits for truncating output
        )

        # Import workspace tools for path resolution
        self.workspace_tool: Optional[WorkspaceTools] = None


    async def post_init(self):
        """Initialize workspace tool reference after all tools are loaded"""
        self.workspace_tool = self.tool_chest.available_tools.get("WorkspaceTools")

    @staticmethod
    def _git_policy() -> Dict[str, Any]:
        """
        Policy provided to the executor. Tune as needed.
        NOTE: push/clone/pull are excluded by default. Add them explicitly
        with host allowlists in your own wrapper if/when needed.
        """
        return {
            "git": {
                "default_timeout": 30,
                "safe_env": {
                    "GIT_TERMINAL_PROMPT": "0",
                    "GIT_CONFIG_NOSYSTEM": "1",
                    "GIT_CONFIG_GLOBAL": "/dev/null",
                    "GIT_ALLOW_PROTOCOL": "https,file",
                },
                "deny_global_flags": ["-c", "--exec-path", "--help", "-P"],
                "subcommands": {
                    "status": {"flags": ["--porcelain", "-s", "-b"], "timeout": 20},
                    "log": {"flags": ["--oneline", "--graph", "--decorate", "-n", "-p", "--name-only"]},
                    "show": {"flags": ["--name-only", "-p"]},
                    "diff": {"flags": ["--name-only", "--staged", "--cached", "-p"]},
                    "add": {"flags": []},
                    "restore": {"flags": ["--staged"]},
                    "reset": {"flags": ["--hard", "--soft", "--mixed"]},
                    "checkout": {"flags": ["-b", "--"]},
                    "switch": {"flags": ["-c", "-"]},  # not git -c; this is switch -c (create)
                    "branch": {"flags": ["-a", "-vv", "-d", "-D"]},
                    "stash": {"flags": ["list", "push", "pop", "apply", "drop", "clear"]},
                    "commit": {"flags": ["-m", "--amend", "--no-verify"]},
                    "rev-parse": {"flags": ["--abbrev-ref", "--short", "HEAD"]},
                    "ls-files": {"flags": ["--exclude-standard", "--others", "--cached"]},
                }
            }
        }

    # ---- helpers ----
    @staticmethod
    def _format_command(args: List[str]) -> str:
        # Coerce to tokens safe for shlex splitting in the executor
        return " ".join([shlex.quote("git")] + [shlex.quote(a) for a in args])


    @json_schema(
        description="Execute git commands in a repository. Use standard git syntax.",
        params={
            "command": {
                "type": "string",
                "description": "Git command to execute (e.g., 'status', 'add .', 'commit -m \"message\"', 'push origin main')",
                "required": True
            },
            "workspace_path": {
                "type": "string",
                "description": "Workspace UNC path to directory where git command should be executed",
                "required": True
            }
        }
    )
    async def execute_git_command(self, **kwargs) -> str:
        """Execute any git command with security validation"""

        success, message = validate_required_fields(kwargs=kwargs, required_fields=['command', 'workspace_path'])

        if not success:
            return message

        tool_context = kwargs.get("tool_context")
        command = kwargs.get("command", "").strip()
        workspace_path = kwargs.get("workspace_path")

        # Ensure command starts with 'git'
        if not command.startswith('git '):
            command = f"git {command}"

        # Resolve workspace path to actual OS directory
        working_directory = None
        try:
            working_directory = await self.resolve_workspace_path(
                workspace_path=workspace_path,
                tool_context=tool_context
            )
            if working_directory.lower().startswith("error:"):
                return working_directory  # Return the error
        except Exception as e:
            return f"ERROR: Failed to resolve workspace path: {str(e)}"

        result: CommandExecutionResult = await self.executor.execute_command(command, working_directory=working_directory,
                                                                             allowed_commands=self._git_policy())
        html_content = await MediaEventHelper.stdout_html(result.to_dict())
        await self._raise_render_media(
            sent_by_class=self.__class__.__name__,
            sent_by_function='execute_git_command',
            content_type="text/html",
            content=html_content,
            tool_context=tool_context
        )

        # token_count = tool_context['agent_runtime'].count_tokens(result.to_yaml())
        counter = tool_context.get("agent_runtime").count_tokens
        if counter is None:
            return result.to_yaml()
        else:
            return result.to_yaml_capped(self.MAX_TOKENS, counter)

    async def resolve_workspace_path(self, workspace_path: str, tool_context: dict) -> str:
        """Convert workspace UNC path to actual OS directory path"""

        if not workspace_path:
            return "ERROR: Workspace path is required"

        err, abs_path = os_path(self.workspace_tool, workspace_path, mkdirs=False)
        if err:
            return f"ERROR: Unable to resolve '{workspace_path}': {err}"
        return abs_path


# Register the toolset
Toolset.register(GitTools, required_tools=['WorkspaceTools'])