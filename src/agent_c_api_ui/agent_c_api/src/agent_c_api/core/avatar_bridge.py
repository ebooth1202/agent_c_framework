import json
import threading
import traceback
from typing import List, Optional, Any, Dict

from fastapi import WebSocket, WebSocketDisconnect
from functools import singledispatchmethod

from agent_c.chat import ChatSessionManager
from agent_c.config.agent_config_loader import AgentConfigLoader
from agent_c.models import ChatSession
from agent_c.models.events import BaseEvent
from agent_c.util.heygen_streaming_avatar_client import HeyGenStreamingAvatarClient
from agent_c.util.registries.event import EventRegistry
from agent_c_api.api.avatar.models.client_events import GetAgentsEvent, ErrorEvent, AgentListEvent, GetAvatarsEvent, AvatarListEvent, TextInputEvent
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
        self.heygen = HeyGenStreamingAvatarClient()
        self.client_wants_cancel = threading.Event()

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
        resp = await self.heygen.list_avatars()
        await self.send_event(AvatarListEvent(avatars=resp.data))

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

    @singledispatchmethod
    async def handle_runtime_event(self, event: BaseEvent):
        """Default handler for runtime events, forward to client"""
        await self.send_event(event)

    async def runtime_callback(self, event: BaseEvent):
        """Handle runtime events from the agent"""
        self.logger.debug(f"AvatarBridge {self.chat_session.session_id}: Received runtime event: {event.type}")
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
