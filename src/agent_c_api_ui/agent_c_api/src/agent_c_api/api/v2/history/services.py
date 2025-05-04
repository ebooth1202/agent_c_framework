from typing import List, Optional, Dict, Any
from agent_c_api.api.v1.interactions.services.interaction_service import InteractionService
from agent_c_api.api.v1.interactions.interaction_models.interaction_model import InteractionSummary, InteractionDetail as V1InteractionDetail
from .models import HistorySummary, HistoryDetail, PaginationParams, HistoryListResponse

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