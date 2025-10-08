from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agent_c_api.core.realtime_bridge import RealtimeBridge

class ChatCommandHandler:
    def __init__(self):
        self.commands = {
            #'!r': ChangeOutputFormatCommand(),
            #'!exit': ExitCommand(),
            #'!call_tool': CallToolCommand(),
            #'!remind': RemindCommand(),
            # ... etc
        }

    async def handle_command(self, user_message: str, context: 'RealtimeBridge') -> bool:
        user_message = user_message.strip()

        if user_message == "":
            return True

        if not user_message.startswith("!"):
            return False

        # Split into command and args
        parts = user_message.split(None, 1)
        command_name = parts[0].lower()
        args_string = parts[1] if len(parts) > 1 else ""

        if command_name not in self.commands:
            return False

        command = self.commands[command_name]

        try:
            parsed_args = command.parser.parse(args_string)
            await command.execute(context, **parsed_args)
        except Exception as e:
            await context.send_system_message(f"Error executing {command_name}: {str(e)}")

        return True