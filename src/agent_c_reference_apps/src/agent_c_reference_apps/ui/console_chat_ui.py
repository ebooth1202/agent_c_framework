import os
import platform
import tempfile
import threading
import webbrowser
from queue import Queue
from typing import List

from prompt_toolkit.key_binding import KeyBindings
from rich.rule import Rule

from prompt_toolkit.history import FileHistory
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.markdown import Markdown

from prompt_toolkit import PromptSession

from agent_c_reference_apps.ui.audio_playback_worker import AudioPlaybackWorker
from agent_c_reference_apps.util.audio_cues import AudioCues
from agent_c import ChatEvent, RenderMedia
from agent_c_reference_apps.ui.markdown_render import MarkdownTokenRenderer
from agent_c.models.events import MessageEvent, ToolCallEvent, InteractionEvent, TextDeltaEvent, HistoryEvent, CompletionEvent, ToolCallDeltaEvent, SessionEvent, RenderMediaEvent


LINE_SEPARATOR: Markdown = Markdown("---\n")

ASSISTANT_LABEL: str = "[bold gold1]Assistant[/]"
USER_LABEL: str      = "[bold dark_magenta]You[/]"
OPI_LABEL: str       = "[bold aquamarine1 u]Open Interpreter[/]"
SYSTEM_LABEL: str    = "[bold orange1 u]System[/]"
EXT_LABEL: str       = "[bold aquamarine1 u]Extraction[/]"
DALLE_LABEL: str     = "[bold green_yellow u]DALL-E-3 Imagee Generation Tool[/]"

SESSION_HELP: str    = "[italic]Use this with [bold]--session[/bold] to resume[/]."
EXIT_INFO: str       = "    Send '[italic gold1]!exit[/]' to exit without saving or '[italic gold1]!!!![/]' to save and exit"

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
        self.audio_worker = AudioPlaybackWorker(sample_rate=48000, channels=1)
        self.system = platform.system()
        self.audio_cues: AudioCues = kwargs.get("audio_cues")
        self.tts_roles: List[str] = kwargs.get("tts_roles", [])
        self.debug_event = kwargs.get("debug_event", threading.Event())
        self.rich_console: Console = Console(record=True)
        self.token_renderer = MarkdownTokenRenderer(self.rich_console)
        self.key_bindings = KeyBindings()

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
        return text_input

    async def get_user_input(self) -> str:
        """
        Prompt the user for input or retrieve speech-to-text input from a queue.

        Returns:
            str: The user input as a string or the processed speech-to-text input.
        """
        self.start_role_message('user')
        self.rich_console.print(": ", end="")

        # Start both the prompt and the queue checking concurrently
        user_input_task = await self._check_keyboard_input()

        return user_input_task


    async def render_media(self, opts: RenderMediaEvent):

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

    def _handle_completion_event(self, event: CompletionEvent):
        if event.running:
            self.rich_console.print()
            self.rich_console.print("[bold gold3]Completion running....[/]", end="")
        else:
            self.token_renderer.flush()
            self.rich_console.print(f"\n[bold gold3] Done![/] ({event.stop_reason})")

    def _handle_tool_call_event(self, event: ToolCallEvent):
        if event.active:
            tool_calls = event.tool_calls
            # TODO Env check

            # Joe for grabbing tool call information
            tool_names = ", ".join([tool_call['name'] for tool_call in tool_calls])
            # Create a formatted string for each tool call with its name and arguments
            formatted_tool_info = ", ".join(
                [f"{tool_call['name']} (Arguments: {tool_call.get("arguments", "")})\n" for tool_call in tool_calls])

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

    def _handle_text_delta_event(self, event: TextDeltaEvent):
        if event.role != self.last_role:
            self.start_role_message(event.role)

        if event.format == 'markdown':
            self.token_renderer.render_token(event.content)
        else:
            self.rich_console.print(event.content, end='')

    def _handle_message_event(self, event: MessageEvent):
        if event.role != self.last_role:
            self.start_role_message(event.role)

        if event.format == 'markdown':
            self.token_renderer.render_token(event.content)
            self.token_renderer.flush()
        else:
            self.rich_console.print(event.content)

    async def chat_event(self, event):
        if event.role != self.last_role:
            self.token_renderer.flush()

        if event.type == 'completion':
            self._handle_completion_event(event)
            return

        if event.type == 'message':
            self._handle_message_event(event)
            return

        if event.type == 'text_delta':
            self._handle_text_delta_event(event)
            return


        if event.type == 'render_media':
            await self.render_media(event)
            return

        if event.type == 'tool_call':
            self._handle_tool_call_event(event)
            return

        if event.type == 'interaction':
            if not event.started:
                self.rich_console.print()
            return

        if event.type == 'audio_delta':
            self.audio_worker.push_chunk(event.content)
            return
