#!/usr/bin/env python3
"""
Test if the circular import fix v2 resolved the issue.
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
    """Test the imports step by step."""
    
    # Setup path
    api_src_path = setup_python_path()
    print(f"🔧 Using API source path: {api_src_path}")
    
    try:
        print("🧪 Testing imports step by step...")
        
        # Test session repository first
        print("1. Testing session_repository...")
        from agent_c_api.core.repositories.session_repository import SessionRepository
        print("   ✅ SessionRepository imported")
        
        # Test repositories init
        print("2. Testing repositories __init__...")
        from agent_c_api.core.repositories import SessionRepository as SessionRepo2
        print("   ✅ repositories.__init__ imported")
        
        # Test the problematic function
        print("3. Testing get_session_repository...")
        from agent_c_api.core.repositories import get_session_repository
        print("   ✅ get_session_repository imported")
        
        # Test auth service
        print("4. Testing auth service...")
        from agent_c_api.core.services.auth_service import AuthService
        print("   ✅ AuthService imported")
        
        print("\n🎉 All imports successful! Circular import resolved.")
        return True
        
    except Exception as e:
        print(f"\n❌ Import still failing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing Circular Import Fix v2")
    print("=" * 40)
    
    success = test_imports()
    
    if success:
        print("\n✅ Ready to test login endpoint!")
        print("🧪 Test commands:")
        print("curl -X POST http://localhost:8001/api/rt/login \\")
        print("  -H \"Content-Type: application/json\" \\")
        print("  -d '{\"username\":\"admin\",\"password\":\"admin123\"}'")
    
    sys.exit(0 if success else 1)