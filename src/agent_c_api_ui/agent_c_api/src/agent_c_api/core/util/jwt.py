from typing import Optional

from fastapi import WebSocket, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta, UTC
import os

# JWT Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY environment variable is required")
ALGORITHM = "HS256"

security = HTTPBearer()


def create_jwt_token(user_id: str, permissions: list = None, time_delta: Optional[timedelta] = None ) -> str:
    """Create a JWT token for a user"""
    if time_delta is None:
        time_delta = timedelta(hours=24)
    now = datetime.now(UTC)  # Python 3.11+ has UTC constant
    payload = {
        "sub": user_id,
        "permissions": permissions or [],
        "exp": now + time_delta,
        "iat": now,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_jwt_token(token: str) -> dict:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {
            "user_id": user_id,
            "permissions": payload.get("permissions", []),
            "exp": payload.get("exp")
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# WebSocket JWT validation
async def validate_websocket_jwt(websocket: WebSocket) -> dict:
    """Extract and validate JWT from WebSocket headers"""
    # Get Authorization header
    auth_header = None
    for name, value in websocket.headers.items():
        if name.lower() == "authorization":
            auth_header = value
            break

    if not auth_header or not auth_header.startswith("Bearer "):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing or invalid authorization header")
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = auth_header[7:]  # Remove "Bearer " prefix
    return verify_jwt_token(token)
