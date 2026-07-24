"""Runnable break-point reactor, built on the official ``livetennisapi`` SDK.

It connects the ULTRA WebSocket feed with ``signals=["break_point"]``, routes
every frame to a :class:`~strategy.Strategy`, and logs the paper action the
strategy would take. It places **no** real bets — see ``strategy.py``.

    cp .env.example .env      # then put your ULTRA key in .env
    pip install -r requirements.txt
    python app.py

The break-point feed and the WebSocket surface are ULTRA-tier only.
"""

from __future__ import annotations

import logging
import os
import sys

from livetennisapi import (
    BreakPoint,
    BreakPointResult,
    LiveScoreStream,
    ScoreUpdate,
    Unauthorized,
    UpgradeRequired,
)

from strategy import Strategy

log = logging.getLogger("starter")


def load_dotenv(path: str = ".env") -> None:
    """Load ``KEY=value`` lines from a .env file into the environment.

    Tiny on purpose: the starter depends only on the SDK, nothing else. Existing
    environment variables always win, so an exported key is not overwritten.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip("'\""))
    except FileNotFoundError:
        pass


def dispatch(frame: object, strategy: Strategy) -> None:
    """Route one stream frame to the matching strategy handler."""
    if isinstance(frame, BreakPoint):
        strategy.on_break_point(frame)
    elif isinstance(frame, BreakPointResult):
        strategy.on_break_point_result(frame)
    elif isinstance(frame, ScoreUpdate):
        strategy.on_score(frame)


def pump(stream: object, strategy: Strategy) -> None:
    """Consume a stream of frames, dispatching each. Testable without a socket."""
    for frame in stream:  # type: ignore[attr-defined]
        dispatch(frame, strategy)


def main() -> int:
    logging.basicConfig(
        level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    load_dotenv()

    key = os.environ.get("LIVETENNISAPI_KEY", "").strip()
    if not key:
        log.error("set LIVETENNISAPI_KEY (see .env.example) — the break-point feed needs an ULTRA key")
        return 2

    strategy = Strategy()
    log.info("connecting to the live feed with signals=['break_point'] …")
    try:
        with LiveScoreStream(api_key=key, signals=["break_point"]) as stream:
            pump(stream, strategy)
    except UpgradeRequired:
        log.error("this key is not on ULTRA — the WebSocket + break-point feed require the ULTRA tier")
        return 3
    except Unauthorized:
        log.error("the API rejected this key; check LIVETENNISAPI_KEY")
        return 3
    except KeyboardInterrupt:
        log.info("stopped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
