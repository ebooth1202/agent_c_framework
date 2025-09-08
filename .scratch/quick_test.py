import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'agent_c_api_ui', 'agent_c_api', 'src'))

print("Testing critical imports...")
try:
    from agent_c_api.core.voice.models import TTSVoice
    print("✅ TTSVoice imported")
    
    from agent_c_api.core.voice.voice_io_manager_stub import VoiceIOManager
    print("✅ VoiceIOManager stub imported")
    
    from agent_c_api.core.realtime_bridge import RealtimeBridge
    print("✅ RealtimeBridge imported")
    
    from agent_c_api.api.rt.realtime_session_router import router
    print("✅ Realtime router imported")
    
    print("🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()