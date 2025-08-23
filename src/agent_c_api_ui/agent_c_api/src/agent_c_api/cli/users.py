#!/usr/bin/env python3
"""
CLI tool for user management in the Avatar API.

This command-line interface allows administrators to create, list, and delete
users for the Avatar API authentication system.
"""

import asyncio
import argparse
import sys
from typing import List
from getpass import getpass


# Automatic path resolution - find the agent_c_api module
import sys
from pathlib import Path

def setup_python_path():
    """Automatically find and add the correct Python path for agent_c_api imports."""
    script_path = Path(__file__).resolve()
    
    # Search upward for a directory containing agent_c_api module
    current = script_path.parent
    while current != current.parent:  # Stop at filesystem root
        # Check if agent_c_api is a subdirectory here
        if (current / "agent_c_api").is_dir():
            if str(current) not in sys.path:
                sys.path.insert(0, str(current))
            return str(current)
        current = current.parent
    
    raise RuntimeError("Could not find agent_c_api module in parent directories")

# Set up path automatically
setup_python_path()


async def create_user(username: str, password: str = None, email: str = None,
                     first_name: str = None, last_name: str = None,
                     roles: List[str] = None):
    """
    Create a new user in the database.
    
    Args:
        username: Username for the new user
        password: Password (will prompt if not provided)
        email: Optional email address
        first_name: Optional first name
        last_name: Optional last name
        roles: Optional list of roles
    """
    try:
        # Import database config directly
        from agent_c_api.config.database import get_database_config, initialize_database
        from agent_c_api.models.auth_models import UserCreateRequest
        
        # Import AuthService directly to avoid circular import through repositories
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "services"))
        from agent_c_api.core.services.auth_service import AuthService
        
        # Initialize database if needed
        await initialize_database()
        
        # Get password securely if not provided
        if not password:
            password = getpass(f"Enter password for user '{username}': ")
            if not password:
                print("❌ Password cannot be empty")
                return False
        
        # Create database session
        db_config = get_database_config()
        async with db_config.async_session_factory() as session:
            auth_service = AuthService(session)
            
            # Create user request
            user_request = UserCreateRequest(
                username=username,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                roles=roles or []
            )
            
            # Create user
            user = await auth_service.create_user(user_request)
            
            print(f"✅ User '{username}' created successfully!")
            print(f"   User ID: {user.user_id}")
            print(f"   Email: {user.email or 'Not provided'}")
            print(f"   Name: {user.first_name} {user.last_name}")
            print(f"   Active: {user.is_active}")
            print(f"   Roles: {', '.join(user.roles) if user.roles else 'None'}")
            
            return True
            
    except ValueError as e:
        # Return the error message for better handling
        print(f"❌ Error: {e}")
        return str(e)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


async def list_users():
    """List all users in the database."""
    try:
        # Import database config directly
        from agent_c_api.config.database import get_database_config, initialize_database
        from agent_c_api.models.auth_models import UserCreateRequest
        
        # Import AuthService directly to avoid circular import through repositories
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "services"))
        from agent_c_api.core.services.auth_service import AuthService
        
        # Initialize database if needed
        await initialize_database()
        
        # Create database session
        db_config = get_database_config()
        async with db_config.async_session_factory() as session:

            auth_service = AuthService(session)
            
            # Get all users
            users = await auth_service.list_users()
            
            if not users:
                print("No users found in the database.")
                return
            
            print(f"\nFound {len(users)} user(s):\n")
            print(f"{'Username':<20} {'User ID':<25} {'Email':<30} {'Active':<8} {'Last Login'}")
            print("-" * 100)
            
            for user in users:
                # last_login is now an ISO string, not datetime
                if user.last_login:
                    from datetime import datetime
                    last_login_dt = datetime.fromisoformat(user.last_login.replace('Z', '+00:00'))
                    last_login = last_login_dt.strftime("%Y-%m-%d %H:%M")
                else:
                    last_login = "Never"
                print(f"{user.user_name:<20} {user.user_id:<25} {user.email or 'N/A':<30} "
                      f"{'Yes' if user.is_active else 'No':<8} {last_login}")
            
    except Exception as e:
        print(f"❌ Error listing users: {e}")


async def delete_user(user_id: str, confirm: bool = False):
    """
    Delete a user from the database.
    
    Args:
        user_id: User ID to delete
        confirm: Skip confirmation prompt if True
    """
    try:
        # Import database config directly
        from agent_c_api.config.database import get_database_config, initialize_database
        from agent_c_api.models.auth_models import UserCreateRequest
        
        # Import AuthService directly to avoid circular import through repositories
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent / "core" / "services"))
        from agent_c_api.core.services.auth_service import AuthService
        
        # Initialize database if needed
        await initialize_database()
        
        # Create database session
        db_config = get_database_config()
        async with db_config.async_session_factory() as session:
            auth_service = AuthService(session)
            
            # Get user first to show details
            user = await auth_service.auth_repo.get_user_by_id(user_id)
            if not user:
                print(f"❌ User with ID '{user_id}' not found.")
                return False
            
            # Confirm deletion unless --force is used
            if not confirm:
                print(f"This will permanently delete user:")
                print(f"  Username: {user.user_name}")
                print(f"  User ID: {user.user_id}")
                print(f"  Email: {user.email or 'N/A'}")
                
                response = input("Are you sure? (yes/no): ").lower()
                if response not in ['yes', 'y']:
                    print("❌ Deletion cancelled.")
                    return False
            
            # Delete user
            success = await auth_service.delete_user(user_id)
            
            if success:
                print(f"✅ User '{user.user_name}' deleted successfully.")
                return True
            else:
                print(f"❌ Failed to delete user '{user_id}'.")
                return False
                
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        return False


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="User management CLI for Avatar API authentication"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Create user command
    create_parser = subparsers.add_parser('create', help='Create a new user')
    create_parser.add_argument('username', help='Username for the new user')
    create_parser.add_argument('--password', '-p', help='Password (will prompt if not provided)')
    create_parser.add_argument('--email', '-e', help='Email address')
    create_parser.add_argument('--first-name', help='First name')
    create_parser.add_argument('--last-name', help='Last name')
    create_parser.add_argument('--roles', '-r', nargs='*', default=[],
                              help='User roles (e.g., admin user demo)')
    
    # List users command
    list_parser = subparsers.add_parser('list', help='List all users')
    
    # Delete user command
    delete_parser = subparsers.add_parser('delete', help='Delete a user')
    delete_parser.add_argument('user_id', help='User ID to delete')
    delete_parser.add_argument('--force', '-f', action='store_true',
                              help='Skip confirmation prompt')
    
    # Create demo users command
    demo_parser = subparsers.add_parser('create-demo', help='Create demo users for testing')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'create':
            success = asyncio.run(create_user(
                username=args.username,
                password=args.password,
                email=args.email,
                first_name=args.first_name,
                last_name=args.last_name,
                roles=args.roles
            ))
            sys.exit(0 if success else 1)
            
        elif args.command == 'list':
            asyncio.run(list_users())
            
        elif args.command == 'delete':
            success = asyncio.run(delete_user(args.user_id, args.force))
            sys.exit(0 if success else 1)
            
        elif args.command == 'create-demo':
            async def create_demo_users():
                # Create demo users
                demo_users = [
                    ("demo", "password123", "demo@example.com", "Demo", "User", ["demo"]),
                    ("admin", "admin123", "admin@example.com", "Admin", "User", ["admin", "demo"]),
                    ("test", "test123", "test@example.com", "Test", "User", ["demo"])
                ]
                
                print("Creating demo users...")
                success_count = 0
                skipped_count = 0
                for username, password, email, first_name, last_name, roles in demo_users:
                    print(f"\nCreating {username}...")
                    result = await create_user(username, password, email, first_name, last_name, roles)
                    if result is True:
                        success_count += 1
                    elif isinstance(result, str) and "already exists" in result:
                        print(f"  ⚠️  {username} already exists, skipping")
                        skipped_count += 1
                
                print(f"\n✅ Demo users summary:")
                print(f"   Created: {success_count}")
                print(f"   Already existed: {skipped_count}")
                print(f"   Total available: {success_count + skipped_count}/{len(demo_users)}")
                
                if success_count + skipped_count == len(demo_users):
                    print("\n🎉 All demo users are ready to use!")
            
            asyncio.run(create_demo_users())
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()