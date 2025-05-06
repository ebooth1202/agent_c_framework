from typing import List, Optional, Dict, Any, AsyncGenerator
from datetime import datetime, timedelta
from uuid import UUID
from fastapi import BackgroundTasks

from agent_c.models.events import MessageEvent, InteractionEvent, ToolCallEvent, CompletionEvent, TextDeltaEvent, SessionEvent
from agent_c.models.events.chat import ThoughtDeltaEvent, HistoryEvent
from agent_c_api.api.v1.interactions.services.interaction_service import InteractionService
from agent_c_api.api.v1.interactions.interaction_models.interaction_model import InteractionSummary, InteractionDetail as V1InteractionDetail
from agent_c_api.api.v1.interactions.services.event_service import EventService as V1EventService
from agent_c_api.api.v1.interactions.interaction_models.event_model import EventType as V1EventType

from agent_c_api.api.v2.models.response_models import APIResponse, PaginatedResponse, PaginationMeta, APIStatus
from agent_c_api.api.v2.models.history_models import (
    StoredEvent, HistoryEventUnion, EventFilter, ReplayStatus, ReplayControl,
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
    ) -> PaginatedResponse[StoredEvent]:
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
        
        # Convert to core event models and wrap in StoredEvent
        stored_events = []
        for i, e in enumerate(v1_events):
            # Determine the core event type based on the V1 event type
            event_type = e.type.value.lower()
            
            # Common event data
            event_data = {
                "session_id": session_id_str,
                "role": e.role,
                "type": event_type
            }
            
            # Create the appropriate core event type based on the event_type
            if event_type == "message":
                core_event = MessageEvent(
                    content=e.content,
                    format=e.format,
                    **event_data
                )
            elif event_type == "interaction":
                core_event = InteractionEvent(
                    started=e.running,
                    id=str(i),  # Using index as placeholder if not available
                    **event_data
                )
            elif event_type == "tool_call":
                core_event = ToolCallEvent(
                    active=e.active,
                    vendor=e.vendor or "unknown", 
                    tool_calls=e.tool_calls or [],
                    tool_results=e.tool_results,
                    **event_data
                )
            elif event_type == "completion":
                core_event = CompletionEvent(
                    running=e.running,
                    completion_options=e.raw or {},
                    **event_data
                )
            elif event_type == "text_delta":
                core_event = TextDeltaEvent(
                    content=e.content,
                    format=e.format,
                    **event_data
                )
            elif event_type == "thought_delta":
                core_event = ThoughtDeltaEvent(
                    content=e.content,
                    format=e.format,
                    **event_data
                )
            elif event_type == "history":
                core_event = HistoryEvent(
                    messages=e.raw.get("messages", []) if e.raw else [],
                    **event_data
                )
            else:
                # Default to a generic SessionEvent for unknown types
                core_event = SessionEvent(
                    type=event_type,
                    **event_data
                )
            
            # Wrap the core event in a StoredEvent
            stored_events.append(
                StoredEvent(
                    id=f"{session_id_str}-{i}",
                    event=core_event,
                    timestamp=e.timestamp
                )
            )
        
        # Create pagination metadata
        pagination = PaginationMeta(
            page=1,  # Since v1 doesn't support pagination, we're always on page 1
            page_size=filter_params.limit,
            total_items=len(stored_events),
            total_pages=1
        )
        
        return PaginatedResponse(
            status=APIStatus(success=True),
            data=stored_events,
            pagination=pagination
        )
    
    def stream_events(
        self, 
        session_id: UUID, 
        event_types: Optional[List[str]] = None,
        real_time: bool = False,
        speed_factor: float = 1.0
    ):
        """
        Stream events for a session, optionally with real-time timing.
        Returns core event models directly.
        """
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
        
        # Use the v1 service's stream_events method, but transform the events to core models
        # This is an async generator that yields events on the fly
        async def event_transformer():
            async for event_json in self._event_service.stream_events(
                session_id=session_id_str,
                event_types=v1_event_types,
                real_time=real_time,
                speed_factor=speed_factor
            ):
                # Parse the event JSON and convert to the appropriate core event type
                # This would normally deserialize the JSON into the appropriate event type
                # For now, we'll return the raw event as a BaseEvent, which clients can parse
                # In a real implementation, this would convert to the proper event type
                # based on the 'type' field
                
                # For now, we'll simply pass through the event as the V1 API already uses
                # the core event models under the hood. In a real implementation with actual
                # type conversion, this would be more complex.
                yield event_json
                
        return event_transformer()
    
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