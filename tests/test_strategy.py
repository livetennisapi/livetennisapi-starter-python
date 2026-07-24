"""Unit + mocked-stream tests for the Python starter.

No network: a fake stream (a plain list of SDK frame objects) is pumped through
the same dispatch path ``app.py`` uses live. The load-bearing safety property —
that the starter places no real bet — is asserted directly.
"""

from __future__ import annotations

import logging

from livetennisapi import BreakPoint, BreakPointResult, ScoreUpdate

import app
from strategy import PaperOrder, Strategy


class SpyStrategy(Strategy):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[str] = []

    def on_score(self, event):
        self.calls.append("score")

    def on_break_point(self, event):
        self.calls.append("break_point")

    def on_break_point_result(self, event):
        self.calls.append("break_point_result")


def test_dispatch_routes_each_frame_type():
    spy = SpyStrategy()
    frames = [
        ScoreUpdate.from_dict({"type": "score", "match_id": 1}),
        BreakPoint.from_dict({"type": "break_point", "match_id": 1, "returner": 2, "break_points": 1}),
        BreakPointResult.from_dict({"type": "break_point_result", "match_id": 1, "outcome": "broken"}),
    ]
    app.pump(frames, spy)
    assert spy.calls == ["score", "break_point", "break_point_result"]


def test_decide_backs_returner_when_server_not_favoured():
    event = BreakPoint.from_dict(
        {"match_id": 5, "returner": 2, "server": 1, "break_points": 2, "server_side_favoured": False}
    )
    order = Strategy().decide(event)
    assert isinstance(order, PaperOrder)
    assert order.side == 2
    assert order.match_id == 5
    assert order.stake == 20.0  # base 10 * 2 break points


def test_decide_stands_aside_when_server_favoured():
    event = BreakPoint.from_dict({"match_id": 5, "returner": 2, "server_side_favoured": True, "break_points": 1})
    assert Strategy().decide(event) is None


def test_on_break_point_logs_a_paper_order(caplog):
    event = BreakPoint.from_dict(
        {"match_id": 7, "returner": 1, "server": 2, "break_points": 1, "server_side_favoured": False}
    )
    with caplog.at_level(logging.INFO, logger="strategy"):
        Strategy().on_break_point(event)
    assert any("PAPER ORDER" in r.message for r in caplog.records)


def test_execute_seam_refuses_to_place_a_real_bet():
    """The safety invariant: the real-execution seam is never wired."""
    order = PaperOrder(match_id=1, side=1, stake=10.0, reason="test")
    try:
        Strategy()._execute(order)
    except NotImplementedError as exc:
        assert "NO real bets" in str(exc)
    else:  # pragma: no cover
        raise AssertionError("_execute must not place a real bet")
