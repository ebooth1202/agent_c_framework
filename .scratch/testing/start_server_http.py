#!/usr/bin/env python3
"""
Start the Agent C API server on HTTP for testing our realtime API fixes.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🚀 Starting Agent C API Server (HTTP)")
    print("=" * 50)
    print(f"📁 Working directory: {project_root}")
    
    # Set up Python path
    api_src_path = project_root / "src" / "agent_c_api_ui" / "agent_c_api" / "src"
    env = os.environ.copy()
    current_pythonpath = env.get('PYTHONPATH', '')
    if current_pythonpath:
        env['PYTHONPATH'] = f"{api_src_path}:{current_pythonpath}"
    else:
        env['PYTHONPATH'] = str(api_src_path)
    
    print(f"🐍 PYTHONPATH: {env['PYTHONPATH']}")
    
    # Test imports first
    print("\n🧪 Testing imports before starting server...")
    try:
        sys.path.insert(0, str(api_src_path))
        from agent_c_api.core.voice.models import TTSVoice
        from agent_c_api.core.voice.voice_io_manager_stub import VoiceIOManager
        from agent_c_api.core.realtime_bridge import RealtimeBridge
        from agent_c_api.api.rt.session import router
        print("✅ All critical imports successful!")
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        print("Cannot start server with broken imports.")
        return 1
    
    # Start the server
    print("\n🌐 Starting uvicorn server on HTTP...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs will be at: http://localhost:8000/docs")
    print("🔌 Realtime endpoints at: http://localhost:8000/api/rt/")
    print("\nPress Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Start uvicorn without SSL
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "agent_c_api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000", 
            "--log-level", "info",
            "--reload"  # Enable auto-reload for development
        ]
        
        subprocess.run(cmd, env=env, cwd=project_root)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"\n❌ Server failed to start: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())