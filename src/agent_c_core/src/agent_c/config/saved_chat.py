"""
Loader class for model configuration data.

This module provides a loader class to handle loading, parsing, and saving
of model configurations from JSON files.
"""
import datetime
import json
from pathlib import Path
from typing import Optional, List, Dict

from sqlalchemy import String, Text, Index, select, delete, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from agent_c.util.string import to_snake_case
from agent_c.models.chat_history.chat_session import ChatSession, ChatSessionIndexEntry, ChatSessionQueryResponse
from agent_c.config.config_loader import ConfigLoader


class Base(DeclarativeBase):
    pass


class ChatSessionIndex(Base):
    """
    SQLAlchemy table model for chat session index entries.
    """
    __tablename__ = "chat_session_index"
    
    session_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    session_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    agent_key:Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    __table_args__ = (
        Index("idx_user_updated", "user_id", "updated_at"),
    )


class SavedChatLoader(ConfigLoader):
    """
    Loader for model configuration files.

    Handles loading, parsing, validation, and saving of model configuration
    data from JSON files.
    """

    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.save_file_folder = Path(self.config_path).joinpath("saved_sessions")
        self._engine = None
        self._async_session_factory = None

    @property
    def db_path(self) -> str:
        """Get the path to the SQLite database file."""
        return str(self.save_file_folder.parent / "chat_sessions.db")

    @property
    def engine(self):
        """Get the async SQLAlchemy engine, creating it if necessary."""
        if self._engine is None:
            self._engine = create_async_engine(f"sqlite+aiosqlite:///{self.db_path}")
        return self._engine

    @property
    def async_session_factory(self):
        """Get the async session factory, creating it if necessary."""
        if self._async_session_factory is None:
            self._async_session_factory = async_sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        return self._async_session_factory

    async def initialize_database(self) -> None:
        """
        Initialize the SQLite database and create tables.
        
        This method should be called during server startup to ensure
        the database and tables exist.
        """
        # Ensure the parent directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Create all tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        self.logger.info(f"Initialized chat session database at {self.db_path}")

    async def close_database(self) -> None:
        """
        Close the database connection.
        
        This should be called during application shutdown.
        """
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._async_session_factory = None

    def _get_user_folder(self, user_id: str) -> Path:
        """
        Get the folder path for a specific user's sessions.
        
        Args:
            user_id: The user ID to get the folder for
            
        Returns:
            Path object for the user's session folder
        """
        sanitized_user_id = to_snake_case(user_id)
        return self.save_file_folder / sanitized_user_id

    def _session_to_index_entry(self, session: ChatSession) -> ChatSessionIndexEntry:
        """
        Convert a ChatSession to a ChatSessionIndexEntry for indexing.
        
        Args:
            session: The ChatSession to convert
            
        Returns:
            ChatSessionIndexEntry with the relevant fields
        """
        return ChatSessionIndexEntry(
            session_id=session.session_id,
            session_name=session.session_name,
            created_at=session.created_at,
            updated_at=session.updated_at,
            user_id=session.user_id,
            agent_key = session.agent_config.key,
            agent_name = session.agent_config.agent_name
        )

    async def _create_index_entry(self, session: ChatSession) -> None:
        """
        Create a new index entry for a chat session.
        
        Args:
            session: The ChatSession to index
        """
        index_entry = self._session_to_index_entry(session)
        
        async with self.async_session_factory() as db_session:
            index_record = ChatSessionIndex(
                session_id=index_entry.session_id,
                session_name=index_entry.session_name,
                created_at=index_entry.created_at,
                updated_at=index_entry.updated_at,
                user_id=index_entry.user_id,
                agent_key = index_entry.key,
                agent_name = index_entry.agent_name
            )
            db_session.add(index_record)
            await db_session.commit()
        
        self.logger.debug(f"Created index entry for session {session.session_id}")

    async def _update_index_entry(self, session: ChatSession) -> None:
        """
        Update an existing index entry for a chat session.
        
        Args:
            session: The ChatSession with updated information
        """
        index_entry = self._session_to_index_entry(session)
        
        async with self.async_session_factory() as db_session:
            # Get existing record
            stmt = select(ChatSessionIndex).where(ChatSessionIndex.session_id == session.session_id)
            result = await db_session.execute(stmt)
            existing_record = result.scalar_one_or_none()
            
            if existing_record:
                # Update fields
                existing_record.session_name = index_entry.session_name
                existing_record.updated_at = index_entry.updated_at
                existing_record.user_id = index_entry.user_id
                existing_record.agent_key = session.agent_config.key
                existing_record.agent_name = session.agent_config.agent_name
                await db_session.commit()
                self.logger.debug(f"Updated index entry for session {session.session_id}")
            else:
                # Record doesn't exist, create it
                await self._create_index_entry(session)

    async def _delete_index_entry(self, session_id: str) -> None:
        """
        Delete an index entry for a chat session.
        
        Args:
            session_id: The ID of the session to remove from the index
        """
        async with self.async_session_factory() as db_session:
            stmt = delete(ChatSessionIndex).where(ChatSessionIndex.session_id == session_id)
            result = await db_session.execute(stmt)
            await db_session.commit()
            
            if result.rowcount > 0:
                self.logger.debug(f"Deleted index entry for session {session_id}")
            else:
                self.logger.warning(f"No index entry found to delete for session {session_id}")

    async def get_user_sessions(self, user_id: str, limit: int = 50, offset: int = 0) -> ChatSessionQueryResponse:
        """
        Get paginated chat sessions for a user, sorted by updated_at descending.
        
        Args:
            user_id: The user ID to query sessions for
            limit: Maximum number of sessions to return (default 50)
            offset: Number of sessions to skip for pagination (default 0)
            
        Returns:
            ChatSessionQueryResponse with chat_sessions list and total_sessions count
        """
        async with self.async_session_factory() as db_session:
            # Get the total count for this user
            count_stmt = select(func.count(ChatSessionIndex.session_id)).where(
                ChatSessionIndex.user_id == user_id
            )
            count_result = await db_session.execute(count_stmt)
            total_sessions = count_result.scalar() or 0
            
            # Get the paginated results
            query_stmt = (
                select(ChatSessionIndex)
                .where(ChatSessionIndex.user_id == user_id)
                .order_by(ChatSessionIndex.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            
            query_result = await db_session.execute(query_stmt)
            session_records = query_result.scalars().all()
            
            # Convert SQLAlchemy records to Pydantic models
            chat_sessions = [
                ChatSessionIndexEntry(
                    session_id=record.session_id,
                    session_name=record.session_name,
                    created_at=record.created_at,
                    updated_at=record.updated_at,
                    user_id=record.user_id,
                    agent_key=record.agent_key,
                    agent_name=record.agent_name
                )
                for record in session_records
            ]
            
            return ChatSessionQueryResponse(
                chat_sessions=chat_sessions,
                total_sessions=total_sessions,
                offset=offset
            )

    def get_user_session_ids(self, user_id: str) -> List[str]:
        """
        Get a list of saved session IDs for a specific user.

        Args:
            user_id: The user ID to get session IDs for
            
        Returns:
            List of session IDs as strings for the specified user
        """
        user_folder = self._get_user_folder(user_id)
        if not user_folder.exists():
            return []

        return [f.stem for f in user_folder.glob("*.json")]
        
    @property 
    def session_id_list(self) -> List[str]:
        """
        Get a list of all saved session IDs across all users.
        
        Note: This method scans all user folders and may be slow with many users.
        Consider using get_user_session_ids() for better performance.

        Returns:
            List of session IDs as strings
        """
        if not self.save_file_folder.exists():
            return []

        all_sessions = []
        # Scan all user folders
        for user_folder in self.save_file_folder.iterdir():
            if user_folder.is_dir() and user_folder.name != "deleted":
                all_sessions.extend([f.stem for f in user_folder.glob("*.json")])
        
        return all_sessions
        
    def get_user_list(self) -> List[str]:
        """
        Get a list of all user IDs that have saved sessions.
        
        Returns:
            List of user IDs (original form, not snake_case folder names)
        """
        if not self.save_file_folder.exists():
            return []
            
        users = set()
        for user_folder in self.save_file_folder.iterdir():
            if user_folder.is_dir() and user_folder.name != "deleted":
                # We need to reverse the snake_case conversion, but for now
                # we'll use the folder name as-is. The rebuild process will
                # help establish the proper mapping.
                users.add(user_folder.name)
                
        return list(users)
    
    async def get_all_users_with_sessions(self) -> List[str]:
        """
        Get a list of all user IDs that have chat sessions (from database index).
        
        This is more efficient than get_user_list() for large deployments
        as it queries the database index rather than scanning folders.
        
        Returns:
            List of user IDs that have sessions
        """
        async with self.async_session_factory() as db_session:
            stmt = select(ChatSessionIndex.user_id).distinct()
            result = await db_session.execute(stmt)
            users = [row[0] for row in result.fetchall()]
            return users

    async def get_user_session_count(self, user_id: str) -> int:
        """
        Get the total number of sessions for a specific user.
        
        Args:
            user_id: The user ID to count sessions for
            
        Returns:
            Total number of sessions for the user
        """
        async with self.async_session_factory() as db_session:
            count_stmt = select(func.count(ChatSessionIndex.session_id)).where(
                ChatSessionIndex.user_id == user_id
            )
            result = await db_session.execute(count_stmt)
            return result.scalar() or 0
    
    async def get_system_session_stats(self) -> Dict[str, int]:
        """
        Get overall statistics about the chat session system.
        
        Returns:
            Dictionary with system-wide session statistics
        """
        async with self.async_session_factory() as db_session:
            # Total sessions
            total_stmt = select(func.count(ChatSessionIndex.session_id))
            total_result = await db_session.execute(total_stmt)
            total_sessions = total_result.scalar() or 0
            
            # Total users
            users_stmt = select(func.count(ChatSessionIndex.user_id.distinct()))
            users_result = await db_session.execute(users_stmt)
            total_users = users_result.scalar() or 0
            
            return {
                "total_sessions": total_sessions,
                "total_users": total_users,
                "average_sessions_per_user": round(total_sessions / max(total_users, 1), 2)
            }

    async def rebuild_index_and_migrate_files(self) -> dict:
        """
        Rebuild the SQLite index from existing JSON files and migrate legacy flat structure.
        
        This method will:
        1. Clear the existing index
        2. Move any files from legacy flat structure to user subfolders
        3. Rebuild the index from all JSON session files
        
        Returns:
            Dictionary with migration statistics
        """
        stats = {
            "migrated_files": 0,
            "indexed_sessions": 0,
            "errors": [],
            "users_processed": set()
        }
        
        # Ensure database is initialized
        await self.initialize_database()
        
        # Clear existing index
        async with self.async_session_factory() as db_session:
            await db_session.execute(delete(ChatSessionIndex))
            await db_session.commit()
        
        self.logger.info("Cleared existing chat session index")
        paths = [self.save_file_folder, self.save_file_folder.joinpath("agent__c__user")]
        # First, migrate any files from legacy flat structure
        for path in paths:
            if path.exists():
                for json_file in path.glob("*.json"):
                    try:
                        # Load the session to get the user_id
                        with open(json_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)

                        session = ChatSession.model_validate(session_data)
                        if session.user_id is None or session.user_id.lower() == "agent c user":
                            session.user_id = "admin"  # Migrate old single user account to 'admin'
                            with open(json_file, 'w', encoding='utf-8') as f:
                                json.dump(session.model_dump(), f, indent=4)

                        user_folder = self._get_user_folder(session.user_id)
                        user_folder.mkdir(parents=True, exist_ok=True)

                        # Move file to user subfolder
                        new_path = user_folder / json_file.name
                        if not new_path.exists():  # Don't overwrite existing files
                            json_file.rename(new_path)
                            stats["migrated_files"] += 1
                            stats["users_processed"].add(session.user_id)
                            self.logger.debug(f"Migrated {json_file.name} to {session.user_id} folder")
                        else:
                            self.logger.warning(f"File {new_path} already exists, skipping migration of {json_file}")

                    except Exception as e:
                        error_msg = f"Failed to migrate {json_file}: {e}"
                        stats["errors"].append(error_msg)
                        self.logger.error(error_msg)
        
        # Now rebuild index from all user folders
        if self.save_file_folder.exists():
            for user_folder in self.save_file_folder.iterdir():
                if user_folder.is_dir() and user_folder.name not in ["deleted"]:
                    await self._rebuild_index_for_user_folder(user_folder, stats)
        
        # Convert set to list for JSON serialization
        stats["users_processed"] = list(stats["users_processed"])
        
        self.logger.info(
            f"Index rebuild complete. Migrated: {stats['migrated_files']} files, "
            f"Indexed: {stats['indexed_sessions']} sessions, "
            f"Users: {len(stats['users_processed'])}, "
            f"Errors: {len(stats['errors'])}"
        )
        
        return stats
    
    async def _rebuild_index_for_user_folder(self, user_folder: Path, stats: dict) -> None:
        """
        Rebuild index entries for all sessions in a user folder.
        
        Args:
            user_folder: Path to the user's session folder
            stats: Statistics dictionary to update
        """
        for json_file in user_folder.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                session = ChatSession.model_validate(session_data)
                await self._create_index_entry(session)
                stats["indexed_sessions"] += 1
                stats["users_processed"].add(session.user_id)
                
            except Exception as e:
                error_msg = f"Failed to index {json_file}: {e}"
                stats["errors"].append(error_msg)
                self.logger.error(error_msg)

    async def initialize_with_migration(self) -> dict:
        """
        Initialize the chat session system, automatically migrating if needed.
        
        This method should be called during server startup. It will:
        1. Check if there are JSON files in the legacy flat structure
        2. If yes, run the full migration and index rebuild
        3. If no, just ensure the database is initialized
        
        Returns:
            Dictionary with initialization results. If migration was needed,
            returns migration statistics. Otherwise returns a simple status.
        """
        # Check if we have legacy files that need migration
        legacy_files_exist = False
        if self.save_file_folder.exists():
            legacy_files = list(self.save_file_folder.glob("*.json"))
            agent_c_user_files = list(self.save_file_folder.joinpath("agent__c__user").glob("*.json"))
            legacy_files_exist = len(legacy_files) > 0 or len(agent_c_user_files) > 0
        
        if legacy_files_exist:
            self.logger.info("Legacy session files detected, running migration...")
            return await self.rebuild_index_and_migrate_files()
        else:
            # No legacy files, just ensure database is initialized
            await self.initialize_database()
            self.logger.info("Chat session system initialized (no migration needed)")
            return {
                "migration_needed": False,
                "migrated_files": 0,
                "indexed_sessions": 0,
                "errors": [],
                "users_processed": []
            }

    def load_session_id(self, session_id: str, user_id: str) -> ChatSession:
        """
        Load a chat session by its ID from the user's subfolder.

        Args:
            session_id: The ID of the session to load
            user_id: The user ID to determine which subfolder to search

        Returns:
            ChatSession instance with the loaded data

        Raises:
            FileNotFoundError: If the session file doesn't exist
            json.JSONDecodeError: If the JSON is malformed
            ValidationError: If the JSON doesn't match the expected schema
        """
        user_folder = self._get_user_folder(user_id)
        session_file = user_folder / f"{session_id}.json"

        if not session_file.exists():
            self.logger.warning(f"Session file not found: {session_file}")
            raise FileNotFoundError(f"Session file not found: {session_file}")

        with open(session_file, 'r', encoding='utf-8') as f:
            session_data = json.load(f)

        return ChatSession.model_validate(session_data)

    async def save_session(self, session: ChatSession) -> None:
        """
        Save a chat session to a file in the user's subfolder and update the index.

        Args:
            session: ChatSession instance to save

        Raises:
            ValueError: If the session ID is not set
        """
        user_folder = self._get_user_folder(session.user_id)
        user_folder.mkdir(parents=True, exist_ok=True)
        session_file = user_folder / f"{session.session_id}.json"

        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump(session.model_dump(), f, indent=4)
        
        # Update the index
        try:
            await self._update_index_entry(session)
        except Exception as e:
            self.logger.error(f"Failed to update index for session {session.session_id}: {e}")

    async def delete_session(self, session_id: str, user_id: str) -> None:
        """
        Delete a chat session file by its ID from the user's subfolder.

        Args:
            session_id: The ID of the session to delete
            user_id: The user ID to determine which subfolder to search

        Raises:
            FileNotFoundError: If the session file doesn't exist
        """
        user_folder = self._get_user_folder(user_id)
        session_file = user_folder / f"{session_id}.json"

        if not session_file.exists():
            raise FileNotFoundError(f"Session file not found: {session_file}")

        session: ChatSession = self.load_session_id(session_id, user_id)
        session.deleted_at = datetime.datetime.now().isoformat()
        await self.save_session(session)
        # move the file to a deleted folder within the user's folder
        deleted_folder = user_folder / "deleted"
        deleted_folder.mkdir(parents=True, exist_ok=True)
        session_file.rename(deleted_folder / session_file.name)
        
        # Remove from index
        try:
            await self._delete_index_entry(session_id)
        except Exception as e:
            self.logger.error(f"Failed to delete index for session {session_id}: {e}")
        
        self.logger.info(f"Deleted session file: {session_file}")