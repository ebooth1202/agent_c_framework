#!/usr/bin/env python3
"""
Test if realtime imports are now working.
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

def test_realtime_imports():
    """Test realtime component imports."""
    
    # Setup path
    api_src_path = setup_python_path()
    print(f"🔧 Using API source path: {api_src_path}")
    
    try:
        print("🧪 Testing realtime imports...")
        
        # Test realtime bridge
        print("1. Testing realtime bridge...")
        from agent_c_api.core.realtime_bridge import RealtimeBridge
        print("   ✅ RealtimeBridge imported")
        
        # Test realtime session manager
        print("2. Testing realtime session manager...")
        from agent_c_api.core.realtime_session_manager import RealtimeSessionManager
        print("   ✅ RealtimeSessionManager imported")
        
        # Test WebSocket router
        print("3. Testing WebSocket router...")
        from agent_c_api.api.rt.session import router
        print("   ✅ WebSocket router imported")
        
        # Check routes
        print("4. Checking available routes...")
        for route in router.routes:
            print(f"   Route: {route.path} - {getattr(route, 'methods', 'WebSocket')}")
        
        print("\n🎉 All realtime imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import still failing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing Realtime Import Fix")
    print("=" * 35)
    
    success = test_realtime_imports()
    
    if success:
        print("\n✅ Realtime components should now work!")
        print("🔄 Restart the server to pick up the fixes.")
    
    sys.exit(0 if success else 1)