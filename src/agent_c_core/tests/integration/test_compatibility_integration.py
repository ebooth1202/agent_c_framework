"""
Integration tests for structured logging compatibility layer.

These tests validate that the compatibility layer works correctly in realistic scenarios.
"""

import logging
import os
import tempfile
from unittest.mock import patch
import pytest

from agent_c.util.structured_logging.compatibility import (
    StructuredLoggingAdapter,
    enable_structured_logging_globally,
    disable_structured_logging_globally,
    get_compatible_logger,
)


class TestCompatibilityIntegration:
    """Integration tests for the compatibility layer."""
    
    def setup_method(self):
        """Clean environment before each test."""
        os.environ.pop('USE_STRUCTURED_LOGGING', None)
        os.environ.pop('STRUCTURED_LOGGING_MODULE_NAME', None)
    
    def teardown_method(self):
        """Clean up after each test."""
        os.environ.pop('USE_STRUCTURED_LOGGING', None)
        os.environ.pop('STRUCTURED_LOGGING_MODULE_NAME', None)
        disable_structured_logging_globally()
    
    def test_adapter_logging_behavior_traditional(self):
        """Test that adapter behaves like LoggingManager when structured logging is disabled."""
        # Ensure structured logging is disabled
        with patch.dict(os.environ, {}, clear=True):
            adapter = StructuredLoggingAdapter("test.module")
            logger = adapter.get_logger()
            
            # Should be a standard logger
            assert isinstance(logger, logging.Logger)
            assert logger.name == "test.module"
            
            # Should be able to log normally
            with patch.object(logger, 'info') as mock_info:
                logger.info("Test message")
                mock_info.assert_called_once_with("Test message")
    
    def test_adapter_logging_behavior_structured(self):
        """Test that adapter uses structured logging when enabled."""
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'true'}):
            # Mock the factory to avoid complex setup
            with patch('agent_c.util.structured_logging.compatibility.StructuredLoggerFactory') as mock_factory:
                with patch('agent_c.util.structured_logging.compatibility.structlog') as mock_structlog:
                    mock_logger = logging.getLogger("test.structured")
                    mock_structlog.stdlib.get_logger.return_value = mock_logger
                    
                    adapter = StructuredLoggingAdapter("test.module")
                    logger = adapter.get_logger()
                    
                    # Should have called the factory
                    mock_factory.assert_called_once()
                    mock_structlog.stdlib.get_logger.assert_called_once_with("test.module")
                    assert logger == mock_logger
    
    def test_module_specific_enablement(self):
        """Test that module-specific enablement works correctly."""
        with patch.dict(os.environ, {
            'USE_STRUCTURED_LOGGING': 'true',
            'STRUCTURED_LOGGING_MODULE_NAME': 'api.sessions'
        }):
            # Mock structured logging components
            with patch('agent_c.util.structured_logging.compatibility.StructuredLoggerFactory') as mock_factory:
                with patch('agent_c.util.structured_logging.compatibility.structlog') as mock_structlog:
                    with patch('agent_c.util.structured_logging.compatibility.LoggingManager') as mock_lm:
                        mock_structured_logger = logging.getLogger("structured")
                        mock_traditional_logger = logging.getLogger("traditional")
                        
                        mock_structlog.stdlib.get_logger.return_value = mock_structured_logger
                        mock_lm_instance = mock_lm.return_value
                        mock_lm_instance.get_logger.return_value = mock_traditional_logger
                        
                        # Should use structured logging for matching module
                        adapter1 = StructuredLoggingAdapter("api.sessions")
                        logger1 = adapter1.get_logger()
                        assert logger1 == mock_structured_logger
                        mock_factory.assert_called()
                        
                        # Should use traditional logging for non-matching module
                        adapter2 = StructuredLoggingAdapter("other.module")
                        logger2 = adapter2.get_logger()
                        assert logger2 == mock_traditional_logger
                        mock_lm.assert_called_with("other.module")
    
    def test_global_enablement_and_disablement(self):
        """Test global enablement and disablement functions."""
        # Initially disabled
        adapter = StructuredLoggingAdapter("test.module")
        assert not adapter._should_use_structured_logging()
        
        # Enable globally
        enable_structured_logging_globally()
        adapter = StructuredLoggingAdapter("test.module")
        assert adapter._should_use_structured_logging()
        
        # Disable globally
        disable_structured_logging_globally()
        adapter = StructuredLoggingAdapter("test.module")
        assert not adapter._should_use_structured_logging()
    
    def test_get_compatible_logger_convenience(self):
        """Test the get_compatible_logger convenience function."""
        with patch('agent_c.util.structured_logging.compatibility.StructuredLoggingAdapter') as mock_adapter_class:
            mock_adapter = mock_adapter_class.return_value
            mock_logger = logging.getLogger("test")
            mock_adapter.get_logger.return_value = mock_logger
            
            logger = get_compatible_logger("test.module")
            
            assert logger == mock_logger
            mock_adapter_class.assert_called_once_with("test.module")
            mock_adapter.get_logger.assert_called_once()
    
    def test_class_method_compatibility(self):
        """Test that class methods work correctly."""
        # These should work regardless of structured logging state
        with patch('agent_c.util.structured_logging.compatibility.LoggingManager') as mock_lm:
            # Test configure_root_logger
            StructuredLoggingAdapter.configure_root_logger()
            mock_lm.configure_root_logger.assert_called_once()
            
            # Test configure_external_loggers
            test_config = {"uvicorn": "WARNING"}
            StructuredLoggingAdapter.configure_external_loggers(test_config)
            mock_lm.configure_external_loggers.assert_called_once_with(test_config)
            
            # Test debug methods
            mock_lm.is_debug_mode.return_value = True
            assert StructuredLoggingAdapter.is_debug_mode() is True
            
            StructuredLoggingAdapter.set_debug_mode(False)
            mock_lm.set_debug_mode.assert_called_once_with(False)
    
    def test_real_logging_output_traditional(self):
        """Test actual logging output with traditional logging."""
        import io
        
        # Set up a string handler to capture output
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))
        
        # Ensure traditional logging
        with patch.dict(os.environ, {}, clear=True):
            adapter = StructuredLoggingAdapter("test.real")
            logger = adapter.get_logger()
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
            
            # Log a message
            logger.info("This is a test message")
            
            # Check output
            output = log_capture.getvalue()
            assert "INFO - test.real - This is a test message" in output
            
            # Clean up
            logger.removeHandler(handler)
    
    def test_feature_flag_environment_isolation(self):
        """Test that feature flags work correctly in different environments."""
        test_cases = [
            # (env_vars, module_name, expected_structured)
            ({}, "any.module", False),
            ({'USE_STRUCTURED_LOGGING': 'false'}, "any.module", False),
            ({'USE_STRUCTURED_LOGGING': 'true'}, "any.module", True),
            ({'USE_STRUCTURED_LOGGING': 'true', 'STRUCTURED_LOGGING_MODULE_NAME': 'specific'}, "specific", True),
            ({'USE_STRUCTURED_LOGGING': 'true', 'STRUCTURED_LOGGING_MODULE_NAME': 'specific'}, "other", False),
            ({'USE_STRUCTURED_LOGGING': 'true', 'STRUCTURED_LOGGING_MODULE_NAME': 'api'}, "api.sessions", True),
            ({'USE_STRUCTURED_LOGGING': 'true', 'STRUCTURED_LOGGING_MODULE_NAME': 'api'}, "ui.components", False),
        ]
        
        for env_vars, module_name, expected in test_cases:
            with patch.dict(os.environ, env_vars, clear=True):
                adapter = StructuredLoggingAdapter(module_name)
                assert adapter._should_use_structured_logging() == expected, \
                    f"Failed for env={env_vars}, module={module_name}, expected={expected}"
    
    def test_logger_caching_behavior(self):
        """Test that loggers are properly cached."""
        with patch.dict(os.environ, {}, clear=True):
            with patch('agent_c.util.structured_logging.compatibility.LoggingManager') as mock_lm:
                mock_manager = mock_lm.return_value
                mock_logger = logging.getLogger("cached.test")
                mock_manager.get_logger.return_value = mock_logger
                
                adapter = StructuredLoggingAdapter("test.caching")
                
                # First call should create the logger
                logger1 = adapter.get_logger()
                assert mock_lm.call_count == 1
                
                # Second call should return cached logger
                logger2 = adapter.get_logger()
                assert mock_lm.call_count == 1  # Should not create another manager
                assert logger1 == logger2
    
    def test_error_handling_in_adapter(self):
        """Test error handling in the adapter."""
        # Test with invalid environment variable
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'invalid_value'}):
            adapter = StructuredLoggingAdapter("test.error")
            # Should default to False for invalid values
            assert not adapter._should_use_structured_logging()
        
        # Test with missing module name when module-specific is enabled
        with patch.dict(os.environ, {
            'USE_STRUCTURED_LOGGING': 'true',
            'STRUCTURED_LOGGING_MODULE_NAME': ''
        }):
            adapter = StructuredLoggingAdapter("test.error")
            # Should handle empty module name gracefully
            result = adapter._should_use_structured_logging()
            assert isinstance(result, bool)  # Should not crash


class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    def setup_method(self):
        """Clean environment before each test."""
        os.environ.pop('USE_STRUCTURED_LOGGING', None)
        os.environ.pop('STRUCTURED_LOGGING_MODULE_NAME', None)
    
    def teardown_method(self):
        """Clean up after each test."""
        os.environ.pop('USE_STRUCTURED_LOGGING', None)
        os.environ.pop('STRUCTURED_LOGGING_MODULE_NAME', None)
        disable_structured_logging_globally()
    
    def test_gradual_migration_scenario(self):
        """Test a gradual migration scenario."""
        # Step 1: Start with traditional logging
        with patch.dict(os.environ, {}, clear=True):
            adapter = StructuredLoggingAdapter("api.sessions")
            assert not adapter._should_use_structured_logging()
        
        # Step 2: Enable for specific module
        with patch.dict(os.environ, {
            'USE_STRUCTURED_LOGGING': 'true',
            'STRUCTURED_LOGGING_MODULE_NAME': 'api.sessions'
        }):
            # Sessions module should use structured logging
            sessions_adapter = StructuredLoggingAdapter("api.sessions")
            assert sessions_adapter._should_use_structured_logging()
            
            # Other modules should still use traditional
            other_adapter = StructuredLoggingAdapter("api.chat")
            assert not other_adapter._should_use_structured_logging()
        
        # Step 3: Enable globally
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'true'}):
            sessions_adapter = StructuredLoggingAdapter("api.sessions")
            other_adapter = StructuredLoggingAdapter("api.chat")
            assert sessions_adapter._should_use_structured_logging()
            assert other_adapter._should_use_structured_logging()
    
    def test_api_compatibility_scenario(self):
        """Test that the adapter is a drop-in replacement for LoggingManager."""
        # This test ensures that existing code using LoggingManager can switch
        # to StructuredLoggingAdapter without any changes
        
        def example_function_using_logging_manager(logger_class):
            """Example function that uses LoggingManager interface."""
            # This represents existing code that uses LoggingManager
            manager = logger_class("example.module")
            logger = manager.get_logger()
            
            # Use class methods
            logger_class.configure_root_logger()
            logger_class.set_debug_mode(True)
            debug_state = logger_class.is_debug_mode()
            
            return logger, debug_state
        
        # Mock LoggingManager methods for testing
        with patch('agent_c.util.structured_logging.compatibility.LoggingManager') as mock_lm:
            mock_manager = mock_lm.return_value
            mock_logger = logging.getLogger("test")
            mock_manager.get_logger.return_value = mock_logger
            mock_lm.is_debug_mode.return_value = True
            
            # Test with StructuredLoggingAdapter
            logger, debug_state = example_function_using_logging_manager(StructuredLoggingAdapter)
            
            assert logger == mock_logger
            assert debug_state is True
            mock_lm.configure_root_logger.assert_called_once()
            mock_lm.set_debug_mode.assert_called_once_with(True)
            mock_lm.is_debug_mode.assert_called_once()
    
    def test_performance_scenario(self):
        """Test performance characteristics of the adapter."""
        import time
        
        # Test that adapter creation is fast
        start_time = time.time()
        adapters = []
        for i in range(100):
            adapter = StructuredLoggingAdapter(f"test.module.{i}")
            adapters.append(adapter)
        creation_time = time.time() - start_time
        
        # Should be very fast (less than 100ms for 100 adapters)
        assert creation_time < 0.1, f"Adapter creation too slow: {creation_time}s"
        
        # Test that logger retrieval is cached and fast
        adapter = adapters[0]
        start_time = time.time()
        for _ in range(100):
            logger = adapter.get_logger()
        retrieval_time = time.time() - start_time
        
        # Should be very fast due to caching
        assert retrieval_time < 0.01, f"Logger retrieval too slow: {retrieval_time}s"