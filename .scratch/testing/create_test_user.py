#!/usr/bin/env python3
"""
Minimal script to create a test user for Agent C realtime client demo.
This script creates the user 'test-user' with password 'test-pass'.
"""

import asyncio
import sys
from pathlib import Path

# Add the Agent C API to Python path
script_dir = Path(__file__).parent
agent_c_api_path = script_dir.parent / "src" / "agent_c_api_ui" / "agent_c_api" / "src"
sys.path.insert(0, str(agent_c_api_path))

async def create_test_user():
    """Create the test-user account for realtime client demo."""
    try:
        # Import required modules
        from agent_c_api.config.database import get_database_config, initialize_database
        from agent_c_api.models.auth_models import UserCreateRequest
        from agent_c_api.core.services.auth_service import AuthService
        
        print("🔧 Initializing database connection...")
        # Initialize database if needed
        await initialize_database()
        
        print("👤 Creating test user account...")
        # Create database session
        db_config = get_database_config()
        async with db_config.async_session_factory() as session:
            auth_service = AuthService(session)
            
            # Create user request for test-user
            user_request = UserCreateRequest(
                username="test-user",
                password="test-pass",
                email="test-user@example.com",
                first_name="Test",
                last_name="User",
                roles=["demo"]  # Give demo role for realtime client access
            )
            
            # Create user
            user = await auth_service.create_user(user_request)
            
            print("✅ Test user created successfully!")
            print(f"   Username: test-user")
            print(f"   Password: test-pass")
            print(f"   User ID: {user.user_id}")
            print(f"   Email: {user.email}")
            print("🚀 User is ready for realtime client demo at localhost:3000")
            
            return True
            
    except ValueError as e:
        if "already exists" in str(e):
            print("✅ Test user already exists!")
            print("   Username: test-user")
            print("   Password: test-pass")
            print("🚀 User is ready for realtime client demo at localhost:3000")
            return True
        else:
            print(f"❌ Error: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("💡 Make sure the Agent C API database is accessible and running.")
        return False

if __name__ == "__main__":
    print("🎯 Agent C Test User Creator")
    print("=" * 40)
    
    try:
        success = asyncio.run(create_test_user())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)