"""Data models for projects."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class Project:
    """Represents a project with all its metadata."""

    id: int
    name: str
    path: Optional[str]
    description: Optional[str]
    status: str  # active, paused, completed, abandoned
    priority: str  # high, medium, low
    language: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_activity: Optional[datetime]
    tags: List[str]

    def __post_init__(self):
        """Convert string timestamps to datetime if needed."""
        # Si created_at est un string (venant de la DB), le convertir
        if isinstance(self.created_at, str):
            self.created_at = datetime.fromisoformat(self.created_at)
        if isinstance(self.updated_at, str):
            self.updated_at = datetime.fromisoformat(self.updated_at)
        if isinstance(self.last_activity, str):
            self.last_activity = datetime.fromisoformat(self.last_activity)
