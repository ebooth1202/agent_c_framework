from fastapi import APIRouter, Form, UploadFile, File, Depends
import logging

from agent_c_api.api.dependencies import get_agent_manager

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/upload_file")
async def upload_file(
        ui_session_id: str = Form(...),
        file: UploadFile = File(...),
        agent_manager=Depends(get_agent_manager)
):
    """
    A simple file upload endpoint to associate a file with a user's session.
    For example, store images that might later be used in the conversation.
    """
    session_data = agent_manager.get_session_data(ui_session_id)
    if not session_data:
        return {"error": "Invalid session_id"}

    # For demonstration, read the file in memory or store it on disk, etc.
    # If you have an ImageInput or other approach, you can do that here.
    content = await file.read()
    filename = file.filename
    # Store or process the file as needed...
    logger.info(f"Received file '{filename}' for session {ui_session_id} of size {len(content)} bytes")

    return {"status": "File uploaded successfully", "filename": filename}
