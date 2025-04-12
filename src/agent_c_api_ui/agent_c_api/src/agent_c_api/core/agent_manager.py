import asyncio
import logging
import uuid
from typing import Dict, Optional, List, Any, AsyncGenerator
import traceback

from agent_c import BaseAgent
from agent_c_api.core.agent_bridge import AgentBridge
from agent_c_api.core.util.logging_utils import LoggingManager


class UItoAgentBridgeManager:
    """
    Manages agent sessions in a multi-agent environment.

    This class handles the lifecycle of agent sessions, including creation,
    cleanup, and response streaming. It supports different LLM backends and
    tool configurations while ensuring thread-safe operations through
    per-session locks.

    Attributes:
        ESSENTIAL_TOOLS (List[str]): Required tool sets for all agents
        logger (logging.Logger): Instance logger
        ui_sessions (Dict[str, Dict[str, Any]]): Active session storage
        _locks (Dict[str, asyncio.Lock]): Session operation locks
    """
    ESSENTIAL_TOOLS = ['MemoryTools', 'WorkspaceTools', 'ThinkTools', 'RandomNumberTools', 'MarkdownToHtmlReportTools']

    def __init__(self):
        logging_manager = LoggingManager(__name__)
        self.logger = logging_manager.get_logger()
        # self.debug_event = LoggingManager.get_debug_event()

        self.ui_sessions: Dict[str, Dict[str, Any]] = {}
        self._locks: Dict[str, asyncio.Lock] = {}


    def get_session_data(self, ui_session_id: str) -> Dict[str, Any]:
        """
        Retrieve session data for a given session ID.

        Args:
            ui_session_id (str): The unique identifier for the session

        Returns:
            Dict[str, Any]: Session data dictionary containing agent and configuration
                information, or None if session doesn't exist
        """
        return self.ui_sessions.get(ui_session_id)

    async def create_session(self,
                             llm_model: str = None,
                             backend: str = None,
                             persona_name: str = None,
                             additional_tools: List[str] = None,
                             existing_ui_session_id: str = None, **kwargs) -> str:
        """
        Create a new session or update an existing session with a new agent.

        Args:
            llm_model: The model to use
            backend: The backend provider ('openai' or 'claude')
            persona_name: The name of the persona to use
            existing_ui_session_id: If provided, updates existing session instead of creating new one
            additional_tools: Additional tools to add to the agent - string names of tool class names
            **kwargs: Additional keyword arguments: currently passes kwargs to ReactJSAgent

        Returns:
            str: The session ID (either new or existing)

        Raises:
            Exception: If agent initialization fails
        """

        # If updating existing session, use that ID, otherwise generate new one - this will transfer chat history
        ui_session_id = existing_ui_session_id if existing_ui_session_id else str(uuid.uuid4())

        # Extract custom_prompt explicitly to avoid it being lost or overridden
        custom_prompt = kwargs.pop('custom_prompt', None)

        # Create lock if it doesn't exist
        if ui_session_id not in self._locks:
            self._locks[ui_session_id] = asyncio.Lock()

        async with self._locks[ui_session_id]:
            # Get existing session data if updating
            existing_session = self.ui_sessions.get(ui_session_id, {})
            existing_agent: BaseAgent | None = existing_session.get("agent", None)

            # IMPORTANT FIX: If we're changing models and no custom_prompt was passed with the model change,
            # but the existing agent has one, we need to preserve it
            if existing_agent and custom_prompt is None and existing_agent.custom_prompt:
                # this should work even if custom_prompt==existing_agent.custom_prompt - will be same value
                custom_prompt = existing_agent.custom_prompt
                self.logger.info(f"Preserving existing custom_prompt: {custom_prompt[:10]}...")

            # Initialize agent bridge for this session - this creates a session manager that will persist history
            agent = AgentBridge(
                user_id=ui_session_id,
                backend=backend,
                model_name=llm_model,
                additional_tools=additional_tools or [],
                persona_name=persona_name,
                agent_name=f"Agent_{ui_session_id}",
                custom_prompt=custom_prompt,
                **kwargs
            )

            # If updating existing session, transfer necessary session manager to preserve chat history
            if existing_agent:
                agent.session_manager = existing_agent.session_manager

            # Now initialize the agent. This fully initializes the agent and its tools as well - with a passed in session manager
            await agent.initialize()

            # Update sessions dictionary
            self.ui_sessions[ui_session_id] = {
                "agent": agent,
                "llm_model": llm_model,
                "created_at": agent._current_timestamp(),
                "agent_name": f"Agent_{ui_session_id}",
                "agent_c_session_id": agent.session_id,
            }

            self.logger.info(f"Session {ui_session_id} created with agent: {agent}")
            return ui_session_id

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
                session_data = self.ui_sessions[ui_session_id]
                # agent: BaseAgent = session_data.get("agent")
                # if agent:
                # if hasattr(agent, 'tool_chest') and agent.tool_chest:
                #     await agent.tool_chest.cleanup()
                # if hasattr(agent, 'session_manager') and agent.session_manager:
                #     await agent.session_manager.close()

                # Remove session data and lock
                del self.ui_sessions[ui_session_id]
                if ui_session_id in self._locks:
                    del self._locks[ui_session_id]

            except Exception as e:
                self.logger.error(f"Error cleaning up session {ui_session_id}: {e}")

    async def stream_response(
            self,
            ui_session_id: str,
            user_message: str,
            custom_prompt: Optional[str] = None,
            file_ids: Optional[List[str]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Get streaming response from the agent for a given message.
        Uses ReactJSAgent's stream_chat method for proper streaming support.

        Args:
            ui_session_id: The session identifier
            user_message: The user's message to process
            custom_prompt: Optional custom prompt to use
            file_ids: Optional list of file IDs to include with the message

        Yields:
            Chunks of the response as they become available

        Raises:
            ValueError: If the session ID is invalid
            Exception: If streaming fails
        """
        session_data = self.get_session_data(ui_session_id)
        if not session_data:
            raise ValueError(f"Invalid session ID: {ui_session_id}")

        agent = session_data["agent"]

        try:
            # Pass file_ids to the agent's stream_chat method if it accepts them
            if file_ids and hasattr(agent, "file_handler") and agent.file_handler is not None:
                # For agents with file handling capabilities
                async for chunk in agent.stream_chat(
                        user_message=user_message,
                        file_ids=file_ids,
                        custom_prompt=custom_prompt
                ):
                    yield chunk
            else:
                # For agents without file handling or no files
                async for chunk in agent.stream_chat(
                        user_message=user_message,
                        custom_prompt=custom_prompt
                ):
                    yield chunk

        except Exception as e:
            self.logger.error(f"Error in stream_response: {e}")
            error_type = type(e).__name__
            error_traceback = traceback.format_exc()
            self.logger.error(f"Error in agent_manager.py:stream_response - {error_type}: {str(e)}\n{error_traceback}")

    async def debug_session(self, ui_session_id: str):
        """
        Generate a diagnostic report for a session to help debug issues.

        Args:
            ui_session_id: The session identifier

        Returns:
            Dict containing diagnostic information about the session

        Raises:
            ValueError: If the session ID is invalid
        """
        session_data = self.get_session_data(ui_session_id)
        if not session_data:
            raise ValueError(f"Invalid session ID: {ui_session_id}")

        agent = session_data.get("agent")
        if not agent:
            return {"error": "No agent found in session data"}

        diagnostic = {
            "session_id": ui_session_id,
            "agent_c_session_id": getattr(agent, "session_id", "unknown"),
            "agent_name": agent.agent_name,
            "created_at": session_data.get("created_at", "unknown"),
            "backend": agent.backend,
            "model_name": agent.model_name,
        }

        # Check session manager
        session_manager = getattr(agent, "session_manager", None)
        if session_manager:
            diagnostic["session_manager"] = {
                "exists": True,
                "user_id": getattr(session_manager, "user_id", "unknown"),
                "has_chat_session": hasattr(session_manager,
                                            "chat_session") and session_manager.chat_session is not None,
            }

            if hasattr(session_manager, "chat_session") and session_manager.chat_session:
                diagnostic["chat_session"] = {
                    "session_id": session_manager.chat_session.session_id,
                    "has_active_memory": hasattr(session_manager,
                                                 "active_memory") and session_manager.active_memory is not None,
                }

                if hasattr(session_manager, "active_memory") and session_manager.active_memory:
                    message_count = len(session_manager.active_memory.messages)
                    diagnostic["messages"] = {
                        "count": message_count,
                        "user_messages": sum(1 for m in session_manager.active_memory.messages if m.role == "user"),
                        "assistant_messages": sum(
                            1 for m in session_manager.active_memory.messages if m.role == "assistant"),
                        "latest_message": str(session_manager.active_memory.messages[-1].content)[:100] + "..."
                        if message_count > 0 else "none"
                    }

                    # Sample of recent messages (last 3)
                    recent_messages = []
                    for msg in list(session_manager.active_memory.messages)[-3:]:
                        recent_messages.append({
                            "role": msg.role,
                            "content_preview": str(msg.content)[:50] + "..." if len(str(msg.content)) > 50 else str(
                                msg.content),
                            "timestamp": str(getattr(msg, "timestamp", "unknown"))
                        })
                    diagnostic["recent_messages"] = recent_messages
        else:
            diagnostic["session_manager"] = {"exists": False}

        # Check current_chat_Log
        current_chat_log = getattr(agent, "current_chat_Log", None)
        diagnostic["current_chat_Log"] = {
            "exists": current_chat_log is not None,
            "count": len(current_chat_log) if current_chat_log else 0
        }

        # Check tool chest
        tool_chest = getattr(agent, "tool_chest", None)
        if tool_chest:
            diagnostic["tool_chest"] = {
                "exists": True,
                "active_tools": list(tool_chest.active_tools.keys()) if hasattr(tool_chest, "active_tools") else []
            }
        else:
            diagnostic["tool_chest"] = {"exists": False}

        return diagnostic
