#!/usr/bin/env python3
"""
Test the login fix with optional HeyGen token.
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

async def test_complete_login():
    """Test the complete login process with optional HeyGen."""
    
    # Setup path and environment
    api_src_path = setup_python_path()
    os.environ['JWT_SECRET_KEY'] = 'dev-secret-key-change-in-production-12345678901234567890'
    
    print(f"🔧 Using API source path: {api_src_path}")
    print("🧪 Testing complete login process...")
    
    try:
        # Import and initialize components
        from agent_c_api.config.database import initialize_database
        from agent_c_api.core.services.auth_service import AuthService
        from agent_c_api.core.util.jwt import create_jwt_token
        from agent_c_api.models.auth_models import RealtimeLoginResponse
        from agent_c.util import MnemonicSlugs
        
        # Initialize database
        print("\n1. Initializing database...")
        await initialize_database()
        print("   ✅ Database initialized")
        
        # Initialize auth service
        print("\n2. Initializing auth service...")
        auth_service = AuthService()
        await auth_service.initialize()
        print("   ✅ Auth service initialized")
        
        # Authenticate user
        print("\n3. Authenticating user...")
        login_response = await auth_service.login("admin", "admin123")
        if not login_response:
            print("   ❌ Login failed")
            return False
        print(f"   ✅ User authenticated: {login_response.user.user_name}")
        
        # Create realtime login response (without HeyGen token)
        print("\n4. Creating realtime login response...")
        realtime_response = RealtimeLoginResponse(
            agent_c_token=login_response.token,
            heygen_token=None,  # Optional - None for development
            ui_session_id=MnemonicSlugs.generate_slug(3)
        )
        
        print("   ✅ Realtime login response created successfully!")
        print(f"   Token: {realtime_response.agent_c_token[:50]}...")
        print(f"   Session ID: {realtime_response.ui_session_id}")
        print(f"   HeyGen Token: {realtime_response.heygen_token or 'None (development mode)'}")
        
        # Close auth service
        await auth_service.close()
        
        print("\n🎉 Complete login process successful!")
        print("💡 The login endpoint should now work without HeyGen token.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during login test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔍 Testing Login Fix")
    print("=" * 25)
    
    success = asyncio.run(test_complete_login())
    
    if success:
        print("\n✅ Ready to test login endpoint!")
        print("🧪 Test command:")
        print("curl -X POST http://localhost:8001/api/rt/login \\")
        print("  -H \"Content-Type: application/json\" \\")
        print("  -d '{\"username\":\"admin\",\"password\":\"admin123\"}'")
        print("\n🔄 Remember to restart the server to pick up the changes!")
    
    sys.exit(0 if success else 1)