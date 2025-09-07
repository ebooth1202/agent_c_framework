import json
import yaml

from typing import Optional, Dict, List

from agent_c.config.saved_chat import SavedChatLoader
from agent_c.models.chat_history.chat_session import ChatSession, ChatSessionQueryResponse, ChatSessionIndexEntry
from agent_c.util.logging_utils import LoggingManager



class ChatSessionManager:
    """
    Interface for managing chat sessions.

    This is the base interface for chat session management and requires derived classes
    to implement all methods for functionality. On its own, it's purely a blueprint.
    """

    def __init__(self, loader: Optional[SavedChatLoader] = None) -> None:
        """
        Initializes a new instance of ChatSessionManager with default values.
        """
        self.is_new_user: bool = True
        self.is_new_session: bool = True
        self._loader: SavedChatLoader = loader or SavedChatLoader()
        # User-based cache: {user_id: {session_id: ChatSession}}
        self._session_cache: Dict[str, Dict[str, ChatSession]] = {}
        self.logger = LoggingManager(__name__).get_logger()

    async def initialize(self) -> dict:
        """
        Initialize the chat session manager and underlying storage.
        
        This should be called during application startup to ensure
        the database is ready and any migrations are handled.
        
        Returns:
            Dictionary with initialization results
        """
        return await self._loader.initialize_with_migration()

    async def delete_session(self, session_id: str, user_id: str) -> None:
        """
        Deletes a chat session by its ID.

        Args:
            session_id (str): The ID of the session to delete.
            user_id (str): The user ID who owns the session.
        """
        # Remove from user's cache if present
        if user_id in self._session_cache and session_id in self._session_cache[user_id]:
            del self._session_cache[user_id][session_id]
            # Clean up empty user cache
            if not self._session_cache[user_id]:
                del self._session_cache[user_id]

        await self._loader.delete_session(session_id, user_id)

    async def new_session(self, session: ChatSession):
        """
        Creates a new session and adds it to the user's cache.
        
        Args:
            session: The ChatSession to create
        """
        user_id = session.user_id
        
        # Ensure user cache exists
        if user_id not in self._session_cache:
            self._session_cache[user_id] = {}
        
        # Add to user's cache
        self._session_cache[user_id][session.session_id] = session
        session.touch()


    async def get_session(self, session_id: str, user_id: str) -> Optional[ChatSession]:
        """
        Retrieves a chat session by its ID.

        Args:
            session_id (str): The ID of the session to retrieve.
            user_id (str): The user ID who owns the session.

        Returns:
            Optional[ChatSession]: The chat session if found, otherwise None.
        """
        # Check user's cache first
        if user_id in self._session_cache and session_id in self._session_cache[user_id]:
            return self._session_cache[user_id][session_id]

        # Try to load from storage
        try:
            session = self._loader.load_session_id(session_id, user_id)
            
            # Add to user's cache
            if user_id not in self._session_cache:
                self._session_cache[user_id] = {}
            self._session_cache[user_id][session_id] = session
            
            return session
        except FileNotFoundError:
            return None

    async def update(self) -> None:
        """
        Asynchronously updates the cached session and user. Meant to sync in-memory changes.
        """
        pass

    async def flush(self, session_id: str, user_id: str) -> None:
        """
        Flushes a session to storage.
        
        Args:
            session_id: The session ID to flush
            user_id: The user ID who owns the session
        """
        session = None
        if user_id in self._session_cache and session_id in self._session_cache[user_id]:
            session = self._session_cache[user_id][session_id]
            
        if session is None or len(session.messages) == 0:
            self.logger.warning(f"Session {session_id} for user {user_id} is empty or not found, skipping flush.")
            return
            
        await self._loader.save_session(session)

    async def get_user_sessions(self, user_id: str, offset: int = 0, limit: int = 50) -> ChatSessionQueryResponse:
        """
        Get paginated chat sessions for a user, sorted by updated_at descending.
        
        Args:
            user_id: The user ID to query sessions for
            limit: Maximum number of sessions to return (default 50)
            offset: Number of sessions to skip for pagination (default 0)
            
        Returns:
            ChatSessionQueryResponse with chat_sessions list and total_sessions count
        """
        return await self._loader.get_user_sessions(user_id, offset, limit)
    
    async def get_user_session_ids(self, user_id: str) -> List[str]:
        """
        Get a list of session IDs for a specific user.
        
        Args:
            user_id: The user ID to get session IDs for
            
        Returns:
            List of session IDs for the user
        """
        return self._loader.get_user_session_ids(user_id)
    
    def get_cached_user_sessions(self, user_id: str) -> Dict[str, ChatSession]:
        """
        Get all cached sessions for a user.
        
        Args:
            user_id: The user ID to get cached sessions for
            
        Returns:
            Dictionary of session_id -> ChatSession for cached sessions
        """
        return self._session_cache.get(user_id, {})
    
    def get_cached_session_count(self, user_id: str) -> int:
        """
        Get the number of cached sessions for a user.
        
        Args:
            user_id: The user ID to count cached sessions for
            
        Returns:
            Number of sessions currently cached for the user
        """
        return len(self._session_cache.get(user_id, {}))
    
    def clear_user_cache(self, user_id: str) -> None:
        """
        Clear all cached sessions for a user.
        
        Args:
            user_id: The user ID to clear cache for
        """
        if user_id in self._session_cache:
            del self._session_cache[user_id]
            self.logger.debug(f"Cleared session cache for user {user_id}")
    
    async def get_all_users_with_sessions(self) -> List[str]:
        """
        Get a list of all user IDs that have chat sessions.
        
        Returns:
            List of user IDs that have sessions
        """
        return await self._loader.get_all_users_with_sessions()
    
    async def get_user_session_count(self, user_id: str) -> int:
        """
        Get the total number of sessions for a specific user.
        
        Args:
            user_id: The user ID to count sessions for
            
        Returns:
            Total number of sessions for the user
        """
        return await self._loader.get_user_session_count(user_id)
    
    async def get_system_session_stats(self) -> Dict[str, int]:
        """
        Get overall statistics about the chat session system.
        
        Returns:
            Dictionary with system-wide session statistics
        """
        return await self._loader.get_system_session_stats()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get statistics about the current cache usage.
        
        Returns:
            Dictionary with cache statistics
        """
        total_sessions = sum(len(user_sessions) for user_sessions in self._session_cache.values())
        
        return {
            "total_users_cached": len(self._session_cache),
            "total_sessions_cached": total_sessions,
            "users_with_sessions": [user_id for user_id in self._session_cache.keys()],
            "sessions_per_user": {user_id: len(sessions) for user_id, sessions in self._session_cache.items()}
        }

    def filtered_session_meta(self, prefix: str) -> Dict:
        """
        Returns session meta information filtered by the specified prefix.

        Args:
            prefix (str): The prefix to filter for.

        Returns:
            Dict: Dictionary containing filtered session metadata.
        """
        return self.get_session_meta_meta(prefix)

    def filtered_user_meta(self, prefix: str) -> Dict:
        """
        Returns user meta information filtered by the specified prefix.

        Args:
            prefix (str): The prefix to filter for.

        Returns:
            Dict: Dictionary containing filtered user metadata.
        """
        return self.get_user_meta_meta(prefix)

    def get_user_meta_meta(self, prefix: str) -> Dict:
        """
        Retrieves 'metameta' user metadata associated with the given prefix.

        Args:
            prefix (str): The desired metadata prefix.

        Returns:
            Dict: A dictionary containing the desired user metadata.

        Raises:
            Exception: If metadata cannot be decoded properly.
        """
        json_str = self.user.metadata.get('metameta', {}).get(prefix, '{}')
        try:
            return json.loads(json_str)
        except Exception as e:
            self.logger.exception(f"Failed to decode metameta for {prefix}")
            return {}

    def set_user_meta_meta(self, prefix: str, metameta: Dict) -> None:
        """
        Sets 'metameta' user metadata under the specified prefix.

        Args:
            prefix (str): The prefix under which metadata should be stored.
            metameta (Dict): The metadata to set.

        Raises:
            Exception: If metadata cannot be encoded into JSON.
        """
        try:
            json_str = json.dumps(metameta)
        except Exception as e:
            self.logger.exception(f"Failed to encode metameta for {prefix}")
            raise

        if not self.user.metadata.get('metameta'):
            self.user.metadata['metameta'] = {prefix: json_str}
        else:
            self.user.metadata['metameta'][prefix] = json_str

    def get_session_meta_meta(self, session_id: str, user_id: str, prefix: str) -> Dict:
        """
        Retrieves 'metameta' session metadata associated with the given prefix.

        Args:
            session_id (str): The ID of the session to retrieve metadata from.
            user_id (str): The user ID who owns the session.
            prefix (str): The desired metadata prefix.

        Returns:
            Dict: A dictionary containing the desired session metadata.

        Raises:
            Exception: If metadata cannot be decoded properly.
        """
        chat_session = None
        if user_id in self._session_cache and session_id in self._session_cache[user_id]:
            chat_session = self._session_cache[user_id][session_id]
            
        if chat_session is None:
            self.logger.warning(f"Session {session_id} for user {user_id} not found in cache")
            return {}
            
        json_str = chat_session.metadata.get('metameta', {}).get(prefix, '{}')
        try:
            return json.loads(json_str)
        except Exception:
            self.logger.exception(f"Failed to decode session metameta for {prefix}")
            return {}

    def set_session_meta_meta(self, session_id: str, user_id: str, prefix: str, metameta: Dict) -> None:
        """
        Sets 'metameta' session metadata under the specified prefix.

        Args:
            session_id (str): The ID of the session to set metadata for.
            user_id (str): The user ID who owns the session.
            prefix (str): The prefix under which the metadata should be stored.
            metameta (Dict): The metadata to store.

        Raises:
            Exception: If metadata cannot be encoded into JSON.
        """
        try:
            json_str = json.dumps(metameta)
        except Exception as e:
            self.logger.exception(f"Failed to encode session metameta for {prefix}")
            raise

        chat_session = None
        if user_id in self._session_cache and session_id in self._session_cache[user_id]:
            chat_session = self._session_cache[user_id][session_id]
            
        if chat_session is None:
            self.logger.warning(f"Session {session_id} for user {user_id} not found in cache")
            return
            
        if not chat_session.metadata.get('metameta'):
            chat_session.metadata['metameta'] = {prefix: json_str}
        else:
            chat_session.metadata['metameta'][prefix] = json_str


    def dict_to_yaml(self, data_dict: Dict) -> str:
        """
        Converts a dictionary into YAML format.

        Args:
            data_dict (Dict): The dictionary to convert.

        Returns:
            str: The YAML string representation of the dictionary.

        Raises:
            yaml.YAMLError: If an error occurs during YAML conversion.
        """
        try:
            return yaml.dump(data_dict)
        except yaml.YAMLError as exc:
            self.logger.error(f"Error serializing to YAML: {exc}")
            return ""

    def filtered_session_meta_string(self, prefix: str) -> str:
        """
        Returns filtered session meta information as a YAML string.

        Args:
            prefix (str): The prefix to filter session meta information for.

        Returns:
            str: YAML string representation of the filtered session meta.
        """
        return self.dict_to_yaml(self.filtered_session_meta(prefix))

    def filtered_user_meta_string(self, prefix: str) -> str:
        """
        Returns filtered user meta information as a YAML string.

        Args:
            prefix (str): The prefix to filter user meta information for.

        Returns:
            str: YAML string representation of the filtered user meta.
        """
        return self.dict_to_yaml(self.filtered_user_meta(prefix))
