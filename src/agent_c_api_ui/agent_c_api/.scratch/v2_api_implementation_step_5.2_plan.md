# v2 API Implementation Step 5.2: File Management

## Summary

**What**: Implement file management endpoints within sessions

**How**:
- Create RESTful endpoints for uploading, listing, downloading, and deleting files
- Leverage existing file handling logic in FileHandler
- Ensure proper multipart/form-data handling
- Implement proper error handling and validation

**Why**: Provides file attachment capabilities for multimodal interactions, allowing users to share files with the agent

## Detailed Design

### 1. Implementation Components

#### 1.1. New Files to Create

- `//api/src/agent_c_api/api/v2/sessions/files.py`: Main module for file management endpoints
- `//api/tests/v2/sessions/test_files.py`: Tests for file endpoints

#### 1.2. Existing Files to Update

- `//api/src/agent_c_api/api/v2/sessions/__init__.py`: Update to include the new files router

### 2. Endpoint Specifications

#### 2.1. Upload File

```python
@router.post(
    "/{session_id}/files",
    response_model=FileUploadResponse,
    status_code=201,
    summary="Upload a file to a session",
    description="Upload a file to be used in a specific session"
)
async def upload_file(
    session_id: UUID,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session_service: SessionService = Depends(get_session_service)
) -> FileUploadResponse:
    # Implementation
```

- **Path Parameters**:
  - `session_id`: The UUID of the session
- **Form Data**:
  - `file`: The file to upload (multipart/form-data)
- **Response**:
  - `201 Created` with file metadata if successful
  - `404 Not Found` if session doesn't exist
  - `500 Internal Server Error` if upload fails
- **Logic**:
  - Verify session exists
  - Save file using FileHandler
  - Process file in background for text extraction
  - Return file metadata

#### 2.2. List Session Files

```python
@router.get(
    "/{session_id}/files",
    response_model=List[FileMeta],
    summary="List files in a session",
    description="Retrieve all files associated with a specific session"
)
async def list_files(
    session_id: UUID,
    session_service: SessionService = Depends(get_session_service)
) -> List[FileMeta]:
    # Implementation
```

- **Path Parameters**:
  - `session_id`: The UUID of the session
- **Response**:
  - `200 OK` with list of file metadata
  - `404 Not Found` if session doesn't exist
- **Logic**:
  - Verify session exists
  - Retrieve files using FileHandler
  - Return list of file metadata

#### 2.3. Get File Metadata

```python
@router.get(
    "/{session_id}/files/{file_id}",
    response_model=FileMeta,
    summary="Get file metadata",
    description="Retrieve metadata for a specific file"
)
async def get_file_metadata(
    session_id: UUID,
    file_id: str,
    session_service: SessionService = Depends(get_session_service)
) -> FileMeta:
    # Implementation
```

- **Path Parameters**:
  - `session_id`: The UUID of the session
  - `file_id`: The ID of the file
- **Response**:
  - `200 OK` with file metadata
  - `404 Not Found` if session or file doesn't exist
- **Logic**:
  - Verify session exists
  - Retrieve file metadata using FileHandler
  - Return file metadata

#### 2.4. Download File Content

```python
@router.get(
    "/{session_id}/files/{file_id}/content",
    summary="Download file content",
    description="Download the content of a specific file"
)
async def download_file(
    session_id: UUID,
    file_id: str,
    session_service: SessionService = Depends(get_session_service)
) -> FileResponse:
    # Implementation
```

- **Path Parameters**:
  - `session_id`: The UUID of the session
  - `file_id`: The ID of the file
- **Response**:
  - FileResponse with appropriate content-type headers
  - `404 Not Found` if session or file doesn't exist
- **Logic**:
  - Verify session exists
  - Retrieve file metadata using FileHandler
  - Return file content as FileResponse

#### 2.5. Delete File

```python
@router.delete(
    "/{session_id}/files/{file_id}",
    status_code=204,
    summary="Delete a file",
    description="Remove a file from a session"
)
async def delete_file(
    session_id: UUID,
    file_id: str,
    session_service: SessionService = Depends(get_session_service)
) -> None:
    # Implementation
```

- **Path Parameters**:
  - `session_id`: The UUID of the session
  - `file_id`: The ID of the file
- **Response**:
  - `204 No Content` if successful
  - `404 Not Found` if session or file doesn't exist
- **Logic**:
  - Verify session exists
  - Verify file exists
  - Delete file using FileHandler

### 3. Implementation Details

#### 3.1 Service Methods

To maintain consistency with other endpoints, we'll add file-related methods to the `SessionService` class:

```python
# In services.py
async def upload_file(self, session_id: UUID, file: UploadFile) -> FileMetadata:
    """Upload a file for a session"""
    # Implementation

async def get_session_files(self, session_id: UUID) -> List[FileMetadata]:
    """Get all files for a session"""
    # Implementation

async def get_file_metadata(self, session_id: UUID, file_id: str) -> Optional[FileMetadata]:
    """Get metadata for a specific file"""
    # Implementation

async def get_file_path(self, session_id: UUID, file_id: str) -> Optional[Path]:
    """Get the file path for a specific file"""
    # Implementation

async def delete_file(self, session_id: UUID, file_id: str) -> bool:
    """Delete a specific file"""
    # Implementation
```

#### 3.2 Model Updates

Current v2 file models seem sufficient, but we'll ensure they're properly used:

```python
# From existing models/file_models.py
class FileMeta(BaseModel):
    """Metadata about an uploaded file"""
    id: str = Field(..., description="File ID")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME content type")
    size: int = Field(..., description="File size in bytes")
    uploaded_at: datetime = Field(..., description="Upload timestamp")
    session_id: UUID = Field(..., description="Session ID the file belongs to")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class FileUploadResponse(BaseModel):
    """Response after file upload"""
    file_id: str = Field(..., description="File ID")
    filename: str = Field(..., description="Original filename")
    content_type: str = Field(..., description="MIME content type")
    size: int = Field(..., description="File size in bytes")
```

#### 3.3 Background Tasks

We'll use FastAPI's background tasks for:

1. Processing files for text extraction
2. Periodic cleanup of expired files

### 4. Testing Strategy

#### 4.1 Unit Tests

For the service layer:

- Test file upload with valid and invalid session IDs
- Test file listing with valid and invalid session IDs
- Test file metadata retrieval with valid and invalid file/session IDs
- Test file deletion with valid and invalid file/session IDs

#### 4.2 API Tests

For the API endpoints:

- Test file upload endpoint with valid and invalid files
- Test file listing endpoint
- Test file metadata endpoint
- Test file content download endpoint
- Test file deletion endpoint
- Test error handling for all endpoints

#### 4.3 Integration Tests

- Test file upload and then using the file in chat
- Test file lifecycle (upload, list, download, delete)

### 5. Implementation Steps

1. Add file-related methods to `SessionService`
2. Create the `files.py` module with all endpoints
3. Update `__init__.py` to include the new router
4. Create test file and implement tests
5. Verify all endpoints function correctly
6. Ensure proper error handling throughout

## Backwards Compatibility

This implementation maintains compatibility with the existing FileHandler class while providing a more RESTful API interface. The v1 API's existing functionality will remain unchanged.

## Dependencies

- FastAPI for API framework
- FileHandler from core module for file operations
- SessionService for session verification
- Pydantic models for request/response validation

## Conclusion

This plan outlines a comprehensive implementation of file management endpoints for the v2 API. By leveraging the existing FileHandler functionality while providing a clean, RESTful interface, we can offer robust file management capabilities within the agent sessions.