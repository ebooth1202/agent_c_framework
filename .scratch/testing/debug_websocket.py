#!/usr/bin/env python3
"""
Debug WebSocket and realtime connection issues.
"""

import sys
import os
import asyncio
from pathlib import Path

def setup_python_path():
    """Add the Agent C API source to Python path."""
    project_root = Path(__file__).parent.parent
    api_src_path = project_root / "src" / "agent_c_api_ui" / "agent_c_api" / "src"
    if str(api_src_path) not in sys.path:
        sys.path.insert(0, str(api_src_path))
    return api_src_path

async def test_websocket_endpoint():
    """Test if WebSocket endpoint is accessible."""
    
    # Setup path and environment
    api_src_path = setup_python_path()
    os.environ['JWT_SECRET_KEY'] = 'dev-secret-key-change-in-production-12345678901234567890'
    
    print("🔍 Testing WebSocket and Realtime Components")
    print("=" * 50)
    
    try:
        # Test realtime session manager import
        print("\n1. Testing realtime session manager...")
        from agent_c_api.core.realtime_session_manager import RealtimeSessionManager
        print("   ✅ RealtimeSessionManager imported")
        
        # Test realtime bridge import
        print("\n2. Testing realtime bridge...")
        from agent_c_api.core.realtime_bridge import RealtimeBridge
        print("   ✅ RealtimeBridge imported")
        
        # Test WebSocket route import
        print("\n3. Testing WebSocket route...")
        from agent_c_api.api.rt.session import router
        print("   ✅ WebSocket router imported")
        
        # Check if WebSocket endpoint exists in router
        print("\n4. Checking WebSocket endpoints...")
        for route in router.routes:
            print(f"   Route: {route.path} ({getattr(route, 'methods', ['WebSocket'])})")
        
        # Test authentication token creation
        print("\n5. Testing token creation for WebSocket...")
        from agent_c_api.config.database import initialize_database
        from agent_c_api.core.services.auth_service import AuthService
        
        await initialize_database()
        auth_service = AuthService()
        await auth_service.initialize()
        
        login_response = await auth_service.login("admin", "admin123")
        if login_response:
            print(f"   ✅ Token for WebSocket: {login_response.token[:50]}...")
        else:
            print("   ❌ Failed to create token")
        
        await auth_service.close()
        
        print("\n🎯 WebSocket Debug Complete!")
        print("\n💡 Next steps to check:")
        print("   1. Browser console errors in demo app")
        print("   2. Server logs when demo app tries to connect")
        print("   3. WebSocket connection attempts in Network tab")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during WebSocket testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_websocket_endpoint())
    sys.exit(0 if success else 1)