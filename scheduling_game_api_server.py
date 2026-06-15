"""Run the scheduling game API server."""

import os
import sys


ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from codeupipe.scheduling_game import SchedulingGameHttpServer, SchedulingGameService


def main() -> int:
    host = os.getenv("SCHED_GAME_HOST", "127.0.0.1")
    port = int(os.getenv("SCHED_GAME_PORT", "8094"))

    service = SchedulingGameService()
    server = SchedulingGameHttpServer(service, host=host, port=port)

    print("Scheduling Game API server starting")
    print("URL: http://%s:%d" % (host, port))
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
