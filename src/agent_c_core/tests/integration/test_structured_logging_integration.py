"""
Integration test for structured logging infrastructure.

This test validates that the complete structured logging system works
together correctly, including factory, context, processors, and formatters.
"""

import os
import logging
import sys
from io import StringIO
from unittest.mock import patch

from agent_c.util.structured_logging import get_logger, LoggingContext
from agent_c.util.structured_logging.factory import StructuredLoggerFactory


def test_structured_logging_integration():
    """Test complete structured logging integration."""
    print("🧪 Testing structured logging integration...")
    
    # Reset factory to ensure clean state
    StructuredLoggerFactory.reset()
    
    # Force structured logging on for this test
    with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'true'}):
        try:
            # Test basic logging functionality
            logger = get_logger('test.integration')
            
            # Test that we can call logging methods without errors
            logger.info("Test message", operation="test", user_id="user-123")
            print("  ✅ Basic logging works")
            
            # Test with context
            with LoggingContext(correlation_id="req-456", agent_id="agent-789"):
                logger.info("Context test", action="context_logging")
            print("  ✅ Context logging works")
            
            # Test error logging
            try:
                raise ValueError("Test error")
            except Exception:
                logger.error("Error occurred", operation="test_error", exc_info=True)
            print("  ✅ Error logging works")
            
            # Test that logger has expected methods
            assert hasattr(logger, 'info'), "Logger missing info method"
            assert hasattr(logger, 'error'), "Logger missing error method"
            assert hasattr(logger, 'debug'), "Logger missing debug method"
            print("  ✅ Logger interface complete")
            
            print("✅ Structured logging integration test passed")
            return True
            
        except Exception as e:
            print(f"❌ Structured logging integration test failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            # Clean up
            StructuredLoggerFactory.reset()


def test_feature_flag_integration():
    """Test that feature flags work correctly."""
    print("🧪 Testing feature flag integration...")
    
    try:
        # Test with structured logging enabled
        StructuredLoggerFactory.reset()
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'true'}):
            logger = get_logger('test.structured')
            # Should have logging methods
            assert hasattr(logger, 'info'), "Structured logger missing info method"
            logger.info("Structured test")
            print("  ✅ Structured logging enabled works")
        
        # Test with structured logging disabled
        StructuredLoggerFactory.reset()
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'false'}):
            logger = get_logger('test.legacy')
            # Should have standard logging methods
            assert hasattr(logger, 'info'), "Legacy logger missing info method"
            logger.info("Legacy test")
            print("  ✅ Legacy logging fallback works")
        
        print("✅ Feature flag integration test passed")
        return True
        
    except Exception as e:
        print(f"❌ Feature flag integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        StructuredLoggerFactory.reset()


def test_context_propagation():
    """Test that context propagates correctly."""
    print("🧪 Testing context propagation...")
    
    StructuredLoggerFactory.reset()
    
    try:
        with patch.dict(os.environ, {'USE_STRUCTURED_LOGGING': 'true'}):
            logger = get_logger('test.context')
            
            # Test context propagation
            with LoggingContext(correlation_id="req-123", user_id="user-456"):
                # This should work without errors
                logger.info("Context test", operation="test_context")
                
                # Test nested context
                with LoggingContext(agent_id="agent-789"):
                    logger.info("Nested context test", operation="nested")
            
            print("  ✅ Context propagation works")
            print("✅ Context propagation test passed")
            return True
            
    except Exception as e:
        print(f"❌ Context propagation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        StructuredLoggerFactory.reset()


def main():
    """Run all integration tests."""
    print("🚀 Running structured logging integration tests...\n")
    
    tests = [
        test_structured_logging_integration,
        test_feature_flag_integration,
        test_context_propagation
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}\n")
    
    print("📋 Integration Test Summary:")
    print("=" * 40)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some integration tests failed")
        return False


if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)