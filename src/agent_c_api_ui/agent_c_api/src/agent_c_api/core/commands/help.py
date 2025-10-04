from typing import List

from .base_command import Command

class HelpCommand(Command):
    @property
    def command_strings(self) -> List[str]:
        return ['!help', '!h', '!?']

    @property
    def help_text(self) -> str:
        return "Show available commands or help for a specific command - Usage: !help [command]"

    async def execute(self, context, **kwargs):
        # Get the command handler from context
        handler = context.command_handler

        # Check if they want help on a specific command
        if 'raw_args' in kwargs and kwargs['raw_args']:
            target = kwargs['raw_args'].strip()
            if not target.startswith('!'):
                target = '!' + target

            # Find the command
            if target in handler.command_map:
                cmd = handler.command_map[target]
                aliases = ', '.join(cmd.command_strings)
                context.chat_ui.fake_role_message("system",
                                                  f"{aliases}\n  {cmd.help_text}")
            else:
                context.chat_ui.fake_role_message("system",
                                                  f"Unknown command: {target}")
        else:
            # Show all commands
            lines = ["Available commands:"]
            # Group by command instance to avoid duplicates
            seen_commands = set()
            for cmd_str, cmd in handler.command_map.items():
                if id(cmd) not in seen_commands:
                    seen_commands.add(id(cmd))
                    aliases = ', '.join(cmd.command_strings)
                    lines.append(f"  {aliases}")
                    lines.append(f"    {cmd.help_text}")

            context.chat_ui.fake_role_message("system", "\n".join(lines))