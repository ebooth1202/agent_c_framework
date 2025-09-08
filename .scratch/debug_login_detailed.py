#!/usr/bin/env python3
"""
Debug the login process step by step to find the exact error.
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

async def test_login_process():
    """Test the login process step by step."""
    
    # Setup path and imports
    api_src_path = setup_python_path()
    print(f"🔧 Using API source path: {api_src_path}")
    
    try:
        print("🧪 Testing login process components...")
        
        # Test database initialization
        print("\n1. Testing database initialization...")
        from agent_c_api.config.database import initialize_database
        await initialize_database()
        print("   ✅ Database initialized")
        
        # Test auth service initialization
        print("\n2. Testing auth service initialization...")
        from agent_c_api.core.services.auth_service import AuthService
        auth_service = AuthService()
        await auth_service.initialize()
        print("   ✅ Auth service initialized")
        
        # Test user authentication (combines lookup and password verification)
        print("\n3. Testing user authentication...")
        admin_user = await auth_service.authenticate_user("admin", "admin123")
        if admin_user:
            print(f"   ✅ Admin user authenticated: {admin_user.user_name} (ID: {admin_user.user_id})")
        else:
            print("   ❌ Admin user authentication failed")
            return False
        
        # Test JWT token creation
        print("\n4. Testing JWT token creation...")
        from agent_c_api.core.util.jwt import create_jwt_token
        jwt_token = create_jwt_token(admin_user)
        print(f"   ✅ JWT token created: {jwt_token[:50]}...")
        
        # Test HeyGen client (this might be the issue)
        print("\n5. Testing HeyGen client...")
        try:
            from agent_c.util.heygen_streaming_avatar_client import HeyGenStreamingClient
            heygen_client = HeyGenStreamingClient()
            print("   ✅ HeyGen client created")
            
            # Try to get token (this might fail and cause the 500 error)
            try:
                print("   🧪 Attempting to get HeyGen access token...")
                token_response = await heygen_client.get_access_token()
                print(f"   ✅ HeyGen token obtained: {token_response[:20]}...")
            except Exception as e:
                print(f"   ⚠️  HeyGen token error (likely cause of 500 error): {e}")
                print("   💡 This is probably why login is failing!")
                
                # Let's see if we can create a response without HeyGen token
                print("   🔧 Testing login response without HeyGen token...")
                from agent_c_api.models.auth_models import RealtimeLoginResponse
                
                # Create response without HeyGen token
                response = RealtimeLoginResponse(
                    access_token=jwt_token,
                    token_type="bearer",
                    heygen_token=None,  # Skip HeyGen token
                    user=admin_user,
                    available_voices=[],  # Empty for now
                    available_avatars=[]  # Empty for now
                )
                print("   ✅ Login response created without HeyGen token")
                print(f"   Response: {response.model_dump()}")
                
        except Exception as e:
            print(f"   ❌ HeyGen client error: {e}")
            return False
        
        # Close auth service
        await auth_service.close()
        
        print("\n📊 Login process test complete!")
        print("🔍 If HeyGen token generation failed, that's likely the cause of the 500 error.")
        
    except Exception as e:
        print(f"❌ Error during login testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Agent C API Login Process Debug")
    print("=" * 45)
    
    success = asyncio.run(test_login_process())
    
    if success:
        print("\n💡 Next steps:")
        print("1. If HeyGen token generation failed, we can modify the login endpoint")
        print("2. To skip HeyGen token generation temporarily")
        print("3. This should resolve the 500 Internal Server Error")
    
    sys.exit(0 if success else 1)