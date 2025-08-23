import datetime
from typing import Optional, Dict, Any, List, Annotated
from pydantic import Field, model_validator, BeforeValidator
from agent_c.util import MnemonicSlugs
from agent_c.models.base import BaseModel


class ChatUser(BaseModel):
    version: int = Field(1, description="The version of the user model. This is used to track changes in the user model.")
    user_id: Optional[str] = Field(
        default_factory=lambda: MnemonicSlugs.generate_slug(2),
        description=("The ID of the user, in slug format. This is the core ID for the user. "
                     "If not provided, it will be generated based on the user name.")
    )
    user_name: str = Field("agent_c_user", description="The user name associated with the user from the application auth")
    email: Optional[str] = Field(None, description="The email of the user, used for notifications and account management.")
    first_name: Optional[str] = Field("New", description="The first name of the user, used for personalization.")
    last_name: Optional[str] = Field("User", description="The last name of the user, used for personalization.")
    created_at: str = Field(default_factory=lambda: datetime.datetime.now().isoformat(),
                            description="The timestamp when the user was created, used for tracking changes.")
    updated_at: Optional[str] = Field(None, description="The timestamp when the user was last updated, used for tracking changes.")
    deleted_at: Optional[str] = Field(None, description="The timestamp when the user was deleted, used for tracking changes.")
    roles: List[str] = Field(default_factory=list, description="Roles associated with the user.")
    groups: List[str] = Field(default_factory=list, description="Groups associated with the user.")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary user metadata.")
    
    # Authentication fields
    password_hash: Optional[str] = Field(None, description="Hashed password for authentication")
    is_active: bool = Field(True, description="Whether the user account is active")
    last_login: Optional[str] = Field(None, description="ISO timestamp of last login")

    @model_validator(mode='after')
    def post_init(self):
        if not self.user_id:
            self.user_id = MnemonicSlugs.generate_id_slug(2, self.user_name)
        return self

    def is_new_user(self) -> bool:
        return self.user_name == self.model_fields['user_name'].default


def _ensure_chat_user(v):
    """BeforeValidator function to coerce inputs to ChatUser."""
    if isinstance(v, ChatUser) or v is None:
        return v
    if isinstance(v, dict):
        return ChatUser(**v)
    if isinstance(v, str):
        # For string input, we need to load from repository
        # This will be implemented in the API layer with proper dependency injection
        # For now, we'll raise a clear error with the user_id
        raise NotImplementedError(f"Loading user by ID string '{v}' requires repository access - implement at application level")
    raise TypeError(f"Expected ChatUser, dict, or str, got {type(v)}")


# Type annotation for ChatUser-like inputs
ChatUserLike = Annotated[ChatUser, BeforeValidator(_ensure_chat_user)]


