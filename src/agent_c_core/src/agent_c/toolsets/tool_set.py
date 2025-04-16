import os
import copy
import inspect
import re
from typing import Union, List, Dict, Any

from agent_c.models.events import RenderMediaEvent, MessageEvent, TextDeltaEvent
from agent_c.prompting.prompt_section import PromptSection
from agent_c.toolsets.tool_cache import ToolCache
from agent_c.chat.session_manager import ChatSessionManager


class Toolset:
    tool_registry: List[Any] = []
    tool_sep: str = "_"

    @classmethod
    def register(cls, tool_cls: Any) -> None:
        """
        Registers a tool class in the tool registry if it's not already present.

        Args:
            tool_cls: The class of the tool to be registered.
        """
        if tool_cls not in cls.tool_registry:
            cls.tool_registry.append(tool_cls)

    def __init__(self, **kwargs: Any) -> None:
        """
        Initializes the Toolset with the provided options.

        Args:
            kwargs:
                name (str): The name of the toolset.
                session_manager (ChatSessionManager): Manages chat sessions.
                tool_chest (ToolChest): Holds the active/tools available to the toolset.
                required_tools (List[str]): A list of tools that are required to be activated.
                tool_cache (ToolCache): Cache for tools.
                section (PromptSection | None): Section-related information.
                agent_can_use_tools (bool): If the agent can use toolsets (defaults to True if unset).
                need_tool_user (bool): Defines if this toolset requires a tool-using agent (defaults to True).
                needed_keys (List[str]): List of environment keys required for the toolset functionality.
                streaming_callback (Callable[..., None]): A callback to be triggered after streaming events.
                output_format (str): Format for output. Defaults to 'raw'.
                tool_role (str): Defines the role of the tool (defaults to 'tool').
        """
        # Initialize properties
        self.name: str = kwargs.get("name")
        if self.name is None:
            raise ValueError("Toolsets must have a name.")

        self.session_manager: ChatSessionManager = kwargs.get("session_manager")
        self.tool_chest: 'ToolChest' = kwargs.get("tool_chest")
        self.use_prefix: bool = kwargs.get("use_prefix", True)

        # Handle required tools activation
        required_tools: List[str] = kwargs.get("required_tools", [])
        for tool_name in required_tools:
            if tool_name not in self.tool_chest.active_tools:
                self.valid: bool = self.tool_chest.activate_tool(tool_name)
                if not self.valid:
                    break

        self.tool_cache: ToolCache = kwargs.get("tool_cache")
        self.section: Union[PromptSection, None] = kwargs.get('section')

        # Agent capabilities and tool requirements
        self.agent_can_use_tools: bool = kwargs.get("agent_can_use_tools", True)
        self.need_tool_user: bool = kwargs.get("need_tool_user", True)

        # Validate environment variables
        needed_keys: List[str] = kwargs.get('needed_keys', [])
        self.tool_valid: bool = self._validate_env_keys(needed_keys)

        # If toolset requires a tool-using agent but the agent cannot use tools, invalid toolset
        if self.need_tool_user and not self.agent_can_use_tools:
            self.tool_valid = False

        self.openai_schemas: List[Dict[str, Any]] = self.__openai_schemas()

        # Additional attributes
        self.streaming_callback = kwargs.get('streaming_callback')
        self.output_format: str = kwargs.get('output_format', 'raw')
        self.tool_role: str = kwargs.get('tool_role', 'tool')

    def _format_markdown(self, markdown: str) -> str:
        """
        Formats markdown to ensure proper rendering by fixing spacing issues.

        Args:
            markdown (str): The markdown string to format.

        Returns:
            str: Properly formatted markdown string.
        """
        if not markdown:
            return ''

        # Step 1: Trim leading/trailing whitespace
        formatted = markdown.strip()

        # Step 2: Fix headers - remove spaces between newlines and # symbols
        formatted = re.sub(r'\n\s+#', r'\n#', formatted)

        # Step 3: Fix list items - remove spaces between newlines and list markers
        formatted = re.sub(r'\n\s+[-*]', r'\n-', formatted)

        # Step 4: Fix the first line if it starts with space+#
        formatted = re.sub(r'^\s+#', '#', formatted)

        # Step 5: Remove extra spaces at the beginning of lines that aren't headers or list items
        formatted = re.sub(r'\n\s+([^-#*])', r'\n\1', formatted)

        return formatted


    async def _raise_render_media(self, **kwargs: Any) -> None:
        """
        Raises a render media event.

        Args:
            kwargs: The arguments to be passed to the render media event.
        """
        kwargs['role'] = kwargs.get('role', self.tool_role)
        kwargs['session_id'] = kwargs.get('session_id', self.session_manager.chat_session.session_id)

        # Format markdown content if content_type is text/markdown
        content_type = kwargs.get('content_type')
        if content_type == 'text/markdown' and 'content' in kwargs:
            kwargs['content'] = self._format_markdown(kwargs['content'])

        # Create the event object
        render_media_event = RenderMediaEvent(**kwargs)

        # Log the event if we have access to an agent with a session_logger
        if hasattr(self.tool_chest, 'agent') and self.tool_chest.agent:
            agent = self.tool_chest.agent
            if hasattr(agent, 'session_logger') and agent.session_logger:
                await agent.session_logger.log_render_media(render_media_event)
        
        # Send it to the streaming callback
        if self.streaming_callback:
            await self.streaming_callback(render_media_event)


    async def _raise_message_event(self, **kwargs: Any) -> None:
        """
        Raises a message event.

        Args:
            kwargs: The arguments to be passed to the message event.
        """
        kwargs['role'] = kwargs.get('role', self.tool_role)
        kwargs['format'] = kwargs.get('format', self.output_format)
        kwargs['session_id'] = kwargs.get('session_id', self.session_manager.chat_session.session_id)
        await self.streaming_callback(MessageEvent(**kwargs))

    async def _raise_text_delta_event(self, **kwargs: Any) -> None:
        """
        Raises a text delta event with additional text

        Args:
            kwargs: The arguments to be passed to the message event.
        """
        kwargs['role'] = kwargs.get('role', self.tool_role)
        kwargs['format'] = kwargs.get('format', self.output_format)
        kwargs['session_id'] = kwargs.get('session_id', self.session_manager.chat_session.session_id)
        await self.streaming_callback(TextDeltaEvent(**kwargs))

    async def post_init(self) -> None:
        """
        Optional post-initialization method that can be used for additional setup.
        """
        pass

    @staticmethod
    def _validate_env_keys(needed_keys: List[str]) -> bool:
        """
        Validates that certain environment keys are present and non-empty.

        Args:
            needed_keys (List[str]): List of keys to check in the environment.

        Returns:
            bool: True if all needed keys are present and non-empty, False otherwise.
        """
        for key in needed_keys:
            if not os.getenv(key):
                return False
        return True

    def dict(self) -> Dict[str, 'Toolset']:
        """
        Returns a dictionary representation of the Toolset.

        Returns:
            Dict[str, Toolset]: A dictionary with the toolset name as the key and the Toolset as the value.
        """
        return {self.name: self}

    def tool_schemas(self) -> List[Dict[str, Any]]:
        """
        Returns the OpenAI schemas for the toolset.

        Returns:
            List[Dict[str, Any]]: A list of OpenAI schemas for the registered methods in the Toolset.
        """
        return self.__openai_schemas()

    def __openai_schemas(self) -> List[Dict[str, Any]]:
        """
        Generate OpenAI-compatible schemas based on method metadata.

        Returns:
            List[Dict[str, Any]]: A list of OpenAI schemas for the registered methods in the Toolset.
        """
        openai_schemas = []
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            if hasattr(method, 'schema'):
                schema = copy.deepcopy(method.schema)
                if self.use_prefix:
                    schema['function']['name'] = f"{self.name}{Toolset.tool_sep}{schema['function']['name']}"
                openai_schemas.append(schema)

        return openai_schemas
