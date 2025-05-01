from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import BackgroundTasks

from agent_c_api.api.v1.interactions.services.interaction_service import InteractionService
from agent_c_api.api.v1.interactions.interaction_models.interaction_model import InteractionSummary, InteractionDetail as V1InteractionDetail
from agent_c_api.api.v1.interactions.services.event_service import EventService as V1EventService
from agent_c_api.api.v1.interactions.interaction_models.event_model import EventType as V1EventType

from agent_c_api.api.v2.models.response_models import APIResponse, PaginatedResponse, PaginationMeta, APIStatus
from agent_c_api.api.v2.models.history_models import (
    Event, EventFilter, ReplayStatus, ReplayControl,
    HistorySummary, HistoryDetail, PaginationParams, HistoryListResponse
)
from agent_c_api.api.v2.models.response_models import APIResponse, PaginatedResponse, PaginationMeta, APIStatus

class HistoryService:
    def __init__(self):
        self._interaction_service = InteractionService()
    
    async def list_histories(self, pagination: PaginationParams) -> HistoryListResponse:
        """List available session histories with pagination"""
        histories = await self._interaction_service.list_sessions(
            limit=pagination.limit,
            offset=pagination.offset,
            sort_by=pagination.sort_by,
            sort_order=pagination.sort_order
        )
        
        # Convert to HistorySummary objects
        history_summaries = [
            HistorySummary(
                id=h.id,
                start_time=h.start_time,
                end_time=h.end_time,
                duration_seconds=h.duration_seconds,
                event_count=h.event_count,
                file_count=h.file_count
            ) for h in histories
        ]
        
        # For total count, we'll use the returned list length as a reasonable proxy
        # A full count query would be expensive and might not be necessary
        # In a production system, we'd want a more efficient way to get this count
        total_count = len(histories)
        if histories and len(histories) == pagination.limit:
            # This is a heuristic - if we got exactly the limit, there may be more
            # For a proper implementation, the service should return a count
            total_count = pagination.offset + pagination.limit + 1  # At least one more
        
        return HistoryListResponse(
            items=history_summaries,
            total=total_count,
            limit=pagination.limit,
            offset=pagination.offset
        )
    
    async def get_history(self, session_id: str) -> Optional[HistoryDetail]:
        """Get detailed information about a specific session history"""
        session = await self._interaction_service.get_session(session_id)
        if not session:
            return None
            
        return HistoryDetail(
            id=session.id,
            start_time=session.start_time,
            end_time=session.end_time,
            duration_seconds=session.duration_seconds,
            event_count=session.event_count,
            file_count=session.file_count,
            files=session.files,
            event_types=session.event_types,
            metadata=session.metadata,
            user_id=session.user_id,
            has_thinking=session.has_thinking,
            tool_calls=session.tool_calls
        )
    
    async def delete_history(self, session_id: str) -> bool:
        """Delete a session history"""
        return await self._interaction_service.delete_session(session_id)


class EventService:
    def __init__(self):
        self._event_service = V1EventService()
    
    async def get_events(
        self, 
        session_id: UUID, 
        filter_params: EventFilter
    ) -> PaginatedResponse[Event]:
        """Get events for a specific session with filtering"""
        # Convert UUID to string for v1 service
        session_id_str = str(session_id)
        
        # Convert string event types to V1EventType enum if provided
        event_types = None
        if filter_params.event_types:
            try:
                event_types = [V1EventType(et.upper()) for et in filter_params.event_types]
            except ValueError:
                # If conversion fails, pass None to get all events
                event_types = None
        
        # Format datetime for v1 service if provided
        start_time = filter_params.start_time.isoformat() if filter_params.start_time else None
        end_time = filter_params.end_time.isoformat() if filter_params.end_time else None
        
        v1_events = await self._event_service.get_events(
            session_id=session_id_str,
            event_types=event_types,
            start_time=start_time,
            end_time=end_time,
            limit=filter_params.limit
        )
        
        # Convert to v2 Event model format
        v2_events = [
            Event(
                id=f"{session_id_str}-{i}",  # Generate an ID if v1 doesn't provide one
                session_id=session_id,
                timestamp=e.timestamp,
                event_type=e.type.value.lower(),  # Convert enum to lowercase string
                data={
                    "role": e.role,
                    "content": e.content,
                    "format": e.format,
                    "running": e.running,
                    "active": e.active,
                    "vendor": e.vendor,
                    "tool_calls": e.tool_calls,
                    "tool_results": e.tool_results,
                    "raw": e.raw
                }
            ) for i, e in enumerate(v1_events)
        ]
        
        # Create pagination metadata
        pagination = PaginationMeta(
            page=1,  # Since v1 doesn't support pagination, we're always on page 1
            page_size=filter_params.limit,
            total_items=len(v2_events),
            total_pages=1
        )
        
        return PaginatedResponse(
            status=APIStatus(success=True),
            data=v2_events,
            pagination=pagination
        )
    
    def stream_events(
        self, 
        session_id: UUID, 
        event_types: Optional[List[str]] = None,
        real_time: bool = False,
        speed_factor: float = 1.0
    ) -> AsyncGenerator[str, None]:
        """Stream events for a session, optionally with real-time timing"""
        # Convert UUID to string for v1 service
        session_id_str = str(session_id)
        
        # Convert string event types to V1EventType enum if provided
        v1_event_types = None
        if event_types:
            try:
                v1_event_types = [V1EventType(et.upper()) for et in event_types]
            except ValueError:
                # If conversion fails, pass None to get all events
                v1_event_types = None
        
        # Use the v1 service's stream_events method directly
        # It already returns an AsyncGenerator that we can pass through
        # Note: We're returning the generator itself, not awaiting it
        return self._event_service.stream_events(
            session_id=session_id_str,
            event_types=v1_event_types,
            real_time=real_time,
            speed_factor=speed_factor
        )
    
    def get_replay_status(self, session_id: UUID) -> Optional[ReplayStatus]:
        """Get the current status of a session replay"""
        session_id_str = str(session_id)
        status = self._event_service.get_replay_status(session_id_str)
        if not status:
            return None
        
        # Default values in case they're not in the v1 status
        current_position = datetime.now()
        start_time = datetime.now() - timedelta(hours=1)  # Placeholder
        end_time = datetime.now()  # Placeholder
        
        # Try to extract current position from v1 status
        if status.get("current_index") is not None and status.get("total_events") is not None:
            # Approximate progress based on index
            progress = status.get("current_index", 0) / max(1, status.get("total_events", 1))
            # Use this to estimate a position between start and end time
            start_time = datetime.now() - timedelta(hours=1)  # Placeholder
            end_time = datetime.now()  # Placeholder
            time_diff = (end_time - start_time).total_seconds()
            position_seconds = start_time.timestamp() + (time_diff * progress)
            current_position = datetime.fromtimestamp(position_seconds)
        
        return ReplayStatus(
            session_id=session_id,
            is_playing=status.get("status") == "playing",
            current_position=current_position,
            start_time=start_time,
            end_time=end_time
        )
    
    async def control_replay(
        self, 
        session_id: UUID, 
        control: ReplayControl,
        background_tasks: Optional[BackgroundTasks] = None
    ) -> APIResponse[bool]:
        """Control a session replay (play, pause, seek)"""
        session_id_str = str(session_id)
        
        # Map v2 action to v1 format (they're the same in this case)
        action = control.action  # play, pause, seek
        position = control.position.isoformat() if control.position else None
        
        result = await self._event_service.control_replay(
            session_id=session_id_str,
            action=action,
            position=position,
            background_tasks=background_tasks
        )
        
        return APIResponse(
            status=APIStatus(
                success=result,
                message=f"Replay control '{action}' {'successful' if result else 'failed'}",
                error_code=None if result else "REPLAY_CONTROL_FAILED"
            ),
            data=result
        )