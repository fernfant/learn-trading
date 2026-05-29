"""
LESSON 19 — Inventory risk: skew your quotes (Track 2: inside the exchange)

In Lesson 18 you became the market maker: you quote a bid and an ask around the
fair price and earn the spread every time a customer trades against you. Easy
money? Not quite. There's a hidden enemy: INVENTORY.

Every fill leaves you holding something. A customer BUYS from you -> you just
SOLD -> you are now SHORT one unit. A customer SELLS to you -> you BOUGHT ->
you are now LONG one unit. You never wanted a position; you only wanted the
spread. But the position piles up, and a position is DIRECTIONAL RISK:

    accidentally LONG and the price drops  -> you lose
    accidentally SHORT and the price rises -> you lose

So a market maker who just quotes a fixed bid/ask around the mid will see its
inventory RANDOM-WALK away from zero and balloon. One big directional move and
the spread you patiently earned is wiped out by the loss on your pile.

THE FIX: SKEW your quotes by inventory. Don't quote around the raw mid; quote
around an inventory-adjusted "reservation price":

    reservation = fair - k * inventory

    too LONG  (inventory > 0) -> reservation BELOW fair -> both quotes shift DOWN
              -> your ask gets cheaper (eager to SELL off the pile)
              -> your bid gets less attractive (reluctant to buy more)
    too SHORT (inventory < 0) -> reservation ABOVE fair -> both quotes shift UP
              -> eager to BUY back, reluctant to sell more

You lean your prices toward the side that gets you FLAT. Flow then rebalances
you back toward zero. This is the core intuition of the Avellaneda-Stoikov
model: quote around a reservation price that bends with your inventory, not the
raw mid. The goal is to capture the spread while keeping inventory mean-
reverting near zero instead of wandering off a cliff.

The trade-off: more skew (bigger k) = tighter inventory control, but you shade
your prices away from the mid, so you capture slightly less spread per trade.

Run it:  python3 19_inventory.py
Then read 19_walkthrough.md.
"""

import random

FAIR = 100.0       # the "true" mid price (held constant here to isolate skew)
HALF = 0.05        # base half-spread: bid = res - HALF, ask = res + HALF
STEPS = 400        # number of time steps (chances for a customer to trade)
BASE = 0.5         # base fill probability when a quote sits right at fair
SENS = 6.0         # how strongly fill probability reacts to quote distance


def fill_prob(dist):
    """Probability a customer trades against a quote sitting `dist` away from
    fair. A quote at fair (dist=0) fills at BASE. A quote ABOVE fair (dist>0,
    a pricey ask / a stingy bid) fills LESS; a quote BELOW fair fills MORE.
    This is the demand curve: a keener price attracts more flow."""
    p = BASE - SENS * dist
    return max(0.02, min(0.98, p))


def run(k, seed=86, shocks=None):
    """Simulate a market maker with skew strength k.

    reservation = FAIR - k * inventory
    bid = reservation - HALF   (price we'll BUY at)
    ask = reservation + HALF   (price we'll SELL at)

    Each step a buyer MIGHT lift our ask and a seller MIGHT hit our bid. How
    likely depends on how attractive that quote is vs fair (fill_prob):

      too LONG  -> reservation below fair -> ask is cheap (fills MORE, we sell
                   off the pile) and bid is far below fair (fills LESS, we stop
                   buying). Inventory gets pulled DOWN toward 0.
      too SHORT -> reservation above fair -> bid is rich (fills more, we buy
                   back) and ask is high (fills less). Inventory pulled UP.

    `shocks` is a list of (u_buy, u_sell) uniform draws so the SAME randomness
    is replayed across different k -- only the quotes (hence fill odds) change.
    A customer BUYS our ask  -> we SELL -> inventory -= 1, receive ask.
    A customer SELLS our bid  -> we BUY  -> inventory += 1, pay bid.
    """
    rng = random.Random(seed)
    if shocks is None:
        shocks = [(rng.random(), rng.random()) for _ in range(STEPS)]

    inv = 0
    cash = 0.0
    inv_hist = [0]
    for u_buy, u_sell in shocks:
        res = FAIR - k * inv
        bid = res - HALF
        ask = res + HALF
        # ask sits at (ask - FAIR) above fair; cheaper ask -> higher buy odds
        if u_buy < fill_prob(ask - FAIR):       # customer BUYS our ask -> we SELL
            cash += ask
            inv -= 1
        # bid sits at (FAIR - bid) below fair; richer bid -> higher sell odds
        if u_sell < fill_prob(FAIR - bid):      # customer SELLS our bid -> we BUY
            cash -= bid
            inv += 1
        inv_hist.append(inv)

    # Mark remaining inventory at FAIR to get total P&L (spread captured minus
    # any loss on the pile we're left holding).
    pnl = cash + inv * FAIR
    return inv_hist, pnl, shocks


def stats(hist):
    n = len(hist)
    mean = sum(hist) / n
    var = sum((x - mean) ** 2 for x in hist) / n
    peak = max(abs(x) for x in hist)
    return mean, var ** 0.5, peak


def sparkline(hist, width=60, span=40):
    """A tiny ASCII plot of inventory over time, centered on 0."""
    blocks = " .:-=+*#%@"
    # sample the history down to `width` columns
    cols = []
    for c in range(width):
        i = int(c * (len(hist) - 1) / (width - 1))
        cols.append(hist[i])
    rows = []
    for level in (span, span // 2, 0, -span // 2, -span):
        line = []
        for v in cols:
            if level == 0:
                line.append("-" if abs(v) < span // 8 else " ")
            elif level > 0:
                line.append("#" if v >= level else " ")
            else:
                line.append("#" if v <= level else " ")
        tag = f"{level:+4d}" if level else "   0"
        rows.append(tag + " |" + "".join(line))
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# PART A — NO SKEW (k = 0): inventory random-walks and balloons
# ---------------------------------------------------------------------------
print("=" * 64)
print("PART A — NO skew (k = 0): inventory is a free random walk")
print("=" * 64)
hist0, pnl0, shocks = run(k=0.0)
m0, sd0, pk0 = stats(hist0)
print(f"final inventory : {hist0[-1]:+d}")
print(f"mean / std / peak |inv| : {m0:+.1f} / {sd0:.1f} / {pk0}")
print(f"total P&L (marked at fair): {pnl0:+.2f}")
print("\ninventory over time (each # = held units; 0-line dashed):")
print(sparkline(hist0))
print("\nWith no skew the quotes never lean. Inventory wanders wherever the")
print("flow pushes it and can sit far from zero for a long time -- that pile")
print("is naked directional risk the market maker never wanted.")


# ---------------------------------------------------------------------------
# PART B — SKEW (k > 0): inventory mean-reverts toward zero
# ---------------------------------------------------------------------------
print("\n" + "=" * 64)
print("PART B — WITH skew (k = 0.010): quotes lean, inventory hugs 0")
print("=" * 64)
hist1, pnl1, _ = run(k=0.010, shocks=shocks)   # SAME order stream as Part A
m1, sd1, pk1 = stats(hist1)
print(f"final inventory : {hist1[-1]:+d}")
print(f"mean / std / peak |inv| : {m1:+.1f} / {sd1:.1f} / {pk1}")
print(f"total P&L (marked at fair): {pnl1:+.2f}")
print("\ninventory over time (same flow as Part A, now pulled back to 0):")
print(sparkline(hist1))
print("\nSame customer orders -- but now every fill nudges the reservation")
print("price, so the quotes lean toward getting flat. Inventory mean-reverts")
print("instead of running away. The std and peak both shrink dramatically.")


# ---------------------------------------------------------------------------
# PART C — the trade-off: more skew = tighter inventory, less spread captured
# ---------------------------------------------------------------------------
print("\n" + "=" * 64)
print("PART C — sweep k: tighter inventory control costs a little spread")
print("=" * 64)
print(f"{'k':>7} | {'std(inv)':>9} | {'peak|inv|':>9} | {'P&L':>9}")
print("-" * 44)
for k in (0.0, 0.004, 0.010, 0.020, 0.040):
    h, p, _ = run(k=k, shocks=shocks)
    _, sd, pk = stats(h)
    print(f"{k:>7.3f} | {sd:>9.1f} | {pk:>9d} | {p:>9.2f}")
print("\nAs k rises, std and peak inventory fall fast -- risk is squeezed out.")
print("P&L stays in a similar band (you still earn ~the spread per trade) but")
print("its VARIANCE across runs drops, because you're no longer carrying a big")
print("directional bet on top of the spread business. That's the whole point:")
print("capture the spread, stay flat. Quote around FAIR - k*inventory, not the")
print("raw mid. (Avellaneda & Stoikov, 2008.)")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. Raise k in Part B to 0.04. Inventory should hug zero even tighter -- the
#    sparkline collapses onto the 0-line. Compare std(inv) to the k=0.01 run.
# 2. One-sided burst: force 60 customer BUYS up front, then random flow. A
#    `shocks` entry is (u_buy, u_sell): set u_buy=0 (always lifts our ask, we
#    sell) and u_sell=1 (never hits our bid) for the burst, then random after:
#        rng = random.Random(1)
#        burst = [(0.0, 1.0)] * 60
#        rest  = [(rng.random(), rng.random()) for _ in range(340)]
#        shocks = burst + rest
#        print(run(k=0.0, shocks=shocks)[0][-1])    # ends deeply SHORT (~ -60)
#        print(run(k=0.02, shocks=shocks)[0][-1])   # skew claws it back to ~0
#    With k=0 the burst drives you deeply short and you never recover; with
#    skew, the leaning (higher) bid buys stock back once the burst ends.
# 3. Make FAIR drift (a real trend): inside run(), add FAIR += rng.gauss(0,0.02)
#    each step. Now naked inventory (k=0) also loses money on the drift, not
#    just carries risk -- skew protects the P&L, not only the inventory.
# 4. Open ../exchange.py -- Lesson 19 has the maker skewing its quotes by
#    `inventory`, exactly this reservation-price idea, living in the book.
