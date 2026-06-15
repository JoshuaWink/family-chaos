"""Person model used in scheduling game scenarios."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Person:
    """A schedulable person in the game scenario."""

    person_id: str
    name: str
    home_location: str
    age: int = 0
    can_drive: bool = False
    occupation: str = ""
    work_schedule: str = ""
    bio: str = ""
    likes: str = ""
    primary_driver_id: Optional[str] = None
