"""
Tests for structured logging formatters.
"""

import json
import logging
from unittest.mock import Mock, patch
import pytest

from agent_c.util.structured_logging.formatters import (
    StructuredConsoleFormatter,
    StructuredJSONFormatter,
    CompatibilityFormatter,
    get_console_formatter,
    get_json_formatter,
    get_compatibility_formatter,
    prepare_for_stdlib,
)


class TestStructuredConsoleFormatter:
    """Test the StructuredConsoleFormatter class."""
    
    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        formatter = StructuredConsoleFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        assert "Test message" in result
        assert "INFO" in result
    
    def test_format_with_structured_data(self):
        """Test formatting with structured data."""
        formatter = StructuredConsoleFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add structured data
        record.structured_data = {
            'user_id': 'user-123',
            'operation': 'create_session',
            'duration': 0.5,
            'metadata': {'key': 'value'}
        }
        
        result = formatter.format(record)
        assert "Test message" in result
        assert "user_id=user-123" in result
        assert "operation=create_session" in result
        assert "duration=0.5" in result
        assert '"key": "value"' in result  # JSON formatted metadata
    
    def test_format_filters_internal_fields(self):
        """Test that internal fields are filtered out."""
        formatter = StructuredConsoleFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add structured data with internal fields
        record.structured_data = {
            'user_id': 'user-123',
            'event': 'should_be_filtered',
            'message': 'should_be_filtered',
            'level': 'should_be_filtered',
            'logger': 'should_be_filtered',
            'timestamp': 'should_be_filtered'
        }
        
        result = formatter.format(record)
        assert "user_id=user-123" in result
        assert "should_be_filtered" not in result
    
    def test_format_without_structured_data(self):
        """Test formatting without structured data."""
        formatter = StructuredConsoleFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        assert "Test message" in result
        # Check that there's no structured data section (should not contain " ["
        # which would indicate structured data, but ANSI color codes may contain "["
        assert " [" not in result  # No structured data section


class TestStructuredJSONFormatter:
    """Test the StructuredJSONFormatter class."""
    
    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        result = formatter.format(record)
        data = json.loads(result)
        
        assert data['level'] == 'INFO'
        assert data['logger'] == 'test.logger'
        assert data['message'] == 'Test message'
        assert 'timestamp' in data
    
    def test_format_with_structured_data(self):
        """Test formatting with structured data."""
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add structured data
        record.structured_data = {
            'user_id': 'user-123',
            'operation': 'create_session',
            'duration': 0.5
        }
        
        result = formatter.format(record)
        data = json.loads(result)
        
        assert data['user_id'] == 'user-123'
        assert data['operation'] == 'create_session'
        assert data['duration'] == 0.5
    
    def test_format_with_exception(self):
        """Test formatting with exception information."""
        formatter = StructuredJSONFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=sys.exc_info()  # Pass actual exception info, not True
            )
        
        result = formatter.format(record)
        data = json.loads(result)
        
        assert data['level'] == 'ERROR'
        assert data['message'] == 'Error occurred'
        assert 'exception' in data
        assert 'ValueError: Test exception' in data['exception']
    
    def test_format_with_stack_info(self):
        """Test formatting with stack information."""
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.stack_info = "Stack trace here"
        
        result = formatter.format(record)
        data = json.loads(result)
        
        assert data['stack_info'] == "Stack trace here"
    
    def test_json_serialization_of_complex_objects(self):
        """Test that complex objects are properly serialized."""
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add complex structured data
        from datetime import datetime
        record.structured_data = {
            'timestamp': datetime.now(),
            'complex_object': {'nested': {'data': True}}
        }
        
        result = formatter.format(record)
        data = json.loads(result)  # Should not raise an exception
        
        assert isinstance(data['timestamp'], str)  # datetime converted to string
        assert data['complex_object']['nested']['data'] is True


class TestCompatibilityFormatter:
    """Test the CompatibilityFormatter class."""
    
    def test_init_with_colors(self):
        """Test initialization with colors enabled."""
        formatter = CompatibilityFormatter(use_colors=True)
        assert formatter.use_colors is True
        assert hasattr(formatter, 'colored_formatter')
    
    def test_init_without_colors(self):
        """Test initialization with colors disabled."""
        formatter = CompatibilityFormatter(use_colors=False)
        assert formatter.use_colors is False
    
    def test_format_structured_record_with_colors(self):
        """Test formatting structured record with colors."""
        formatter = CompatibilityFormatter(use_colors=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.structured_data = {'user_id': 'user-123'}
        
        result = formatter.format(record)
        assert "Test message" in result
        assert "user_id=user-123" in result
    
    def test_format_structured_record_without_colors(self):
        """Test formatting structured record without colors."""
        formatter = CompatibilityFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        record.structured_data = {'user_id': 'user-123'}
        
        result = formatter.format(record)
        data = json.loads(result)  # Should be JSON format
        assert data['message'] == 'Test message'
        assert data['user_id'] == 'user-123'
    
    def test_format_traditional_record_with_colors(self):
        """Test formatting traditional record with colors."""
        formatter = CompatibilityFormatter(use_colors=True)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        # No structured_data attribute
        
        with patch.object(formatter, 'colored_formatter') as mock_colored:
            mock_colored.format.return_value = "Colored output"
            result = formatter.format(record)
            assert result == "Colored output"
            mock_colored.format.assert_called_once_with(record)
    
    def test_format_traditional_record_without_colors(self):
        """Test formatting traditional record without colors."""
        formatter = CompatibilityFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        # No structured_data attribute
        
        result = formatter.format(record)
        # Should use parent formatter (basic formatting)
        assert "Test message" in result


class TestFormatterFactoryFunctions:
    """Test the formatter factory functions."""
    
    def test_get_console_formatter(self):
        """Test get_console_formatter function."""
        formatter = get_console_formatter()
        assert isinstance(formatter, StructuredConsoleFormatter)
    
    def test_get_json_formatter(self):
        """Test get_json_formatter function."""
        formatter = get_json_formatter()
        assert isinstance(formatter, StructuredJSONFormatter)
    
    def test_get_compatibility_formatter_with_colors(self):
        """Test get_compatibility_formatter with colors."""
        formatter = get_compatibility_formatter(use_colors=True)
        assert isinstance(formatter, CompatibilityFormatter)
        assert formatter.use_colors is True
    
    def test_get_compatibility_formatter_without_colors(self):
        """Test get_compatibility_formatter without colors."""
        formatter = get_compatibility_formatter(use_colors=False)
        assert isinstance(formatter, CompatibilityFormatter)
        assert formatter.use_colors is False
    
    def test_get_compatibility_formatter_default(self):
        """Test get_compatibility_formatter with default parameters."""
        formatter = get_compatibility_formatter()
        assert isinstance(formatter, CompatibilityFormatter)
        assert formatter.use_colors is True  # Default should be True


class TestPrepareForStdlibProcessor:
    """Test the prepare_for_stdlib processor."""
    
    def test_prepare_for_stdlib_basic(self):
        """Test basic preparation for stdlib logging."""
        event_dict = {
            'event': 'Test message',
            'user_id': 'user-123',
            'operation': 'create_session'
        }
        
        result = prepare_for_stdlib(None, 'info', event_dict)
        
        assert result['event'] == 'Test message'
        assert result['structured_data']['user_id'] == 'user-123'
        assert result['structured_data']['operation'] == 'create_session'
        assert 'event' not in result['structured_data']
    
    def test_prepare_for_stdlib_no_event(self):
        """Test preparation when no event key is present."""
        event_dict = {
            'user_id': 'user-123',
            'operation': 'create_session'
        }
        
        result = prepare_for_stdlib(None, 'info', event_dict)
        
        assert result['event'] == ''
        assert result['structured_data']['user_id'] == 'user-123'
        assert result['structured_data']['operation'] == 'create_session'
    
    def test_prepare_for_stdlib_empty_dict(self):
        """Test preparation with empty event dictionary."""
        event_dict = {}
        
        result = prepare_for_stdlib(None, 'info', event_dict)
        
        assert result['event'] == ''
        assert result['structured_data'] == {}
    
    def test_prepare_for_stdlib_only_event(self):
        """Test preparation with only event key."""
        event_dict = {'event': 'Test message'}
        
        result = prepare_for_stdlib(None, 'info', event_dict)
        
        assert result['event'] == 'Test message'
        assert result['structured_data'] == {}


class TestFormatterIntegration:
    """Integration tests for formatters."""
    
    def test_console_formatter_with_real_logger(self):
        """Test console formatter with a real logger."""
        import io
        import sys
        
        # Capture output
        captured_output = io.StringIO()
        handler = logging.StreamHandler(captured_output)
        handler.setFormatter(StructuredConsoleFormatter())
        
        logger = logging.getLogger("test.integration")
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        # Create a record with structured data
        record = logging.LogRecord(
            name="test.integration",
            level=logging.INFO,
            pathname="test.py",
            lineno=42,
            msg="Integration test",
            args=(),
            exc_info=None
        )
        record.structured_data = {'test_key': 'test_value'}
        
        logger.handle(record)
        
        output = captured_output.getvalue()
        assert "Integration test" in output
        assert "test_key=test_value" in output
        
        # Clean up
        logger.removeHandler(handler)
    
    def test_json_formatter_produces_valid_json(self):
        """Test that JSON formatter always produces valid JSON."""
        formatter = StructuredJSONFormatter()
        
        # Test various record types
        records = [
            # Basic record
            logging.LogRecord("test", logging.INFO, "test.py", 42, "Test", (), None),
            # Record with structured data
            logging.LogRecord("test", logging.INFO, "test.py", 42, "Test", (), None),
            # Record with exception
            logging.LogRecord("test", logging.ERROR, "test.py", 42, "Error", (), True),
        ]
        
        # Add structured data to second record
        records[1].structured_data = {'key': 'value', 'number': 42}
        
        for record in records:
            result = formatter.format(record)
            # Should not raise an exception
            data = json.loads(result)
            assert isinstance(data, dict)
            assert 'level' in data
            assert 'message' in data