# Live Tennis API — Break-Point Starter (Python)

A tiny, runnable app that reacts to **break points** on the
[Live Tennis API](https://livetennisapi.com) live feed. It shows exactly where
your trading logic goes — and it places **no real bets**.

It rides the official [`livetennisapi`](https://pypi.org/project/livetennisapi/)
SDK: it opens the ULTRA WebSocket feed with `signals=["break_point"]`, routes
every frame to a `Strategy`, and logs the paper action the strategy would take.

> **Requires an ULTRA key.** The WebSocket feed and the break-point signals are
> ULTRA-tier only. Get a key at <https://livetennisapi.com/#pricing>.
> No key yet? A **FREE** key (no card — <https://livetennisapi.com/subscribe/free>)
> lets you explore the REST endpoints first, but this starter's WebSocket feed
> still needs ULTRA.

## Run it

```bash
cp .env.example .env          # then put your ULTRA key in .env
pip install -r requirements.txt
python app.py
```

You'll see output like:

```
INFO starter connecting to the live feed with signals=['break_point'] …
INFO strategy BREAK POINT  match=18953  p1 serving, p2 holds 2 break point(s)  swing=0.22
INFO strategy PAPER ORDER  back p2 on match 18953 for 20.00  (2 break point(s) against an unfavoured server)
INFO strategy   -> break point broken  match=18953  p1 win prob now 0.63
```

## Where your code goes

Everything you edit is in **`strategy.py`**:

- `on_break_point(event)` — the headline signal lands here.
- `decide(event)` — return a `PaperOrder` (or `None`). Put your edge here.
- `place_paper_order(order)` — logs the intended order. **Nothing real happens.**

### Wiring a real venue

`place_paper_order` contains a clearly marked block:

```
# ================= WIRE YOUR OWN EXCHANGE / VENUE HERE =================
```

The real-execution seam is `Strategy._execute`. It is **unimplemented and never
called on purpose**, so a fresh clone can never move money. To go live, implement
`_execute` against your venue's API and call it from `place_paper_order`. That
choice — and any risk it carries — is entirely yours.

## Test

```bash
pip install -r requirements.txt
pytest
```

The tests pump canned frames through the same dispatch path the live app uses
(no network), and assert the safety invariant: the execution seam refuses to
place a real bet.

## How it maps to the API

The subscribe frame this starter sends:

```json
{ "topics": ["live-scores"], "signals": ["break_point"] }
```

Frames it reacts to: `score`, `break_point`, `break_point_result`. See the
[WebSocket section of the API reference](https://docs.livetennisapi.com/reference.html#websocket).

## License

MIT — see [LICENSE](./LICENSE).

## Affiliate program

Know developers who need tennis data? The [affiliate program](https://affiliates.livetennisapi.com/program) pays 51% recurring commission for the life of every referred subscription — 30-day cookie, and the people you refer get 10% off.
