"""Integration tests for scheduling game HTTP API (M1)."""

import json
import socket
import urllib.error
import urllib.request

import pytest

from game.scheduling_game import SchedulingGameHttpServer, SchedulingGameService


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _get_json(url: str) -> tuple[int, dict]:
    request = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(request) as response:
        body = json.loads(response.read().decode("utf-8"))
        return int(response.status), body


def _post_json(url: str, body: dict) -> tuple[int, dict]:
    payload = json.dumps(body).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        response_body = json.loads(response.read().decode("utf-8"))
        return int(response.status), response_body


@pytest.mark.unit
class TestSchedulingGameApi:
    """M1 API loop over stdlib HTTP server."""

    def test_health_and_full_success_loop(self):
        port = _free_port()
        server = SchedulingGameHttpServer(
            SchedulingGameService(),
            host="127.0.0.1",
            port=port,
        )
        server.start_background()

        try:
            status, health = _get_json(f"http://127.0.0.1:{port}/health")
            assert status == 200
            assert health.get("status") == "ok"

            status, created = _post_json(
                f"http://127.0.0.1:{port}/game/new",
                {"difficulty": "normal"},
            )
            assert status == 200
            session_id = created.get("session_id")
            assert session_id
            assert len(created.get("people") or []) >= 10
            assert len(created.get("tasks") or []) >= 12

            status, scheduled_1 = _post_json(
                f"http://127.0.0.1:{port}/game/{session_id}/schedule",
                {
                    "task_id": "t1",
                    "person_id": "p3",
                    "start_time": "2026-06-15T09:00:00",
                },
            )
            assert status == 200
            assert scheduled_1.get("scheduled_count") == 1

            status, scheduled_2 = _post_json(
                f"http://127.0.0.1:{port}/game/{session_id}/schedule",
                {
                    "task_id": "t9",
                    "person_id": "p3",
                    "start_time": "2026-06-15T10:00:00",
                },
            )
            assert status == 200
            assert scheduled_2.get("scheduled_count") == 2

            status, report = _post_json(
                f"http://127.0.0.1:{port}/game/{session_id}/simulate",
                {},
            )
            assert status == 200
            assert report.get("is_valid") is True
            assert report.get("conflicts") == []
            assert report.get("scheduled_count") == 2
        finally:
            server.stop()

    def test_simulate_reports_resource_conflict(self):
        port = _free_port()
        server = SchedulingGameHttpServer(
            SchedulingGameService(),
            host="127.0.0.1",
            port=port,
        )
        server.start_background()

        try:
            _, created = _post_json(
                f"http://127.0.0.1:{port}/game/new",
                {"difficulty": "normal"},
            )
            session_id = created.get("session_id")

            _post_json(
                f"http://127.0.0.1:{port}/game/{session_id}/schedule",
                {
                    "task_id": "t5",
                    "person_id": "p1",
                    "start_time": "2026-06-15T09:00:00",
                },
            )
            _post_json(
                f"http://127.0.0.1:{port}/game/{session_id}/schedule",
                {
                    "task_id": "t7",
                    "person_id": "p2",
                    "start_time": "2026-06-15T09:30:00",
                },
            )

            status, report = _post_json(
                f"http://127.0.0.1:{port}/game/{session_id}/simulate",
                {},
            )
            assert status == 200
            assert report.get("is_valid") is False
            assert any(item.get("type") == "resource_conflict" for item in report.get("conflicts") or [])
        finally:
            server.stop()

    def test_schedule_missing_session_returns_not_found(self):
        port = _free_port()
        server = SchedulingGameHttpServer(
            SchedulingGameService(),
            host="127.0.0.1",
            port=port,
        )
        server.start_background()

        try:
            payload = json.dumps(
                {
                    "task_id": "t1",
                    "person_id": "p1",
                    "start_time": "2026-06-15T09:00:00",
                }
            ).encode("utf-8")
            request = urllib.request.Request(
                f"http://127.0.0.1:{port}/game/missing-session/schedule",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with pytest.raises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(request)
            assert int(error.value.code) == 404
            body = json.loads(error.value.read().decode("utf-8"))
            assert body.get("error") == "session_not_found"
        finally:
            server.stop()
