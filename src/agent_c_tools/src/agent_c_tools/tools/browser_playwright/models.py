from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime


ElementType = Literal["link", "button", "input", "text", "image", "checkbox", "radio", "select", "other"]
TabActionType = Literal["new", "close", "select", "list"]


class ElementModel(BaseModel):
    """Model for an element in a page snapshot."""
    ref: str
    element_type: ElementType
    description: str
    text: Optional[str] = None
    value: Optional[str] = None
    attributes: Dict[str, str] = Field(default_factory=dict)
    accessible_name: Optional[str] = None
    is_visible: bool = True
    is_enabled: bool = True
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    

class SnapshotModel(BaseModel):
    """Model for a page snapshot containing accessibility information."""
    url: str
    title: str
    elements: List[ElementModel] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)


class TabModel(BaseModel):
    """Model for a browser tab."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    index: int
    title: str
    url: str
    is_active: bool = False


class BrowserSessionModel(BaseModel):
    """Model for a browser session."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    tabs: List[TabModel] = Field(default_factory=list)
    active_tab_index: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)