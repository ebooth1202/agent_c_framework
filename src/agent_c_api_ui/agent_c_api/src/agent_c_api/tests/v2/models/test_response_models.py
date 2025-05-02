# src/agent_c_api/tests/v2/models/test_response_models.py
import pytest
from typing import List
from agent_c_api.api.v2.models.response_models import APIStatus, APIResponse, PaginationMeta, PaginatedResponse

def test_api_status_model():
    """Test that APIStatus model works correctly"""
    # Default instance
    status = APIStatus()
    assert status.success is True
    assert status.message is None
    assert status.error_code is None
    
    # Error instance
    error_status = APIStatus(success=False, message="Not found", error_code="NOT_FOUND")
    assert error_status.success is False
    assert error_status.message == "Not found"
    assert error_status.error_code == "NOT_FOUND"

def test_api_response_model():
    """Test that APIResponse model works correctly"""
    # String data
    response = APIResponse[str](data="test")
    assert response.status.success is True
    assert response.data == "test"
    
    # Dict data
    response = APIResponse[dict](data={"key": "value"})
    assert response.status.success is True
    assert response.data == {"key": "value"}
    
    # Error response
    error_response = APIResponse[str](
        status=APIStatus(success=False, message="Error occurred", error_code="ERROR"),
        data=None
    )
    assert error_response.status.success is False
    assert error_response.status.message == "Error occurred"
    assert error_response.data is None

def test_pagination_meta_model():
    """Test that PaginationMeta model works correctly"""
    meta = PaginationMeta(page=1, page_size=10, total_items=100, total_pages=10)
    assert meta.page == 1
    assert meta.page_size == 10
    assert meta.total_items == 100
    assert meta.total_pages == 10

def test_paginated_response_model():
    """Test that PaginatedResponse model works correctly"""
    response = PaginatedResponse[str](
        data=["item1", "item2", "item3"],
        pagination=PaginationMeta(page=1, page_size=3, total_items=5, total_pages=2)
    )
    assert response.status.success is True
    assert len(response.data) == 3
    assert response.pagination.page == 1
    assert response.pagination.total_pages == 2