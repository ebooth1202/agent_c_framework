from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from uuid import uuid4
from pydantic import BaseModel, Field, field_serializer


class Entity(BaseModel):
    """Model for an entity in a knowledge graph."""
    name: str
    entity_type: str
    observations: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()


class Relation(BaseModel):
    """Model for a relation between entities in a knowledge graph."""
    from_entity: str
    to_entity: str
    relation_type: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('created_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()


class KnowledgeGraph(BaseModel):
    """Model for a knowledge graph that contains entities and relations."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    description: str = ""
    entities: Dict[str, Entity] = Field(default_factory=dict)
    relations: List[Relation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime) -> str:
        return dt.isoformat()