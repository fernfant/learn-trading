# Lesson 19 — Inventory risk: skew your quotes

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for
> this lesson: [`19_inventory.py`](19_inventory.py) ·
> interactive: [`html/lesson_19.html`](html/lesson_19.html)

Lesson 18 put you in the market maker's seat: quote a bid and an ask around the
fair price, and earn the spread every time a customer trades against you. It
looks like a money printer. It isn't. There's a hidden enemy that quietly
builds up every time you get filled: **inventory**.

> **Every fill leaves you holding a position you never wanted.**

A customer **buys** from you — so you just **sold** — and now you're **short**
one unit. A customer **sells** to you — you **bought** — now you're **long**
one unit. You only ever wanted the spread. But the leftover position piles up,
and a position is **directional risk**:

- accidentally **long** and the price drops → you lose
- accidentally **short** and the price rises → you lose

A maker who quotes a fixed bid/ask around the mid watches its inventory
**random-walk away from zero**. One big move while you're holding a fat pile
and the loss swamps all the spread you patiently earned.

## The fix: lean your prices toward flat

The trick is to stop quoting around the raw mid. Quote around an
inventory-adjusted **reservation price**:

```python
reservation = fair - k * inventory
bid = reservation - HALF      # the price you'll BUY at
ask = reservation + HALF      # the price you'll SELL at
```

`k` is the **skew strength** — a dial for how hard you lean.

- **Too long** (`inventory > 0`) → `reservation` drops *below* fair → both
  quotes shift **down**. Your ask is now cheap (eager to **sell off** the pile);
  your bid is far below fair (reluctant to buy *more*).
- **Too short** (`inventory < 0`) → `reservation` rises *above* fair → both
  quotes shift **up**. Your bid is now rich (eager to **buy back**); your ask is
  high (reluctant to sell more).

You bend your prices toward the side that gets you **flat**. Flow then
rebalances you back toward zero. That single line —
`reservation = fair - k * inventory` — is the heart of the
**Avellaneda–Stoikov** model: quote around a reservation price that moves with
your inventory, not the raw mid.

## How the script proves it

[`19_inventory.py`](19_inventory.py) runs a market maker over 400 time steps.
Each step a buyer *might* lift your ask and a seller *might* hit your bid — how
likely depends on how attractive that quote is versus fair (`fill_prob`): a
keener price pulls in more flow. The randomness (`shocks`) is fixed and replayed
across every `k`, so the only thing that changes is **where you quote**.

### Part A — no skew (`k = 0`): the random walk

```
final inventory : -33
mean / std / peak |inv| : -16.5 / 9.5 / 34
total P&L (marked at fair): +7.65

inventory over time (each # = held units; 0-line dashed):
 +40 |
 +20 |
   0 |---- - -
 -20 |                                  ##########################
 -40 |
```

With no skew the quotes never lean. Inventory drifts off and **parks at −33** —
a deep short, naked directional risk the maker never asked for. It earned the
spread (+7.65), but it's sitting on a position that one upward jump in `fair`
would turn into a brutal loss.

### Part B — with skew (`k = 0.010`): it hugs zero

```
final inventory : -1
mean / std / peak |inv| : -0.5 / 1.1 / 3
total P&L (marked at fair): +7.21

inventory over time (same flow as Part A, now pulled back to 0):
 +40 |
 +20 |
   0 |------------------------------------------------------------
 -20 |
 -40 |
```

**Same customer orders.** But now every fill nudges the reservation price, so
the quotes lean toward getting flat. The instant inventory goes short, the bid
ticks up and buys stock back. Inventory **mean-reverts** instead of running
away: peak `|inv|` collapses from **34 → 3**, std from **9.5 → 1.1**. And you
still kept almost all the spread (+7.21 vs +7.65).

### Part C — the trade-off

```
      k |  std(inv) | peak|inv| |       P&L
--------------------------------------------
  0.000 |       9.5 |        34 |      7.65
  0.004 |       1.6 |         5 |      7.45
  0.010 |       1.1 |         3 |      7.21
  0.020 |       0.8 |         2 |      6.96
  0.040 |       0.7 |         2 |      5.50
```

As `k` rises, std and peak inventory **fall fast** — risk is squeezed out. The
P&L drifts down only gently: you shade your quotes away from the mid to lean, so
you capture a hair less spread per trade. That's the whole bargain: **a little
less spread in exchange for a lot less directional risk.** Crank `k` too high
(0.040) and you over-shade and start giving away spread for inventory control
you no longer need — there's a sweet spot in the middle.

The deeper payoff isn't visible in one run: with inventory pinned near zero,
your P&L *across many runs* stops swinging on whichever way the price happened
to drift. You're back to running a spread business, not a hidden directional
bet.

## What this becomes in `exchange.py`

In the cumulative artifact, the market maker stops quoting symmetric ticks
around the mid and instead computes `reservation = fair - k * inventory`, then
quotes `bid/ask` around *that*. The one new idea this lesson adds is the maker
**skewing its quotes by `inventory`** so its book position mean-reverts toward
flat — the foundation for the Lesson 22 capstone, a maker that stays profitable
**and** flat.

## Try it (in [`19_inventory.py`](19_inventory.py))

1. Raise `k` in Part B to `0.04` — inventory hugs zero even tighter and the
   sparkline collapses onto the 0-line.
2. Hit it with a **one-sided burst**: force 60 customer buys up front (you go
   deeply short), then random flow. With `k = 0` you end near −60 and never
   recover; with `k = 0.02` the leaning bid claws you back to ~0.
3. Let `fair` actually **drift**. Now naked inventory (`k = 0`) doesn't just
   carry risk — it *loses money* on the trend, while skew protects the P&L too.

---

**Next:** [Lesson 20 — Latency & the queue: why microseconds pay](20_latency.py)
— your skewed quotes are only good if they're *first in line*. We add per-order
latency and watch the race for the front of the queue.

*Reference: Avellaneda & Stoikov (2008), "High-frequency trading in a limit
order book."*
