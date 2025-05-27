"""
Tests for the structured logging compatibility layer.
"""

import logging
import os
import threading
from unittest.mock import Mock, patch
import pytest

from agent_c.util.structured_logging.compatibility import (
    StructuredLoggingAdapter,
    StructuredLoggingMonkeyPatch,
    enable_structured_logging_globally,
    disable_structured_logging_globally,
    enable_structured_logging_for_module,
    get_migration_status,
    get_compatible_logger,
)


class TestStructuredLoggingAdapter:
    """Test the StructuredLoggingAdapter class."""
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        adapter = StructuredLoggingAdapter("test.module")
        assert adapter.logger_name == "test.module"
        assert adapter._logger is None
        assert adapter._structured_logger is None
    
    def test_should_use_structured_logging_disabled_by_default(self):
        """Test that structured logging is disabled by default."""
        with patch.dict(os.environ, {}, clear=True):
            adapter = StructuredLoggingAdapter("test.module")
            assert not adapter._should_use_structured_logging()
    
    def test_should_use_structured_logging_enabled_globally(self):
        """Test global enablement of structured logging."""
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'true'}):
            adapter = StructuredLoggingAdapter("test.module")
            assert adapter._should_use_structured_logging()
    
    def test_should_use_structured_logging_module_specific(self):
        """Test module-specific enablement."""
        with patch.dict(os.environ, {
            'USE_STRUCTURED_LOGGING': 'true',
            'STRUCTURED_LOGGING_MODULE_NAME': 'test.module'
        }):
            adapter = StructuredLoggingAdapter("test.module")
            assert adapter._should_use_structured_logging()
            
            adapter2 = StructuredLoggingAdapter("other.module")
            assert not adapter2._should_use_structured_logging()
    
    def test_should_use_structured_logging_module_prefix(self):
        """Test module prefix matching."""
        with patch.dict(os.environ, {
            'USE_STRUCTURED_LOGGING': 'true',
            'STRUCTURED_LOGGING_MODULE_NAME': 'test'
        }):
            adapter = StructuredLoggingAdapter("test.submodule")
            assert adapter._should_use_structured_logging()
            
            adapter2 = StructuredLoggingAdapter("other.module")
            assert not adapter2._should_use_structured_logging()
    
    @patch('agent_c.util.structured_logging.compatibility.StructuredLoggerFactory')
    @patch('agent_c.util.structured_logging.compatibility.structlog')
    def test_get_logger_structured(self, mock_structlog, mock_factory):
        """Test getting a structured logger."""
        mock_stdlib_logger = Mock()
        mock_structlog.stdlib.get_logger.return_value = mock_stdlib_logger
        
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'true'}):
            adapter = StructuredLoggingAdapter("test.module")
            logger = adapter.get_logger()
            
            assert logger == mock_stdlib_logger
            mock_factory.assert_called_once()
            mock_structlog.stdlib.get_logger.assert_called_once_with("test.module")
    
    @patch('agent_c.util.structured_logging.compatibility.LoggingManager')
    def test_get_logger_traditional(self, mock_logging_manager):
        """Test getting a traditional logger."""
        mock_logger = Mock()
        mock_manager_instance = Mock()
        mock_manager_instance.get_logger.return_value = mock_logger
        mock_logging_manager.return_value = mock_manager_instance
        
        with patch.dict(os.environ, {}, clear=True):
            adapter = StructuredLoggingAdapter("test.module")
            logger = adapter.get_logger()
            
            assert logger == mock_logger
            mock_logging_manager.assert_called_once_with("test.module")
            mock_manager_instance.get_logger.assert_called_once()
    
    def test_logger_caching(self):
        """Test that loggers are cached."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('agent_c.util.structured_logging.compatibility.LoggingManager') as mock_lm:
                mock_logger = Mock()
                mock_manager = Mock()
                mock_manager.get_logger.return_value = mock_logger
                mock_lm.return_value = mock_manager
                
                adapter = StructuredLoggingAdapter("test.module")
                logger1 = adapter.get_logger()
                logger2 = adapter.get_logger()
                
                assert logger1 == logger2
                assert mock_lm.call_count == 1  # Should only create manager once
    
    @patch('agent_c.util.structured_logging.compatibility.LoggingManager')
    def test_class_method_delegation(self, mock_logging_manager):
        """Test that class methods are properly delegated."""
        # Test configure_root_logger
        StructuredLoggingAdapter.configure_root_logger()
        mock_logging_manager.configure_root_logger.assert_called_once()
        
        # Test configure_external_loggers
        test_levels = {"test": "DEBUG"}
        StructuredLoggingAdapter.configure_external_loggers(test_levels)
        mock_logging_manager.configure_external_loggers.assert_called_once_with(test_levels)
        
        # Test get_debug_event
        mock_event = Mock()
        mock_logging_manager.get_debug_event.return_value = mock_event
        event = StructuredLoggingAdapter.get_debug_event()
        assert event == mock_event
        
        # Test set_debug_mode
        StructuredLoggingAdapter.set_debug_mode(True)
        mock_logging_manager.set_debug_mode.assert_called_once_with(True)
        
        # Test is_debug_mode
        mock_logging_manager.is_debug_mode.return_value = True
        result = StructuredLoggingAdapter.is_debug_mode()
        assert result is True


class TestStructuredLoggingMonkeyPatch:
    """Test the monkey patching functionality."""
    
    def setup_method(self):
        """Ensure clean state before each test."""
        StructuredLoggingMonkeyPatch.unpatch_logging_manager()
    
    def teardown_method(self):
        """Clean up after each test."""
        StructuredLoggingMonkeyPatch.unpatch_logging_manager()
    
    def test_patch_and_unpatch(self):
        """Test patching and unpatching LoggingManager."""
        # Initially not patched
        assert not StructuredLoggingMonkeyPatch.is_patched()
        
        # Patch
        StructuredLoggingMonkeyPatch.patch_logging_manager()
        assert StructuredLoggingMonkeyPatch.is_patched()
        
        # Unpatch
        StructuredLoggingMonkeyPatch.unpatch_logging_manager()
        assert not StructuredLoggingMonkeyPatch.is_patched()
    
    def test_double_patch_is_safe(self):
        """Test that double patching doesn't cause issues."""
        StructuredLoggingMonkeyPatch.patch_logging_manager()
        StructuredLoggingMonkeyPatch.patch_logging_manager()  # Should be safe
        assert StructuredLoggingMonkeyPatch.is_patched()
    
    def test_unpatch_without_patch_is_safe(self):
        """Test that unpatching without patching is safe."""
        StructuredLoggingMonkeyPatch.unpatch_logging_manager()  # Should be safe
        assert not StructuredLoggingMonkeyPatch.is_patched()


class TestConvenienceFunctions:
    """Test convenience functions for enabling/disabling structured logging."""
    
    def setup_method(self):
        """Clean environment before each test."""
        # Clean up environment
        os.environ.pop('USE_STRUCTURED_LOGGING', None)
        os.environ.pop('STRUCTURED_LOGGING_MODULE_NAME', None)
        StructuredLoggingMonkeyPatch.unpatch_logging_manager()
    
    def teardown_method(self):
        """Clean up after each test."""
        os.environ.pop('USE_STRUCTURED_LOGGING', None)
        os.environ.pop('STRUCTURED_LOGGING_MODULE_NAME', None)
        StructuredLoggingMonkeyPatch.unpatch_logging_manager()
    
    def test_enable_structured_logging_globally(self):
        """Test global enablement."""
        enable_structured_logging_globally()
        
        assert os.environ.get('USE_STRUCTURED_LOGGING') == 'true'
        assert StructuredLoggingMonkeyPatch.is_patched()
    
    def test_disable_structured_logging_globally(self):
        """Test global disabling."""
        # First enable
        enable_structured_logging_globally()
        
        # Then disable
        disable_structured_logging_globally()
        
        assert 'USE_STRUCTURED_LOGGING' not in os.environ
        assert not StructuredLoggingMonkeyPatch.is_patched()
    
    def test_enable_structured_logging_for_module(self):
        """Test module-specific enablement."""
        enable_structured_logging_for_module("test.module")
        
        assert os.environ.get('USE_STRUCTURED_LOGGING') == 'true'
        assert os.environ.get('STRUCTURED_LOGGING_MODULE_NAME') == 'test.module'
    
    def test_get_migration_status(self):
        """Test migration status reporting."""
        # Test default state
        status = get_migration_status()
        assert not status['structured_logging_enabled']
        assert status['module_override'] is None
        assert not status['monkey_patch_active']
        
        # Test enabled state
        enable_structured_logging_for_module("test.module")
        status = get_migration_status()
        assert status['structured_logging_enabled']
        assert status['module_override'] == 'test.module'
        assert not status['monkey_patch_active']  # enable_for_module doesn't patch
        
        # Test with monkey patch
        StructuredLoggingMonkeyPatch.patch_logging_manager()
        status = get_migration_status()
        assert status['monkey_patch_active']
    
    @patch('agent_c.util.structured_logging.compatibility.StructuredLoggingAdapter')
    def test_get_compatible_logger(self, mock_adapter_class):
        """Test the get_compatible_logger convenience function."""
        mock_adapter = Mock()
        mock_logger = Mock()
        mock_adapter.get_logger.return_value = mock_logger
        mock_adapter_class.return_value = mock_adapter
        
        logger = get_compatible_logger("test.module")
        
        assert logger == mock_logger
        mock_adapter_class.assert_called_once_with("test.module")
        mock_adapter.get_logger.assert_called_once()


class TestIntegration:
    """Integration tests for the compatibility layer."""
    
    def setup_method(self):
        """Clean state before each test."""
        os.environ.pop('USE_STRUCTURED_LOGGING', None)
        os.environ.pop('STRUCTURED_LOGGING_MODULE_NAME', None)
        StructuredLoggingMonkeyPatch.unpatch_logging_manager()
    
    def teardown_method(self):
        """Clean up after each test."""
        os.environ.pop('USE_STRUCTURED_LOGGING', None)
        os.environ.pop('STRUCTURED_LOGGING_MODULE_NAME', None)
        StructuredLoggingMonkeyPatch.unpatch_logging_manager()
    
    def test_adapter_behaves_like_logging_manager(self):
        """Test that the adapter provides the same interface as LoggingManager."""
        # This test ensures API compatibility
        adapter = StructuredLoggingAdapter("test.module")
        
        # Should have all the same methods as LoggingManager
        assert hasattr(adapter, 'get_logger')
        assert hasattr(adapter, 'configure_root_logger')
        assert hasattr(adapter, 'configure_external_loggers')
        assert hasattr(adapter, 'get_debug_event')
        assert hasattr(adapter, 'set_debug_mode')
        assert hasattr(adapter, 'is_debug_mode')
        
        # Methods should be callable
        logger = adapter.get_logger()
        assert isinstance(logger, logging.Logger)
    
    def test_feature_flag_behavior(self):
        """Test that feature flags work correctly."""
        # Test disabled
        with patch.dict(os.environ, {}, clear=True):
            adapter = StructuredLoggingAdapter("test.module")
            assert not adapter._use_structured
        
        # Test enabled globally
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'true'}):
            adapter = StructuredLoggingAdapter("test.module")
            assert adapter._use_structured
        
        # Test module-specific
        with patch.dict(os.environ, {
            'USE_STRUCTURED_LOGGING': 'true',
            'STRUCTURED_LOGGING_MODULE_NAME': 'specific.module'
        }):
            adapter1 = StructuredLoggingAdapter("specific.module")
            adapter2 = StructuredLoggingAdapter("other.module")
            assert adapter1._use_structured
            assert not adapter2._use_structured