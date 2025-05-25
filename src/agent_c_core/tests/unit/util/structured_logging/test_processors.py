"""
Unit tests for structured logging processors.

This module tests all the core processors to ensure they work correctly
and provide the expected log enrichment functionality.
"""

import time
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
from typing import Dict, Any

from agent_c.util.structured_logging.processors import (
    add_framework_context,
    add_correlation_id,
    add_timing_info,
    enrich_errors,
    add_agent_context,
    filter_sensitive_data,
    get_default_processors,
    get_simple_processors,
    _get_recovery_hint
)
from agent_c.util.structured_logging.context import LoggingContext


class TestFrameworkContextProcessor:
    """Test the framework context processor."""
    
    def test_adds_framework_metadata(self):
        """Test that framework metadata is added."""
        event_dict = {"event": "test_event"}
        
        result = add_framework_context(None, "info", event_dict)
        
        assert result["framework"] == "agent_c"
        assert "framework_version" in result
        assert result["event"] == "test_event"  # Original data preserved
    
    def test_injects_context_variables(self):
        """Test that context variables are injected."""
        with LoggingContext(correlation_id="req-123", agent_id="agent-456"):
            event_dict = {"event": "test_event"}
            
            result = add_framework_context(None, "info", event_dict)
            
            assert result["correlation_id"] == "req-123"
            assert result["agent_id"] == "agent-456"
            assert result["event"] == "test_event"
    
    def test_does_not_override_explicit_values(self):
        """Test that explicit values in event_dict are not overridden."""
        with LoggingContext(correlation_id="req-123"):
            event_dict = {"event": "test_event", "correlation_id": "explicit-456"}
            
            result = add_framework_context(None, "info", event_dict)
            
            # Should keep the explicit value, not the context value
            assert result["correlation_id"] == "explicit-456"
    
    def test_empty_context(self):
        """Test behavior with empty context."""
        event_dict = {"event": "test_event"}
        
        result = add_framework_context(None, "info", event_dict)
        
        # Should still add framework metadata
        assert result["framework"] == "agent_c"
        assert "framework_version" in result
        # No context variables should be added
        assert "correlation_id" not in result
        assert "agent_id" not in result


class TestCorrelationIDProcessor:
    """Test the correlation ID processor."""
    
    def test_preserves_existing_correlation_id(self):
        """Test that existing correlation ID is preserved."""
        event_dict = {"event": "test", "correlation_id": "existing-123"}
        
        result = add_correlation_id(None, "info", event_dict)
        
        assert result["correlation_id"] == "existing-123"
    
    def test_missing_correlation_id(self):
        """Test behavior when correlation ID is missing."""
        event_dict = {"event": "test"}
        
        result = add_correlation_id(None, "info", event_dict)
        
        # Should not add correlation_id if missing (current implementation)
        assert "correlation_id" not in result
        assert result["event"] == "test"


class TestTimingProcessor:
    """Test the timing information processor."""
    
    def test_adds_timestamp(self):
        """Test that ISO timestamp is added."""
        event_dict = {"event": "test"}
        
        with patch('agent_c.util.structured_logging.processors.datetime') as mock_dt:
            mock_dt.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"
            
            result = add_timing_info(None, "info", event_dict)
            
            assert result["timestamp"] == "2023-01-01T12:00:00Z"
    
    def test_preserves_existing_timestamp(self):
        """Test that existing timestamp is preserved."""
        event_dict = {"event": "test", "timestamp": "existing-timestamp"}
        
        result = add_timing_info(None, "info", event_dict)
        
        assert result["timestamp"] == "existing-timestamp"
    
    def test_adds_nanosecond_timestamp(self):
        """Test that high-precision timestamp is added."""
        event_dict = {"event": "test"}
        
        with patch('time.time_ns', return_value=1234567890123456789):
            result = add_timing_info(None, "info", event_dict)
            
            assert result["time_ns"] == 1234567890123456789
    
    def test_preserves_existing_time_ns(self):
        """Test that existing time_ns is preserved."""
        event_dict = {"event": "test", "time_ns": 999999999}
        
        result = add_timing_info(None, "info", event_dict)
        
        assert result["time_ns"] == 999999999


class TestErrorEnrichmentProcessor:
    """Test the error enrichment processor."""
    
    def test_enriches_error_level_logs(self):
        """Test that error-level logs are enriched."""
        event_dict = {"event": "something_failed"}
        
        result = enrich_errors(None, "error", event_dict)
        
        assert result["error_category"] == "unknown"
        assert "recovery_hint" in result
    
    def test_enriches_critical_level_logs(self):
        """Test that critical-level logs are enriched."""
        event_dict = {"event": "system_failure"}
        
        result = enrich_errors(None, "critical", event_dict)
        
        assert result["error_category"] == "unknown"
        assert "recovery_hint" in result
    
    def test_does_not_enrich_info_logs(self):
        """Test that info-level logs are not enriched."""
        event_dict = {"event": "normal_operation"}
        
        result = enrich_errors(None, "info", event_dict)
        
        assert "error_category" not in result
        assert "recovery_hint" not in result
        assert result["event"] == "normal_operation"
    
    def test_preserves_existing_error_category(self):
        """Test that existing error category is preserved."""
        event_dict = {"event": "test", "error_category": "validation"}
        
        result = enrich_errors(None, "error", event_dict)
        
        assert result["error_category"] == "validation"
    
    def test_adds_stack_trace_for_exceptions(self):
        """Test that stack trace is added for exceptions."""
        event_dict = {"event": "exception_occurred", "exc_info": True}
        
        with patch('traceback.format_exc', return_value="Mock stack trace"):
            result = enrich_errors(None, "exception", event_dict)
            
            assert result["stack_trace"] == "Mock stack trace"
    
    def test_preserves_existing_stack_trace(self):
        """Test that existing stack trace is preserved."""
        event_dict = {
            "event": "test", 
            "exc_info": True,
            "stack_trace": "existing trace"
        }
        
        result = enrich_errors(None, "error", event_dict)
        
        assert result["stack_trace"] == "existing trace"


class TestRecoveryHints:
    """Test the recovery hint generation."""
    
    def test_redis_connection_hint(self):
        """Test recovery hint for Redis connection errors."""
        event_dict = {"event": "redis_connection_failed"}
        
        hint = _get_recovery_hint(event_dict)
        
        assert "Redis connection" in hint
        assert "retry" in hint
    
    def test_session_not_found_hint(self):
        """Test recovery hint for session not found errors."""
        event_dict = {"event": "session_not_found"}
        
        hint = _get_recovery_hint(event_dict)
        
        assert "session ID" in hint
        assert "expiration" in hint
    
    def test_validation_error_hint(self):
        """Test recovery hint for validation errors."""
        event_dict = {"event": "validation_failed"}
        
        hint = _get_recovery_hint(event_dict)
        
        assert "input parameters" in hint
        assert "format" in hint
    
    def test_permission_error_hint(self):
        """Test recovery hint for permission errors."""
        event_dict = {"event": "unauthorized_access"}
        
        hint = _get_recovery_hint(event_dict)
        
        assert "permissions" in hint
        assert "authentication" in hint
    
    def test_generic_hint(self):
        """Test generic recovery hint for unknown errors."""
        event_dict = {"event": "unknown_error"}
        
        hint = _get_recovery_hint(event_dict)
        
        assert "Check logs" in hint
        assert "retry" in hint


class TestAgentContextProcessor:
    """Test the agent context processor."""
    
    def test_detects_chat_events(self):
        """Test detection and enrichment of chat events."""
        event_dict = {"event": "chat_message_sent"}
        
        result = add_agent_context(None, "info", event_dict)
        
        assert result["component"] == "agent"
        assert result["operation_type"] == "conversation"
    
    def test_detects_tool_events(self):
        """Test detection and enrichment of tool events."""
        event_dict = {"event": "tool_execution_started"}
        
        result = add_agent_context(None, "info", event_dict)
        
        assert result["component"] == "agent"
        assert result["operation_type"] == "tool_usage"
    
    def test_detects_agent_events(self):
        """Test detection and enrichment of agent events."""
        event_dict = {"event": "agent_created"}
        
        result = add_agent_context(None, "info", event_dict)
        
        assert result["component"] == "agent"
        assert result["operation_type"] == "agent_management"
    
    def test_ignores_non_agent_events(self):
        """Test that non-agent events are not enriched."""
        event_dict = {"event": "database_query"}
        
        result = add_agent_context(None, "info", event_dict)
        
        assert "component" not in result
        assert "operation_type" not in result
        assert result["event"] == "database_query"
    
    def test_does_not_override_existing_values(self):
        """Test that existing component/operation_type values are preserved."""
        event_dict = {
            "event": "chat_started",
            "component": "custom",
            "operation_type": "custom_op"
        }
        
        result = add_agent_context(None, "info", event_dict)
        
        assert result["component"] == "custom"
        assert result["operation_type"] == "custom_op"


class TestSensitiveDataFilter:
    """Test the sensitive data filtering processor."""
    
    def test_filters_password_fields(self):
        """Test that password fields are redacted."""
        event_dict = {
            "event": "login_attempt",
            "username": "user123",
            "password": "secret123"
        }
        
        result = filter_sensitive_data(None, "info", event_dict)
        
        assert result["username"] == "user123"  # Not sensitive
        assert result["password"] == "[REDACTED]"
    
    def test_filters_token_fields(self):
        """Test that token fields are redacted."""
        event_dict = {
            "event": "api_call",
            "api_key": "abc123xyz",
            "access_token": "bearer_token_here"
        }
        
        result = filter_sensitive_data(None, "info", event_dict)
        
        assert result["api_key"] == "[REDACTED]"
        assert result["access_token"] == "[REDACTED]"
    
    def test_filters_sensitive_message_content(self):
        """Test that sensitive content in messages is masked."""
        event_dict = {
            "event": "processing_request",
            "message": "Processing token abc123def456ghi789jkl012mno345pqr678stu901vwx234"
        }
        
        result = filter_sensitive_data(None, "info", event_dict)
        
        # Long alphanumeric strings should be masked
        assert "[TOKEN]" in result["message"]
        assert "abc123def456ghi789jkl012mno345pqr678stu901vwx234" not in result["message"]
    
    def test_preserves_non_sensitive_data(self):
        """Test that non-sensitive data is preserved."""
        event_dict = {
            "event": "user_action",
            "user_id": "user123",
            "action": "view_page",
            "page": "dashboard"
        }
        
        result = filter_sensitive_data(None, "info", event_dict)
        
        assert result["user_id"] == "user123"
        assert result["action"] == "view_page"
        assert result["page"] == "dashboard"


class TestDefaultProcessors:
    """Test the default processor chain."""
    
    def test_returns_processor_list(self):
        """Test that get_default_processors returns a list."""
        processors = get_default_processors()
        
        assert isinstance(processors, list)
        assert len(processors) > 0
    
    def test_includes_framework_processors(self):
        """Test that framework-specific processors are included."""
        processors = get_default_processors()
        
        # Check that our custom processors are in the chain
        assert add_framework_context in processors
        assert add_correlation_id in processors
        assert add_timing_info in processors
        assert enrich_errors in processors
        assert add_agent_context in processors
        assert filter_sensitive_data in processors
    
    def test_includes_structlog_processors(self):
        """Test that standard structlog processors are included."""
        import structlog
        
        processors = get_default_processors()
        
        # Check for some standard structlog processors
        assert structlog.stdlib.filter_by_level in processors
        assert structlog.stdlib.add_logger_name in processors
        assert structlog.stdlib.add_log_level in processors
    
    def test_simple_processors(self):
        """Test the simplified processor chain."""
        processors = get_simple_processors()
        
        assert isinstance(processors, list)
        assert len(processors) > 0
        
        # Check that our custom processors are included
        assert add_framework_context in processors
        assert add_correlation_id in processors
        assert add_timing_info in processors
        assert enrich_errors in processors
        assert add_agent_context in processors
        assert filter_sensitive_data in processors
        
        # Should not include stdlib-specific processors
        import structlog
        assert structlog.stdlib.filter_by_level not in processors
        assert structlog.stdlib.add_logger_name not in processors


class TestProcessorPerformance:
    """Test processor performance characteristics."""
    
    def test_framework_context_performance(self):
        """Test that framework context processor is fast."""
        event_dict = {"event": "performance_test"}
        
        start_time = time.perf_counter()
        for _ in range(1000):
            add_framework_context(None, "info", event_dict.copy())
        end_time = time.perf_counter()
        
        # Should be very fast - less than 1ms per call on average
        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.001, f"Framework context processor too slow: {avg_time:.6f}s"
    
    def test_error_enrichment_performance(self):
        """Test that error enrichment processor is fast."""
        event_dict = {"event": "error_test"}
        
        start_time = time.perf_counter()
        for _ in range(1000):
            enrich_errors(None, "error", event_dict.copy())
        end_time = time.perf_counter()
        
        # Should be fast even for error processing
        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.001, f"Error enrichment processor too slow: {avg_time:.6f}s"
    
    def test_sensitive_data_filter_performance(self):
        """Test that sensitive data filter is reasonably fast."""
        event_dict = {
            "event": "performance_test",
            "message": "This is a test message with some content",
            "user_id": "user123",
            "session_id": "session456"
        }
        
        start_time = time.perf_counter()
        for _ in range(1000):
            filter_sensitive_data(None, "info", event_dict.copy())
        end_time = time.perf_counter()
        
        # Should be reasonably fast even with regex processing
        avg_time = (end_time - start_time) / 1000
        assert avg_time < 0.002, f"Sensitive data filter too slow: {avg_time:.6f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])