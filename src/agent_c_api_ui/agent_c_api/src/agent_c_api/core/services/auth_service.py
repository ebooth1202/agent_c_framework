"""
Authentication service for user management and authentication.

This module provides high-level authentication operations including password
hashing, user authentication, and token management for the Avatar API.
"""

import time
from typing import Optional, Dict, Any, List
from datetime import timedelta
import structlog
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from agent_c.models.chat_history.user import ChatUser
from agent_c_api.core.repositories.auth_repository import AuthRepository
from agent_c_api.core.util.jwt import create_jwt_token, verify_jwt_token
from agent_c_api.models.auth_models import UserCreateRequest, ChatUserResponse, LoginResponse


class AuthService:
    """Service for user authentication and management operations."""
    
    def __init__(self, db_session: AsyncSession):
        """
        Initialize the authentication service.
        
        Args:
            db_session: Database session for repository operations
        """
        self.db_session = db_session
        self.auth_repo = AuthRepository(db_session)
        self.logger = structlog.get_logger(__name__)
        
        # Initialize password hashing context
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def _hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            str: Hashed password
        """
        return self.pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Stored hash to verify against
            
        Returns:
            bool: True if password matches
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    async def create_user(self, user_request: UserCreateRequest) -> ChatUserResponse:
        """
        Create a new user with hashed password.
        
        Args:
            user_request: User creation request data
            
        Returns:
            UserResponse: Created user data (without password)
            
        Raises:
            ValueError: If username already exists
        """
        start_time = time.time()
        
        try:
            self.logger.info(
                "auth_user_creating",
                username=user_request.username,
                has_email=bool(user_request.email),
                roles=user_request.roles
            )
            
            # Hash the password
            password_hash = self._hash_password(user_request.password)
            
            # Create user in database
            user = await self.auth_repo.create_user(
                username=user_request.username,
                password_hash=password_hash,
                email=user_request.email,
                first_name=user_request.first_name,
                last_name=user_request.last_name,
                roles=user_request.roles
            )
            
            duration = time.time() - start_time
            self.logger.info(
                "auth_user_created",
                username=user_request.username,
                user_id=user.user_id,
                duration_ms=round(duration * 1000, 2)
            )
            
            return ChatUserResponse.from_chat_user(user)
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                "auth_user_creation_failed",
                username=user_request.username,
                error=str(e),
                duration_ms=round(duration * 1000, 2)
            )
            raise
    
    async def authenticate_user(self, username: str, password: str) -> Optional[ChatUser]:
        """
        Authenticate a user with username and password.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            Optional[User]: User model if authentication successful, None otherwise
        """
        start_time = time.time()
        
        try:
            self.logger.info(
                "auth_user_authenticating",
                username=username
            )
            
            # Get user from database
            user = await self.auth_repo.get_user_by_username(username)
            if not user:
                duration = time.time() - start_time
                self.logger.warning(
                    "auth_user_not_found",
                    username=username,
                    duration_ms=round(duration * 1000, 2)
                )
                return None
            
            # Check if user is active
            if not user.is_active:
                duration = time.time() - start_time
                self.logger.warning(
                    "auth_user_inactive",
                    username=username,
                    user_id=user.user_id,
                    duration_ms=round(duration * 1000, 2)
                )
                return None
            
            # Verify password
            if not self._verify_password(password, user.password_hash):
                duration = time.time() - start_time
                self.logger.warning(
                    "auth_password_invalid",
                    username=username,
                    user_id=user.user_id,
                    duration_ms=round(duration * 1000, 2)
                )
                return None
            
            # Update last login time
            await self.auth_repo.update_last_login(user.user_id)
            
            duration = time.time() - start_time
            self.logger.info(
                "auth_user_authenticated",
                username=username,
                user_id=user.user_id,
                duration_ms=round(duration * 1000, 2)
            )
            
            return user
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                "auth_authentication_error",
                username=username,
                error=str(e),
                duration_ms=round(duration * 1000, 2)
            )
            raise
    
    async def login(self, username: str, password: str) -> Optional[LoginResponse]:
        """
        Perform user login and return JWT token with user data.
        
        Args:
            username: Username to authenticate
            password: Plain text password
            
        Returns:
            Optional[LoginResponse]: Login response with token and user data, or None if failed
        """
        start_time = time.time()
        
        try:
            # Authenticate user
            user = await self.authenticate_user(username, password)
            if not user:
                return None
            
            # Generate JWT token
            token = create_jwt_token(
                user_id=user.user_id,
                permissions=user.roles,
                time_delta=timedelta(hours=24)  # 24-hour token expiration
            )
            
            # Prepare response
            user_response = ChatUserResponse.from_chat_user(user)
            
            # Basic config payload (will be enhanced in Phase 2)
            config = {
                "user_id": user.user_id,
                "username": user.username,
                "roles": user.roles,
                "session_settings": {
                    "timeout_minutes": 30,
                    "max_connections": 5
                }
            }
            
            duration = time.time() - start_time
            self.logger.info(
                "auth_login_successful",
                username=username,
                user_id=user.user_id,
                token_created=True,
                duration_ms=round(duration * 1000, 2)
            )
            
            return LoginResponse(
                token=token,
                user=user_response,
                config=config
            )
            
        except Exception as e:
            duration = time.time() - start_time
            self.logger.error(
                "auth_login_error",
                username=username,
                error=str(e),
                duration_ms=round(duration * 1000, 2)
            )
            raise
    
    async def get_user_by_token(self, token: str) -> Optional[ChatUser]:
        """
        Get user information from JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Optional[ChatUser]: User model if token is valid, None otherwise
        """
        try:
            # Verify and decode token
            payload = verify_jwt_token(token)
            user_id = payload.get("user_id")
            
            if not user_id:
                self.logger.warning("auth_token_missing_user_id")
                return None
            
            # Get user from database
            user = await self.auth_repo.get_user_by_id(user_id)
            if not user or not user.is_active:
                self.logger.warning(
                    "auth_token_user_invalid",
                    user_id=user_id,
                    user_found=user is not None,
                    user_active=user.is_active if user else False
                )
                return None
            
            # Convert to ChatUser for framework compatibility
            return user.to_chat_user()
            
        except Exception as e:
            self.logger.warning(
                "auth_token_verification_failed",
                error=str(e)
            )
            return None
    
    async def list_users(self) -> List[ChatUserResponse]:
        """
        Get list of all users.
        
        Returns:
            List[UserResponse]: List of all users (without passwords)
        """
        users = await self.auth_repo.list_users()
        return [ChatUserResponse.from_chat_user(user) for user in users]
    
    async def delete_user(self, user_id: str) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id: User ID to delete
            
        Returns:
            bool: True if user was deleted, False if not found
        """
        self.logger.info("auth_user_deleting", user_id=user_id)
        result = await self.auth_repo.delete_user(user_id)
        
        if result:
            self.logger.info("auth_user_deleted", user_id=user_id)
        else:
            self.logger.warning("auth_user_delete_not_found", user_id=user_id)
        
        return result