# src/agent_c_api/api/v2/models/response_models.py
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')

class APIStatus(BaseModel):
    """Standard API response status"""
    success: bool = Field(True, description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Optional message about the request")
    error_code: Optional[str] = Field(None, description="Error code if applicable")

class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status information")
    data: Optional[T] = Field(None, description="Response data")

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number", ge=1)
    page_size: int = Field(..., description="Number of items per page", ge=1)
    total_items: int = Field(..., description="Total number of items", ge=0)
    total_pages: int = Field(..., description="Total number of pages", ge=0)

class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status information")
    data: List[T] = Field(default_factory=list, description="Paginated items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")