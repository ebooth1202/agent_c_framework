import json
import os
import asyncio
import logging
import argparse
import threading
from typing import Union, List
from dotenv import load_dotenv

from agent_c.toolsets import Toolset

from agent_c.models.image_input import ImageInput
from agent_c.prompting import DynamicPersonaSection
from agent_c_reference_apps.ui.markdown_render import MarkdownTokenRenderer


# Note: we load the env file here so that it's loaded when we start loading the libs that depend on API KEYs.   I'm looking at you Eleven Labs
load_dotenv(override=True)

from agent_c_voice import MPVPlayer, TTSElevenLabs
from agent_c_reference_apps.util.audio_cues import AudioCues
from agent_c_reference_apps.util.chat_commands import CommandHandler

# Without this none of the rest matter
from agent_c import GPTChatAgent, ClaudeChatAgent, ChatEvent, ChatSessionManager, ToolChest, ToolCache

# Vision support
from agent_c_vision import CV2Feed


from agent_c.util import debugger_is_active
from agent_c_tools.tools.user_preferences import AssistantPersonalityPreference, AddressMeAsPreference, UserPreference
from agent_c_voice.tools.voice_eleven_labs.preferences import DefaultVoicePreference
from agent_c.prompting import CoreInstructionSection, HelpfulInfoStartSection, EndOperatingGuideLinesSection, \
    EnvironmentInfoSection, PromptBuilder, PersonaSection



# Ensure all our toolsets get registered
from agent_c_tools.tools import *  # noqa
from agent_c_demo.tools import *  # noqa
from agent_c_voice.tools import *  # noqa
from agent_c_tools.tools.user_bio.prompt import UserBioSection
from agent_c_voice.speech_to_text.speechmatics_transcriber import SpeechmaticsTranscriber

# These are only for the CLI app.
from agent_c_reference_apps.ui.console_chat_ui import ConsoleChatUI

# These are the fake agent messages that show up when you start / end a chat.
NEW_SESSION_WELCOME: str = "New here?  Ask me about my toolsets."
OLD_SESSION_WELCOME: str = "[bold]Welcome back![/] Remember, I have toolsets available feel free to ask me about them."


class CLIChat:
    """
    A reference app that implements a chat interface with a centric_one_shot.ChatAgent.

    Zep is used as a chat session manager to track chat history. Visit https://www.getzep.com/ and grab their docker
    compose file to set it up. This uses streaming responses from the agent.

    Note:
    - The console outputs Markdown. If you're seeing garbled output, you need a better shell.
    - Tested on *nix terminals and Windows Terminal Preview on Windows.
    """

    def __init__(self, **kwargs):
        self.__init_events()
        self.logger: logging.Logger = self.__setup_logging()
        self.user_id = kwargs['user_id']
        self.session_id: Union[str, None] = kwargs.get('session_id', None)
        self.audio_cues = AudioCues()

        self.__init_tts(**kwargs)
        self.__init_agent_params(**kwargs)
        self.__init_camera(**kwargs)
        self.__init_transcription(**kwargs)
        self.cmd_handler = CommandHandler()

        self.chat_ui = ConsoleChatUI(tts_engine=self.tts_engine, transcriber=self.transcriber, stt_keybind=self.stt_keybind,
                                     audio_cues=self.audio_cues, tts_roles=['assistant'], debug_event=self.debug_event)
        self.audio_cues.play_sound('app_start')
        self.__init_workspaces()

        # This sets up a few preferences
        # "Default voice" should be self-explanatory, the VoiceTools consume this.
        # "Address me as" defaults to "First name", but if you tell the agent "call me by my last name" or "call me big poppa"
        #                 it will do so in every session until you ask to change or reset it.
        # "Assistant Personality" allows the user to change the tone of the responses as long as the change doesn't conflict with rules in the
        #                         `Operating Guidelines` portion of the prompt. So "from not on talk like a pirate" works just fine.
        self.user_prefs: List[UserPreference] = [AddressMeAsPreference(), AssistantPersonalityPreference()]

        self.can_use_tools = True

    def __init_tts(self, **kwargs):
        """
        Initializes the TTS engine and TTS player if voice mode is on.
        """
        self.logger.debug("Initializing TTS engine...")
        self.voice_mode: bool = kwargs.get('voice', False)
        self.tts_player: Union[None, MPVPlayer] = None
        self.tts_engine: Union[None, TTSElevenLabs] = None
        self.tts_model_id: str = "eleven_multilingual_v2"

        if os.environ.get('ELEVEN_API_KEY', None) is None:
            logging.error('You must have an ELEVEN_API_KEY to use TTS.  Disabling voice mode.')
            self.voice_mode = False
            return

        if not self.voice_mode:
            return

        try:
            self.tts_engine = TTSElevenLabs(exit_event=self.exit_event, debug_event=self.debug_event, audio_cues=self.audio_cues)
            self.mpv_cancel_event = threading.Event()
            self.tts_player = MPVPlayer(self.exit_event, self.mpv_cancel_event, self.tts_engine.output_queue)
            self.tts_player.start()

        except Exception as e:
            self.tts_engine = None
            self.tts_player = None
            self.voice_mode = False
            self.logger.error(f"An error occurred while initializing the TTS engine: {e}")

    def __init_workspaces(self):
        self.logger.debug("Initializing Workspaces...")
        self.workspaces = [LocalStorageWorkspace(name="project", workspace_path=os.getcwd(),
                                                 description="A workspace holding the `Agent C` source code in Python.")]

        try:
            local_workspaces = json.load(open(".local_workspaces.json", "r"))
            for ws in local_workspaces['local_workspaces']:
                self.workspaces.append(LocalStorageWorkspace(**ws))
        except FileNotFoundError:
            pass

    def __init_events(self):
        self.exit_event = threading.Event()
        self.input_active_event = threading.Event()
        self.cancel_tts_event = threading.Event()
        self.debug_event = threading.Event()

        if debugger_is_active():
            self.debug_event.set()

    def __init_agent_params(self, **kwargs):
        self.logger.debug("Initializing Agent parameters...")
        self.backend = kwargs.get('backend', 'openai')
        self.prompt = kwargs['prompt']
        self.model_name = kwargs.get('model_name', os.environ.get('MODEL_NAME', 'gpt-4o'))
        self.agent_output_format = kwargs.get('output_format', 'raw')

        # We keep the full message array resident in memory while the session is active
        # as Zep does not persist tool calls and tool call results (rightfully so).
        #
        # DOING IT THIS WAY IS NOT A GOOD IDEA IN PRODUCTION
        #
        # This needs to be made smarter before use in prod. By not allowing Zep to manage the message log
        # we could easily blow the context window.  This is a DEMO app being used in short bursts,
        # a tool call if the user asks a followup question.
        self.current_chat_Log: Union[list[dict], None] = None

        # The toolchest holds all the toolsets for the session
        self.tool_chest: Union[ToolChest, None] = None

        # The tool cache allows the different toolsets to make use of a shared disk cache.
        self.tool_cache_dir = kwargs.get("tool_cache_dir", ".tool_cache")
        self.tool_cache = ToolCache(cache_dir=self.tool_cache_dir)

        # Experimental support for Open Interpreter
        self.allow_oi = kwargs.get("allow_oi", False)
        # Temporarily disabled due to new user issues
        # self.oi_tool: Union[OpenInterpreterTools, None] = None

    def __init_transcription(self, **kwargs):
        self.logger.debug("Initializing Transcription...")
        self.can_transcribe = os.environ.get('SPEECHMATICS_API_KEY', None) is not None
        self.stt_keybind = kwargs.get('stt_keybind', os.environ.get('STT_KEYBIND', 'c-pagedown'))
        self.transcriber: Union[None, SpeechmaticsTranscriber] = None
        if self.can_transcribe:
            self.transcriber = SpeechmaticsTranscriber(exit_event=self.exit_event, audio_cues=self.audio_cues,
                                                       ccv2_feed=self.ccv2_feed, partials=True,
                                                       listen_event=self.input_active_event)

    async def run(self):
        """
        Initializes the console and starts the input loop to interact with the user.
        """
        await self.__init_voice()
        await self.__init_session()

        if self.backend == 'claude':
            await self.__init_claude_chat_agent(self.prompt)
        else:
            await self.__init_gpt_chat_agent(self.prompt)

        self.logger.debug("Initializing complete, starting UI.")

        self.__print_session_banner()
        await self.__show_welcome_message()
        await self.__core_input_loop()

    async def __init_voice(self):
        """
        Initializes the voice toolsets if voice mode is on and the ELEVEN_API_KEY is set.
        """
        self.logger.debug("Initializing Voice toolsets...")

        if not self.voice_mode: return

        self.user_prefs.append(DefaultVoicePreference())

        from agent_c_voice.tools import VoiceTools     # noqa

    async def __init_session(self):
        self.logger.debug("Initializing Session...")
        self.session_manager = ChatSessionManager()
        await self.session_manager.init(self.user_id, self.session_id)
        self.session_id = self.session_manager.chat_session.session_id

    def __print_session_banner(self):
        self.chat_ui.show_session_info(self.session_manager)

    async def __init_gpt_chat_agent(self, persona_prompt: str):
        """
        This sets up the chat agent for the current session.
        Here's where we declare the toolsets we want to use with the agent as well as how our system prompt will look.

        Args:
            persona_prompt (str): The prompt to initialize the ChatAgent with.
        """
        self.logger.debug("Initializing GPT Chat Agent...")
        # Declare a "tool chest" of toolsets for the model.
        # In this reference app we're not supplying a tool_classes parameter so it will grab the "kitchen sink"
        # of all tool classes that have been registered.
        self.tool_chest = ToolChest()

        # These are the default and extra options for the various toolsets, since the toolsets all use kwargs
        # we can send them the whole bag of options without worry.
        tool_opts = {'tool_cache': self.tool_cache, 'session_manager': self.session_manager, 'user_preferences': self.user_prefs,
                     'workspaces': self.workspaces, 'streaming_callback': self.chat_callback}

        self.logger.debug("Initializing GPT Chat Agent... Initializing toolsets...")
        await self.tool_chest.init_tools(**tool_opts)

        # The prompt sections are grouped into "operational" and informational categories.
        # Note the XML tag as the template for the Core Instruction template, by default the core instruction set template
        # contains stuff that make talking to a development agent harder, so we shortcircuit it here BUT we have to have the XML tag there
        # That tag anchors the critical parts of the prompt into a logical group that the model can "hold on to" easier.
        # this also provides us a way to CLEARLY delineate between things WHICH MUST BE FOLLOWED and things that are informational
        # or (more importantly) USER generated.  By establishing 'operating guidelines' as a thing we can make the model evaluate its output
        # as well as user requests based on them with far greater accuracy and reliability.
        self.logger.debug("Initializing GPT Chat Agent... Initializing sections...")
        operating_sections = [
            CoreInstructionSection(template="<operating_guidelines>\n"),
            PersonaSection(template=persona_prompt),
            EndOperatingGuideLinesSection()
        ]

        operating_sections.extend(self.tool_chest.active_tool_sections)

        # Anything outside the operating guidelines is basically helpful information for the model to know.
        # These are demo sections that tell the model a little about the user as well as things like the current date / time.
        info_sections = [HelpfulInfoStartSection(),
                         EnvironmentInfoSection(session_manager=self.session_manager, voice_tools=self.tool_chest.active_tools.get('voice')),
                         UserBioSection(session_manager=self.session_manager)]

        self.logger.debug("Initializing GPT Chat Agent... Initializing agent...")
        # FINALLY we create the agent
        self.agent: GPTChatAgent = GPTChatAgent(prompt_builder=PromptBuilder(sections=operating_sections + info_sections),
                                                model_name=self.model_name,
                                                tool_chest=self.tool_chest,
                                                streaming_callback=self.chat_callback,
                                                output_format=self.agent_output_format)

    async def __init_claude_chat_agent(self, persona_prompt: str):
        self.logger.debug("Initializing Claude Chat Agent...")
        operating_sections = [
            CoreInstructionSection(template="<operating_guidelines>\n"),
            PersonaSection(template=persona_prompt),
            EndOperatingGuideLinesSection()
        ]
        self.can_use_tools = False
        self.tool_chest = ToolChest()

        # These are the default and extra options for the various toolsets, since the toolsets all use kwargs
        # we can send them the whole bag of options without worry.
        tool_opts = {'tool_cache': self.tool_cache, 'session_manager': self.session_manager, 'user_preferences': self.user_prefs,
                     'workspaces': self.workspaces, 'streaming_callback': self.chat_callback, 'agent_can_use_tools': self.can_use_tools}

        await self.tool_chest.init_tools(**tool_opts)

        # These are demo sections that tell the model a little about the user as well as things like the current date / time.
        info_sections = [HelpfulInfoStartSection(),
                         EnvironmentInfoSection(session_manager=self.session_manager, voice_tools=None),
                         UserBioSection(session_manager=self.session_manager)]

        # FINALLY we create the agent
        self.agent: ClaudeChatAgent = ClaudeChatAgent(prompt_builder=PromptBuilder(sections=operating_sections + info_sections), model_name=self.model_name,
                                                      streaming_callback=self.chat_callback, output_format=self.agent_output_format)

    def __setup_logging(self) -> logging.Logger:
        """
        Set up a logger instance with specified log level.

        Returns:
            logging.Logger: Configured logger instance.
        """
        logger = logging.getLogger(__name__)
        other_loggers = ['httpx', 'LiteLLM', 'openai', 'httpcore', 'websockets', 'speechmatics', 'asyncio', 'linkedin_api',
                         'urllib3']

        debug_other_loggers = []

        if self.debug_event.is_set():
            logger.setLevel(logging.DEBUG)
            for log in debug_other_loggers:
                logging.getLogger(log).setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.WARN)

        for log in other_loggers:
            logging.getLogger(log).setLevel(logging.WARN)

        return logger

    async def chat_callback(self, event: ChatEvent):
        """
        Called by the ChatAgent and toolsets to notify us of events as they happen.
        """
        if event.completed and event.role == 'assistant':
            self.current_chat_Log = event.messages

        # Note we forward most events to the UI layer, if you want to see how to make a console UI feel free to dig in.
        # all this thing is doing is managing the output so that Markdown renders correctly.
        await self.chat_ui.chat_event(event)

    async def __build_prompt_metadata(self):
        """
        Pretty much all of this could be in a prompt sections instead but it's left as an example of how to inject data
        into the PromptBuilder chain
        """
        memory_summary = ""
        if self.session_manager.chat_session.active_memory is not None:
            memory = self.session_manager.chat_session.active_memory
            if memory.summary is not None:
                memory_summary = memory.summary.content

        return {"session_id": self.session_id,
                "current_user_username": self.session_manager.user.user_id,
                "current_user_name": self.session_manager.user.first_name,
                "session_summary": memory_summary}

    async def __core_input_loop(self):
        """
        This is the core loop for user input and chat interaction.

        Continuously prompts input from the user and sends it to the ChatAgent, unless '!exit' command is entered
        or an EOF(End-of-File)/KeyboardInterrupt exception occurs.

        The chat responses and events are handled asynchronously by a callback.

        If any other exception occurs, it is logged.
        """
        self.logger.debug("Starting core input loop...")

        if self.voice_mode and self.tts_engine is not None:
            voice_tool = self.tool_chest.active_tools.get('voice')
            self.tts_engine.set_voice(voice_tool.voice, self.tts_model_id)

        while not self.exit_event.is_set():
            try:
                user_message, frame = await self.chat_ui.get_user_input()
                if self.tts_engine and self.tts_engine.tts_active.is_set():
                    self.tts_engine.cancel()

                if self.transcriber is not None:
                    self.transcriber.shutdown()

                if await self.cmd_handler.handle_command(user_message, self):
                    continue

                # We wait till the last minute to refresh out data from Zep so we can allow it to summarize and whatnot in the background
                await self.session_manager.update()

                # Here's where we send agent the input from the user.
                # We give it a zep cache to construct a message array from if the current_chat_log is None.
                # We als pass it a property bag to be used in prompt templates.

                # The output of the gen_chat method is an async iterator that yields content tokens only.
                # This iterator can then be passed to our async TTS engine to minimize the latency between
                # when the tokens start coming in and the agent starts speaking.
                #   agent_iter yields a token of text which gets consumed by the TTS engine
                #   the TTS engine send the token up to ElevenLabs via a websocket whenever it gets a response, it yields that response
                #   The response from that websocket is a chunk of MP3 audio, which we then stream to the audio player.
                if frame is not None and self.agent.supports_multimodal:
                    image_inputs = [frame.to_image_input()]
                else:
                    image_inputs = None

                await self.agent.chat(session_manager=self.session_manager, user_message=user_message, prompt_metadata=await self.__build_prompt_metadata(),
                                      messages=self.current_chat_Log, output_format=self.agent_output_format, images=image_inputs)

                await self.session_manager.flush()
            except (EOFError, KeyboardInterrupt):
                # Handle exit upon EOF (Ctrl-D) or Keyboard Interrupt (Ctrl-C)
                break
            except Exception as e:
                self.logger.exception(f"An error occurred: {e}")

        if self.session_manager.is_new_session:
            await self.session_manager.delete_session()

    def show_output_mode_hint(self):
        if self.agent_output_format == "markdown":
            mode_msg = f"Output mode is set to [bold gold3]markdown[/] mode.  Use [bold gold3]!r[/] to switch to raw mode."
        else:
            mode_msg = f"Output mode is set to [bold gold3]raw[/] mode.  Use [bold gold3]!m[/] to switch to markdown mode."

        self.chat_ui.fake_role_message("system", mode_msg)

    async def __show_welcome_message(self):
        """
        Basic UI stuff to show the welcome message and replay the chat log if resuming a session.
        """
        if self.session_manager.is_new_session:
            message = NEW_SESSION_WELCOME
        else:
            message = OLD_SESSION_WELCOME
            messages = await self.session_manager.zep_client.message.aget_session_messages(self.session_manager.chat_session.session_id)
            for msg in messages:
                self.chat_ui.fake_role_message(msg.role, msg.content)
        if self.tts_engine is None:
            self.chat_ui.fake_role_message("assistant", message)

        self.show_output_mode_hint()

        if self.allow_oi:
            self.chat_ui.fake_role_message("system",
                                           ("OI support is enabled. You can ask Agent C to talk to [bold aquamarine1]Opi[/], the Open Interpreter Agent, "
                                            "on your behalf, or you can speak to [bold aquamarine1]Opi[/] directly with the '[italic gold1]!opi [/]' prefix on your message.\n\n"
                                            "The OI support is still in the [bold u]experimental[/] stage and should be used with caution as [bold gold3]it currently has unfettered access to your machine,"
                                            "and can write and execute arbitrary Python code. [/]"
                                            "[bold aquamarine1]Opi[/] [bold u]will[/] ask for permission before executing code it has written, but there's no guarantee that the code it writes will be bug free."))

    def __init_camera(self, **kwargs):
        camera_no: int = kwargs.get('camera_no', -1)
        self.ccv2_feed: Union[CV2Feed, None] = None
        if camera_no > -1:
            self.logger.debug(f"Initializing Camera...Camera number: {camera_no}")
            self.ccv2_feed = CV2Feed(video_capture_device_id=camera_no, activate_event=self.input_active_event, exit_event=self.exit_event, debug_event=self.debug_event)

def main():
    parser = argparse.ArgumentParser(description="CLI Chat Interface")
    parser.add_argument('--session', type=str, help='Existing session ID to use', default=None)
    parser.add_argument('--model', type=str, help='The model name to use', default="gpt-4o")
    parser.add_argument('--prompt_file', type=str, help='Path to a file containing the system prompt to use.', default='personas/default.md')
    parser.add_argument('--userid', type=str, help='The userid for the session', default=os.environ.get("CLI_CHAT_USER_ID", "default"))
    parser.add_argument('--voice', action='store_true', help='Enable text_iter to speech via ElevenLabs.  Requires ELEVEN_LABS_API_KEY be set.')
    parser.add_argument('--oi', action='store_true', help='Enable experimental Open Interpreter support')
    parser.add_argument('--vision', action='store_true', help='Enable vision support')
    parser.add_argument('--camera', type=int, default=-1, help='What camera number to use for vision support.  Defaults to -1 which checks the env var, which defaults to 0.')
    parser.add_argument('--claude', action='store_true', help='Use Claude as the agent instead of GPT-4-1106-preview.  This is experimental.')
    args = parser.parse_args()
    load_dotenv(override=True)

    if args.prompt_file is not None:
        try:
            # Read file content into prompt
            with open(args.prompt_file, 'r', encoding='utf-8') as file:
                prompt = file.read()
        except FileNotFoundError:
            print(f"The file {args.prompt_file} was not found.")
            exit(1)
        except Exception as e:
            print(f"An error occurred while reading the prompt file: {e}")
            exit(1)

    model: str = args.model
    backend: str = 'openai'
    if args.claude and args.model == 'gpt-4o':
        model = 'claude-3-sonnet-20240229'

    camera: int = args.camera
    if args.vision:
        if camera == -1:
            camera = int(os.environ.get('VIDEO_CAPTURE_DEVICE_NUM', 0))

    if args.claude:
        backend = 'claude'

    chat = CLIChat(user_id=args.userid, prompt=prompt, session_id=args.session, voice=args.voice, model_name=model, allow_oi=args.oi, backend=backend,
                   camera_no=camera)
    asyncio.run(chat.run())


if __name__ == "__main__":
    main()
