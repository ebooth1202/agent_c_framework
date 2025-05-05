from fastapi import APIRouter, Depends, HTTPException, Query, Path
from fastapi_versioning import version
from typing import Optional
from uuid import UUID

from agent_c_api.api.v2.models.session_models import SessionCreate, SessionDetail, SessionListResponse, SessionUpdate
from .services import SessionService


def get_session_service():
    """Dependency to get the session service"""
    return SessionService()


router = APIRouter(
    tags=["sessions"], 
    prefix="/sessions",
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Invalid session parameter"
                    }
                }
            }
        },
        404: {
            "description": "Session Not Found",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Session 550e8400-e29b-41d4-a716-446655440000 not found"
                    }
                }
            }
        },
        500: {
            "description": "Internal Server Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Failed to process session request"
                    }
                }
            }
        }
    }
)


@router.post("", 
         response_model=SessionDetail, 
         status_code=201,
         summary="Create a new agent session",
         description="Creates a new session with the specified model, persona, and configuration parameters")
@version(2)
async def create_session(
    session_data: SessionCreate,
    service: SessionService = Depends(get_session_service)
):
    """
    Create a new agent session.
    
    Creates a new AI agent session with the specified model, persona, and configuration parameters.
    Returns the detailed session information including the generated session ID.
    
    Args:
        session_data: Parameters for creating the session including model ID, persona, and configuration
        service: Session service dependency injection
        
    Returns:
        SessionDetail: Detailed information about the created session
        
    Raises:
        HTTPException: 400 if parameters are invalid
        HTTPException: 500 if session creation fails
        
    Example:
        ```python
        import requests
        
        session_data = {
            "model_id": "gpt-4",
            "persona_id": "programmer",
            "name": "Code Review Session",
            "temperature": 0.7,
            "tools": ["search", "code_analysis"]
        }
        
        response = requests.post(
            "https://your-agent-c-instance.com/api/v2/sessions",
            json=session_data
        )
        
        if response.status_code == 201:
            session = response.json()
            print(f"Created session {session['id']} named {session['name']}")
        ```
    """
    return await service.create_session(session_data)


@router.get("", 
         response_model=SessionListResponse,
         summary="List all sessions",
         description="Retrieves a paginated list of all active sessions with support for pagination")
@version(2)
async def list_sessions(
    limit: int = Query(10, ge=1, le=100, description="Maximum number of sessions to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip for pagination"),
    service: SessionService = Depends(get_session_service)
):
    """
    List all sessions.
    
    Retrieves a paginated list of all active sessions. The response includes
    basic information about each session and pagination details.
    
    Args:
        limit: Maximum number of sessions to return (1-100)
        offset: Number of sessions to skip for pagination
        service: Session service dependency injection
        
    Returns:
        SessionListResponse: Paginated list of sessions with total count
        
    Example:
        ```python
        import requests
        
        # Get first page of sessions (10 per page)
        response = requests.get(
            "https://your-agent-c-instance.com/api/v2/sessions",
            params={"limit": 10, "offset": 0}
        )
        
        if response.status_code == 200:
            result = response.json()
            sessions = result["items"]
            total = result["total"]
            
            print(f"Showing {len(sessions)} of {total} total sessions")
            
            # Get next page if there are more sessions
            if total > 10:
                next_page = requests.get(
                    "https://your-agent-c-instance.com/api/v2/sessions",
                    params={"limit": 10, "offset": 10}
                )
        ```
    """
    return await service.get_sessions(limit, offset)


@router.get("/{session_id}", 
         response_model=SessionDetail,
         summary="Get session details",
         description="Retrieves comprehensive information about a specific session including its configuration")
@version(2)
async def get_session(
    session_id: UUID = Path(..., description="Unique identifier of the session to retrieve"),
    service: SessionService = Depends(get_session_service)
):
    """
    Get session details.
    
    Retrieves detailed information about a specific session identified by its UUID.
    The response includes all session configuration parameters, tools, and metadata.
    
    Args:
        session_id: UUID of the session to retrieve
        service: Session service dependency injection
        
    Returns:
        SessionDetail: Comprehensive information about the session
        
    Raises:
        HTTPException: 404 if the session doesn't exist
        
    Example:
        ```python
        import requests
        from uuid import UUID
        
        session_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        response = requests.get(
            f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}"
        )
        
        if response.status_code == 200:
            session = response.json()
            print(f"Session {session['name']} is using model {session['model_id']}")
            print(f"Last activity: {session['last_activity']}")
        elif response.status_code == 404:
            print("Session not found")
        ```
    """
    session = await service.get_session(str(session_id))
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    return session


@router.patch("/{session_id}", 
           response_model=SessionDetail,
           summary="Update session properties",
           description="Updates one or more properties of an existing session, such as name, persona, or model parameters")
@version(2)
async def update_session(
    session_id: UUID = Path(..., description="Unique identifier of the session to update"),
    update_data: SessionUpdate = Body(..., description="Session properties to update"),
    service: SessionService = Depends(get_session_service)
):
    """
    Update session properties.
    
    Updates one or more properties of a specific session. Only the properties included
    in the request body will be updated; others will remain unchanged.
    
    Args:
        session_id: UUID of the session to update
        update_data: Session properties to update, with null/None values ignored
        service: Session service dependency injection
        
    Returns:
        SessionDetail: Updated session information reflecting the changes
        
    Raises:
        HTTPException: 404 if the session doesn't exist
        HTTPException: 400 if update parameters are invalid
        HTTPException: 500 if update operation fails
        
    Example:
        ```python
        import requests
        from uuid import UUID
        
        session_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        
        # Update the session name and temperature
        update_data = {
            "name": "Refactoring Session",
            "temperature": 0.8
        }
        
        response = requests.patch(
            f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}",
            json=update_data
        )
        
        if response.status_code == 200:
            updated_session = response.json()
            print(f"Session renamed to {updated_session['name']}")
            print(f"Temperature updated to {updated_session['temperature']}")
        ```
    """
    try:
        return await service.update_session(str(session_id), update_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")


@router.delete("/{session_id}", 
           status_code=204,
           summary="Delete a session",
           description="Permanently removes a session and releases its resources")
@version(2)
async def delete_session(
    session_id: UUID = Path(..., description="Unique identifier of the session to delete"),
    service: SessionService = Depends(get_session_service)
):
    """
    Delete a session.
    
    Permanently removes a session and releases all associated resources.
    This operation cannot be undone, and all session data will be lost.
    
    Args:
        session_id: UUID of the session to delete
        service: Session service dependency injection
        
    Returns:
        None: Returns no content on success (204 status code)
        
    Raises:
        HTTPException: 404 if the session doesn't exist
        HTTPException: 500 if deletion fails
        
    Example:
        ```python
        import requests
        from uuid import UUID
        
        session_id = UUID("550e8400-e29b-41d4-a716-446655440000")
        
        response = requests.delete(
            f"https://your-agent-c-instance.com/api/v2/sessions/{session_id}"
        )
        
        if response.status_code == 204:
            print("Session successfully deleted")
        elif response.status_code == 404:
            print("Session not found")
        else:
            print(f"Error: {response.text}")
        ```
    """
    session = await service.get_session(str(session_id))
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    
    success = await service.delete_session(str(session_id))
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete session")