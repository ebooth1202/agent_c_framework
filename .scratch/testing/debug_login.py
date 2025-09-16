#!/usr/bin/env python3
"""
Debug the login endpoint to identify the internal server error.
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

async def test_login_components():
    """Test the individual components of the login process."""
    
    # Setup path and imports
    api_src_path = setup_python_path()
    print(f"🔧 Using API source path: {api_src_path}")
    
    try:
        print("🧪 Testing login components...")
        
        # Test database initialization
        print("\n1. Testing database initialization...")
        from agent_c_api.config.database import initialize_database
        await initialize_database()
        print("   ✅ Database initialized")
        
        # Test auth service
        print("\n2. Testing authentication service...")
        from agent_c_api.core.services.auth_service import AuthService
        auth_service = AuthService()
        await auth_service.initialize()
        print("   ✅ Auth service initialized")
        
        # Test user lookup
        print("\n3. Testing user lookup...")
        admin_user = await auth_service.get_user_by_username("admin")
        if admin_user:
            print(f"   ✅ Found admin user: {admin_user.username} (ID: {admin_user.user_id})")
        else:
            print("   ❌ Admin user not found")
        
        test_user = await auth_service.get_user_by_username("test")
        if test_user:
            print(f"   ✅ Found test user: {test_user.username} (ID: {test_user.user_id})")
        else:
            print("   ❌ Test user not found")
        
        # Test password verification
        print("\n4. Testing password verification...")
        if admin_user:
            try:
                is_valid = await auth_service.verify_password("admin123", admin_user.password_hash)
                print(f"   Admin password valid: {is_valid}")
            except Exception as e:
                print(f"   ❌ Error verifying admin password: {e}")
        
        if test_user:
            try:
                is_valid = await auth_service.verify_password("test123", test_user.password_hash)
                print(f"   Test password valid: {is_valid}")
            except Exception as e:
                print(f"   ❌ Error verifying test password: {e}")
        
        # Test HeyGen client (this might be the issue)
        print("\n5. Testing HeyGen client...")
        try:
            from agent_c.util.heygen_streaming_avatar_client import HeyGenStreamingClient
            heygen_client = HeyGenStreamingClient()
            print("   ✅ HeyGen client created")
            
            # Try to get token (this might fail and cause the 500 error)
            try:
                token_response = await heygen_client.get_access_token()
                print(f"   ✅ HeyGen token obtained: {token_response[:20]}...")
            except Exception as e:
                print(f"   ⚠️  HeyGen token error (this might be the 500 error cause): {e}")
                
        except Exception as e:
            print(f"   ❌ HeyGen client error: {e}")
        
        # Test JWT creation
        print("\n6. Testing JWT creation...")
        try:
            from agent_c_api.core.util.jwt import create_jwt_token
            if admin_user:
                token = create_jwt_token(admin_user.user_id, admin_user.username)
                print(f"   ✅ JWT created: {token[:50]}...")
        except Exception as e:
            print(f"   ❌ JWT creation error: {e}")
        
        # Close auth service
        await auth_service.close()
        
        print("\n📊 Component test complete!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Agent C API Login Debug")
    print("=" * 40)
    
    success = asyncio.run(test_login_components())
    sys.exit(0 if success else 1)