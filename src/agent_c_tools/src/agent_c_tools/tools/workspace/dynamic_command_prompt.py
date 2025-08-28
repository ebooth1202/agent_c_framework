from typing import Any, Optional

from agent_c.prompting.prompt_section import PromptSection

class DynamicCommandPromptSection(PromptSection):
    def __init__(self, **data: Any):
        TEMPLATE = ("""This toolset provides you a way to run specific allowed commands in workspaces that support executables. 
                    - **Command Execution**: Use `run_command` to execute allowlisted commands only\n
                      - Only specific pre-approved commands are allowed (git, pytest, npm, dotnet, node, etc.)\n
                      - Each command has restricted subcommands and flags for security\n
                      - Arbitrary shell commands, pipes, redirection, and scripting are NOT supported\n
                      - Examples of allowed commands: 'git status', 'npm test', 'pytest --help'\n
                      - Use platform-agnostic tools when possible (e.g., 'git ls-files \"*.md\"' instead of find/where)\n
                      - Prefer optimized outputs, e.g., 'git status -s' for concise status or 'git log --oneline -n 50' (and avoid -p unless truly needed)\n"""
                    )

        super().__init__(template=TEMPLATE, required=True, name="DynamicCommands", render_section_header=True, **data)
