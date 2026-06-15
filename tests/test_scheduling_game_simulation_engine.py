"""Tests for scheduling game simulation conflict detection."""

from datetime import datetime

from game.scheduling_game import ScheduledEvent, SimulationEngine


def _dt(value: str) -> datetime:
    return datetime.fromisoformat(value)


class TestSimulationEngine:
    """Simulation engine validates schedules against core constraints."""

    def test_accepts_conflict_free_schedule(self):
        engine = SimulationEngine(travel_buffer_minutes=30)
        events = [
            ScheduledEvent(
                task_id="t1",
                person_id="p1",
                start_time=_dt("2026-06-15T09:00:00"),
                duration_minutes=60,
                location="school",
                resource_id=None,
            ),
            ScheduledEvent(
                task_id="t2",
                person_id="p1",
                start_time=_dt("2026-06-15T10:45:00"),
                duration_minutes=30,
                location="clinic",
                resource_id=None,
            ),
            ScheduledEvent(
                task_id="t3",
                person_id="p2",
                start_time=_dt("2026-06-15T09:15:00"),
                duration_minutes=45,
                location="office",
                resource_id="car_2",
            ),
        ]

        report = engine.simulate(events)

        assert report.is_valid is True
        assert report.conflicts == []

    def test_flags_double_booking_for_same_person(self):
        engine = SimulationEngine(travel_buffer_minutes=30)
        events = [
            ScheduledEvent(
                task_id="t1",
                person_id="p1",
                start_time=_dt("2026-06-15T09:00:00"),
                duration_minutes=60,
                location="school",
                resource_id=None,
            ),
            ScheduledEvent(
                task_id="t2",
                person_id="p1",
                start_time=_dt("2026-06-15T09:30:00"),
                duration_minutes=45,
                location="clinic",
                resource_id=None,
            ),
        ]

        report = engine.simulate(events)

        assert report.is_valid is False
        assert any(conflict.get("type") == "double_booking" for conflict in report.conflicts)

    def test_flags_travel_buffer_violation(self):
        engine = SimulationEngine(travel_buffer_minutes=30)
        events = [
            ScheduledEvent(
                task_id="t1",
                person_id="p1",
                start_time=_dt("2026-06-15T09:00:00"),
                duration_minutes=60,
                location="school",
                resource_id=None,
            ),
            ScheduledEvent(
                task_id="t2",
                person_id="p1",
                start_time=_dt("2026-06-15T10:10:00"),
                duration_minutes=30,
                location="clinic",
                resource_id=None,
            ),
        ]

        report = engine.simulate(events)

        assert report.is_valid is False
        assert any(conflict.get("type") == "travel_buffer" for conflict in report.conflicts)

    def test_flags_resource_contention(self):
        engine = SimulationEngine(travel_buffer_minutes=30)
        events = [
            ScheduledEvent(
                task_id="t1",
                person_id="p1",
                start_time=_dt("2026-06-15T09:00:00"),
                duration_minutes=60,
                location="school",
                resource_id="family_car",
            ),
            ScheduledEvent(
                task_id="t2",
                person_id="p2",
                start_time=_dt("2026-06-15T09:15:00"),
                duration_minutes=30,
                location="clinic",
                resource_id="family_car",
            ),
        ]

        report = engine.simulate(events)

        assert report.is_valid is False
        assert any(conflict.get("type") == "resource_conflict" for conflict in report.conflicts)
