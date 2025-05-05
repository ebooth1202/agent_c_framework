# tests/v2/sessions/test_files.py

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4
from fastapi import UploadFile, HTTPException
from fastapi.testclient import TestClient
from datetime import datetime
from pathlib import Path

from agent_c_api.main import app
from agent_c_api.api.v2.models.file_models import FileMeta, FileUploadResponse
from agent_c_api.api.v2.sessions.services import SessionService
from agent_c_api.api.v2.sessions.files import (
    upload_file, list_files, get_file_metadata, download_file, delete_file, get_session_service
)


# Test client
client = TestClient(app)


# Mock file metadata for testing
@pytest.fixture
def mock_file_metadata():
    return MagicMock(
        id="test-file-id",
        filename=str(Path("uploads/test-session/test-file.txt")),
        original_filename="test-file.txt",
        mime_type="text/plain",
        size=100,
        upload_time=datetime.now(),
        processed=True,
        processing_status="complete",
        processing_error=None
    )


# Mock session service
@pytest.fixture
def mock_session_service():
    service = MagicMock(spec=SessionService)
    session_uuid = uuid4()
    
    # Configure get_session to return a session for our test UUID
    def mock_get_session(session_id):
        if session_id == str(session_uuid):
            return {"id": session_id, "name": "Test Session"}
        return None
    
    service.get_session.side_effect = mock_get_session
    service.agent_manager = MagicMock()
    service.agent_manager.get_session_data.return_value = {"agent": MagicMock()}
    
    return service, session_uuid


# Mock file handler
@pytest.fixture
def mock_file_handler(mock_file_metadata):
    with patch("agent_c_api.api.v2.sessions.files.file_handler") as mock_handler:
        mock_handler.save_file = AsyncMock(return_value=mock_file_metadata)
        mock_handler.get_session_files.return_value = [mock_file_metadata]
        mock_handler.get_file_metadata.return_value = mock_file_metadata
        mock_handler.process_file = AsyncMock(return_value=mock_file_metadata)
        mock_handler.session_files = {"test-session-id": [mock_file_metadata]}
        yield mock_handler


# Tests for upload_file endpoint
@pytest.mark.asyncio
async def test_upload_file_success(mock_session_service, mock_file_handler, mock_file_metadata):
    service, session_uuid = mock_session_service
    
    # Create a mock upload file
    mock_upload_file = MagicMock(spec=UploadFile)
    mock_upload_file.filename = "test-file.txt"
    
    # Create mock background tasks
    mock_background_tasks = MagicMock()
    
    # Call the endpoint
    response = await upload_file(
        session_id=session_uuid,
        file=mock_upload_file,
        background_tasks=mock_background_tasks,
        session_service=service
    )
    
    # Verify response
    assert isinstance(response, FileUploadResponse)
    assert response.file_id == mock_file_metadata.id
    assert response.filename == mock_file_metadata.original_filename
    assert response.content_type == mock_file_metadata.mime_type
    assert response.size == mock_file_metadata.size
    
    # Verify background tasks were added
    assert mock_background_tasks.add_task.call_count == 2
    
    # Verify file handler methods were called
    mock_file_handler.save_file.assert_awaited_once_with(
        mock_upload_file, str(session_uuid)
    )


@pytest.mark.asyncio
async def test_upload_file_session_not_found(mock_session_service, mock_file_handler):
    service, _ = mock_session_service
    invalid_uuid = uuid4()
    
    # Create a mock upload file
    mock_upload_file = MagicMock(spec=UploadFile)
    mock_upload_file.filename = "test-file.txt"
    
    # Create mock background tasks
    mock_background_tasks = MagicMock()
    
    # Test with invalid session ID
    with pytest.raises(HTTPException) as exc_info:
        await upload_file(
            session_id=invalid_uuid,
            file=mock_upload_file,
            background_tasks=mock_background_tasks,
            session_service=service
        )
    
    assert exc_info.value.status_code == 404
    assert "Session not found" in exc_info.value.detail


# Tests for list_files endpoint
@pytest.mark.asyncio
async def test_list_files_success(mock_session_service, mock_file_handler, mock_file_metadata):
    service, session_uuid = mock_session_service
    
    # Call the endpoint
    response = await list_files(
        session_id=session_uuid,
        session_service=service
    )
    
    # Verify response
    assert isinstance(response, list)
    assert len(response) == 1
    assert isinstance(response[0], FileMeta)
    assert response[0].id == mock_file_metadata.id
    assert response[0].filename == mock_file_metadata.original_filename
    assert response[0].content_type == mock_file_metadata.mime_type
    assert response[0].size == mock_file_metadata.size
    assert "processed" in response[0].metadata
    
    # Verify file handler methods were called
    mock_file_handler.get_session_files.assert_called_once_with(str(session_uuid))


@pytest.mark.asyncio
async def test_list_files_session_not_found(mock_session_service, mock_file_handler):
    service, _ = mock_session_service
    invalid_uuid = uuid4()
    
    # Test with invalid session ID
    with pytest.raises(HTTPException) as exc_info:
        await list_files(
            session_id=invalid_uuid,
            session_service=service
        )
    
    assert exc_info.value.status_code == 404
    assert "Session not found" in exc_info.value.detail


# Tests for get_file_metadata endpoint
@pytest.mark.asyncio
async def test_get_file_metadata_success(mock_session_service, mock_file_handler, mock_file_metadata):
    service, session_uuid = mock_session_service
    file_id = "test-file-id"
    
    # Call the endpoint
    response = await get_file_metadata(
        session_id=session_uuid,
        file_id=file_id,
        session_service=service
    )
    
    # Verify response
    assert isinstance(response, FileMeta)
    assert response.id == mock_file_metadata.id
    assert response.filename == mock_file_metadata.original_filename
    assert response.content_type == mock_file_metadata.mime_type
    assert response.size == mock_file_metadata.size
    assert "processed" in response.metadata
    
    # Verify file handler methods were called
    mock_file_handler.get_file_metadata.assert_called_once_with(file_id, str(session_uuid))


@pytest.mark.asyncio
async def test_get_file_metadata_session_not_found(mock_session_service, mock_file_handler):
    service, _ = mock_session_service
    invalid_uuid = uuid4()
    file_id = "test-file-id"
    
    # Test with invalid session ID
    with pytest.raises(HTTPException) as exc_info:
        await get_file_metadata(
            session_id=invalid_uuid,
            file_id=file_id,
            session_service=service
        )
    
    assert exc_info.value.status_code == 404
    assert "Session not found" in exc_info.value.detail


@pytest.mark.asyncio
async def test_get_file_metadata_file_not_found(mock_session_service, mock_file_handler):
    service, session_uuid = mock_session_service
    file_id = "nonexistent-file-id"
    
    # Configure file handler to return None for this file ID
    mock_file_handler.get_file_metadata.return_value = None
    
    # Test with invalid file ID
    with pytest.raises(HTTPException) as exc_info:
        await get_file_metadata(
            session_id=session_uuid,
            file_id=file_id,
            session_service=service
        )
    
    assert exc_info.value.status_code == 404
    assert f"File {file_id} not found" in exc_info.value.detail


# Tests for download_file endpoint
@pytest.mark.asyncio
async def test_download_file_success(mock_session_service, mock_file_handler, mock_file_metadata):
    service, session_uuid = mock_session_service
    file_id = "test-file-id"
    
    # Mock FileResponse
    with patch("agent_c_api.api.v2.sessions.files.FileResponse") as mock_file_response:
        mock_file_response.return_value = "file_response_object"
        
        # Call the endpoint
        response = await download_file(
            session_id=session_uuid,
            file_id=file_id,
            session_service=service
        )
        
        # Verify response
        assert response == "file_response_object"
        
        # Verify FileResponse was called correctly
        mock_file_response.assert_called_once_with(
            path=mock_file_metadata.filename,
            filename=mock_file_metadata.original_filename,
            media_type=mock_file_metadata.mime_type
        )
        
        # Verify file handler methods were called
        mock_file_handler.get_file_metadata.assert_called_once_with(file_id, str(session_uuid))


@pytest.mark.asyncio
async def test_download_file_file_not_found(mock_session_service, mock_file_handler):
    service, session_uuid = mock_session_service
    file_id = "nonexistent-file-id"
    
    # Configure file handler to return None for this file ID
    mock_file_handler.get_file_metadata.return_value = None
    
    # Test with invalid file ID
    with pytest.raises(HTTPException) as exc_info:
        await download_file(
            session_id=session_uuid,
            file_id=file_id,
            session_service=service
        )
    
    assert exc_info.value.status_code == 404
    assert f"File {file_id} not found" in exc_info.value.detail


# Tests for delete_file endpoint
@pytest.mark.asyncio
async def test_delete_file_success(mock_session_service, mock_file_handler, mock_file_metadata):
    service, session_uuid = mock_session_service
    file_id = "test-file-id"
    
    # Mock os.remove
    with patch("os.remove") as mock_remove:
        # Call the endpoint
        response = await delete_file(
            session_id=session_uuid,
            file_id=file_id,
            session_service=service
        )
        
        # Verify response is None (204 No Content)
        assert response is None
        
        # Verify os.remove was called
        mock_remove.assert_called_once_with(mock_file_metadata.filename)
        
        # Verify file handler methods were called
        mock_file_handler.get_file_metadata.assert_called_once_with(file_id, str(session_uuid))


@pytest.mark.asyncio
async def test_delete_file_file_not_found(mock_session_service, mock_file_handler):
    service, session_uuid = mock_session_service
    file_id = "nonexistent-file-id"
    
    # Configure file handler to return None for this file ID
    mock_file_handler.get_file_metadata.return_value = None
    
    # Test with invalid file ID
    with pytest.raises(HTTPException) as exc_info:
        await delete_file(
            session_id=session_uuid,
            file_id=file_id,
            session_service=service
        )
    
    assert exc_info.value.status_code == 404
    assert f"File {file_id} not found" in exc_info.value.detail