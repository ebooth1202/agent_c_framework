#!/usr/bin/env python3
"""
Test runner for YAML serialization unit tests.

This script runs the comprehensive YAML serialization test suite and provides
detailed reporting on test results, performance benchmarks, and coverage.
"""

import sys
import os
import unittest
import time
from io import StringIO
from contextlib import redirect_stdout, redirect_stderr


def run_yaml_tests():
    """Run the YAML serialization test suite with detailed reporting."""
    
    print("🧪 YAML Serialization Unit Test Suite")
    print("=" * 60)
    print("Running comprehensive tests for all YAML optimization features...")
    print()
    
    # Discover and load tests
    loader = unittest.TestLoader()
    
    try:
        # Import the test module
        from test_yaml_serialization import (
            TestYAMLDependencies, TestYAMLOptimizer, TestSearchResultYAML,
            TestSearchResponseYAML, TestSearchParametersYAML, TestEngineCapabilitiesYAML,
            TestWebSearchConfigYAML, TestEngineHealthStatusYAML, TestPerformanceBenchmarks,
            TestEdgeCasesAndErrorHandling
        )
        
        # Create test suite
        suite = unittest.TestSuite()
        
        # Add test classes
        test_classes = [
            TestYAMLDependencies,
            TestYAMLOptimizer,
            TestSearchResultYAML,
            TestSearchResponseYAML,
            TestSearchParametersYAML,
            TestEngineCapabilitiesYAML,
            TestWebSearchConfigYAML,
            TestEngineHealthStatusYAML,
            TestPerformanceBenchmarks,
            TestEdgeCasesAndErrorHandling
        ]
        
        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        print(f"📊 Test Suite Information:")
        print(f"   Test classes: {len(test_classes)}")
        print(f"   Total tests: {suite.countTestCases()}")
        print()
        
        # Run tests with detailed output
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            buffer=True
        )
        
        print("🚀 Running Tests...")
        print("-" * 50)
        
        start_time = time.time()
        result = runner.run(suite)
        end_time = time.time()
        
        print("-" * 50)
        print(f"⏱️  Test Execution Time: {end_time - start_time:.2f} seconds")
        print()
        
        # Print detailed results
        print("📈 Test Results Summary:")
        print(f"   Tests run: {result.testsRun}")
        print(f"   Failures: {len(result.failures)}")
        print(f"   Errors: {len(result.errors)}")
        print(f"   Skipped: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
        print()
        
        # Print failure details if any
        if result.failures:
            print("❌ Test Failures:")
            for test, traceback in result.failures:
                print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
            print()
        
        # Print error details if any
        if result.errors:
            print("💥 Test Errors:")
            for test, traceback in result.errors:
                print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
            print()
        
        # Success summary
        if result.wasSuccessful():
            print("🎉 All Tests Passed Successfully!")
            print("✅ YAML serialization implementation is ready for production")
            print()
            print("🚀 Key Features Validated:")
            print("   - Token efficiency optimization")
            print("   - Round-trip serialization accuracy")
            print("   - Edge case handling")
            print("   - Performance benchmarks")
            print("   - Error handling and fallbacks")
            print("   - All model implementations")
            return True
        else:
            print("⚠️  Some tests failed. Please review the failures above.")
            return False
            
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        print("   Make sure you're running from the correct directory")
        return False
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_specific_test_class(test_class_name):
    """Run a specific test class."""
    print(f"🧪 Running {test_class_name} Tests")
    print("=" * 50)
    
    try:
        # Import the test module
        import test_yaml_serialization
        
        # Get the test class
        test_class = getattr(test_yaml_serialization, test_class_name)
        
        # Create and run test suite
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(test_class)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ Failed to run {test_class_name}: {e}")
        return False


def run_performance_benchmarks():
    """Run only the performance benchmarks."""
    print("⚡ YAML Performance Benchmarks")
    print("=" * 50)
    
    try:
        from test_yaml_serialization import TestPerformanceBenchmarks
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestPerformanceBenchmarks)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
            print("\n🏆 Performance benchmarks completed successfully!")
            print("📊 YAML optimization provides significant token savings")
        
        return result.wasSuccessful()
        
    except Exception as e:
        print(f"❌ Performance benchmark failed: {e}")
        return False


def main():
    """Main test runner with command line options."""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'performance':
            success = run_performance_benchmarks()
        elif command.startswith('test'):
            # Run specific test class
            test_class_name = command.replace('test', 'Test') + 'YAML' if not command.endswith('YAML') else command
            success = run_specific_test_class(test_class_name)
        elif command == 'help':
            print("YAML Test Runner Usage:")
            print("  python run_yaml_tests.py                 - Run all tests")
            print("  python run_yaml_tests.py performance     - Run performance benchmarks")
            print("  python run_yaml_tests.py TestYAMLDependencies - Run specific test class")
            print("  python run_yaml_tests.py help            - Show this help")
            return
        else:
            print(f"Unknown command: {command}")
            print("Use 'python run_yaml_tests.py help' for usage information")
            return
    else:
        success = run_yaml_tests()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()