"""
LESSON 9 — Costs that kill: spread + overnight funding + slippage
(Track 1: trading on capital.com)

This is the lesson the whole "honesty" theme has been building toward. You have
a signal now (Lesson 8). On paper it makes money. So why does capital.com's own
warning say the large majority of retail CFD accounts LOSE?

The answer is three quiet costs that never show up in a "gross" backtest:

    1. SPREAD          — you open on the bad side of the two prices and close on
                         the other bad side, so every round trip pays a FULL
                         spread (half in, half out). Trade often → pay it often.
    2. OVERNIGHT SWAP  — a small daily charge for holding a leveraged position
                         past the cutoff. Tiny per day; relentless over time.
    3. SLIPPAGE        — a market order fills a hair WORSE than the quoted price,
                         because by the time it lands the price has moved / the
                         top of the book is thin. Another bite on every fill.

None of these is dramatic on its own. Stacked together they turn a clearly
"winning" gross strategy into a net loser. That is the lesson.

In the cumulative artifact (../market.py) this is the line:
    cash -= half_spread * abs(position) + OVERNIGHT_SWAP * abs(position)
plus slippage baked into the fill price.

Run it:  python3 09_costs.py
Then read 09_walkthrough.md.
"""

import random

# ---- THE EDGE (clearly profitable BEFORE costs) ----------------------------
# We don't model a fancy signal here — we just GRANT ourselves a small, real
# edge so we can study what costs do to it. Each round trip is a position held
# for a few days that, on average, earns a little. gauss(EDGE, WOBBLE) per trip
# means: usually a small gain, sometimes a loss, but a positive average. This is
# already generous — a genuine retail edge is usually smaller or zero.
random.seed(9)

START = 2000.0      # starting cash, like the capital.com demo
QTY = 100           # units per trade (CFD "size")
EDGE = 0.18         # average gross profit per unit, per round trip
WOBBLE = 1.4        # how noisy each trip's result is
SPREAD = 0.10       # the gap between Buy and Sell (Lesson 2)
SWAP = 0.02         # overnight funding per unit, per day held (Lesson 9)
SLIP = 0.03         # slippage per unit, per fill (worse than quoted)
HOLD_DAYS = 3       # days each trade is held (swap is charged per day)


def gross_trips(n):
    """n round-trip results BEFORE any costs — the rose-tinted backtest."""
    return [random.gauss(EDGE, WOBBLE) * QTY for _ in range(n)]


def equity_after(trips, spread=0.0, swap=0.0, slip=0.0):
    """Apply cost layers to a fixed list of gross trips and return final equity.

    Costs charged per round trip (the artifact's `cash -= ...` line):
      * spread : a FULL spread per round trip (half on open + half on close)
      * slip   : two fills per round trip (open and close), each slips `slip`
      * swap   : charged for every day the position is held
    """
    eq = START
    for g in trips:
        cost = (spread * QTY) + (2 * slip * QTY) + (swap * QTY * HOLD_DAYS)
        eq += g - cost
    return eq


def curve_after(trips, spread=0.0, swap=0.0, slip=0.0):
    """Same as equity_after but returns the running equity for plotting."""
    eq = START
    out = [eq]
    for g in trips:
        cost = (spread * QTY) + (2 * slip * QTY) + (swap * QTY * HOLD_DAYS)
        eq += g - cost
        out.append(eq)
    return out


def bar(value, base=START, width=44):
    """Tiny ASCII bar: how far equity sits above/below the starting line."""
    span = 600.0  # full bar width maps to +-$600 around START
    frac = max(-1.0, min(1.0, (value - base) / span))
    cells = int(round(abs(frac) * width))
    if frac >= 0:
        return "." * width + "|" + "#" * cells + f"  ${value:,.0f}"
    return "." * (width - cells) + "#" * cells + "|" + " " * width + f"  ${value:,.0f}"


# ---------------------------------------------------------------------------
# PART A — peel the costs off ONE layer at a time
# ---------------------------------------------------------------------------
# Same 40 gross trips throughout, so every line below is the SAME strategy —
# only the costs we admit to change. Watch equity fall as each layer lands.
N = 40
trips = gross_trips(N)

print(f"A modest edge traded {N} times, ${START:,.0f} start, {QTY} units/trade.")
print("Same trades every row — we only add one more real cost each time.\n")
print(f"  {'cost layer':28}{'final equity':>14}   gross→net")
print("  " + "-" * 70)

gross = equity_after(trips)
print(f"  {'0. gross (no costs)':28}{gross:>14,.2f}")

after_spread = equity_after(trips, spread=SPREAD)
print(f"  {'1. + spread (per round trip)':28}{after_spread:>14,.2f}")

after_swap = equity_after(trips, spread=SPREAD, swap=SWAP)
print(f"  {'2. + overnight swap (per day)':28}{after_swap:>14,.2f}")

after_slip = equity_after(trips, spread=SPREAD, swap=SWAP, slip=SLIP)
print(f"  {'3. + slippage (per fill)':28}{after_slip:>14,.2f}")

print()
print("  Visually, the very same edge sinking under each cost layer:")
print(f"  gross       {bar(gross)}")
print(f"  +spread     {bar(after_spread)}")
print(f"  +swap       {bar(after_swap)}")
print(f"  +slippage   {bar(after_slip)}")

net_pl = after_slip - START
gross_pl = gross - START
print()
print(f"  Gross profit was ${gross_pl:+,.2f}. After all three costs: ${net_pl:+,.2f}.")
print(f"  Costs alone ate ${gross_pl - net_pl:,.2f} — and flipped a winner into a "
      f"{'LOSER' if net_pl < 0 else 'thinner winner'}.")


# ---------------------------------------------------------------------------
# PART B — FREQUENCY amplifies the spread
# ---------------------------------------------------------------------------
# The spread is paid PER ROUND TRIP. So the same total edge, chopped into many
# small trades, pays the spread many more times. Here we hold the TOTAL gross
# edge fixed and only change how many trades we slice it into.
print("\n" + "=" * 72)
print("  FREQUENCY: the spread is a toll you pay on EVERY round trip")
print("=" * 72)
total_gross_edge = EDGE * QTY * 40          # the same gross edge to capture
print(f"  Same ${total_gross_edge:,.0f} of gross edge to capture, sliced two ways:\n")
print(f"  {'plan':22}{'trips':>7}{'spread paid':>14}{'net equity':>14}")
print("  " + "-" * 60)

for label, n in (("trade rarely", 5), ("trade often", 100)):
    per_trip = total_gross_edge / n         # split the SAME edge across n trips
    these = [per_trip] * n                  # ignore wobble here to isolate cost
    eq = equity_after(these, spread=SPREAD, swap=SWAP, slip=SLIP)
    spread_paid = SPREAD * QTY * n
    print(f"  {label:22}{n:>7}{spread_paid:>13,.0f} {eq:>14,.2f}")

print()
print("  Identical gross edge. The 5-trade plan keeps most of it; the 100-trade")
print("  plan hands it all back in spread + slippage on every fill. 'Overtrading'")
print("  is how a real edge dies — you pay the toll twenty times to earn it once.")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. Lower the SPREAD to 0.04 (a tight, liquid market) and re-run Part A. Does
#    the net flip back to positive? The spread is usually the biggest single bite.
# 2. Cut HOLD_DAYS from 3 to 1 (get in and out same-day). How much overnight swap
#    do you save? Swap only bites while you're still holding past the cutoff.
# 3. In Part B, change the rare plan from 5 to 1 trip and the busy one to 250.
#    Watch the gap widen — frequency is a multiplier on every per-trip cost.
# 4. Set EDGE = 0.30 (a fat, unrealistic edge). Even a strong edge has a break-
#    even trade count: beyond it, costs win. Find where the busy plan goes red.
