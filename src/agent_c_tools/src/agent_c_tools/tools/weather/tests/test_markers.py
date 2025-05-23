#!/usr/bin/env python3
"""
Quick test to verify pytest markers and configuration work correctly.
"""
import subprocess
import sys
import os

def test_markers():
    """Test that pytest markers work correctly."""
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(tests_dir)
    
    print("Testing pytest markers...")
    print("=" * 40)
    
    # Test component marker
    print("\n🔍 Testing component marker:")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "-m", "component", 
        "--collect-only", 
        "-q"
    ], capture_output=True, text=True)
    
    print("Component tests found:")
    print(result.stdout)
    
    # Test integration marker
    print("\n🔍 Testing integration marker:")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "-m", "integration", 
        "--collect-only", 
        "-q"
    ], capture_output=True, text=True)
    
    print("Integration tests found:")
    print(result.stdout)
    
    # Test that warnings are fixed
    print("\n🔍 Testing for warnings:")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "--collect-only",
        "-q"
    ], capture_output=True, text=True)
    
    if "PytestUnknownMarkWarning" in result.stdout or "PytestUnknownMarkWarning" in result.stderr:
        print("❌ Still have mark warnings")
    else:
        print("✅ No mark warnings found")
    
    if "asyncio_default_fixture_loop_scope" in result.stderr:
        print("❌ Still have asyncio warnings")  
    else:
        print("✅ No asyncio warnings found")

if __name__ == "__main__":
    test_markers()
