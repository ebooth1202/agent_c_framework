import datetime
from pydantic import Field
from typing import Optional, Dict, Any, List

from agent_c.models.base import BaseModel
from agent_c.util.slugs import MnemonicSlugs
from agent_c.models.agent_config import CurrentAgentConfiguration


class ChatSessionIndexEntry(BaseModel):
    """
    Represents a lightweight index entry for a chat session.
    """
    session_id: str = Field(..., description="Unique identifier for the chat session")
    session_name: Optional[str] = Field(None, description="The name of the session, if any")
    created_at: Optional[str] = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    user_id: Optional[str] = Field("Agent C user", description="The user ID associated with the session")


class ChatSessionQueryResponse(BaseModel):
    """
    Response model for paginated chat session queries.
    """
    chat_sessions: List[ChatSessionIndexEntry] = Field(default_factory=list, description="List of chat session index entries")
    total_sessions: int = Field(0, description="Total number of sessions available for the query")
    offset: int = Field(0, description="The offset used in the query")


class ChatSession(BaseModel):
    """
    Represents a session object with a unique identifier, metadata,
    and other attributes.
    """
    version: int = Field(1, description="Version of the chat session schema")
    session_id: str = Field(default_factory=lambda: MnemonicSlugs.generate_slug(2))
    token_count: int = Field(0, description="The number of tokens used in the session")
    context_window_size: int = Field(0, description="The number of tokens in the context window")
    session_name: Optional[str] = Field(None, description="The name of the session, if any")
    created_at: Optional[str] = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.datetime.now().isoformat())
    deleted_at: Optional[str] = Field(None, description="Timestamp when the session was deleted")
    user_id: Optional[str] = Field("Agent C user", description="The user ID associated with the session")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata associated with the session")
    messages: List[dict[str, Any]] = Field(default_factory=list, description="List of messages in the session")
    agent_config: Optional[CurrentAgentConfiguration] = Field(None, description="Configuration for the agent associated with the session")

    def touch(self) -> None:
        """
        Updates the updated_at timestamp to the current time.
        """
        self.updated_at = datetime.datetime.now().isoformat()
