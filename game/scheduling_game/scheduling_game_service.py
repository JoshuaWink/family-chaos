"""Service layer for scheduling game API operations."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .game_session_store import GameSessionStore
from .scheduled_event import ScheduledEvent
from .scenario_generator import ScenarioGenerator
from .simulation_engine import SimulationEngine


def _parse_datetime(value: str) -> datetime:
    text = str(value or "").strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    return datetime.fromisoformat(text)


class SchedulingGameService:
    """High-level game service used by HTTP handlers."""

    def __init__(
        self,
        session_store: Optional[GameSessionStore] = None,
        scenario_generator: Optional[ScenarioGenerator] = None,
        simulation_engine: Optional[SimulationEngine] = None,
        session_ttl_seconds: int = 24 * 60 * 60,
    ) -> None:
        self._session_store = session_store or GameSessionStore()
        self._scenario_generator = scenario_generator or ScenarioGenerator()
        self._simulation_engine = simulation_engine or SimulationEngine()
        self._session_ttl_seconds = int(session_ttl_seconds)

    def health(self) -> Dict[str, Any]:
        """Service health payload."""
        return {
            "status": "ok",
            "service": "scheduling-game",
        }

    def new_game(self, difficulty: str = "normal") -> Dict[str, Any]:
        """Create a new game session from a generated scenario."""
        scenario = self._scenario_generator.generate(difficulty)
        people = []
        for person in scenario.get("people") or []:
            people.append(
                {
                    "person_id": person.person_id,
                    "name": person.name,
                    "home_location": person.home_location,
                    "age": person.age,
                    "can_drive": person.can_drive,
                    "occupation": person.occupation,
                    "work_schedule": person.work_schedule,
                    "bio": person.bio,
                    "likes": person.likes,
                    "primary_driver_id": person.primary_driver_id,
                }
            )

        tasks = []
        for task in scenario.get("tasks") or []:
            tasks.append(
                {
                    "task_id": task.task_id,
                    "description": task.description,
                    "duration_minutes": int(task.duration_minutes),
                    "location": task.location,
                    "resource_id": task.resource_id,
                    "for_person_id": task.for_person_id,
                    "travel_minutes": int(task.travel_minutes),
                    "notes": task.notes,
                }
            )

        session_payload = {
            "scenario_id": scenario.get("scenario_id") or "scenario",
            "difficulty": scenario.get("difficulty") or "normal",
            "people": people,
            "tasks": tasks,
            "schedule": [],
        }

        session_id = self._session_store.create_session(
            session_payload,
            ttl_seconds=self._session_ttl_seconds,
        )
        created = self._session_store.get_session(session_id) or session_payload
        return self._public_session(created)

    def schedule_event(self, session_id: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """Append an event to a session schedule."""
        session = self._session_store.get_session(session_id)
        if session is None:
            return {"ok": False, "error": "session_not_found"}

        normalized = self._normalize_event(session, event)
        if normalized is None:
            return {"ok": False, "error": "invalid_event"}

        stored = self._session_store.append_event(session_id, normalized)
        if not stored:
            return {"ok": False, "error": "session_not_found"}

        updated = self._session_store.get_session(session_id) or session
        schedule = updated.get("schedule") or []

        return {
            "ok": True,
            "session_id": session_id,
            "event": normalized,
            "scheduled_count": len(schedule),
        }

    def simulate_session(self, session_id: str) -> Dict[str, Any]:
        """Run simulation against scheduled events for a session."""
        session = self._session_store.get_session(session_id)
        if session is None:
            return {"ok": False, "error": "session_not_found"}

        events = self._build_events(session)
        report = self._simulation_engine.simulate(events)
        return {
            "ok": True,
            "session_id": session_id,
            "is_valid": bool(report.is_valid),
            "conflicts": list(report.conflicts),
            "scheduled_count": len(events),
        }

    def _public_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "session_id": session.get("session_id"),
            "scenario_id": session.get("scenario_id"),
            "difficulty": session.get("difficulty"),
            "people": list(session.get("people") or []),
            "tasks": list(session.get("tasks") or []),
            "schedule": list(session.get("schedule") or []),
        }

    def _normalize_event(self, session: Dict[str, Any], event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        task_id = (event or {}).get("task_id")
        person_id = (event or {}).get("person_id")
        start_time_raw = (event or {}).get("start_time")
        if not task_id or not person_id or not start_time_raw:
            return None

        try:
            start_time = _parse_datetime(str(start_time_raw))
        except Exception:
            return None

        task = self._find_task(session, str(task_id))

        duration_minutes = (event or {}).get("duration_minutes")
        if duration_minutes is None and task is not None:
            duration_minutes = task.get("duration_minutes")

        location = (event or {}).get("location")
        if not location and task is not None:
            location = task.get("location")

        resource_id = (event or {}).get("resource_id")
        if resource_id is None and task is not None:
            resource_id = task.get("resource_id")

        if duration_minutes is None or not location:
            return None

        return {
            "task_id": str(task_id),
            "person_id": str(person_id),
            "start_time": start_time.isoformat(),
            "duration_minutes": int(duration_minutes),
            "location": str(location),
            "resource_id": resource_id,
        }

    def _find_task(self, session: Dict[str, Any], task_id: str) -> Optional[Dict[str, Any]]:
        for task in session.get("tasks") or []:
            if str(task.get("task_id")) == str(task_id):
                return dict(task)
        return None

    def _build_events(self, session: Dict[str, Any]) -> List[ScheduledEvent]:
        # Last-entry-wins per task_id — supports drag-to-reschedule without
        # a dedicated unschedule endpoint.
        latest: Dict[str, Any] = {}
        for raw in session.get("schedule") or []:
            tid = str((raw or {}).get("task_id") or "")
            if tid:
                latest[tid] = raw

        events = []
        for raw in latest.values():
            try:
                event = ScheduledEvent(
                    task_id=str(raw.get("task_id") or ""),
                    person_id=str(raw.get("person_id") or ""),
                    start_time=_parse_datetime(str(raw.get("start_time") or "")),
                    duration_minutes=int(raw.get("duration_minutes") or 0),
                    location=str(raw.get("location") or ""),
                    resource_id=raw.get("resource_id"),
                )
            except Exception:
                continue

            if not event.task_id or not event.person_id or event.duration_minutes <= 0 or not event.location:
                continue
            events.append(event)

        return events
