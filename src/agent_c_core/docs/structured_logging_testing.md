# Structured Logging Testing Infrastructure

This document provides comprehensive guidance on using the structured logging testing infrastructure to validate logging behavior in your applications.

## Overview

The structured logging testing infrastructure provides powerful tools for:

- **Log Capture**: Capturing and validating structured log entries
- **Assertion Helpers**: Rich assertion capabilities for log content and context
- **Mock Loggers**: Testing logging behavior without actual log output
- **Performance Testing**: Measuring logging overhead and performance
- **Context Validation**: Ensuring proper context propagation
- **Pattern Testing**: Common testing patterns for different application layers

## Quick Start

### Basic Log Capture and Assertion

```python
from agent_c.util.structured_logging.testing import temporary_log_capture
from agent_c.util.structured_logging import get_logger

def test_user_creation():
    """Test user creation logging."""
    with temporary_log_capture() as capture:
        logger = get_logger("test.user_service")
        
        # Your code that logs
        logger.info("User created", user_id="123", email="test@example.com")
        
        # Validate logging behavior
        capture.assert_logged("User created", level="info", 
                             user_id="123", email="test@example.com")
```

### Using Pytest Fixtures

```python
def test_with_fixtures(log_capture, isolated_context):
    """Test using pytest fixtures."""
    logger = get_logger("test.service")
    
    with LoggingContext(user_id="test-123", operation="test_op"):
        logger.info("Operation completed", status="success")
    
    # Validate context propagation
    log_capture.assert_context_propagated(user_id="test-123", operation="test_op")
    log_capture.assert_logged("Operation completed", status="success")
```

## Core Components

### StructuredLogCapture

The main component for capturing and validating structured logs.

```python
from agent_c.util.structured_logging.testing import StructuredLogCapture

capture = StructuredLogCapture()
capture.start_capture()
try:
    # Your logging code here
    logger.info("Test message", key="value")
    
    # Validate logs
    capture.assert_logged("Test message", level="info", key="value")
finally:
    capture.stop_capture()
```

#### Key Methods

- **`assert_logged(message_pattern, level, count, **context)`**: Assert log entry exists
- **`assert_not_logged(message_pattern, level, **context)`**: Assert log entry doesn't exist
- **`assert_context_propagated(**context)`**: Assert context in all entries
- **`assert_correlation_id_consistent()`**: Assert consistent correlation IDs
- **`get_entries(level, message_pattern, **context_filter)`**: Get filtered entries

### MockStructuredLogger

Mock logger for testing logging calls without actual output.

```python
from agent_c.util.structured_logging.testing import MockStructuredLogger

def test_service_logging():
    """Test service logging with mock logger."""
    mock_logger = MockStructuredLogger("test_service")
    
    # Your code that uses the logger
    service = UserService(logger=mock_logger)
    service.create_user({"id": "123", "email": "test@example.com"})
    
    # Validate logging calls
    mock_logger.assert_called_with("User creation started", level="info", 
                                  id="123", email="test@example.com")
    mock_logger.assert_called_with("User creation completed", level="info")
    
    assert mock_logger.get_call_count() == 2
    assert mock_logger.get_call_count(level="info") == 2
```

### PerformanceTester

Tool for measuring and validating logging performance.

```python
from agent_c.util.structured_logging.testing import PerformanceTester

def test_logging_performance():
    """Test logging performance overhead."""
    tester = PerformanceTester(max_duration_ms=1.0, max_overhead_percentage=5.0)
    
    for _ in range(100):
        with tester.measure_operation():
            logger.info("Performance test", data={"key": "value"})
    
    # Assert performance is acceptable
    tester.assert_performance_acceptable(baseline_ms=0.1)
    
    # Get performance summary
    summary = tester.get_summary()
    print(f"Average duration: {summary['avg_duration_ms']:.2f}ms")
```

## Pytest Fixtures

The testing infrastructure provides several pytest fixtures for easy integration.

### Available Fixtures

- **`log_capture`**: Provides StructuredLogCapture instance
- **`mock_logger`**: Provides MockStructuredLogger instance
- **`isolated_context`**: Ensures clean logging context for each test
- **`performance_tester`**: Provides PerformanceTester instance
- **`factory_reset`**: Resets StructuredLoggerFactory between tests

### Example Usage

```python
def test_with_all_fixtures(log_capture, mock_logger, isolated_context, performance_tester):
    """Test using multiple fixtures."""
    # Context is automatically isolated
    with LoggingContext(user_id="test-123"):
        # Performance is automatically measured
        with performance_tester.measure_operation():
            # Logs are automatically captured
            logger = get_logger("test.service")
            logger.info("Test operation", status="success")
    
    # Validate everything
    log_capture.assert_logged("Test operation", status="success")
    log_capture.assert_context_propagated(user_id="test-123")
    performance_tester.assert_performance_acceptable()
```

## Testing Patterns

### Repository Layer Testing

```python
def test_repository_logging():
    """Test repository layer logging patterns."""
    with temporary_log_capture() as capture:
        repo = UserRepository()
        
        # Test successful operation
        result = repo.create_user({"id": "user-123", "email": "test@example.com"})
        
        # Validate repository logging
        capture.assert_logged("Creating user", level="info", 
                             id="user-123", email="test@example.com")
        capture.assert_logged("Database operation completed", level="info")
        capture.assert_context_propagated(operation="create_user", user_id="user-123")
        capture.assert_not_logged(level="error")
        
        assert result["status"] == "created"
```

### Service Layer Testing

```python
def test_service_layer_logging():
    """Test service layer logging patterns."""
    with temporary_log_capture() as capture:
        service = NotificationService()
        
        result = service.send_notification("user-123", "welcome", "Welcome!")
        
        # Validate service logging
        capture.assert_logged("Notification send started", level="info", 
                             user_id="user-123", message_type="welcome")
        capture.assert_logged("Notification sent successfully", level="info")
        capture.assert_correlation_id_consistent()
        
        assert result["status"] == "sent"
```

### API Endpoint Testing

```python
def test_api_endpoint_logging():
    """Test API endpoint logging patterns."""
    with temporary_log_capture() as capture:
        response = api_handler({
            "email": "test@example.com",
            "correlation_id": "api-test-123"
        })
        
        # Validate API logging
        capture.assert_logged("API request received", level="info", 
                             method="POST", endpoint="/api/v2/users")
        capture.assert_logged("API request completed", level="info", 
                             status_code=201)
        capture.assert_context_propagated(correlation_id="api-test-123")
        
        assert response["status"] == 201
```

### Error Handling Testing

```python
def test_error_handling_logging():
    """Test error handling and logging patterns."""
    with temporary_log_capture() as capture:
        with pytest.raises(ValueError):
            service.invalid_operation()
        
        # Validate error logging
        capture.assert_logged("Operation started", level="info")
        capture.assert_logged("Operation failed", level="error", 
                             error_type="validation_error")
        capture.assert_not_logged("Operation completed")
```

### Performance Testing

```python
@performance_test(max_overhead_ms=2.0, iterations=50)
def test_logging_performance():
    """Test logging performance with decorator."""
    logger = get_logger("test.performance")
    
    with LoggingContext(user_id="perf-test", operation="performance_test"):
        logger.info("Performance test operation", 
                   data_size=1024, processing_time_ms=1.5)

def test_manual_performance_testing():
    """Test logging performance manually."""
    def logging_operation():
        logger.info("Test message", context={"key": "value"})
    
    summary = assert_log_performance(logging_operation, 
                                   max_duration_ms=1.0, 
                                   iterations=100)
    
    print(f"Average logging time: {summary['avg_duration_ms']:.2f}ms")
```

### Concurrent Logging Testing

```python
def test_concurrent_logging():
    """Test logging behavior under concurrent conditions."""
    def worker_function(worker_id):
        logger = get_logger(f"test.worker_{worker_id}")
        
        with LoggingContext(correlation_id=f"worker-{worker_id}", worker_id=worker_id):
            logger.info("Worker operation started")
            time.sleep(0.001)  # Simulate work
            logger.info("Worker operation completed", result="success")
    
    with temporary_log_capture() as capture:
        # Run workers concurrently
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(worker_function, i) for i in range(3)]
            for future in futures:
                future.result()
        
        # Validate concurrent logging
        assert len(capture.entries) == 6  # 3 workers * 2 log entries each
        
        for worker_id in range(3):
            worker_entries = capture.get_entries(worker_id=worker_id)
            assert len(worker_entries) == 2
            capture.assert_context_propagated(worker_id=worker_id)
```

### Async Logging Testing

```python
@pytest.mark.asyncio
async def test_async_logging():
    """Test async logging patterns."""
    async def async_operation():
        logger = get_logger("test.async")
        
        with LoggingContext(correlation_id="async-123", operation="async_op"):
            logger.info("Async operation started")
            await asyncio.sleep(0.001)  # Simulate async work
            logger.info("Async operation completed", status="success")
    
    with temporary_log_capture() as capture:
        await async_operation()
        
        # Validate async logging
        capture.assert_logged("Async operation started", level="info")
        capture.assert_logged("Async operation completed", level="info", status="success")
        capture.assert_context_propagated(correlation_id="async-123")
```

## Advanced Features

### Custom Log Entry Validation

```python
def test_custom_validation():
    """Test with custom log entry validation."""
    with temporary_log_capture() as capture:
        logger.info("Custom message", timestamp=time.time(), custom_field="value")
        
        # Get entries for custom validation
        entries = capture.get_entries(message_pattern="Custom message")
        assert len(entries) == 1
        
        entry = entries[0]
        assert entry.has_context(custom_field="value")
        assert "timestamp" in entry.context
        assert entry.context["timestamp"] > 0
```

### Performance Baseline Comparison

```python
def test_performance_with_baseline():
    """Test logging performance against baseline."""
    # Measure baseline (no logging)
    baseline_tester = PerformanceTester()
    for _ in range(100):
        with baseline_tester.measure_operation():
            pass  # No-op
    
    baseline_ms = baseline_tester.metrics.avg_duration_ms
    
    # Measure with logging
    logging_tester = PerformanceTester()
    for _ in range(100):
        with logging_tester.measure_operation():
            logger.info("Test message", data={"key": "value"})
    
    # Assert overhead is acceptable
    logging_tester.assert_performance_acceptable(baseline_ms=baseline_ms)
```

### Context Isolation Testing

```python
@with_isolated_context
def test_context_isolation():
    """Test that context is properly isolated."""
    # Context starts clean
    assert get_current_context().user_id is None
    
    with LoggingContext(user_id="test-123"):
        logger.info("Inside context")
        assert get_current_context().user_id == "test-123"
    
    # Context is cleaned up
    assert get_current_context().user_id is None
```

## Best Practices

### 1. Use Appropriate Fixtures

Choose the right fixtures for your test needs:

```python
# For basic log validation
def test_basic(log_capture):
    pass

# For context-sensitive tests
def test_with_context(log_capture, isolated_context):
    pass

# For performance-critical tests
def test_performance(log_capture, performance_tester):
    pass
```

### 2. Test Both Success and Failure Cases

```python
def test_complete_scenarios(log_capture):
    """Test both success and failure scenarios."""
    # Test success case
    result = service.operation(valid_data)
    log_capture.assert_logged("Operation completed", level="info")
    log_capture.assert_not_logged(level="error")
    
    # Clear logs and test failure case
    log_capture.clear()
    
    with pytest.raises(ValueError):
        service.operation(invalid_data)
    
    log_capture.assert_logged("Operation failed", level="error")
    log_capture.assert_not_logged("Operation completed")
```

### 3. Validate Context Propagation

```python
def test_context_propagation(log_capture, isolated_context):
    """Always test context propagation in multi-step operations."""
    with LoggingContext(correlation_id="test-123", user_id="user-456"):
        service.multi_step_operation()
    
    # Ensure context was propagated to all log entries
    log_capture.assert_context_propagated(correlation_id="test-123", user_id="user-456")
    log_capture.assert_correlation_id_consistent()
```

### 4. Test Performance Impact

```python
def test_logging_overhead(performance_tester):
    """Test that logging doesn't significantly impact performance."""
    # Measure critical path with logging
    for _ in range(100):
        with performance_tester.measure_operation():
            critical_business_operation()  # This includes logging
    
    # Assert performance is acceptable
    performance_tester.assert_performance_acceptable()
    
    # Log performance summary for monitoring
    summary = performance_tester.get_summary()
    logger.info("Performance test completed", **summary)
```

### 5. Use Descriptive Test Names and Assertions

```python
def test_user_creation_logs_all_required_information(log_capture):
    """Test that user creation logs all required audit information."""
    user_service.create_user({"id": "user-123", "email": "test@example.com"})
    
    # Be specific about what you're validating
    log_capture.assert_logged("User creation started", level="info", 
                             user_id="user-123", email="test@example.com")
    log_capture.assert_logged("User validation completed", level="debug")
    log_capture.assert_logged("Database insert executed", level="debug", table="users")
    log_capture.assert_logged("User creation completed", level="info", 
                             user_id="user-123", operation_duration_ms=lambda x: x > 0)
```

## Troubleshooting

### Common Issues

1. **Tests failing due to existing context**
   - Use `isolated_context` fixture or `clear_context()` in setup

2. **Performance tests are flaky**
   - Increase iteration count for more stable measurements
   - Use appropriate performance limits for your environment

3. **Log assertions failing unexpectedly**
   - Check log capture is properly started/stopped
   - Verify message patterns and context filters
   - Use `capture.entries` to inspect actual log entries

4. **Async tests not capturing logs**
   - Ensure proper async test setup with `@pytest.mark.asyncio`
   - Use `temporary_log_capture()` context manager

### Debugging Tips

```python
def debug_log_capture(log_capture):
    """Debug log capture issues."""
    # Print all captured entries
    for i, entry in enumerate(log_capture.entries):
        print(f"Entry {i}: {entry.level} - {entry.message}")
        print(f"  Context: {entry.context}")
    
    # Check specific filters
    filtered = log_capture.get_entries(level="info", user_id="123")
    print(f"Filtered entries: {len(filtered)}")
```

## Migration from Existing Tests

### Updating Existing Tests

1. **Add testing imports**:
```python
from agent_c.util.structured_logging.testing import temporary_log_capture, log_capture
```

2. **Replace manual log checking**:
```python
# Old way
with patch('logging.getLogger') as mock_logger:
    service.operation()
    mock_logger.assert_called_with("Expected message")

# New way
with temporary_log_capture() as capture:
    service.operation()
    capture.assert_logged("Expected message", level="info", user_id="123")
```

3. **Add context validation**:
```python
# Add context validation to existing tests
capture.assert_context_propagated(correlation_id="req-123")
capture.assert_correlation_id_consistent()
```

4. **Add performance validation**:
```python
# Add performance testing to critical paths
@performance_test(max_overhead_ms=5.0)
def test_critical_operation():
    service.critical_operation()
```

This testing infrastructure provides comprehensive tools for validating structured logging behavior, ensuring your logging implementation is correct, performant, and maintainable.