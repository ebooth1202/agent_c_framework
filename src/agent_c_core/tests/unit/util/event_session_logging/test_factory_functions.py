#!/usr/bin/env python3
"""
Factory Functions Test Suite

This script tests the comprehensive factory functions and utilities for creating
EventSessionLogger instances with various configurations and patterns.
"""

import asyncio
import os
import sys
import tempfile
import warnings
from datetime import datetime
from pathlib import Path

# Add the src directory to Python path for imports
agent_c_core_dir = Path(__file__).parents[4]
sys.path.insert(0, str(agent_c_core_dir / 'src'))

from agent_c.util.event_session_logger_factory import (
    LoggerConfiguration, LoggerEnvironment, TransportType,
    load_configuration_from_env, create_logger_from_config,
    create_development_logger, create_testing_logger, create_production_logger,
    create_migration_logger, create_monitoring_logger, create_multi_transport_logger,
    validate_logger_config, print_logger_info, create_logger_with_validation,
    create_session_logger, create_logging_only, create_with_callback, create_with_transport,
    create_from_environment, create_backward_compatible
)
from agent_c.util.transports import LoggingTransport, NullTransport, FileTransport
from agent_c.util.transport_exceptions import EventSessionLoggerError
from agent_c.models.events.chat import MessageEvent


class MockSessionLogger:
    """Mock old SessionLogger for migration testing"""
    def __init__(self, log_file_path: str, include_system_prompt: bool = True):
        self.log_file_path = Path(log_file_path)
        self.include_system_prompt = include_system_prompt


async def test_logger_configuration():
    """Test LoggerConfiguration class"""
    print("Testing LoggerConfiguration...")
    
    # Test default configuration
    config = LoggerConfiguration()
    assert config.log_base_dir == "logs/sessions", "Should have default log directory"
    assert config.environment == LoggerEnvironment.DEVELOPMENT, "Should default to development"
    assert config.include_system_prompt == True, "Should include system prompts by default"
    
    # Test validation
    errors = config.validate()
    assert len(errors) == 0, "Default configuration should be valid"
    
    # Test invalid configuration
    invalid_config = LoggerConfiguration(
        max_retry_attempts=-1,
        retry_delay_seconds=-1.0,
        transport_type=TransportType.HTTP,
        transport_config={}  # Missing required endpoint_url
    )
    
    errors = invalid_config.validate()
    assert len(errors) > 0, "Invalid configuration should have errors"
    assert any("max_retry_attempts" in error for error in errors), "Should validate retry attempts"
    assert any("retry_delay_seconds" in error for error in errors), "Should validate retry delay"
    assert any("endpoint_url" in error for error in errors), "Should validate HTTP config"
    
    print("✅ LoggerConfiguration test passed")


async def test_environment_configuration():
    """Test environment-based configuration loading"""
    print("Testing environment configuration...")
    
    # Save original environment
    original_env = {}
    test_env = {
        'AGENT_LOG_DIR': '/tmp/test_env_logs',
        'AGENT_TRANSPORT_TYPE': 'logging',
        'AGENT_ENVIRONMENT': 'production',
        'AGENT_DEBUG': 'true',
        'AGENT_LOG_MAX_RETRIES': '5'
    }
    
    for key, value in test_env.items():
        original_env[key] = os.environ.get(key)
        os.environ[key] = value
    
    try:
        config = load_configuration_from_env()
        
        assert config.log_base_dir == '/tmp/test_env_logs', "Should load log directory from env"
        assert config.transport_type == TransportType.LOGGING, "Should load transport type from env"
        assert config.environment == LoggerEnvironment.PRODUCTION, "Should load environment from env"
        assert config.debug_mode == True, "Should load debug mode from env"
        assert config.max_retry_attempts == 5, "Should load retry attempts from env"
        
    finally:
        # Restore original environment
        for key, original_value in original_env.items():
            if original_value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = original_value
    
    print("✅ Environment configuration test passed")


async def test_basic_factory_functions():
    """Test basic factory functions"""
    print("Testing basic factory functions...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test create_session_logger
        logger1 = create_session_logger(log_base_dir=temp_dir)
        assert str(logger1.log_base_dir) == temp_dir, "Should set log directory"
        assert logger1.downstream_callback is None, "Should have no callback by default"
        await logger1.close()
        
        # Test create_logging_only
        logger2 = create_logging_only(log_base_dir=temp_dir)
        assert logger2.downstream_transport is None, "Should have no transport"
        await logger2.close()
        
        # Test create_with_callback
        test_events = []
        async def test_callback(event):
            test_events.append(event)
        
        logger3 = create_with_callback(test_callback, log_base_dir=temp_dir)
        assert logger3.downstream_callback == test_callback, "Should have callback set"
        await logger3.close()
        
        # Test create_with_transport
        transport = NullTransport()
        logger4 = create_with_transport(transport, log_base_dir=temp_dir)
        assert logger4.downstream_transport == transport, "Should have transport set"
        await logger4.close()
        
        # Test create_backward_compatible
        logger5 = create_backward_compatible(log_base_dir=temp_dir)
        assert logger5.log_format == "jsonl", "Should use JSON Lines format"
        assert logger5.include_system_prompt == True, "Should include system prompts"
        await logger5.close()
    
    print("✅ Basic factory functions test passed")


async def test_environment_specific_loggers():
    """Test environment-specific logger creation"""
    print("Testing environment-specific loggers...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test development logger with default path
        dev_logger = create_development_logger()
        assert "dev" in str(dev_logger.log_base_dir), "Should use dev directory"
        assert dev_logger.downstream_transport is not None, "Should have transport for development"
        await dev_logger.close()
        
        # Test development logger with custom path
        dev_logger_custom = create_development_logger(log_base_dir=temp_dir)
        assert str(dev_logger_custom.log_base_dir) == temp_dir, "Should use custom directory"
        await dev_logger_custom.close()
        
        # Test testing logger with default path
        test_logger = create_testing_logger()
        assert "test" in str(test_logger.log_base_dir), "Should use test directory"
        assert isinstance(test_logger.downstream_transport, NullTransport), "Should use null transport for testing"
        await test_logger.close()
        
        # Test testing logger with custom path
        test_logger_custom = create_testing_logger(log_base_dir=temp_dir)
        assert str(test_logger_custom.log_base_dir) == temp_dir, "Should use custom directory"
        await test_logger_custom.close()
        
        # Test production logger
        prod_config = {
            'queue_name': 'prod_events',
            'connection_string': 'amqp://prod-queue'
        }
        prod_logger = create_production_logger(
            temp_dir, 
            TransportType.QUEUE, 
            prod_config
        )
        assert str(prod_logger.log_base_dir) == temp_dir, "Should use specified directory"
        assert prod_logger.downstream_transport is not None, "Should have transport"
        await prod_logger.close()
    
    print("✅ Environment-specific loggers test passed")


async def test_migration_logger():
    """Test migration logger functionality"""
    print("Testing migration logger...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create mock old SessionLogger
        old_logger = MockSessionLogger(
            log_file_path=f"{temp_dir}/session/test.jsonl",
            include_system_prompt=False
        )
        
        # Test migration without warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            migration_logger = create_migration_logger(
                old_logger, 
                enable_warnings=False
            )
            
            # Should not generate warnings
            assert len(w) == 0, "Should not generate warnings when disabled"
            assert migration_logger.include_system_prompt == False, "Should extract config from old logger"
            await migration_logger.close()
        
        # Test migration with warnings
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            
            migration_logger = create_migration_logger(
                old_logger,
                enable_warnings=True
            )
            
            # Should generate deprecation warning
            assert len(w) > 0, "Should generate deprecation warning"
            assert issubclass(w[0].category, DeprecationWarning), "Should be deprecation warning"
            await migration_logger.close()
    
    print("✅ Migration logger test passed")


async def test_monitoring_logger():
    """Test monitoring logger functionality"""
    print("Testing monitoring logger...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        monitoring_data = []
        
        def monitoring_callback(data):
            monitoring_data.append(data)
        
        logger = create_monitoring_logger(temp_dir, monitoring_callback)
        
        # Send test event
        event = MessageEvent(
            session_id="monitoring_test",
            role="assistant",
            content="Test monitoring"
        )
        
        result = await logger(event)
        assert result == True, "Should succeed"
        
        # Check monitoring data
        assert len(monitoring_data) > 0, "Should capture monitoring data"
        
        monitor_entry = monitoring_data[0]
        assert 'event_type' in monitor_entry, "Should include event type"
        assert 'success' in monitor_entry, "Should include success status"
        assert 'duration_ms' in monitor_entry, "Should include duration"
        assert 'timestamp' in monitor_entry, "Should include timestamp"
        
        await logger.close()
    
    print("✅ Monitoring logger test passed")


async def test_multi_transport_logger():
    """Test multi-transport logger functionality"""
    print("Testing multi-transport logger...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create multiple transports
        transport1 = LoggingTransport("transport1")
        transport2 = NullTransport()
        file_path = Path(temp_dir) / "multi_transport.jsonl"
        transport3 = FileTransport(str(file_path))
        
        await transport3.connect()
        
        # Create multi-transport logger
        logger = create_multi_transport_logger(
            temp_dir, 
            [transport1, transport2, transport3]
        )
        
        # Send test event
        event = MessageEvent(
            session_id="multi_test",
            role="assistant",
            content="Multi-transport test"
        )
        
        result = await logger(event)
        assert result == True, "Should succeed with multi-transport"
        
        # Verify file transport received event
        assert file_path.exists(), "File transport should create file"
        
        await logger.close()
    
    print("✅ Multi-transport logger test passed")


async def test_configuration_validation():
    """Test configuration validation utilities"""
    print("Testing configuration validation...")
    
    # Test valid configuration
    valid_config = LoggerConfiguration(
        log_base_dir="logs/test",
        transport_type=TransportType.NULL
    )
    
    assert validate_logger_config(valid_config) == True, "Valid config should pass validation"
    
    # Test invalid configuration
    invalid_config = LoggerConfiguration(
        max_retry_attempts=-1,
        transport_type=TransportType.HTTP,
        transport_config={}  # Missing endpoint_url
    )
    
    # Capture print output
    import io
    from contextlib import redirect_stdout
    
    output = io.StringIO()
    with redirect_stdout(output):
        result = validate_logger_config(invalid_config)
    
    assert result == False, "Invalid config should fail validation"
    output_text = output.getvalue()
    assert "Configuration validation errors:" in output_text, "Should print validation errors"
    
    print("✅ Configuration validation test passed")


async def test_logger_info_printing():
    """Test logger info printing utility"""
    print("Testing logger info printing...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        logger = create_testing_logger(log_base_dir=temp_dir)
        
        # Capture print output
        import io
        from contextlib import redirect_stdout
        
        output = io.StringIO()
        with redirect_stdout(output):
            print_logger_info(logger)
        
        output_text = output.getvalue()
        assert "EventSessionLogger Configuration:" in output_text, "Should print configuration header"
        assert "Log Directory:" in output_text, "Should print log directory"
        assert "Local Logging:" in output_text, "Should print local logging status"
        assert "Downstream Transport:" in output_text, "Should print transport info"
        
        await logger.close()
    
    print("✅ Logger info printing test passed")


async def test_logger_with_validation():
    """Test create_logger_with_validation function"""
    print("Testing logger with validation...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test valid configuration
        valid_config = LoggerConfiguration(
            log_base_dir=temp_dir,
            transport_type=TransportType.NULL
        )
        
        # Capture print output
        import io
        from contextlib import redirect_stdout
        
        output = io.StringIO()
        with redirect_stdout(output):
            logger = create_logger_with_validation(valid_config)
        
        output_text = output.getvalue()
        assert "EventSessionLogger Configuration:" in output_text, "Should print logger info"
        
        await logger.close()
        
        # Test invalid configuration
        invalid_config = LoggerConfiguration(
            max_retry_attempts=-1
        )
        
        try:
            create_logger_with_validation(invalid_config)
            assert False, "Should raise exception for invalid config"
        except EventSessionLoggerError as e:
            assert "Configuration validation failed" in str(e), "Should raise validation error"
    
    print("✅ Logger with validation test passed")


async def run_all_tests():
    """Run all factory function tests"""
    print("=== Factory Functions Test Suite ===")
    print(f"Test started at: {datetime.now()}")
    print()
    
    tests = [
        test_logger_configuration,
        test_environment_configuration,
        test_basic_factory_functions,
        test_environment_specific_loggers,
        test_migration_logger,
        test_monitoring_logger,
        test_multi_transport_logger,
        test_configuration_validation,
        test_logger_info_printing,
        test_logger_with_validation
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=== TEST SUMMARY ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {len(tests)}")
    
    if failed == 0:
        print("🎉 All factory function tests passed!")
        return True
    else:
        print("❌ Some factory function tests failed!")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)