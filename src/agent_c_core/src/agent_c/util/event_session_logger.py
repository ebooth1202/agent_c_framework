"""
EventSessionLogger - Gateway Pattern Implementation

This module implements the EventSessionLogger class which acts as a gateway between
agent events and transport layers, providing local logging with optional downstream
forwarding for future decoupling to queues, message buses, etc.
"""

import asyncio
import json
import logging
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional, Dict, Union, Awaitable
from agent_c.models.events.session_event import SessionEvent, SemiSessionEvent
from .transport_exceptions import (
    EventSessionLoggerError, LocalLoggingError, TransportError, 
    TransportConnectionError, TransportTimeoutError, SerializationError
)
from .transports import TransportInterface








class EventSessionLogger:
    """
    Gateway pattern implementation for event-driven session logging.
    
    Acts as a bridge between agent events and transport layers, providing:
    - Local logging with session-based file organization
    - Optional downstream forwarding (callback or transport)
    - Error isolation between logging and transport concerns
    - Backward compatibility with current SessionLogger behavior
    """
    
    def __init__(
        self,
        log_base_dir: Union[str, Path] = None,
        downstream_callback: Optional[Callable[[Any], Awaitable[None]]] = None,
        downstream_transport: Optional[TransportInterface] = None,
        include_system_prompt: bool = True,
        log_format: str = "jsonl",
        file_naming_pattern: str = "%Y%m%d_%H%M%S",
        error_handler: Optional[Callable[[Exception, str], None]] = None,
        max_retry_attempts: int = 3,
        retry_delay_seconds: float = 1.0,
        enable_local_logging: bool = True,
        session_directory_pattern: str = "{session_id}",
        unknown_session_pattern: str = "unknown_{uuid}",
        **kwargs
    ) -> None:
        """
        Initialize EventSessionLogger gateway.
        
        Args:
            log_base_dir: Base directory for logs (default: from AGENT_LOG_DIR env var)
            downstream_callback: Optional callback for current transition pattern
            downstream_transport: Optional transport interface for future decoupling
            include_system_prompt: Whether to log system prompts (backward compatibility)
            log_format: Log format ("jsonl", "json", "custom")
            file_naming_pattern: strftime pattern for log files
            error_handler: Custom error handling callback
            max_retry_attempts: Maximum retries for downstream operations
            retry_delay_seconds: Delay between retry attempts
            enable_local_logging: Whether to perform local logging
            session_directory_pattern: Pattern for session directories
            unknown_session_pattern: Pattern for unknown session directories
        """
        # Load configuration from environment if not provided
        config = self._load_configuration()
        
        # Override with provided parameters
        self.log_base_dir = Path(log_base_dir or config['log_base_dir'])
        self.downstream_callback = downstream_callback
        self.downstream_transport = downstream_transport
        self.include_system_prompt = include_system_prompt
        self.log_format = log_format
        self.file_naming_pattern = file_naming_pattern
        self.error_handler = error_handler or self._default_error_handler
        self.max_retry_attempts = max_retry_attempts
        self.retry_delay_seconds = retry_delay_seconds
        self.enable_local_logging = enable_local_logging
        self.session_directory_pattern = session_directory_pattern
        self.unknown_session_pattern = unknown_session_pattern
        
        # Internal state
        self._directory_cache = set()  # Cache for created directories
        self._logger = logging.getLogger(__name__)
        self._closed = False
        
        # Ensure base directory exists
        if self.enable_local_logging:
            self._ensure_directory_exists(self.log_base_dir)
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load configuration from environment variables with defaults"""
        return {
            'log_base_dir': os.getenv('AGENT_LOG_DIR', 'logs/sessions'),
            'log_format': os.getenv('AGENT_LOG_FORMAT', 'jsonl'),
            'include_system_prompt': os.getenv('AGENT_LOG_INCLUDE_PROMPT', 'true').lower() == 'true',
            'max_retry_attempts': int(os.getenv('AGENT_LOG_MAX_RETRIES', '3')),
            'retry_delay_seconds': float(os.getenv('AGENT_LOG_RETRY_DELAY', '1.0')),
            'file_naming_pattern': os.getenv('AGENT_LOG_FILE_PATTERN', '%Y%m%d_%H%M%S'),
            'enable_local_logging': os.getenv('AGENT_LOG_ENABLE_LOCAL', 'true').lower() == 'true',
            'session_directory_pattern': os.getenv('AGENT_LOG_SESSION_PATTERN', '{session_id}'),
            'unknown_session_pattern': os.getenv('AGENT_LOG_UNKNOWN_PATTERN', 'unknown_{uuid}')
        }
    
    def _default_error_handler(self, error: Exception, context: str) -> None:
        """Default error handler - logs errors"""
        self._logger.error(f"EventSessionLogger error in {context}: {error}", exc_info=True)
    
    def _ensure_directory_exists(self, directory: Path) -> bool:
        """
        Ensure directory exists with caching optimization.
        
        Args:
            directory: Directory path to create
            
        Returns:
            bool: True if directory exists or was created successfully
        """
        directory_str = str(directory)
        if directory_str in self._directory_cache:
            return True
        
        try:
            directory.mkdir(parents=True, exist_ok=True)
            self._directory_cache.add(directory_str)
            return True
        except Exception as e:
            self.error_handler(e, f"directory_creation:{directory}")
            return False
    
    def _extract_session_info(self, event: Any) -> tuple[str, str]:
        """
        Extract session_id and role from event.
        
        Args:
            event: Event object
            
        Returns:
            tuple: (session_id, role) - uses fallbacks for missing information
        """
        # Extract session_id
        session_id = "unknown"
        if hasattr(event, 'session_id') and event.session_id:
            session_id = event.session_id
        elif isinstance(event, dict) and event.get('session_id'):
            session_id = event['session_id']
        
        # Generate unique session_id for unknown sessions
        if session_id == "unknown":
            session_id = self.unknown_session_pattern.format(uuid=str(uuid.uuid4())[:8])
        
        # Extract role
        role = "system"
        if hasattr(event, 'role') and event.role:
            role = event.role
        elif isinstance(event, dict) and event.get('role'):
            role = event['role']
        
        return session_id, role
    
    def get_session_directory(self, session_id: str) -> Path:
        """Get the session directory path"""
        session_dir_name = self.session_directory_pattern.format(session_id=session_id)
        return self.log_base_dir / session_dir_name
    
    def get_log_file_path(self, session_id: str) -> Path:
        """Get the current log file path for a session"""
        session_dir = self.get_session_directory(session_id)
        timestamp = datetime.now().strftime(self.file_naming_pattern)
        return session_dir / f"{timestamp}.jsonl"
    
    def _serialize_event(self, event: Any) -> Dict[str, Any]:
        """
        Serialize event to dictionary format.
        
        Args:
            event: Event object to serialize
            
        Returns:
            dict: Serialized event data
            
        Raises:
            SerializationError: If serialization fails
        """
        try:
            # Handle Pydantic models
            if hasattr(event, 'model_dump'):
                return event.model_dump()
            
            # Handle dictionaries
            if isinstance(event, dict):
                return event
            
            # Handle string events (try JSON parsing)
            if isinstance(event, str):
                try:
                    return json.loads(event)
                except json.JSONDecodeError:
                    return {"type": "string_event", "content": event}
            
            # Handle other objects
            if hasattr(event, '__dict__'):
                return event.__dict__
            
            # Fallback to string representation
            return {"type": "unknown_event", "content": str(event)}
            
        except Exception as e:
            raise SerializationError(f"Failed to serialize event: {e}")
    
    async def _log_locally(self, event: Any) -> bool:
        """
        Log event to local file system.
        
        Args:
            event: Event to log
            
        Returns:
            bool: True if logging succeeded
            
        Raises:
            LocalLoggingError: If local logging fails
        """
        if not self.enable_local_logging:
            return True
        
        try:
            # Extract session information
            session_id, role = self._extract_session_info(event)
            
            # Get session directory and ensure it exists
            session_dir = self.get_session_directory(session_id)
            if not self._ensure_directory_exists(session_dir):
                raise LocalLoggingError(f"Failed to create session directory: {session_dir}")
            
            # Serialize event
            event_data = self._serialize_event(event)
            
            # Create log entry
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "event": event_data
            }
            
            # Get log file path (create new file for each session)
            log_file = self.get_log_file_path(session_id)
            
            # Write to file (JSON Lines format)
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, default=str) + '\n')
            
            return True
            
        except Exception as e:
            raise LocalLoggingError(f"Local logging failed: {e}")
    
    async def _retry_operation(self, operation: Callable, operation_name: str) -> bool:
        """
        Retry an operation with exponential backoff.
        
        Args:
            operation: Async operation to retry
            operation_name: Name for logging
            
        Returns:
            bool: True if operation succeeded
        """
        last_exception = None
        
        for attempt in range(self.max_retry_attempts):
            try:
                await operation()
                return True
            except Exception as e:
                last_exception = e
                if attempt < self.max_retry_attempts - 1:
                    delay = self.retry_delay_seconds * (2 ** attempt)  # Exponential backoff
                    await asyncio.sleep(delay)
                    self._logger.debug(f"Retrying {operation_name} (attempt {attempt + 2}/{self.max_retry_attempts})")
        
        # All retries failed
        self.error_handler(last_exception, f"retry_failed:{operation_name}")
        return False
    
    async def _forward_downstream(self, event: Any) -> bool:
        """
        Forward event to downstream callback or transport.
        
        Args:
            event: Event to forward
            
        Returns:
            bool: True if any forwarding succeeded
        """
        callback_success = False
        transport_success = False
        
        # Try callback (current transition pattern)
        if self.downstream_callback:
            try:
                callback_success = await self._retry_operation(
                    lambda: self.downstream_callback(event),
                    "downstream_callback"
                )
            except Exception as e:
                self.error_handler(e, "downstream_callback")
        
        # Try transport (future pattern)
        if self.downstream_transport:
            try:
                transport_success = await self._retry_operation(
                    lambda: self.downstream_transport.send(event),
                    "downstream_transport"
                )
            except Exception as e:
                self.error_handler(e, "downstream_transport")
        
        return callback_success or transport_success
    
    async def __call__(self, event: Any) -> bool:
        """
        Main gateway method - processes events through the logging pipeline.
        
        Always logs locally first, then forwards to downstream if configured.
        Error isolation ensures local logging success doesn't depend on transport.
        
        Args:
            event: Event object (SessionEvent, SemiSessionEvent, or any serializable object)
            
        Returns:
            bool: True if local logging succeeded (transport failures don't affect return value)
            
        Raises:
            EventSessionLoggerError: Only for critical local logging failures
        """
        if self._closed:
            raise EventSessionLoggerError("EventSessionLogger is closed")
        
        local_success = False
        
        # PHASE 1: Local logging (never fails due to transport issues)
        try:
            local_success = await self._log_locally(event)
        except Exception as e:
            self.error_handler(e, "local_logging")
            raise LocalLoggingError(f"Local logging failed: {e}")
        
        # PHASE 2: Downstream forwarding (isolated from local logging)
        if self.downstream_callback or self.downstream_transport:
            try:
                await self._forward_downstream(event)
            except Exception as e:
                # Transport errors are logged but don't affect local logging success
                self.error_handler(e, "downstream_forwarding")
        
        return local_success
    
    def configure_from_env(self) -> None:
        """Load configuration from environment variables"""
        config = self._load_configuration()
        
        # Update configuration (preserve existing values if not in env)
        self.log_base_dir = Path(config['log_base_dir'])
        self.include_system_prompt = config['include_system_prompt']
        self.max_retry_attempts = config['max_retry_attempts']
        self.retry_delay_seconds = config['retry_delay_seconds']
        self.file_naming_pattern = config['file_naming_pattern']
        self.enable_local_logging = config['enable_local_logging']
        self.session_directory_pattern = config['session_directory_pattern']
        self.unknown_session_pattern = config['unknown_session_pattern']
    
    def update_downstream_callback(self, callback: Optional[Callable]) -> None:
        """Update downstream callback (for runtime reconfiguration)"""
        self.downstream_callback = callback
    
    def update_downstream_transport(self, transport: Optional[TransportInterface]) -> None:
        """Update downstream transport (for runtime reconfiguration)"""
        self.downstream_transport = transport
    
    async def close(self) -> None:
        """Clean shutdown - close transport connections and flush logs"""
        if self._closed:
            return
        
        self._closed = True
        
        # Close transport if available
        if self.downstream_transport:
            try:
                await self.downstream_transport.close()
            except Exception as e:
                self.error_handler(e, "transport_close")
        
        # Clear caches
        self._directory_cache.clear()
    
    async def __aenter__(self) -> 'EventSessionLogger':
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit with cleanup"""
        await self.close()