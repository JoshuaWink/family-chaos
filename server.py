"""Run the Family Chaos scheduling game API + UI server."""

import os
import sys

ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from game.scheduling_game import SchedulingGameHttpServer, SchedulingGameService


def main() -> int:
    host = os.getenv("SCHED_GAME_HOST", "127.0.0.1")
    port = int(os.getenv("SCHED_GAME_PORT", "8094"))

    service = SchedulingGameService()
    server = SchedulingGameHttpServer(service, host=host, port=port)

    print("Family Chaos server starting")
    print("URL: http://%s:%d" % (host, port))
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
