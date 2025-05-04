# src/agent_c_api/api/v2/models/response_models.py
from typing import Any, Dict, Generic, List, Optional, TypeVar, Union
from pydantic import BaseModel, Field

T = TypeVar('T')

class APIStatus(BaseModel):
    """Standard API response status"""
    success: bool = Field(True, description="Whether the request was successful")
    message: Optional[str] = Field(None, description="Optional message about the request")
    error_code: Optional[str] = Field(None, description="Error code if applicable")

class APIResponse(Generic[T], BaseModel):
    """Standard API response wrapper"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status information")
    data: Optional[T] = Field(None, description="Response data")

class PaginationMeta(BaseModel):
    """Pagination metadata"""
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_items: int = Field(..., description="Total number of items")
    total_pages: int = Field(..., description="Total number of pages")

class PaginatedResponse(Generic[T], BaseModel):
    """Paginated response wrapper"""
    status: APIStatus = Field(default_factory=APIStatus, description="Response status information")
    data: List[T] = Field(default_factory=list, description="Paginated items")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")