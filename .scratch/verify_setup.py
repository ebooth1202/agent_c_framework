#!/usr/bin/env python3
"""
Verify that everything is ready for starting the Agent C API server.
"""

import sys
import os
from pathlib import Path

def main():
    project_root = Path(__file__).parent.parent
    api_src_path = project_root / "src" / "agent_c_api_ui" / "agent_c_api" / "src"
    
    print("🔍 Agent C API Setup Verification")
    print("=" * 40)
    
    # Check if API source exists
    if not api_src_path.exists():
        print(f"❌ API source path not found: {api_src_path}")
        return 1
    print(f"✅ API source path exists: {api_src_path}")
    
    # Test imports
    print("\n🧪 Testing critical imports...")
    sys.path.insert(0, str(api_src_path))
    
    try:
        from agent_c_api.core.voice.models import TTSVoice
        print("✅ TTSVoice imported successfully")
        
        from agent_c_api.core.voice.voice_io_manager_stub import VoiceIOManager
        print("✅ VoiceIOManager stub imported successfully")
        
        from agent_c_api.core.realtime_bridge import RealtimeBridge
        print("✅ RealtimeBridge imported successfully")
        
        from agent_c_api.api.rt.realtime_session_router import router
        print("✅ Realtime session router imported successfully")
        
        print("\n🎉 All imports successful! Server should start without issues.")
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Show startup commands
    print("\n🚀 Ready to start server! Use one of these commands:")
    print("-" * 50)
    print("Option 1 - Using our Python script:")
    print(f"  cd {project_root}")
    print("  python .scratch/start_server_http.py")
    print()
    print("Option 2 - Direct uvicorn command:")
    print(f"  cd {project_root}")
    print(f"  export PYTHONPATH=\"{api_src_path}:$PYTHONPATH\"")
    print("  python -m uvicorn agent_c_api.main:app --host 0.0.0.0 --port 8000 --log-level info")
    print()
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("🔌 Realtime API at: http://localhost:8000/api/rt/")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())