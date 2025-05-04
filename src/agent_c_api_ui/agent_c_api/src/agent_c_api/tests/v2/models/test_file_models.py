# src/agent_c_api/tests/v2/models/test_file_models.py
import pytest
from datetime import datetime
from uuid import UUID, uuid4
from agent_c_api.api.v2.models.file_models import (
    FileMeta, FileUploadResponse
)

def test_file_meta():
    session_id = uuid4()
    now = datetime.now()
    
    # Test with minimal fields
    file_meta = FileMeta(
        id="file-123",
        filename="document.pdf",
        content_type="application/pdf",
        size=12345,
        uploaded_at=now,
        session_id=session_id
    )
    assert file_meta.id == "file-123"
    assert file_meta.filename == "document.pdf"
    assert file_meta.content_type == "application/pdf"
    assert file_meta.size == 12345
    assert file_meta.uploaded_at == now
    assert file_meta.session_id == session_id
    assert file_meta.metadata == {}
    
    # Test with all fields
    file_meta = FileMeta(
        id="file-456",
        filename="image.jpg",
        content_type="image/jpeg",
        size=54321,
        uploaded_at=now,
        session_id=session_id,
        metadata={"width": 1920, "height": 1080}
    )
    assert file_meta.id == "file-456"
    assert file_meta.filename == "image.jpg"
    assert file_meta.content_type == "image/jpeg"
    assert file_meta.size == 54321
    assert file_meta.uploaded_at == now
    assert file_meta.session_id == session_id
    assert file_meta.metadata == {"width": 1920, "height": 1080}

def test_file_upload_response():
    # Test file upload response
    response = FileUploadResponse(
        file_id="file-123",
        filename="document.pdf",
        content_type="application/pdf",
        size=12345
    )
    assert response.file_id == "file-123"
    assert response.filename == "document.pdf"
    assert response.content_type == "application/pdf"
    assert response.size == 12345
    
    # Test with missing required field
    with pytest.raises(ValueError):
        FileUploadResponse(
            file_id="file-123",
            # filename is missing
            content_type="application/pdf",
            size=12345
        )