# src/agent_c_api/api/v2/sessions/files.py
import logging
from typing import List
from uuid import UUID


from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from fastapi.responses import FileResponse

from agent_c_api.api.v2.models.file_models import FileMeta, FileUploadResponse
from .services import SessionService, get_session_service
from agent_c_api.core.file_handler import FileHandler


# Setup router
router = APIRouter(prefix="/sessions")

# Initialize logger
logger = logging.getLogger(__name__)


# Create a shared file handler
file_handler = FileHandler(base_dir="uploads", retention_days=7)

# Background tasks
def cleanup_expired_files():
    """Background task to clean up expired files"""
    try:
        count = file_handler.cleanup_expired_files()
        if count > 0:
            logger.info(f"Cleaned up {count} expired files")
    except Exception as e:
        logger.error(f"Error cleaning up expired files: {str(e)}")

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
    """Upload a file to a session
    
    Args:
        session_id: The UUID of the session
        file: The file to upload
        background_tasks: FastAPI background tasks
        session_service: Session service dependency
        
    Returns:
        FileUploadResponse: Information about the uploaded file
        
    Raises:
        HTTPException: If session not found or upload fails
    """
    # Schedule expired files cleanup
    background_tasks.add_task(cleanup_expired_files)
    
    # Get session and verify it exists
    session = session_service.get_session(str(session_id))
    if not session:
        logger.error(f"No session found for session_id: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Save the file
        metadata = await file_handler.save_file(file, str(session_id))
        
        # Set the file handler on the agent if needed
        session_data = session_service.agent_manager.get_session_data(str(session_id))
        agent = session_data.get("agent")
        if agent and not hasattr(agent, "file_handler"):
            agent.file_handler = file_handler
        elif agent and agent.file_handler is None:
            agent.file_handler = file_handler
        
        # Process the file in the background for text extraction
        background_tasks.add_task(file_handler.process_file, metadata.id, str(session_id))
        
        # Return response
        return FileUploadResponse(
            file_id=metadata.id,
            filename=metadata.original_filename,
            content_type=metadata.mime_type,
            size=metadata.size
        )
    except Exception as e:
        logger.error(f"Error uploading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

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
    """List all files for a session
    
    Args:
        session_id: The UUID of the session
        session_service: Session service dependency
        
    Returns:
        List[FileMeta]: List of file metadata
        
    Raises:
        HTTPException: If session not found
    """
    # Get session and verify it exists
    session = session_service.get_session(str(session_id))
    if not session:
        logger.error(f"No session found for session_id: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get files for the session
        files = file_handler.get_session_files(str(session_id))
        
        # Convert to FileMeta models
        return [
            FileMeta(
                id=f.id,
                filename=f.original_filename,
                content_type=f.mime_type,
                size=f.size,
                uploaded_at=f.upload_time,
                session_id=session_id,
                metadata={
                    "processed": f.processed,
                    "processing_status": f.processing_status,
                    "processing_error": f.processing_error
                }
            )
            for f in files
        ]
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error listing files: {str(e)}")

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
    """Get metadata for a specific file
    
    Args:
        session_id: The UUID of the session
        file_id: The ID of the file
        session_service: Session service dependency
        
    Returns:
        FileMeta: File metadata
        
    Raises:
        HTTPException: If session or file not found
    """
    # Get session and verify it exists
    session = session_service.get_session(str(session_id))
    if not session:
        logger.error(f"No session found for session_id: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get file metadata
        metadata = file_handler.get_file_metadata(file_id, str(session_id))
        if not metadata:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        
        # Return as FileMeta model
        return FileMeta(
            id=metadata.id,
            filename=metadata.original_filename,
            content_type=metadata.mime_type,
            size=metadata.size,
            uploaded_at=metadata.upload_time,
            session_id=session_id,
            metadata={
                "processed": metadata.processed,
                "processing_status": metadata.processing_status,
                "processing_error": metadata.processing_error
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving file metadata: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving file metadata: {str(e)}")

@router.get(
    "/{session_id}/files/{file_id}/content",
    summary="Download file content",
    description="Download the content of a specific file"
)
async def download_file(
    session_id: UUID,
    file_id: str,
    session_service: SessionService = Depends(get_session_service)
):
    """Download a file's content
    
    Args:
        session_id: The UUID of the session
        file_id: The ID of the file
        session_service: Session service dependency
        
    Returns:
        FileResponse: The file content with appropriate headers
        
    Raises:
        HTTPException: If session or file not found
    """
    # Get session and verify it exists
    session = session_service.get_session(str(session_id))
    if not session:
        logger.error(f"No session found for session_id: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get file metadata
        metadata = file_handler.get_file_metadata(file_id, str(session_id))
        if not metadata:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        
        # Return file content
        return FileResponse(
            path=metadata.filename,
            filename=metadata.original_filename,
            media_type=metadata.mime_type
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error downloading file: {str(e)}")

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
    """Delete a file from a session
    
    Args:
        session_id: The UUID of the session
        file_id: The ID of the file
        session_service: Session service dependency
        
    Returns:
        None
        
    Raises:
        HTTPException: If session or file not found
    """
    # Get session and verify it exists
    session = session_service.get_session(str(session_id))
    if not session:
        logger.error(f"No session found for session_id: {session_id}")
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        # Get file metadata
        metadata = file_handler.get_file_metadata(file_id, str(session_id))
        if not metadata:
            raise HTTPException(status_code=404, detail=f"File {file_id} not found")
        
        # Delete the file
        try:
            import os
            os.remove(metadata.filename)
            
            # Update the session files
            session_files = file_handler.session_files.get(str(session_id), [])
            file_handler.session_files[str(session_id)] = [
                f for f in session_files if f.id != file_id
            ]
            
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error deleting file: {str(e)}")