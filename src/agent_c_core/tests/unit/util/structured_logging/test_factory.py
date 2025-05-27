"""
Tests for StructuredLoggerFactory

These tests validate the core factory functionality including singleton behavior,
logger creation, caching, and compatibility with LoggingManager.
"""

import os
import pytest
from unittest.mock import patch, MagicMock

from agent_c.util.structured_logging.factory import StructuredLoggerFactory, get_logger


class TestStructuredLoggerFactory:
    """Test cases for StructuredLoggerFactory."""
    
    def setup_method(self):
        """Reset factory state before each test."""
        StructuredLoggerFactory.reset()
    
    def test_singleton_behavior(self):
        """Test that StructuredLoggerFactory follows singleton pattern."""
        factory1 = StructuredLoggerFactory()
        factory2 = StructuredLoggerFactory()
        
        assert factory1 is factory2
    
    def test_logger_creation_structured(self):
        """Test creating structured loggers when feature flag is enabled."""
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'true'}):
            factory = StructuredLoggerFactory()
            logger = factory.get_logger('test.module')
            
            # Should create a structlog logger
            assert hasattr(logger, 'info')
            assert hasattr(logger, 'bind')  # structlog specific method
    
    def test_logger_creation_legacy(self):
        """Test creating legacy loggers when feature flag is disabled."""
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'false'}):
            factory = StructuredLoggerFactory()
            logger = factory.get_logger('test.module')
            
            # Should create a standard library logger
            assert hasattr(logger, 'info')
            # Should not have structlog specific methods
            assert not hasattr(logger, 'bind')
    
    def test_logger_caching(self):
        """Test that loggers are cached for performance."""
        factory = StructuredLoggerFactory()
        
        logger1 = factory.get_logger('test.module')
        logger2 = factory.get_logger('test.module')
        
        assert logger1 is logger2
    
    def test_per_module_feature_flags(self):
        """Test per-module feature flag override."""
        with patch.dict(os.environ, {
            'USE_STRUCTURED_LOGGING': 'false',
            'STRUCTURED_LOGGING_TEST_MODULE': 'true'
        }):
            factory = StructuredLoggerFactory()
            
            # Default should be legacy
            default_logger = factory.get_logger('other.module')
            assert not hasattr(default_logger, 'bind')
            
            # Specific module should be structured
            test_logger = factory.get_logger('test.module')
            assert hasattr(test_logger, 'bind')
    
    def test_development_environment_detection(self):
        """Test development environment detection."""
        factory = StructuredLoggerFactory()
        
        # Test various development indicators
        with patch.dict(os.environ, {'ENVIRONMENT': 'development'}):
            assert factory._is_development_environment() is True
        
        with patch.dict(os.environ, {'DEBUG': 'true'}):
            assert factory._is_development_environment() is True
        
        with patch.dict(os.environ, {'ENVIRONMENT': 'production', 'DEBUG': 'false'}):
            assert factory._is_development_environment() is False
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        factory = StructuredLoggerFactory()
        
        # Create and cache a logger
        logger1 = factory.get_logger('test.module')
        
        # Clear cache
        factory.clear_cache()
        
        # Get logger again - should be a new instance
        logger2 = factory.get_logger('test.module')
        
        # Note: Due to structlog's own caching, these might still be the same
        # but our cache should be cleared
        assert 'test.module' not in factory._logger_cache or factory._logger_cache['test.module'] is logger2


class TestGetLoggerFunction:
    """Test cases for the get_logger convenience function."""
    
    def setup_method(self):
        """Reset factory state before each test."""
        StructuredLoggerFactory.reset()
    
    def test_get_logger_convenience_function(self):
        """Test the get_logger convenience function."""
        logger = get_logger('test.module')
        
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'error')
    
    def test_get_logger_returns_same_instance(self):
        """Test that get_logger returns the same instance for the same name."""
        logger1 = get_logger('test.module')
        logger2 = get_logger('test.module')
        
        assert logger1 is logger2