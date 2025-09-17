import asyncio
import threading

from typing import Dict, Optional, List, Any

from agent_c.models import ChatUser
from agent_c.util import MnemonicSlugs
from agent_c.config.agent_config_loader import AgentConfigLoader
from agent_c.models.agent_config import AgentConfiguration
from agent_c.chat.session_manager import ChatSessionManager, ChatSession
from agent_c_api.core.realtime_bridge import RealtimeBridge
from agent_c_api.core.util.logging_utils import LoggingManager
from agent_c_api.models.realtime_session import RealtimeSession


class RealtimeSessionManager:
    """
    Maintains the connection between client UI
    """

    def __init__(self, session_manager: ChatSessionManager):
        logging_manager = LoggingManager(__name__)
        self.logger = logging_manager.get_logger()


        self.ui_sessions: Dict[str, RealtimeSession] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._cancel_events: Dict[str, threading.Event] = {}
        self.agent_config_loader: AgentConfigLoader = AgentConfigLoader()
        self.chat_session_manager: ChatSessionManager = session_manager

    def get_session_data(self, ui_session_id: str) -> Optional[RealtimeSession]:
        """
        Retrieve session data for a given session ID.

        Args:
            ui_session_id (str): The unique identifier for the session

        Returns:
            Optional[RealtimeSession]: The session data if found, else None
        """
        return self.ui_sessions.get(ui_session_id, None)

    def get_user_session_data(self, ui_session_id: str, user_id: str) ->  Optional[RealtimeSession]:
        session = self.get_session_data(ui_session_id)

        if not session or session.user_id != user_id:
            return None

        return session

    async def get_or_create_realtime_session(self, user: ChatUser, session_id: Optional[str] = None) -> RealtimeSession:
        """
        Retrieve an existing session or create a new one if it doesn't exist.

        Args:
            user: The chat user for the session
            session_id: Optional existing session ID to retrieve
        Returns:
            RealtimeSession: The existing or newly created session
        """
        if session_id and session_id in self.ui_sessions:
            return self.ui_sessions[session_id]

        return await self.create_realtime_session(user)


    async def create_realtime_session(self, user: ChatUser, session_id: Optional[str] = None) -> RealtimeSession:
        """
        Create a new session or update an existing session with a new agent.

        Args:
            user: The chat user for the session
            session_id: Optional session ID to use; if None, a new ID is generated
        Returns:
            RealtimeSession: The bridge handling the session
        """
        ui_session_id = session_id if session_id else RealtimeSession.generate_session_id(user.user_id)

        self._locks[ui_session_id] = asyncio.Lock()

        async with self._locks[ui_session_id]:
            agent_bridge = RealtimeBridge(user, ui_session_id, self.chat_session_manager)
            await agent_bridge.initialize()
            self.ui_sessions[ui_session_id] = RealtimeSession(session_id=ui_session_id, user_id=user.user_id, bridge=agent_bridge)

            self.logger.info(f"Session {ui_session_id} created")
            return self.ui_sessions[ui_session_id]

    async def cleanup_session(self, ui_session_id: str):
        """
        Clean up resources associated with a specific session.

        Removes session data and releases associated locks. Any errors during
        cleanup are logged but don't halt execution.

        Args:
            ui_session_id (str): The unique identifier of the session to clean up

        Note:
            This method is safe to call multiple times on the same session ID
        """
        if ui_session_id in self.ui_sessions:
            try:
                del self.ui_sessions[ui_session_id]
                if ui_session_id in self._locks:
                    del self._locks[ui_session_id]

            except Exception as e:
                self.logger.error(f"Error cleaning up session {ui_session_id}: {e}")

    def cancel_interaction(self, ui_session_id: str) -> bool:
        """
        Cancel an ongoing interaction for the specified session.

        Args:
            ui_session_id: The session identifier

        Returns:
            bool: True if cancellation was triggered, False if session not found
        """
        if ui_session_id not in self.ui_sessions:
            return False

        # Set the event to signal cancellation
        self.logger.info(f"Cancelling interaction for session: {ui_session_id}")
        self.ui_sessions[ui_session_id].bridge.client_wants_cancel.set()
        return True
