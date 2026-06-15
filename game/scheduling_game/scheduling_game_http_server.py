"""Scheduling game HTTP server exposing M1 endpoints."""

import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from .game_ui import GAME_UI_HTML
from .scheduling_game_service import SchedulingGameService


class SchedulingGameHttpServer:
    """Serve scheduling game API over stdlib HTTP."""

    def __init__(
        self,
        service: SchedulingGameService,
        host: str = "127.0.0.1",
        port: int = 8094,
    ) -> None:
        self._service = service
        self._host = host
        self._port = int(port)
        self._httpd: Optional[ThreadingHTTPServer] = None
        self._thread: Optional[threading.Thread] = None
        self._running = False

    def serve_forever(self) -> None:
        """Run server in blocking mode."""
        if self._running:
            return

        self._running = True
        handler_cls = self._build_handler()
        self._httpd = ThreadingHTTPServer((self._host, self._port), handler_cls)
        try:
            self._httpd.serve_forever()
        finally:
            self._running = False
            if self._httpd is not None:
                self._httpd.server_close()
                self._httpd = None

    def start_background(self) -> None:
        """Run server in a background thread."""
        if self._running:
            return

        handler_cls = self._build_handler()
        self._httpd = ThreadingHTTPServer((self._host, self._port), handler_cls)
        self._thread = threading.Thread(
            target=self._httpd.serve_forever,
            daemon=True,
            name="scheduling-game-http",
        )
        self._running = True
        self._thread.start()

    def stop(self) -> None:
        """Stop server and release network resources."""
        if not self._running:
            return

        self._running = False
        if self._httpd is not None:
            self._httpd.shutdown()
            self._httpd.server_close()
            self._httpd = None

        if self._thread is not None:
            self._thread.join(timeout=5)
            self._thread = None

    def _build_handler(self):
        service = self._service

        class _Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                path = urlparse(self.path).path
                if path == "/health":
                    self._send_json(200, service.health())
                    return

                if path == "/":
                    self._send_html(200, GAME_UI_HTML)
                    return

                self._send_json(404, {"error": "not_found"})

            def do_POST(self):
                path = urlparse(self.path).path
                if path == "/game/new":
                    body = self._read_json()
                    if body is None:
                        self._send_json(400, {"error": "invalid_json"})
                        return

                    difficulty = str((body or {}).get("difficulty") or "normal")
                    try:
                        created = service.new_game(difficulty)
                    except Exception:
                        self._send_json(400, {"error": "invalid_difficulty"})
                        return

                    self._send_json(200, created)
                    return

                parts = [part for part in path.split("/") if part]
                if len(parts) == 3 and parts[0] == "game" and parts[2] == "schedule":
                    session_id = parts[1]
                    body = self._read_json()
                    if body is None:
                        self._send_json(400, {"error": "invalid_json"})
                        return

                    result = service.schedule_event(session_id, body)
                    if not result.get("ok"):
                        if result.get("error") == "session_not_found":
                            self._send_json(404, {"error": "session_not_found"})
                            return
                        self._send_json(400, {"error": "invalid_event"})
                        return

                    self._send_json(200, result)
                    return

                if len(parts) == 3 and parts[0] == "game" and parts[2] == "simulate":
                    session_id = parts[1]
                    result = service.simulate_session(session_id)
                    if not result.get("ok"):
                        self._send_json(404, {"error": "session_not_found"})
                        return

                    self._send_json(200, result)
                    return

                self._send_json(404, {"error": "not_found"})

            def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
                return

            def _read_json(self) -> Optional[Dict[str, Any]]:
                length_raw = self.headers.get("Content-Length")
                if length_raw is None:
                    return {}

                try:
                    length = int(length_raw)
                except ValueError:
                    return None

                raw = self.rfile.read(length).decode("utf-8")
                try:
                    parsed = json.loads(raw)
                except Exception:
                    return None

                if isinstance(parsed, dict):
                    return parsed
                return None

            def _send_json(self, status_code: int, body: Dict[str, Any]) -> None:
                payload = json.dumps(body).encode("utf-8")
                self.send_response(status_code)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

            def _send_html(self, status_code: int, html: str) -> None:
                payload = html.encode("utf-8")
                self.send_response(status_code)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        return _Handler
