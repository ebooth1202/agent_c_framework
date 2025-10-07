from agent_c_api.core.commands.base_command import Command
from agent_c_api.core.commands.parsers import JsonStyleParser


class RewindCommand(Command):
    def __init__(self):
        super().__init__(JsonStyleParser())

    async def execute(self, context, args: list, **kwargs):
        if len(args) < 2:
            context.chat_ui.fake_role_message("system",
                                              "Usage: !remind \"time\", \"message\"")
            return

        time, message = args[0], args[1]
        # Your reminder logic here
        context.chat_ui.fake_role_message("system",
                                          f"Reminder set for {time}: {message}")