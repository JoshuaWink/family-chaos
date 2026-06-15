"""Task model used in scheduling game scenarios."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Task:
    """A task that must be placed on a schedule."""

    task_id: str
    description: str
    duration_minutes: int
    location: str
    resource_id: Optional[str] = None
    for_person_id: Optional[str] = None
    travel_minutes: int = 0
    notes: str = ""
