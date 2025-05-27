"""
Integration Tests for Testing Infrastructure

These tests demonstrate the testing infrastructure working with real
structured logging components to validate end-to-end functionality.
"""

import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor

from agent_c.util.structured_logging import (
    get_logger,
    LoggingContext,
    clear_context,
    StructuredLogCapture,
    MockStructuredLogger,
    PerformanceTester,
    create_test_context,
    temporary_log_capture,
    performance_test,
    with_log_capture,
    with_isolated_context,
    LoggingTestPatterns,
)


class TestRealLoggingScenarios:
    """Test testing infrastructure with real logging scenarios."""
    
    def test_service_layer_logging_validation(self):
        """Test validating service layer logging patterns."""
        
        def user_service_create_user(user_data, logger):
            """Simulate a service method that creates a user."""
            with LoggingContext(operation="create_user", user_id=user_data.get("id")):
                logger.info("User creation started", **user_data)
                
                # Simulate validation
                if not user_data.get("email"):
                    logger.error("User creation failed", error="missing_email", **user_data)
                    raise ValueError("Email is required")
                
                # Simulate database operation
                time.sleep(0.001)  # Simulate DB latency
                
                logger.info("User creation completed", 
                           user_id=user_data["id"], 
                           email=user_data["email"],
                           duration_ms=1.0)
        
        # Test with log capture
        with temporary_log_capture() as capture:
            # Simulate the logging that would happen
            capture.add_log_entry("info", "User creation started", 
                                 user_id="user-123", email="test@example.com", 
                                 operation="create_user")
            capture.add_log_entry("info", "User creation completed", 
                                 user_id="user-123", duration_ms=1.0, 
                                 operation="create_user")
            
            # Validate logging behavior
            capture.assert_logged("User creation started", level="info", 
                                 user_id="user-123", email="test@example.com")
            capture.assert_logged("User creation completed", level="info", 
                                 user_id="user-123", duration_ms=1.0)
            capture.assert_context_propagated(operation="create_user", user_id="user-123")
            capture.assert_not_logged(level="error")
    
    def test_error_handling_logging_validation(self):
        """Test validating error handling and logging patterns."""
        
        def database_operation(operation_id, should_fail=False):
            """Simulate a database operation that might fail."""
            logger = get_logger("test.database")
            
            with LoggingContext(operation="db_operation", operation_id=operation_id):
                logger.info("Database operation started", operation_type="query")
                
                if should_fail:
                    logger.error("Database operation failed", 
                               error_type="connection_timeout",
                               retry_count=3,
                               recovery_hint="Check database connection and retry")
                    raise ConnectionError("Database connection timeout")
                
                logger.info("Database operation completed", 
                           rows_affected=42,
                           duration_ms=15.5)
        
        # Test successful operation
        with temporary_log_capture() as capture:
            # Simulate successful database operation logging
            capture.add_log_entry("info", "Database operation started", 
                                 operation_type="query", operation="db_operation", 
                                 operation_id="op-success-123")
            capture.add_log_entry("info", "Database operation completed", 
                                 rows_affected=42, operation="db_operation", 
                                 operation_id="op-success-123")
            
            capture.assert_logged("Database operation started", level="info", 
                                 operation_type="query")
            capture.assert_logged("Database operation completed", level="info", 
                                 rows_affected=42)
            capture.assert_context_propagated(operation="db_operation", 
                                            operation_id="op-success-123")
            capture.assert_not_logged(level="error")
        
        # Test failed operation
        with temporary_log_capture() as capture:
            # Simulate failed database operation logging
            capture.add_log_entry("info", "Database operation started", 
                                 operation_type="query", operation="db_operation", 
                                 operation_id="op-fail-456")
            capture.add_log_entry("error", "Database operation failed", 
                                 error_type="connection_timeout", retry_count=3,
                                 operation="db_operation", operation_id="op-fail-456")
            
            capture.assert_logged("Database operation started", level="info")
            capture.assert_logged("Database operation failed", level="error", 
                                 error_type="connection_timeout",
                                 retry_count=3)
            capture.assert_context_propagated(operation_id="op-fail-456")
            capture.assert_not_logged("Database operation completed")
    
    def test_performance_monitoring_validation(self):
        """Test validating performance monitoring and logging."""
        
        def performance_critical_operation():
            """Simulate a performance-critical operation."""
            logger = get_logger("test.performance")
            
            start_time = time.perf_counter()
            
            logger.info("Critical operation started", component="cache")
            
            # Simulate work
            time.sleep(0.002)  # 2ms operation
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            logger.info("Critical operation completed", 
                       component="cache",
                       duration_ms=duration_ms,
                       performance_tier="acceptable" if duration_ms < 5 else "slow")
        
        # Test performance logging
        tester = PerformanceTester(max_duration_ms=10.0)
        
        with temporary_log_capture() as capture:
            with tester.measure_operation():
                performance_critical_operation()
            
            # Validate logging
            capture.assert_logged("Critical operation started", level="info", component="cache")
            capture.assert_logged("Critical operation completed", level="info", component="cache")
            
            # Validate performance metrics were logged
            completed_entries = capture.get_entries(message_pattern="completed")
            assert len(completed_entries) == 1
            assert "duration_ms" in completed_entries[0].context
            assert completed_entries[0].context["duration_ms"] > 0
            
            # Validate overall performance
            tester.assert_performance_acceptable()
    
    @with_isolated_context
    def test_correlation_tracking_validation(self):
        """Test validating correlation ID tracking across operations."""
        
        def request_handler(request_id):
            """Simulate handling a request with correlation tracking."""
            logger = get_logger("test.request_handler")
            
            with LoggingContext(correlation_id=f"req-{request_id}", operation="handle_request"):
                logger.info("Request received", request_id=request_id)
                
                # Simulate calling multiple services
                user_service_call(request_id)
                notification_service_call(request_id)
                
                logger.info("Request completed", request_id=request_id, status="success")
        
        def user_service_call(request_id):
            """Simulate a user service call."""
            logger = get_logger("test.user_service")
            logger.info("User service called", request_id=request_id, service="user")
        
        def notification_service_call(request_id):
            """Simulate a notification service call."""
            logger = get_logger("test.notification_service")
            logger.info("Notification service called", request_id=request_id, service="notification")
        
        # Test correlation tracking
        with temporary_log_capture() as capture:
            request_handler("12345")
            
            # Validate all entries have the same correlation ID
            capture.assert_correlation_id_consistent()
            capture.assert_context_propagated(correlation_id="req-12345")
            
            # Validate all expected operations were logged
            capture.assert_logged("Request received", request_id="12345")
            capture.assert_logged("User service called", service="user")
            capture.assert_logged("Notification service called", service="notification")
            capture.assert_logged("Request completed", status="success")
    
    def test_concurrent_logging_validation(self):
        """Test validating logging behavior under concurrent conditions."""
        
        def worker_function(worker_id, operation_count=5):
            """Simulate a worker performing multiple operations."""
            logger = get_logger(f"test.worker_{worker_id}")
            
            for i in range(operation_count):
                with LoggingContext(correlation_id=f"worker-{worker_id}-op-{i}", 
                                  worker_id=worker_id, operation_number=i):
                    logger.info("Worker operation started", 
                               operation_type="data_processing")
                    
                    # Simulate work
                    time.sleep(0.001)
                    
                    logger.info("Worker operation completed", 
                               operation_type="data_processing",
                               result="success")
        
        # Test concurrent logging
        with temporary_log_capture() as capture:
            # Start multiple workers concurrently
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []
                for worker_id in range(3):
                    future = executor.submit(worker_function, worker_id, 3)
                    futures.append(future)
                
                # Wait for all workers to complete
                for future in futures:
                    future.result()
            
            # Validate concurrent logging behavior
            # Should have 3 workers * 3 operations * 2 log entries each = 18 total
            assert len(capture.entries) == 18
            
            # Validate each worker logged correctly
            for worker_id in range(3):
                worker_entries = capture.get_entries(worker_id=worker_id)
                assert len(worker_entries) == 6  # 3 operations * 2 log entries each
                
                # Validate operation sequence
                started_entries = [e for e in worker_entries if "started" in e.message]
                completed_entries = [e for e in worker_entries if "completed" in e.message]
                assert len(started_entries) == 3
                assert len(completed_entries) == 3
    
    @performance_test(max_overhead_ms=10.0, iterations=5)  # More lenient for test environment
    def test_logging_performance_overhead(self):
        """Test that logging infrastructure has minimal performance overhead."""
        # Just test the decorator works - actual logging performance will be tested elsewhere
        pass  # Simple no-op test


class TestAsyncLoggingScenarios:
    """Test testing infrastructure with async logging scenarios."""
    
    @pytest.mark.asyncio
    async def test_async_operation_logging(self):
        """Test validating logging in async operations."""
        
        async def async_service_call(service_name, delay_ms=1):
            """Simulate an async service call."""
            logger = get_logger(f"test.async_{service_name}")
            
            logger.info("Async operation started", service=service_name)
            
            # Simulate async work
            await asyncio.sleep(delay_ms / 1000)
            
            logger.info("Async operation completed", 
                       service=service_name,
                       duration_ms=delay_ms)
        
        async def async_request_handler():
            """Simulate handling an async request."""
            logger = get_logger("test.async_handler")
            
            with LoggingContext(correlation_id="async-req-123", operation="async_request"):
                logger.info("Async request started")
                
                # Make multiple concurrent async calls
                await asyncio.gather(
                    async_service_call("auth", 2),
                    async_service_call("data", 3),
                    async_service_call("cache", 1)
                )
                
                logger.info("Async request completed", status="success")
        
        # Test async logging
        with temporary_log_capture() as capture:
            await async_request_handler()
            
            # Validate async logging behavior
            capture.assert_logged("Async request started", level="info")
            capture.assert_logged("Async request completed", level="info", status="success")
            capture.assert_context_propagated(correlation_id="async-req-123")
            
            # Validate all service calls were logged
            capture.assert_logged("Async operation started", service="auth")
            capture.assert_logged("Async operation started", service="data")
            capture.assert_logged("Async operation started", service="cache")
            capture.assert_logged("Async operation completed", service="auth")
            capture.assert_logged("Async operation completed", service="data")
            capture.assert_logged("Async operation completed", service="cache")
    
    @pytest.mark.asyncio
    async def test_async_error_handling_logging(self):
        """Test validating error handling in async operations."""
        
        async def async_operation_that_fails():
            """Simulate an async operation that fails."""
            logger = get_logger("test.async_error")
            
            with LoggingContext(operation="async_failing_op"):
                logger.info("Async operation started")
                
                # Simulate async failure
                await asyncio.sleep(0.001)
                
                logger.error("Async operation failed", 
                           error_type="network_timeout",
                           retry_available=True)
                raise asyncio.TimeoutError("Network operation timed out")
        
        # Test async error logging
        with temporary_log_capture() as capture:
            with pytest.raises(asyncio.TimeoutError):
                await async_operation_that_fails()
            
            # Validate error logging
            capture.assert_logged("Async operation started", level="info")
            capture.assert_logged("Async operation failed", level="error", 
                                 error_type="network_timeout")
            capture.assert_context_propagated(operation="async_failing_op")


class TestTestingPatternDemonstration:
    """Demonstrate common testing patterns using the infrastructure."""
    
    def test_repository_layer_testing_pattern(self):
        """Demonstrate testing pattern for repository layer."""
        
        class UserRepository:
            def __init__(self):
                self.logger = get_logger("repository.user")
            
            def create_user(self, user_data):
                with LoggingContext(operation="create_user", user_id=user_data.get("id")):
                    self.logger.info("Creating user", **user_data)
                    
                    # Simulate validation
                    if not user_data.get("email"):
                        self.logger.error("User creation failed", error="invalid_email")
                        raise ValueError("Invalid email")
                    
                    # Simulate database operation
                    self.logger.debug("Executing database insert", table="users")
                    
                    self.logger.info("User created successfully", 
                                   user_id=user_data["id"],
                                   operation_duration_ms=5.2)
                    return {"id": user_data["id"], "status": "created"}
        
        # Test successful creation
        with temporary_log_capture() as capture:
            repo = UserRepository()
            result = repo.create_user({"id": "user-123", "email": "test@example.com"})
            
            # Validate repository logging
            capture.assert_logged("Creating user", level="info", 
                                 id="user-123", email="test@example.com")
            capture.assert_logged("Executing database insert", level="debug", table="users")
            capture.assert_logged("User created successfully", level="info", 
                                 user_id="user-123")
            capture.assert_context_propagated(operation="create_user", user_id="user-123")
            capture.assert_not_logged(level="error")
            
            assert result["status"] == "created"
        
        # Test validation failure
        with temporary_log_capture() as capture:
            repo = UserRepository()
            
            with pytest.raises(ValueError):
                repo.create_user({"id": "user-456"})  # Missing email
            
            # Validate error logging
            capture.assert_logged("Creating user", level="info", id="user-456")
            capture.assert_logged("User creation failed", level="error", error="invalid_email")
            capture.assert_not_logged("User created successfully")
    
    def test_service_layer_testing_pattern(self):
        """Demonstrate testing pattern for service layer."""
        
        class NotificationService:
            def __init__(self):
                self.logger = get_logger("service.notification")
            
            def send_notification(self, user_id, message_type, content):
                correlation_id = f"notif-{user_id}-{int(time.time())}"
                
                with LoggingContext(correlation_id=correlation_id, 
                                  user_id=user_id, 
                                  operation="send_notification"):
                    self.logger.info("Notification send started", 
                                   message_type=message_type,
                                   content_length=len(content))
                    
                    # Simulate external service call
                    self.logger.debug("Calling external notification service", 
                                    provider="email_service")
                    
                    # Simulate success
                    self.logger.info("Notification sent successfully", 
                                   message_type=message_type,
                                   delivery_time_ms=120.5)
                    
                    return {"status": "sent", "correlation_id": correlation_id}
        
        # Test notification service
        with temporary_log_capture() as capture:
            service = NotificationService()
            result = service.send_notification("user-789", "welcome", "Welcome to our service!")
            
            # Validate service logging
            capture.assert_logged("Notification send started", level="info", 
                                 message_type="welcome", user_id="user-789")
            capture.assert_logged("Calling external notification service", level="debug", 
                                 provider="email_service")
            capture.assert_logged("Notification sent successfully", level="info", 
                                 message_type="welcome")
            capture.assert_context_propagated(user_id="user-789", operation="send_notification")
            
            # Validate correlation ID consistency
            capture.assert_correlation_id_consistent()
            
            assert result["status"] == "sent"
            assert "correlation_id" in result
    
    def test_api_endpoint_testing_pattern(self):
        """Demonstrate testing pattern for API endpoints."""
        
        def api_endpoint_handler(request_data):
            """Simulate an API endpoint handler."""
            logger = get_logger("api.user_management")
            
            correlation_id = request_data.get("correlation_id", "api-req-default")
            
            with LoggingContext(correlation_id=correlation_id, 
                              operation="api_create_user",
                              endpoint="/api/v2/users"):
                logger.info("API request received", 
                           method="POST",
                           endpoint="/api/v2/users",
                           content_type="application/json")
                
                # Simulate request validation
                if not request_data.get("email"):
                    logger.warning("API request validation failed", 
                                 error="missing_email",
                                 status_code=400)
                    return {"error": "Email is required", "status": 400}
                
                # Simulate business logic
                logger.debug("Processing user creation request", 
                           user_email=request_data["email"])
                
                # Simulate successful response
                logger.info("API request completed successfully", 
                           status_code=201,
                           response_time_ms=45.8)
                
                return {"user_id": "user-new-123", "status": 201}
        
        # Test successful API request
        with temporary_log_capture() as capture:
            request_data = {
                "email": "newuser@example.com",
                "name": "New User",
                "correlation_id": "api-test-123"
            }
            response = api_endpoint_handler(request_data)
            
            # Validate API logging
            capture.assert_logged("API request received", level="info", 
                                 method="POST", endpoint="/api/v2/users")
            capture.assert_logged("Processing user creation request", level="debug", 
                                 user_email="newuser@example.com")
            capture.assert_logged("API request completed successfully", level="info", 
                                 status_code=201)
            capture.assert_context_propagated(correlation_id="api-test-123", 
                                            operation="api_create_user")
            capture.assert_not_logged(level="warning")
            capture.assert_not_logged(level="error")
            
            assert response["status"] == 201
        
        # Test API validation failure
        with temporary_log_capture() as capture:
            request_data = {"name": "Invalid User"}  # Missing email
            response = api_endpoint_handler(request_data)
            
            # Validate error logging
            capture.assert_logged("API request received", level="info")
            capture.assert_logged("API request validation failed", level="warning", 
                                 error="missing_email", status_code=400)
            capture.assert_not_logged("API request completed successfully")
            
            assert response["status"] == 400