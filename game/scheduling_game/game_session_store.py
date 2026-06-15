"""In-memory TTL session store for scheduling game state."""

import time
import uuid
from typing import Any, Dict, Optional


class GameSessionStore:
    """Store ephemeral game sessions with expiration semantics."""

    def __init__(self) -> None:
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def create_session(
        self,
        scenario: Dict[str, Any],
        ttl_seconds: int = 24 * 60 * 60,
        now_ts: Optional[float] = None,
    ) -> str:
        """Create a new session and return its ID."""
        now = self._now(now_ts)
        session_id = uuid.uuid4().hex

        session = dict(scenario or {})
        session["session_id"] = session_id
        session["schedule"] = list(session.get("schedule") or [])
        session["created_at"] = now
        session["expires_at"] = now + float(ttl_seconds)

        self._sessions[session_id] = session
        return session_id

    def get_session(self, session_id: str, now_ts: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """Read a session by ID. Expired sessions return None."""
        self._purge_expired(now_ts)
        session = self._sessions.get(session_id)
        if session is None:
            return None

        return self._clone_session(session)

    def append_event(self, session_id: str, event: Dict[str, Any], now_ts: Optional[float] = None) -> bool:
        """Append a scheduled event to an existing session."""
        self._purge_expired(now_ts)
        session = self._sessions.get(session_id)
        if session is None:
            return False

        schedule = session.get("schedule")
        if not isinstance(schedule, list):
            schedule = []
            session["schedule"] = schedule

        schedule.append(dict(event or {}))
        return True

    def delete_session(self, session_id: str) -> bool:
        """Delete a session if present."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def _clone_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        copied = dict(session)
        copied["schedule"] = [dict(item) for item in session.get("schedule") or []]
        return copied

    def _purge_expired(self, now_ts: Optional[float]) -> None:
        now = self._now(now_ts)
        expired_ids = []
        for session_id, session in self._sessions.items():
            expires_at = float(session.get("expires_at") or 0.0)
            if expires_at <= now:
                expired_ids.append(session_id)

        for session_id in expired_ids:
            del self._sessions[session_id]

    def _now(self, now_ts: Optional[float]) -> float:
        if now_ts is None:
            return time.time()
        return float(now_ts)
