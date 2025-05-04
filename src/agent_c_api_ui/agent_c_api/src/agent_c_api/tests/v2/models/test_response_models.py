# src/agent_c_api/tests/v2/models/test_response_models.py
import pytest
from typing import List
from pydantic import BaseModel
from agent_c_api.api.v2.models.response_models import (
    APIStatus, APIResponse, PaginationMeta, PaginatedResponse
)

def test_api_status_model():
    # Test default values
    status = APIStatus()
    assert status.success is True
    assert status.message is None
    assert status.error_code is None
    
    # Test with custom values
    status = APIStatus(success=False, message="An error occurred", error_code="VALIDATION_ERROR")
    assert status.success is False
    assert status.message == "An error occurred"
    assert status.error_code == "VALIDATION_ERROR"

def test_api_response_model():
    # Simple data model for testing
    class TestData(BaseModel):
        name: str
        value: int
    
    # Test with default status
    response = APIResponse[TestData](data=TestData(name="test", value=42))
    assert response.status.success is True
    assert response.data.name == "test"
    assert response.data.value == 42
    
    # Test with custom status
    status = APIStatus(success=False, message="Error", error_code="TEST_ERROR")
    response = APIResponse[TestData](status=status, data=None)
    assert response.status.success is False
    assert response.status.message == "Error"
    assert response.data is None

def test_pagination_meta_model():
    # Test valid pagination metadata
    meta = PaginationMeta(page=2, page_size=10, total_items=25, total_pages=3)
    assert meta.page == 2
    assert meta.page_size == 10
    assert meta.total_items == 25
    assert meta.total_pages == 3

def test_paginated_response_model():
    # Test with list of strings
    pagination = PaginationMeta(page=1, page_size=2, total_items=3, total_pages=2)
    response = PaginatedResponse[str](
        data=["item1", "item2"],
        pagination=pagination
    )
    
    assert response.status.success is True
    assert response.data == ["item1", "item2"]
    assert response.pagination.page == 1
    assert response.pagination.total_items == 3