"""Tests for scheduling game session storage."""

from game.scheduling_game import GameSessionStore


class TestGameSessionStore:
    """TTL session storage for mock gameplay state."""

    def test_create_and_read_session(self):
        store = GameSessionStore()
        session_id = store.create_session(
            {
                "scenario_id": "family_chaos_normal_001",
                "difficulty": "normal",
                "people": [],
                "tasks": [],
            },
            ttl_seconds=120,
            now_ts=100.0,
        )

        loaded = store.get_session(session_id, now_ts=110.0)

        assert loaded is not None
        assert loaded.get("scenario_id") == "family_chaos_normal_001"
        assert loaded.get("difficulty") == "normal"
        assert loaded.get("schedule") == []

    def test_append_event_updates_schedule(self):
        store = GameSessionStore()
        session_id = store.create_session({"scenario_id": "s1"}, ttl_seconds=120, now_ts=100.0)

        success = store.append_event(
            session_id,
            {
                "task_id": "t1",
                "person_id": "p1",
                "start_time": "2026-06-15T09:00:00",
            },
            now_ts=101.0,
        )

        loaded = store.get_session(session_id, now_ts=102.0)

        assert success is True
        assert loaded is not None
        assert len(loaded.get("schedule") or []) == 1
        assert (loaded.get("schedule") or [])[0].get("task_id") == "t1"

    def test_expired_session_returns_none(self):
        store = GameSessionStore()
        session_id = store.create_session({"scenario_id": "s1"}, ttl_seconds=10, now_ts=100.0)

        assert store.get_session(session_id, now_ts=109.0) is not None
        assert store.get_session(session_id, now_ts=111.0) is None

    def test_append_event_fails_for_missing_session(self):
        store = GameSessionStore()
        success = store.append_event("missing", {"task_id": "t1"}, now_ts=100.0)
        assert success is False
