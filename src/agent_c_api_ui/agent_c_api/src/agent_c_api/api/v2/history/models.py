from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Dict, Any, Optional

class HistorySummary(BaseModel):
    """Summary of a recorded session history"""
    id: str = Field(..., description="Session ID")
    start_time: datetime = Field(..., description="When the session started")
    end_time: Optional[datetime] = Field(None, description="When the session ended")
    duration_seconds: Optional[float] = Field(None, description="Session duration in seconds")
    event_count: int = Field(..., description="Number of events in the session")
    file_count: int = Field(..., description="Number of log files for the session")

class HistoryDetail(HistorySummary):
    """Detailed information about a session history"""
    files: List[str] = Field(..., description="List of log files for the session")
    event_types: Dict[str, int] = Field(..., description="Count of each event type")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional session metadata")
    user_id: Optional[str] = Field(None, description="User ID associated with the session")
    has_thinking: bool = Field(False, description="Whether the session includes thinking events")
    tool_calls: List[str] = Field([], description="List of tools used in the session")

class PaginationParams(BaseModel):
    """Parameters for pagination"""
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results to return")
    offset: int = Field(0, ge=0, description="Number of results to skip")
    sort_by: str = Field("start_time", description="Field to sort by")
    sort_order: str = Field("desc", description="Sort order (asc or desc)")

class HistoryListResponse(BaseModel):
    """Response for listing session histories"""
    items: List[HistorySummary] = Field(..., description="List of session histories")
    total: int = Field(..., description="Total number of session histories")
    limit: int = Field(..., description="Maximum number of results returned")
    offset: int = Field(..., description="Number of results skipped")