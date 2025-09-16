#!/usr/bin/env python3
"""
Check the current status of the Agent C API server and test our fixes.
"""

import sys
import os
import requests
from pathlib import Path

# Add the Agent C API source to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / 'src' / 'agent_c_api_ui' / 'agent_c_api' / 'src'))

def test_server_connection():
    """Test if the server is running and accessible."""
    print("🔍 Testing server connection...")
    
    base_url = "http://localhost:8000"
    endpoints_to_test = [
        "/",
        "/docs", 
        "/api/rt/login"
    ]
    
    for endpoint in endpoints_to_test:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5)
            print(f"   {endpoint}: {response.status_code} {response.reason}")
        except requests.exceptions.ConnectionError:
            print(f"   {endpoint}: ❌ Connection refused - server not running")
        except requests.exceptions.Timeout:
            print(f"   {endpoint}: ⏱️  Timeout")
        except Exception as e:
            print(f"   {endpoint}: ❌ Error: {e}")

def test_imports():
    """Test that our import fixes are working."""
    print("\n🧪 Testing import fixes...")
    
    try:
        # Test the core imports that were failing
        from agent_c_api.core.voice.models import TTSVoice
        from agent_c_api.core.voice.voice_io_manager_stub import VoiceIOManager  
        from agent_c_api.core.realtime_bridge import RealtimeBridge
        from agent_c_api.api.rt.realtime_session_router import router
        
        print("   ✅ All critical imports successful")
        return True
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_startup_script():
    """Check if the startup script exists."""
    print("\n📋 Checking startup script...")
    
    startup_script = project_root / "start_agent_c.sh"
    if startup_script.exists():
        print(f"   ✅ Found startup script: {startup_script}")
        return True
    else:
        print(f"   ❌ Startup script not found: {startup_script}")
        return False

if __name__ == "__main__":
    print("🚀 Agent C API Status Check")
    print("=" * 50)
    
    # Test imports first
    imports_ok = test_imports()
    
    # Check server connection
    test_server_connection()
    
    # Check startup script
    script_exists = check_startup_script()
    
    print("\n📊 Summary:")
    print(f"   Import fixes: {'✅ Working' if imports_ok else '❌ Failed'}")
    print(f"   Startup script: {'✅ Found' if script_exists else '❌ Missing'}")
    
    if imports_ok and not script_exists:
        print("\n💡 Next steps:")
        print("   1. The import fixes are working correctly")
        print("   2. Need to start the Agent C API server")
        print("   3. Look for startup script or start manually")
    elif not imports_ok:
        print("\n⚠️  Import issues detected - need to fix before starting server")