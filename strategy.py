"""Your break-point strategy — the one file you are meant to edit.

``on_break_point`` is where the headline signal lands. The default
implementation decides on a **paper** action and hands it to
:meth:`Strategy.place_paper_order`, which only logs. Nothing in this file places
a real bet.

The seam for real execution is :meth:`Strategy._execute`. It is deliberately
left unimplemented and is deliberately **not** called, so this starter can never
move money. Wire your own exchange or venue there when you are ready — see the
clearly marked block in :meth:`place_paper_order`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

log = logging.getLogger("strategy")


def _get(event: Any, name: str, default: Any = None) -> Any:
    """Read a field off an SDK model, a dict, or any object, tolerantly."""
    if isinstance(event, dict):
        return event.get(name, default)
    return getattr(event, name, default)


@dataclass
class PaperOrder:
    """An intended (paper) order. Logged, never sent."""

    match_id: int | None
    side: int | None  # which player (1 or 2) this order backs
    stake: float
    reason: str


class Strategy:
    """A minimal, illustrative break-point reactor.

    The logic here is intentionally simple — it exists to show *where* your code
    goes, not to be a profitable model. Replace :meth:`decide` with your own.
    """

    def __init__(self, base_stake: float = 10.0) -> None:
        self.base_stake = base_stake
        self.break_points_seen = 0

    # -- event handlers -------------------------------------------------------

    def on_score(self, event: Any) -> None:
        """A routine score change. Kept quiet so break points stand out."""
        log.debug("score  match=%s sets=%s", _get(event, "match_id"), _get(_get(event, "score"), "sets"))

    def on_break_point(self, event: Any) -> None:
        """The headline signal: a break point is on the board."""
        self.break_points_seen += 1
        match_id = _get(event, "match_id")
        returner = _get(event, "returner")
        server = _get(event, "server")
        n = _get(event, "break_points")
        log.info(
            "BREAK POINT  match=%s  p%s serving, p%s holds %s break point(s)  swing=%s",
            match_id, server, returner, n, _get(event, "prob_swing"),
        )
        order = self.decide(event)
        if order is not None:
            self.place_paper_order(order)

    def on_break_point_result(self, event: Any) -> None:
        outcome = _get(event, "outcome")
        log.info(
            "  -> break point %s  match=%s  p1 win prob now %s",
            outcome, _get(event, "match_id"), _get(event, "win_probability_p1_after"),
        )

    # -- decision -------------------------------------------------------------

    def decide(self, event: Any) -> PaperOrder | None:
        """Turn a break-point event into an intended paper order, or ``None``.

        Illustrative rule: when the serving side is *not* favoured to hold, back
        the returner to convert. Stake scales with how many break points are
        live. This is a placeholder — put your real edge here.
        """
        if _get(event, "server_side_favoured"):
            return None
        returner = _get(event, "returner")
        if returner not in (1, 2):
            return None
        n = _get(event, "break_points") or 1
        stake = round(self.base_stake * min(int(n), 3), 2)
        return PaperOrder(
            match_id=_get(event, "match_id"),
            side=returner,
            stake=stake,
            reason=f"{n} break point(s) against an unfavoured server",
        )

    # -- execution (paper only) ----------------------------------------------

    def place_paper_order(self, order: PaperOrder) -> None:
        """Log the intended order. Places NO real bet."""
        log.info(
            "PAPER ORDER  back p%s on match %s for %.2f  (%s)",
            order.side, order.match_id, order.stake, order.reason,
        )

        # ================= WIRE YOUR OWN EXCHANGE / VENUE HERE =================
        # This starter intentionally stops at logging. To go live, implement
        # `_execute` against your venue's API and call it here. It is left
        # commented out on purpose so a fresh clone can never move real money.
        #
        #     self._execute(order)
        # ======================================================================

    def _execute(self, order: PaperOrder) -> None:
        """Seam for real order placement. Unimplemented by design."""
        raise NotImplementedError(
            "wire your real exchange/venue here; this starter places NO real bets"
        )
