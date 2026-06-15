"""Core schedule validation logic for the scheduling game."""

from typing import Dict, Iterable, List

from .scheduled_event import ScheduledEvent
from .simulation_report import SimulationReport


class SimulationEngine:
    """Validate scheduled events against conflict rules."""

    def __init__(self, travel_buffer_minutes: int = 30) -> None:
        self.travel_buffer_minutes = int(travel_buffer_minutes)

    def simulate(self, events: Iterable[ScheduledEvent]) -> SimulationReport:
        """Evaluate all rules and return a report."""
        event_list = list(events)
        conflicts = []
        conflicts.extend(self._find_double_booking_conflicts(event_list))
        conflicts.extend(self._find_travel_buffer_conflicts(event_list))
        conflicts.extend(self._find_resource_conflicts(event_list))
        return SimulationReport(is_valid=len(conflicts) == 0, conflicts=conflicts)

    def _find_double_booking_conflicts(self, events: List[ScheduledEvent]) -> List[Dict[str, str]]:
        by_person = {}
        for event in events:
            by_person.setdefault(event.person_id, []).append(event)

        conflicts = []
        for person_id, person_events in by_person.items():
            ordered = sorted(person_events, key=lambda item: item.start_time)
            for index in range(len(ordered) - 1):
                first = ordered[index]
                second = ordered[index + 1]
                if first.overlaps(second):
                    conflicts.append({
                        "type": "double_booking",
                        "person_id": person_id,
                        "task_a": first.task_id,
                        "task_b": second.task_id,
                    })
        return conflicts

    def _find_travel_buffer_conflicts(self, events: List[ScheduledEvent]) -> List[Dict[str, str]]:
        by_person = {}
        for event in events:
            by_person.setdefault(event.person_id, []).append(event)

        conflicts = []
        for person_id, person_events in by_person.items():
            ordered = sorted(person_events, key=lambda item: item.start_time)
            for index in range(len(ordered) - 1):
                first = ordered[index]
                second = ordered[index + 1]
                if first.location == second.location:
                    continue

                gap_minutes = (second.start_time - first.end_time()).total_seconds() / 60.0
                if gap_minutes < float(self.travel_buffer_minutes):
                    conflicts.append({
                        "type": "travel_buffer",
                        "person_id": person_id,
                        "from_task": first.task_id,
                        "to_task": second.task_id,
                    })
        return conflicts

    def _find_resource_conflicts(self, events: List[ScheduledEvent]) -> List[Dict[str, str]]:
        by_resource = {}
        for event in events:
            if event.resource_id:
                by_resource.setdefault(event.resource_id, []).append(event)

        conflicts = []
        for resource_id, resource_events in by_resource.items():
            ordered = sorted(resource_events, key=lambda item: item.start_time)
            for index in range(len(ordered) - 1):
                first = ordered[index]
                second = ordered[index + 1]
                if first.overlaps(second):
                    conflicts.append({
                        "type": "resource_conflict",
                        "resource_id": resource_id,
                        "task_a": first.task_id,
                        "task_b": second.task_id,
                    })
        return conflicts
