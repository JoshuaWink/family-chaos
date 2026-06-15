"""ScheduledEvent model for user-placed tasks."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


@dataclass(frozen=True)
class ScheduledEvent:
    """A concrete placement of a task on a person's calendar."""

    task_id: str
    person_id: str
    start_time: datetime
    duration_minutes: int
    location: str
    resource_id: Optional[str] = None

    def end_time(self) -> datetime:
        """Return event end time based on start + duration."""
        return self.start_time + timedelta(minutes=self.duration_minutes)

    def overlaps(self, other: "ScheduledEvent") -> bool:
        """Return True when time ranges intersect."""
        return self.start_time < other.end_time() and other.start_time < self.end_time()
