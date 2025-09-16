#!/usr/bin/env python3
"""
Create demo users for the Agent C API authentication system.
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

async def create_demo_users():
    """Create the demo users needed for testing."""
    
    # Setup path and imports
    api_src_path = setup_python_path()
    print(f"🔧 Using API source path: {api_src_path}")
    
    try:
        # Import required modules
        from agent_c_api.core.services.auth_service import AuthService
        from agent_c_api.config.database import initialize_database
        
        print("🗄️ Initializing database...")
        await initialize_database()
        
        print("🔐 Initializing authentication service...")
        auth_service = AuthService()
        await auth_service.initialize()
        
        # Demo users to create
        demo_users = [
            ("demo", "password123", "demo@example.com", "Demo", "User", ["demo"]),
            ("admin", "admin123", "admin@example.com", "Admin", "User", ["admin", "demo"]),
            ("test", "test123", "test@example.com", "Test", "User", ["demo"])
        ]
        
        print("\n👥 Creating demo users...")
        success_count = 0
        skipped_count = 0
        
        for username, password, email, first_name, last_name, roles in demo_users:
            print(f"\n📝 Creating user: {username}")
            try:
                # Check if user already exists
                existing_user = await auth_service.get_user_by_username(username)
                if existing_user:
                    print(f"   ⚠️  User '{username}' already exists, skipping")
                    skipped_count += 1
                    continue
                
                # Create the user
                user = await auth_service.create_user(
                    username=username,
                    password=password,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    roles=roles
                )
                
                if user:
                    print(f"   ✅ User '{username}' created successfully")
                    success_count += 1
                else:
                    print(f"   ❌ Failed to create user '{username}'")
                    
            except Exception as e:
                print(f"   ❌ Error creating user '{username}': {e}")
        
        print(f"\n📊 Demo users summary:")
        print(f"   Created: {success_count}")
        print(f"   Already existed: {skipped_count}")
        print(f"   Total available: {success_count + skipped_count}/{len(demo_users)}")
        
        if success_count + skipped_count == len(demo_users):
            print("\n🎉 All demo users are ready to use!")
            print("\n🔑 Available credentials:")
            for username, password, _, _, _, _ in demo_users:
                print(f"   {username} / {password}")
        
        # Close the auth service
        await auth_service.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Agent C API Demo User Creation")
    print("=" * 40)
    
    success = asyncio.run(create_demo_users())
    sys.exit(0 if success else 1)