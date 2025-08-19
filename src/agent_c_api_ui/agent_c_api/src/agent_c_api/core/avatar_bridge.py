import json
import threading
import traceback
from typing import List, Optional, Any, Dict

from fastapi import WebSocket, WebSocketDisconnect
from functools import singledispatchmethod

from agent_c.chat import ChatSessionManager
from agent_c.config.agent_config_loader import AgentConfigLoader
from agent_c.models import ChatSession
from agent_c.models.events import BaseEvent, TextDeltaEvent, CompletionEvent
from agent_c.models.events.chat import ThoughtDeltaEvent
from agent_c.models.heygen import HeygenAvatarSessionData, NewSessionRequest
from agent_c.util.heygen_streaming_avatar_client import HeyGenClient, HeyGenStreamingClient
from agent_c.util.registries.event import EventRegistry
from agent_c_api.api.avatar.models.client_events import GetAgentsEvent, ErrorEvent, AgentListEvent, GetAvatarsEvent, AvatarListEvent, TextInputEvent, SetAvatarEvent, AvatarConnectionChangedEvent, \
    SetAgentEvent, AgentConfigurationChangedEvent
from agent_c_api.core.agent_bridge import AgentBridge
from agent_c.models.input import AudioInput

from agent_c.models.input.file_input import FileInput
from agent_c_api.core.file_handler import FileHandler
from agent_c.models.input.image_input import ImageInput
from agent_c_tools.tools.think.prompt import ThinkSection
from agent_c.prompting import PromptBuilder
from agent_c.prompting.basic_sections.persona import DynamicPersonaSection


class AvatarBridge(AgentBridge):
    def __init__(self,
                 chat_session: ChatSession,
                 session_manager: ChatSessionManager,
                 file_handler: Optional[FileHandler] = None):
        super().__init__(chat_session, session_manager, file_handler)
        self.websocket: Optional[WebSocket] = None
        self.is_running = False
        self.agent_config_loader: AgentConfigLoader = AgentConfigLoader()
        self.heygen_base_client = HeyGenClient()
        self.heygen_stream_client: Optional[HeyGenStreamingClient] = None
        self.client_wants_cancel = threading.Event()
        self.avatar_session: Optional[HeygenAvatarSessionData] = None
        self._partial_agent_message: str = ""
        self._avatar_did_think = False

    # Handlers for events coming from the client websocket
    @singledispatchmethod
    async def handle_client_event(self, event: BaseEvent) -> None:
        """Default handler for unknown events"""
        self.logger.warning(f"AvatarBridge {self.chat_session.session_id}: Unhandled event type: {event.type}")
        await self.send_error(f"Unknown event type: {event.type}")

    @handle_client_event.register
    async def _(self, _: GetAgentsEvent) -> None:
        await self.send_agent_list()

    @handle_client_event.register
    async def _(self, event: TextInputEvent) -> None:
        await self.interact(user_message=event.text, file_ids=event.file_ids)

    async def send_agent_list(self) -> None:
        await self.send_event(AgentListEvent(agents=self.agent_config_loader.client_catalog))

    @handle_client_event.register
    async def _(self, _: GetAvatarsEvent) -> None:
        await self.send_avatar_list()

    async def send_avatar_list(self) -> None:
        resp = await self.heygen_base_client.list_avatars()
        await self.send_event(AvatarListEvent(avatars=resp.data))

    async def end_avatar_session(self) -> None:
        """End the current avatar session if it exists"""
        if self.avatar_session:
            try:
                await self.heygen_stream_client.close_session()
                self.logger.info(f"Avatar session {self.avatar_session.session_id} ended successfully")
            except Exception as e:
                self.logger.error(f"Failed to end avatar session {self.avatar_session.session_id}: {e}")
            finally:
                self.avatar_session = None
                self.heygen_stream_client = None

    @handle_client_event.register
    async def _(self, event: SetAvatarEvent) -> None:
        await self.set_avatar(event.avatar_id)

    async def set_avatar(self, avatar_id: str, quality: str = "medium", vide0_encoding: str = "vp8") -> None:
        """Set the avatar for the current session by creating a HeyGen session"""
        if self.avatar_session is not None:
            await self.end_avatar_session()

        self.heygen_stream_client = await self.heygen_base_client.create_streaming_client()
        self.avatar_session = await self.heygen_stream_client.create_new_session(NewSessionRequest(avatar_id=avatar_id, quality=quality, video_encoding=vide0_encoding))
        await self.send_event(AvatarConnectionChangedEvent(avatar_session=self.avatar_session))

    @handle_client_event.register
    async def _(self, event: SetAgentEvent) -> None:
        await self.set_agent(event.agent_key)

    async def set_agent(self, agent_key: str) -> None:
        """Set the agent for the current session"""
        if not self.chat_session.agent_config or self.chat_session.agent_config.key != agent_key:
            agent_config = self.agent_config_loader.duplicate(agent_key)
            if not agent_config:
                await self.send_error(f"Agent '{agent_key}' not found")
                return

            self.chat_session.agent_config = agent_config
            await self.tool_chest.activate_toolset(self.chat_session.agent_config.tools)
            self.logger.info(f"AvatarBridge {self.chat_session.session_id}: Agent set to {agent_key}")

        await self.send_event(AgentConfigurationChangedEvent(agent_config=self.chat_session.agent_config))

    def parse_event(self, data: dict) -> BaseEvent:
        """Parse incoming data into appropriate event type"""
        event_type = data.get("type")
        if not event_type:
            raise ValueError("Event must have a 'type' field")

        event_class = EventRegistry.get_class(event_type)

        if event_class:
            return event_class(**data)
        else:
            self.logger.warning(f"Unknown event type '{event_type}', using BaseEvent")
            return BaseEvent(**data)

    async def send_event(self, event: BaseEvent):
        """Send event to the client"""
        try:
            await self.websocket.send_text(event.model_dump_json())
        except Exception as e:
            self.logger.exception(f"Failed to send event to {self.chat_session.session_id}: {e}")
            self.is_running = False

    async def send_error(self, message: str):
        """Send error message to client"""
        await self.send_event(ErrorEvent(message=message))

    # Handlers for runtime events coming over the callback
    @singledispatchmethod
    async def handle_runtime_event(self, event: BaseEvent):
        """Default handler for runtime events, forward to client"""
        await self.send_event(event)

    @handle_runtime_event.register
    async def _(self, event: CompletionEvent):
        if event.running == False and len(self._partial_agent_message.rstrip()):
            # Send any remaining partial message
            await self.avatar_say(self._partial_agent_message, role="assistant")
            self._partial_agent_message = ""

        await self.send_event(event)

    @handle_runtime_event.register
    async def _(self, event: TextDeltaEvent):
        self._avatar_did_think = False
        self._partial_agent_message += event.text_delta
        await self._handle_partial_agent_message()

    @property
    def avatar_think_message(self) -> str:
        # Placeholder for avatar thinking message
        return "Let me think about that..."

    @handle_runtime_event.register
    async def _(self, event: ThoughtDeltaEvent):
        """Handle thought events from the agent"""
        await self._handle_agent_thought_token()
        await self.send_event(event)

    async def _handle_agent_thought_token(self):
        """Handle agent thought messages"""
        if not self._avatar_did_think:
            self._avatar_did_think = True
            try:
                await self.heygen_stream_client.send_task(self.avatar_think_message)
            except Exception as e:
                self.logger.error(f"AvatarBridge {self.chat_session.session_id}: Failed to send message to avatar: {e}")

    async def _handle_partial_agent_message(self):
        if "\n" not in self._partial_agent_message:
            return

        left, right = self._partial_agent_message.rsplit("\n", 1)
        self._partial_agent_message = right
        await self.avatar_say(left + "\n", role="assistant")

    async def avatar_say(self, text: str, role: str = "assistant"):
        if not self.heygen_stream_client or not self.avatar_session:
            self.logger.error(f"AvatarBridge {self.chat_session.session_id}: No active avatar session to send message")
            return
        try:
            await self.heygen_stream_client.send_task(text)
        except Exception as e:
            self.logger.error(f"AvatarBridge {self.chat_session.session_id}: Failed to send message to avatar: {e}")
            await self.send_error(f"Failed to send message to avatar: {str(e)}")

        await self.send_event(TextDeltaEvent(
            content=text,
            session_id=self.chat_session.session_id,
            role=role
        ))

    async def runtime_callback(self, event: BaseEvent):
        """Handle runtime events from the agent"""
        self.logger.debug(f"AvatarBridge {self.chat_session.session_id}: Received runtime event: {event.type}")
        # These are already in model format and don't need parsed.
        await self.handle_runtime_event(event)


    async def run(self, websocket: WebSocket):
        """Main run loop for the bridge"""
        self.websocket=websocket
        self.is_running = True
        self.logger.info (f"AvatarBridge started for session {self.chat_session.session_id}")

        try:
            await self.send_agent_list()
            await self.send_avatar_list()

            while self.is_running:
                try:
                    data = await self.websocket.receive_json()
                    event = self.parse_event(data)
                    await self.handle_client_event(event)

                except WebSocketDisconnect:
                    self.logger.info(f"Session {self.chat_session.session_id} disconnected normally")
                    break
                except json.JSONDecodeError:
                    await self.send_error("Invalid JSON received")
                except Exception as e:
                    self.logger.exception(f"Error handling event for session {self.chat_session.session_id}: {e}")
                    await self.send_error(f"Error processing event: {str(e)}")

        finally:
            self.logger.info(f"AvatarBridge stopped for session {self.chat_session.session_id}")


    async def interact(
        self,
        user_message: str,
        file_ids: Optional[List[str]] = None,
    ) -> None:
        """
        Streams chat responses for a given user message.

        This method handles the complete chat interaction process, including:
        - Session updates
        - Custom prompt integration
        - Message processing
        - Response streaming
        - Event handling

        Args:
            user_message (str): The message from the user to process
            file_ids (List[str], optional): IDs of files to include with the message
        Raises:
            Exception: Any errors during chat processing
        """
        self.client_wants_cancel.clear()

        try:
            await self.session_manager.update()
            agent_runtime = self.runtime_for_agent(self.chat_session.agent_config)
            file_inputs = []
            if file_ids and self.file_handler:
                file_inputs = await self.process_files_for_message(file_ids, self.chat_session.session_id)

                # Log information about processed files
                if file_inputs:
                    input_types = {type(input_obj).__name__: 0 for input_obj in file_inputs}
                    for input_obj in file_inputs:
                        input_types[type(input_obj).__name__] += 1
                    self.logger.info(f"Processing {len(file_inputs)} files: {input_types}")

            prompt_metadata = await self.__build_prompt_metadata()
            # Prepare chat parameters
            tool_params = {}
            if len(self.chat_session.agent_config.tools):
                await self.tool_chest.initialize_toolsets(self.chat_session.agent_config.tools)
                tool_params = self.tool_chest.get_inference_data(self.chat_session.agent_config.tools, agent_runtime.tool_format)
                tool_params["toolsets"] = self.chat_session.agent_config.tools

            if self.sections is not None:
                agent_sections = self.sections
            elif "ThinkTools" in self.chat_session.agent_config.tools:
                agent_sections = [ThinkSection(), DynamicPersonaSection()]
            else:
                agent_sections = [DynamicPersonaSection()]

            chat_params: Dict[str, Any] = {
                "user_id": self.chat_session.user_id,
                "chat_session": self.chat_session,
                "tool_chest": self.tool_chest,
                "user_message": user_message,
                "prompt_metadata": prompt_metadata,
                "client_wants_cancel": self.client_wants_cancel,
                "streaming_callback": self.runtime_callback,
                'tool_call_context': {'active_agent': self.chat_session.agent_config},
                'prompt_builder': PromptBuilder(sections=agent_sections)
            }

            # Categorize file inputs by type to pass to appropriate parameters
            image_inputs = [input_obj for input_obj in file_inputs
                            if isinstance(input_obj, ImageInput)]
            audio_inputs = [input_obj for input_obj in file_inputs
                            if isinstance(input_obj, AudioInput)]
            document_inputs = [input_obj for input_obj in file_inputs
                               if isinstance(input_obj, FileInput) and
                               not isinstance(input_obj, ImageInput) and
                               not isinstance(input_obj, AudioInput)]

            # Only add parameters if there are inputs of that type
            if image_inputs:
                chat_params["images"] = image_inputs
            if audio_inputs:
                chat_params["audio_clips"] = audio_inputs
            if document_inputs:
                chat_params["files"] = document_inputs

            full_params = chat_params | tool_params
        except Exception as e:
            error_type = type(e).__name__
            error_traceback = traceback.format_exc()
            self.logger.error(f"Error preparing chat parameters: {error_type}: {str(e)}\n{error_traceback}")
            await self.send_error(f"Error preparing chat parameters: {error_type}: {str(e)}\n{error_traceback}")
            return

        try:
            await agent_runtime.chat(**full_params)
        except Exception as e:
            error_type = type(e).__name__
            error_traceback = traceback.format_exc()
            self.logger.error(f"Error in agent_runtime.chat: {error_type}: {str(e)}\n{error_traceback}")
            await  self.send_error( f"Error in agent_runtime.chat: {error_type}: {str(e)}\n{error_traceback}")
            return

        try:
            await self.session_manager.flush(self.chat_session.session_id)

        except Exception as e:
            error_type = type(e).__name__
            error_traceback = traceback.format_exc()
            self.logger.error(f"Error flushing session manager: {error_type}: {str(e)}\n{error_traceback}")
            await self.send_error(f"Error flushing session manager: {error_type}: {str(e)}\n{error_traceback}")
            return
