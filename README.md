# Live Tennis API — Break-Point Starter (Python)

[![ci](https://github.com/livetennisapi/livetennisapi-starter-python/actions/workflows/ci.yml/badge.svg)](https://github.com/livetennisapi/livetennisapi-starter-python/actions/workflows/ci.yml)
[![license: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](./LICENSE)

A tiny, runnable app that reacts to **break points** on the
[Live Tennis API](https://livetennisapi.com) live feed — ATP, WTA, Challenger,
ITF and juniors. It shows exactly where your trading logic goes — and it places
**no real bets**.

It rides the official [`livetennisapi`](https://pypi.org/project/livetennisapi/)
SDK: it opens the ULTRA WebSocket feed with `signals=["break_point"]`, routes
every frame to a `Strategy`, and logs the paper action the strategy would take.

> **Requires an ULTRA key.** The WebSocket feed and the break-point signals are
> ULTRA-tier only. Get a key at <https://livetennisapi.com/#pricing>.
> No key yet? A **FREE** key (no card — <https://livetennisapi.com/subscribe/free>)
> lets you explore the REST endpoints first, but this starter's WebSocket feed
> still needs ULTRA.

## Run it

> Needs **Python 3.10+** (the app runs on 3.9, but the pinned `pytest` needs 3.10).

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

The subscribe frame this starter (via the SDK) sends:

```json
{ "topics": ["live-scores"], "signals": ["break_point"] }
```

The server keys off `topics` (plus the optional `signals` list) — nothing else
belongs in the frame. Swap the topic to `["match:<id>"]` to follow one match.
Frames it reacts to: `score`, `break_point`, `break_point_result` (the SDK
swallows the ~15s `ping` heartbeat and the `subscribed` ack for you). Every
`score` frame nests its payload under `score` and carries the ULTRA model
fields `win_probability_p1` and `danger` — a `None` there means the model had
no output for that state, not that the feed withheld it. The feed allows at
most **2 concurrent connections per key**; the SDK authenticates REST with
`Authorization: Bearer twjp_…` (preferred; `X-API-Key` also works) and the
WebSocket with `?token=`. See the
[WebSocket section of the API reference](https://docs.livetennisapi.com/reference.html#websocket).

## Error handling

The SDK raises typed errors — the starter already exits cleanly on
`UpgradeRequired` (not ULTRA) and `Unauthorized` (bad key). If you add REST
calls, also expect:

- `429 rate_limited` — over the per-minute or per-day cap (`RateLimited` in the
  SDK). Honour `Retry-After`; a daily 429 also carries `resets_at`, the exact
  UTC instant your quota resets.
- `429 abuse_throttled` — a ~24-hour block for clients that chronically ignore
  their caps; the body's `retry_at_epoch` says when it lifts. Fix the polling
  or retry loop rather than retrying harder.

On a FREE key (100 requests/day) poll REST no faster than every 15 minutes; an
always-on dashboard should run on BASIC or above.

## Quotas

| Tier | Rate limit | Price |
|---|---|---|
| FREE | 30/min · 100/day | $0 — no card |
| BASIC | 60/min · 1,000/day | $9.99/mo |
| PRO | 300/min · 10,000/day | $29.99/mo |
| ULTRA | 600/min · 500,000/day | $99.99/mo |

The WebSocket feed and the break-point signals need ULTRA; `/usage` reports
your key's consumption without counting against it.

## Links

[Documentation](https://docs.livetennisapi.com) ·
[Free API key](https://livetennisapi.com/subscribe/free) ·
[Discord](https://discord.gg/f8WUZHgDm6) ·
[GitHub org](https://github.com/livetennisapi)

## License

MIT — see [LICENSE](./LICENSE).

## Affiliate program

Know developers who need tennis data? The [affiliate program](https://affiliates.livetennisapi.com/program) pays 51% recurring commission for the life of every referred subscription — 30-day cookie, and the people you refer get 10% off.
