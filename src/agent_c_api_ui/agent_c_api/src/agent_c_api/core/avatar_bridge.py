import json
from typing import Optional

from fastapi import WebSocket, WebSocketDisconnect
from functools import singledispatchmethod

from agent_c.chat import ChatSessionManager
from agent_c.config.agent_config_loader import AgentConfigLoader
from agent_c.models import ChatSession
from agent_c.models.events import BaseEvent
from agent_c.util.heygen_streaming_avatar_client import HeyGenStreamingAvatarClient
from agent_c.util.registries.event import EventRegistry
from agent_c_api.api.avatar.models.client_events import GetAgentsEvent, ErrorEvent, AgentListEvent, GetAvatarsEvent, AvatarListEvent
from agent_c_api.core.agent_bridge import AgentBridge
from agent_c_api.core.file_handler import FileHandler


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

    @singledispatchmethod
    async def handle_client_event(self, event: BaseEvent) -> None:
        """Default handler for unknown events"""
        self.logger.warning(f"AvatarBridge {self.chat_session.session_id}: Unhandled event type: {event.type}")
        await self.send_error(f"Unknown event type: {event.type}")

    @handle_client_event.register
    async def _(self, _: GetAgentsEvent) -> None:
        await self.send_agent_list()

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

