"""
Data models for the AI Notes/Task Manager
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import time

class ItemType(Enum):
    NOTE = "note"
    TASK = "task"
    RESOURCE = "resource"

@dataclass
class NoteItem:
    id: Optional[int]
    timestamp: float
    raw_content: str
    enhanced_content: str
    item_type: ItemType = ItemType.NOTE
    is_completed: bool = False
    
    @property
    def formatted_date(self) -> str:
        return time.strftime("%Y-%m-%d %H:%M", time.localtime(self.timestamp))

@dataclass
class SearchResult:
    """Result from semantic search"""
    item: NoteItem
    similarity_score: float
