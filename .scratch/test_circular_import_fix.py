#!/usr/bin/env python3
"""
Test if the circular import fix resolved the login issue.
"""

import sys
import os
from pathlib import Path

def setup_python_path():
    """Add the Agent C API source to Python path."""
    project_root = Path(__file__).parent.parent
    api_src_path = project_root / "src" / "agent_c_api_ui" / "agent_c_api" / "src"
    if str(api_src_path) not in sys.path:
        sys.path.insert(0, str(api_src_path))
    return api_src_path

def test_imports():
    """Test the imports that were failing."""
    
    # Setup path
    api_src_path = setup_python_path()
    print(f"🔧 Using API source path: {api_src_path}")
    
    try:
        print("🧪 Testing repository imports...")
        
        # Test the problematic import
        print("1. Testing repositories module...")
        from agent_c_api.core.repositories import get_session_repository
        print("   ✅ get_session_repository imported successfully")
        
        # Test auth service import
        print("2. Testing auth service import...")
        from agent_c_api.core.services.auth_service import AuthService
        print("   ✅ AuthService imported successfully")
        
        # Test that we can create an AuthService instance
        print("3. Testing AuthService instantiation...")
        auth_service = AuthService()
        print("   ✅ AuthService instance created")
        
        print("\n🎉 All imports successful! Circular import issue resolved.")
        return True
        
    except Exception as e:
        print(f"\n❌ Import still failing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing Circular Import Fix")
    print("=" * 35)
    
    success = test_imports()
    
    if success:
        print("\n✅ Ready to test login endpoint!")
        print("Run this command to test:")
        print("curl -X POST http://localhost:8001/api/rt/login \\")
        print("  -H \"Content-Type: application/json\" \\")
        print("  -d '{\"username\":\"admin\",\"password\":\"admin123\"}'")
    
    sys.exit(0 if success else 1)