import asyncio
import os
import platform
import tempfile
import threading
import webbrowser
from queue import Queue
from typing import Union, List

from prompt_toolkit.key_binding import KeyBindings
from rich.rule import Rule

from prompt_toolkit.history import FileHistory
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.markdown import Markdown

from prompt_toolkit import PromptSession

from agent_c_vision import CV2Frame
from agent_c_reference_apps.util.audio_cues import AudioCues
from agent_c import ChatEvent, RenderMedia
from agent_c_reference_apps.ui.markdown_render import MarkdownTokenRenderer
from agent_c_voice import SpeechmaticsTranscriber, TTSElevenLabs



LINE_SEPARATOR: Markdown = Markdown("---\n")
ASSISTANT_LABEL = "[bold gold1]Assistant[/]"
USER_LABEL = "[bold dark_magenta]You[/]"
OPI_LABEL = "[bold aquamarine1 u]Open Interpreter[/]"
SYSTEM_LABEL = "[bold orange1 u]System[/]"
EXT_LABEL = "[bold aquamarine1 u]Extraction[/]"
DALLE_LABEL = "[bold green_yellow u]DALL-E-3 Image Generation Tool[/]"

SESSION_HELP: str = "[italic]Use this with [bold]--session[/bold] to resume[/]."
EXIT_INFO: str = "    Send '[italic gold1]!exit[/]' to exit without saving or '[italic gold1]!!!![/]' to save and exit"

ROLE_LINE_STYLES = {"user": {"label": USER_LABEL, "line_style": "bold gold1"},
                    "assistant": {"label": ASSISTANT_LABEL, "line_style": "bold dark_magenta"},
                    "opi": {"label": OPI_LABEL, "line_style": "bold aquamarine1"},
                    "extraction": {"label": EXT_LABEL, "line_style": "bold aquamarine1"},
                    "dalle3": {"label": DALLE_LABEL, "line_style": "bold hot_pink2"},
                    "system": {"label": SYSTEM_LABEL, "line_style": "bold orange1"}}

OUTPUT_TOOL_ARGS = os.getenv('OUTPUT_TOOL_ARGS', 'False').lower() in ('true', '1', 'yes')


class ConsoleChatUI:
    def __init__(self, **kwargs):
        history = FileHistory(".chat_input")
        self.system = platform.system()
        self.audio_cues: AudioCues = kwargs.get("audio_cues")
        self.tts_roles: List[str] = kwargs.get("tts_roles", [])
        self.transcriber: Union[SpeechmaticsTranscriber, None] = kwargs.get("transcriber", None)
        self.tts_engine: Union[TTSElevenLabs, None] = kwargs.get("tts_engine", None)
        self.debug_event = kwargs.get("debug_event", threading.Event())
        self.rich_console: Console = Console(record=True)
        self.token_renderer = MarkdownTokenRenderer(self.rich_console)
        self.key_bindings = KeyBindings()
        if self.transcriber is not None and kwargs.get("stt_keybind", None) is not None:
            self.key_bindings.add(kwargs.get("stt_keybind"))(self._toggle_stt)

        self.key_bindings.add(kwargs.get("debug_keybind", 'c-d'))(self._toggle_debug)
        self.prompt_session = PromptSession(history=history, key_bindings=self.key_bindings)

        self.rich_console.clear()
        self.rich_console.print(f"[bold]Agent[/bold] [bold gold1]C[/] by [bold gold1](( [/][bold dark_magenta]Centric[/][bold gold1] ))[/]", justify="center")
        self.last_role = 'user'
        self.temp_dir: tempfile.TemporaryDirectory = tempfile.TemporaryDirectory()
        self.transcript_queue: Queue = kwargs.get("transcript_queue", Queue())

    def _toggle_debug(self, _):
        if self.debug_event.is_set():
            self.debug_event.clear()
            self.system_message("[bold red]Debug mode disabled[/]")
        else:
            self.debug_event.set()
            self.system_message("[bold green]Debug mode enabled[/]")

    def _toggle_stt(self, _):
        if self.transcriber is not None:
            if self.transcriber.is_listening:
                self.transcriber.input_complete()
            else:
                if self.tts_engine and self.tts_engine.tts_active.is_set():
                    self.tts_engine.cancel()
                    self.tts_engine.tts_active.wait()

                self.transcriber.listen()

    def print_session_info(self, session_id: str) -> None:
        self.start_role_message("system")
        self.rich_console.print(f"Session will be kept after exit. Use `[bold gold1]--session {session_id}[/]` to resume")

    def start_role_message(self, role: str):
        self.last_role = role
        opts = ROLE_LINE_STYLES.get(role, {"label": f"[hot_pink]{role}[/]", "line_style": "bold hot_pink"})
        self.__line_separator(opts['label'], opts["line_style"])

    def __line_separator(self, label, style):
        self.rich_console.print()
        self.rich_console.print(Rule(title=label, style=style, align="right"))

    def system_message(self, content):
        self.start_role_message("system")
        self.rich_console.print(content)

    def fake_role_message(self, role: str, content: str):
        self.start_role_message(role)
        self.rich_console.print(content)

    def show_session_info(self, zep_cache):
        if zep_cache.is_new_session:
            left_text = f"[bold]New chat Session[/] send `[gold1]!keep[/]` to persist session."
        else:
            left_text = f"[bold]Session ID:[/bold] [bold medium_purple3]{zep_cache.session.session_id}[/]"

        right_text = Align(EXIT_INFO, "right")
        # Create Columns with two items and expand to the full width
        columns = Columns([left_text, right_text], expand=True)

        # Print the columns to the console
        self.rich_console.print(columns)

    async def _check_keyboard_input(self):
        text_input = await self.prompt_session.prompt_async()
        # Still not quite working
        # self.rich_console.control(Control.move(0, -1))
        # self.rich_console.print(Markdown(f"{text_input}"))
        return text_input, None

    async def get_user_input(self) -> (str, Union[CV2Frame, None]):
        """
        Prompt the user for input or retrieve speech-to-text input from a queue.

        Returns:
            str: The user input as a string or the processed speech-to-text input.
        """
        self.start_role_message('user')
        self.rich_console.print(": ", end="")
        if self.transcriber is not None:
            self.transcriber.start()

        # Start both the prompt and the queue checking concurrently
        user_input_task = asyncio.create_task(self._check_keyboard_input())
        queue_input_task = asyncio.create_task(self._check_queue())

        done, pending = await asyncio.wait(
            {user_input_task, queue_input_task},
            return_when=asyncio.FIRST_COMPLETED  # Return as soon as one task is done
        )

        # Cancel any task that is still pending
        for task in pending:
            task.cancel()

        if self.transcriber is not None:
            self.transcriber.listen_stop()

        # Return result from the task that finished first
        if user_input_task in done:
            return user_input_task.result()
        else:
            return queue_input_task.result()

    async def _check_queue(self):
        """
        Check the message queue for speech-to-text input.
        """
        final_speech_input: str = ""
        pending_speech_input: str = ""
        current_partial: str = ""
        last_frame: Union[CV2Frame, None] = None
        while True:
            if self.transcriber is not None and not self.transcriber.queue.empty():
                message = self.transcriber.queue.get()
                if message["type"] == "final":
                    current_partial = ""
                    for line in message["transcript"]:
                        if line.content[0] in " .!?;:'\"":
                            final_speech_input = f"{final_speech_input}{line.content}"
                        else:
                            final_speech_input = f"{final_speech_input} {line.content}"

                        if message["frame"] is not None:
                            last_frame = message["frame"]

                        pending_speech_input = final_speech_input

                elif message["type"] == "partial":
                    current_partial = message["transcript"].content
                    pending_speech_input = f"{final_speech_input} {current_partial}"

                    self.rich_console.print(f"\r[bold]Spoken: [/]{pending_speech_input}", end="\r")
                elif message["type"] == "pause_final":
                    output = pending_speech_input or current_partial
                    if len(pending_speech_input) > 0:
                        self.rich_console.print(f"\r[bold]Spoken (final): [/]{output}")
                        return output, last_frame

            await asyncio.sleep(0.01)

    async def render_media(self, opts: RenderMedia):

        if opts.url is not None:
            webbrowser.open(opts.url)
        elif opts.name is not None:
            temp_path = os.path.join(self.temp_dir.name, opts.name)
            if opts.content_bytes is not None:
                with open(temp_path, 'wb') as f:
                    f.write(opts.content_bytes)
            elif opts.content is not None:
                with open(temp_path, 'w') as f:
                    f.write(opts.content)

            os.startfile(temp_path)
        else:
            self.rich_console.print(f"Unsupported media type: {opts.content_type}")

    async def chat_event(self, event: ChatEvent):

        if event.role != self.last_role:
            self.token_renderer.flush()

        if event.completion_running is not None:
            if event.completion_running:
                self.rich_console.print()
                self.rich_console.print("[bold gold3]Completion running....[/]", end="")
            else:
                self.rich_console.print("[bold gold3] Done![/]")

            return

        if event.render_media is not None:
            await self.render_media(event.render_media)
            return

        if event.tool_use_active is not None:
            # Indicate tool usage status in the console.
            if event.tool_use_active:
                tool_calls = event.tool_calls
                # TODO Env check

                # Joe for grabbing tool call information
                tool_names = ", ".join([tool_call.name for tool_call in tool_calls])
                # Create a formatted string for each tool call with its name and arguments
                formatted_tool_info = ", ".join(
                    [f"{tool_call.name} (Arguments: {tool_call.arguments})\n" for tool_call in tool_calls])

                self.start_role_message("system")
                if OUTPUT_TOOL_ARGS:
                    self.rich_console.print(
                        f"Agent '[bold]{event.role}[/bold]' is executing the following tools: {formatted_tool_info}.")
                else:
                    self.rich_console.print(
                        f"Agent '[bold]{event.role}[/bold]' is executing the following tools: {tool_names}.")
            else:
                if self.last_role != 'system':
                    self.start_role_message("system")
                self.rich_console.print(f"Agent '[bold]{event.role}[/bold]' has completed tool use and is evaluating the results")

            return

        if event.role != self.last_role:
            self.start_role_message(event.role)
            if self.tts_engine is not None and event.role in self.tts_roles:
                self.tts_engine.start()

        if event.output_format == 'markdown':
            if event.content is not None:
                tts_str = self.token_renderer.render_token(event.content)
                if tts_str is not None and self.tts_engine is not None and event.role in self.tts_roles:
                    self.tts_engine.input_queue.put(tts_str)

            if event.completed:
                self.token_renderer.flush()
        else:
            if event.content is not None:
                self.rich_console.print(event.content, end='')
                if self.tts_engine is not None and event.role in self.tts_roles:
                    self.tts_engine.input_queue.put(event.content)

            if event.completed:
                self.rich_console.print()
