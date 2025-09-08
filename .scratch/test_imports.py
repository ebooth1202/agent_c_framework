#!/usr/bin/env python3
"""
Quick test to verify that our realtime API import fixes are working.
"""

import sys
import os

# Add the Agent C API source to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'agent_c_api_ui', 'agent_c_api', 'src'))

def test_imports():
    """Test that all the critical imports work without errors."""
    print("Testing imports...")
    
    try:
        # Test the voice models import (this was the main issue)
        print("1. Testing voice models import...")
        from agent_c_api.core.voice.models import TTSVoice, OpenAIVoiceModel
        print(f"   ✅ TTSVoice type: {TTSVoice}")
        print(f"   ✅ OpenAIVoiceModel imported successfully")
        
        # Test the VoiceIOManager stub import
        print("2. Testing VoiceIOManager stub import...")
        from agent_c_api.core.voice.voice_io_manager_stub import VoiceIOManager
        print("   ✅ VoiceIOManager stub imported successfully")
        
        # Test the realtime bridge import (this should now work)
        print("3. Testing realtime bridge import...")
        from agent_c_api.core.realtime_bridge import RealtimeBridge
        print("   ✅ RealtimeBridge imported successfully")
        
        # Test the realtime session router import (this was failing before)
        print("4. Testing realtime session router import...")
        from agent_c_api.api.rt.realtime_session_router import router
        print("   ✅ Realtime session router imported successfully")
        
        print("\n🎉 All imports successful! The fixes are working.")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)