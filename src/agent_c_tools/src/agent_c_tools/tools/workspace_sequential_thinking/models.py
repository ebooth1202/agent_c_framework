from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, field_serializer


class ThoughtModel(BaseModel):
    """Model for a thought in a sequential thinking process."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool = True
    is_revision: bool = False
    revises_thought: Optional[int] = None
    branch_from_thought: Optional[int] = None
    branch_id: Optional[str] = None
    needs_more_thoughts: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()


class ThoughtBranchModel(BaseModel):
    """Model for a branch in the sequential thinking process."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str = ""
    parent_thought_id: str
    thought_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()


class SequentialThinkingModel(BaseModel):
    """Model for a sequential thinking process that contains thoughts and branches."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    thoughts: Dict[str, ThoughtModel] = Field(default_factory=dict)
    branches: Dict[str, ThoughtBranchModel] = Field(default_factory=dict)
    thought_history: List[str] = Field(default_factory=list)  # List of thought IDs in order
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()