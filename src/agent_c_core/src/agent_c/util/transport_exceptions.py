"""
Transport Exception Classes

This module contains all transport-related exception classes to avoid circular imports.
"""


class EventSessionLoggerError(Exception):
    """Base exception for EventSessionLogger"""
    pass


class LocalLoggingError(EventSessionLoggerError):
    """Raised when local logging fails"""
    pass


class TransportError(EventSessionLoggerError):
    """Base exception for transport-related errors"""
    pass


class TransportConnectionError(TransportError):
    """Raised when transport connection fails"""
    pass


class TransportTimeoutError(TransportError):
    """Raised when transport operations timeout"""
    pass


class SerializationError(EventSessionLoggerError):
    """Raised when event serialization fails"""
    pass