#!/usr/bin/env python3
"""
Test runner for the weather tool - runs both component and integration tests.
Run this script from the tests directory to test the weather functionality.
"""
import subprocess
import sys
import os


def run_tests(test_type="all"):
    """Run tests and display results."""
    if test_type == "all":
        print("🧪 Running Weather Tool Tests (Component + Integration)...")
        print("=" * 60)
    elif test_type == "component":
        print("🧪 Running Weather Component Tests...")
        print("=" * 40)
    elif test_type == "integration":
        print("🧪 Running Weather Integration Tests...")
        print("=" * 40)
    
    print("NOTE: Integration tests make real API calls to weather service")
    print("=" * 60)
    
    # We're already in the tests directory
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(tests_dir)
    
    try:
        # Determine which tests to run - now support both file-based and marker-based
        if test_type == "component":
            # Use marker-based selection for component tests
            pytest_args = [
                sys.executable, "-m", "pytest", 
                "-v", 
                "--tb=short",
                "-m", "component"
            ]
        elif test_type == "integration":
            # Use marker-based selection for integration tests
            pytest_args = [
                sys.executable, "-m", "pytest", 
                "-v", 
                "--tb=short",
                "-m", "integration"
            ]
        else:  # all
            # Run all test files
            pytest_args = [
                sys.executable, "-m", "pytest", 
                "-v", 
                "--tb=short",
                "test_weather_component.py",
                "test_weather_integration.py"
            ]
        
        print(f"\nRunning: {' '.join(pytest_args[3:])}")
        print("=" * 60)
        
        # Run pytest
        result = subprocess.run(pytest_args, capture_output=True, text=True)
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"\n✅ All {test_type} tests passed!")
        else:
            print(f"\n❌ Some {test_type} tests failed with return code: {result.returncode}")
            print("Note: Some tests may fail due to network issues or API rate limits")
            
        return result.returncode == 0
        
    except FileNotFoundError:
        print("❌ pytest not found. Please install test requirements:")
        print("pip install -r test-requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False


def check_dependencies():
    """Check if test dependencies are installed."""
    try:
        import pytest
        import pytest_asyncio
        print("✅ Test dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing test dependency: {e}")
        print("Please install: pip install -r test-requirements.txt")
        return False


def print_usage():
    """Print usage information."""
    print("Weather Tool Test Runner")
    print("=" * 30)
    print("Usage:")
    print("  python run_tests.py [all|component|integration]")
    print("")
    print("Options:")
    print("  all          - Run both component and integration tests (default)")
    print("  component    - Run only component tests (Weather class)")
    print("  integration  - Run only integration tests (WeatherTools via debug_tool)")


if __name__ == "__main__":
    # Parse command line arguments
    test_type = "all"
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["all", "component", "integration"]:
            test_type = arg
        else:
            print(f"Unknown test type: {arg}")
            print_usage()
            sys.exit(1)
    
    print_usage()
    print("")
    
    if not check_dependencies():
        sys.exit(1)
    
    success = run_tests(test_type)
    sys.exit(0 if success else 1)
