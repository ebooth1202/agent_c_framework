from datetime import datetime
from typing import Optional, Any

from fastapi import Depends, HTTPException

from agent_c_api.api.dependencies import get_agent_manager
from agent_c_api.core.agent_manager import UItoAgentBridgeManager


from .models import SessionCreate, SessionDetail, SessionListResponse, SessionSummary, SessionUpdate


class SessionService:
    """Service for managing sessions using the underlying agent manager"""

    def __init__(self, agent_manager: UItoAgentBridgeManager = Depends(get_agent_manager)):
        self.agent_manager = agent_manager

    async def create_session(self, session_data: SessionCreate) -> SessionDetail:
        """Create a new session
        
        Args:
            session_data: The session creation parameters
            
        Returns:
            SessionDetail: Details of the created session
            
        Raises:
            HTTPException: If session creation fails
        """
        try:
            # Convert SessionCreate to kwargs for agent_manager.create_session
            # This matches how v1 API initializes sessions
            model_params = {
                "temperature": session_data.temperature,
                "reasoning_effort": session_data.reasoning_effort,
                "budget_tokens": session_data.budget_tokens,
                "max_tokens": session_data.max_tokens,
            }
            
            additional_params: dict[str, Any] = {
                "persona_name": session_data.persona_id,
                "custom_prompt": session_data.custom_prompt,
            }
            
            # Handle tools parameter - must be List[str] or None
            # The session_data.tools might be None, an empty list, or a populated list
            if session_data.tools is not None and len(session_data.tools) > 0:
                # Ensure all items are strings
                additional_params["additional_tools"] = session_data.tools
            
            # Filter out None values
            model_params = {k: v for k, v in model_params.items() if v is not None}
            additional_params = {k: v for k, v in additional_params.items() if v is not None}
            
            # Create the session in the agent manager
            ui_session_id = await self.agent_manager.create_session(
                llm_model=session_data.model_id,
                **model_params,
                **additional_params
            )
            
            # Get the created session data
            session_data = self.agent_manager.get_session_data(ui_session_id)
            if not session_data:
                raise HTTPException(status_code=500, detail="Session created but data not found")
            
            # Extract agent_c_session_id
            agent_c_session_id = session_data.get("agent_c_session_id", "")
            
            # Transform into our response model
            return SessionDetail(
                id=ui_session_id,
                model_id=session_data.get("model_name", ""),
                persona_id=session_data.get("persona_name", "default"),
                created_at=session_data.get("created_at", datetime.now()),
                last_activity=session_data.get("last_activity"),
                agent_internal_id=agent_c_session_id,
                tools=session_data.get("additional_tools", []),
                temperature=session_data.get("temperature"),
                reasoning_effort=session_data.get("reasoning_effort"),
                budget_tokens=session_data.get("budget_tokens"),
                max_tokens=session_data.get("max_tokens"),
                custom_prompt=session_data.get("custom_prompt"),
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

    async def get_sessions(self, limit: int = 10, offset: int = 0) -> SessionListResponse:
        """Get list of sessions with pagination
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            
        Returns:
            SessionListResponse: Paginated list of sessions
        """
        # Get all sessions from the agent manager
        sessions = self.agent_manager.ui_sessions
        
        # Convert to list for pagination
        session_list = [
            SessionSummary(
                id=session_id,
                model_id=session_data.get("model_name", ""),
                persona_id=session_data.get("persona_name", "default"),
                created_at=session_data.get("created_at", datetime.now()),
                last_activity=session_data.get("last_activity"),
            )
            for session_id, session_data in sessions.items()
        ]
        
        # Apply pagination
        total = len(session_list)
        paginated_sessions = session_list[offset : offset + limit]
        
        # Return paginated response
        return SessionListResponse(
            items=paginated_sessions,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def get_session(self, session_id: str) -> Optional[SessionDetail]:
        """Get detailed information about a specific session
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            SessionDetail: Session details if found, None otherwise
        """
        # Get session data using the manager's method
        session_data = self.agent_manager.get_session_data(session_id)
        if not session_data:
            return None
            
        # Extract agent_c_session_id
        agent_c_session_id = session_data.get("agent_c_session_id", "")
        
        # Get tools - use the tools that were provided at creation time
        tools = session_data.get("additional_tools", [])
        
        # Construct and return the SessionDetail response
        return SessionDetail(
            id=session_id,
            model_id=session_data.get("model_name", ""),
            persona_id=session_data.get("persona_name", "default"),
            created_at=session_data.get("created_at", datetime.now()),
            last_activity=session_data.get("last_activity"),
            agent_internal_id=agent_c_session_id,
            tools=tools,
            temperature=session_data.get("temperature"),
            reasoning_effort=session_data.get("reasoning_effort"),
            budget_tokens=session_data.get("budget_tokens"),
            max_tokens=session_data.get("max_tokens"),
            custom_prompt=session_data.get("custom_prompt"),
        )

    async def update_session(self, session_id: str, update_data: SessionUpdate) -> SessionDetail:
        """Update session properties by recreating the session with new parameters
        
        Since UItoAgentBridgeManager doesn't provide a direct update method,
        we implement updates by creating a new session with the updated parameters
        and transferring the session ID.
        
        Args:
            session_id: ID of the session to update
            update_data: New session properties
            
        Returns:
            SessionDetail: Updated session details
            
        Raises:
            HTTPException: If session not found or update fails
        """
        # Get current session data
        current_session = self.agent_manager.get_session_data(session_id)
        if not current_session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
            
        try:
            # Prepare update parameters by merging current and new values
            # Get only non-None values from the update
            updates = update_data.model_dump(exclude_unset=True, exclude_none=True)
            
            # Create new parameters based on current session
            model_params = {
                "temperature": current_session.get("temperature"),
                "reasoning_effort": current_session.get("reasoning_effort"),
                "budget_tokens": current_session.get("budget_tokens"),
                "max_tokens": current_session.get("max_tokens"),
            }
            
            additional_params = {
                "persona_name": current_session.get("persona_name", "default"),
                "custom_prompt": current_session.get("custom_prompt"),
                "additional_tools": current_session.get("additional_tools", []),
            }
            
            # Apply updates
            for key, value in updates.items():
                if key == "persona_id":
                    additional_params["persona_name"] = value
                elif key in model_params:
                    model_params[key] = value
                elif key in additional_params:
                    additional_params[key] = value
                    
            # Remove None values
            model_params = {k: v for k, v in model_params.items() if v is not None}
            additional_params = {k: v for k, v in additional_params.items() if v is not None}
            
            # Create a new session with existing session ID
            session_params = {"existing_ui_session_id": session_id}
            
            await self.agent_manager.create_session(
                llm_model=current_session.get("model_name"),
                **model_params,
                **additional_params,
                **session_params
            )
            
            # Return updated session details
            return await self.get_session(session_id)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

    async def delete_session(self, session_id: str) -> bool:
        """Delete a specific session by cleaning it up
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            bool: True if successful, False if session not found
        """
        # Check if the session exists
        if not self.agent_manager.get_session_data(session_id):
            return False

        # Delete the session in the agent manager using cleanup_session
        try:
            await self.agent_manager.cleanup_session(session_id)
            return True
        except Exception as e:
            # Log the error but still return False
            import logging
            logging.error(f"Error deleting session {session_id}: {str(e)}")
            return False