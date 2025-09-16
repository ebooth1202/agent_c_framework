#!/usr/bin/env python3
"""
Test just the core imports that were causing issues, avoiding circular imports.
"""

import sys
import os
from pathlib import Path

def main():
    # Add the Agent C API source to Python path
    project_root = Path(__file__).parent.parent
    api_src_path = project_root / "src" / "agent_c_api_ui" / "agent_c_api" / "src"
    sys.path.insert(0, str(api_src_path))
    
    print("🧪 Testing core imports (avoiding circular dependencies)")
    print("=" * 60)
    
    try:
        # Test the voice models import (this was the main original issue)
        print("1. Testing voice models import...")
        from agent_c_api.core.voice.models import TTSVoice, OpenAIVoiceModel
        print(f"   ✅ TTSVoice type: {TTSVoice}")
        print(f"   ✅ OpenAIVoiceModel imported successfully")
        
        # Test the VoiceIOManager stub import
        print("2. Testing VoiceIOManager stub import...")
        from agent_c_api.core.voice.voice_io_manager_stub import VoiceIOManager
        print("   ✅ VoiceIOManager stub imported successfully")
        
        # Test that we can create a VoiceIOManager instance with None bridge (avoiding circular import)
        print("3. Testing VoiceIOManager stub instantiation...")
        # We'll pass None for the bridge to avoid the circular import during testing
        voice_manager = VoiceIOManager(None)
        print("   ✅ VoiceIOManager stub can be instantiated")
        
        # Test the session router import (this should work now)
        print("4. Testing realtime session router import...")
        from agent_c_api.api.rt.session import router
        print("   ✅ Realtime session router imported successfully")
        
        print("\n🎉 Core imports successful! The original fixes are working.")
        print("📝 Note: RealtimeBridge import avoided to prevent circular dependency during testing")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)