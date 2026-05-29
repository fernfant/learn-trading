"""
LESSON 10 — Backtesting honestly: return, Sharpe, max drawdown & the OOS trap
(Track 1: trading on capital.com)

You have a strategy now (a signal, a size, and the costs that bite it — Lessons
8 & 9). The last question before you ever risk a cent: IS IT ANY GOOD? A single
equity curve isn't an answer. You need numbers, and you need to read them
honestly — because the easiest person to fool with a backtest is yourself.

Three numbers describe almost any strategy. We compute all three from one thing:
the EQUITY CURVE (your account value, day by day).

    1. TOTAL RETURN %  — how much the account grew end to end. The headline, and
                         the most over-rated number: it says nothing about HOW.
    2. SHARPE RATIO    — return per unit of wobble: mean daily return / std of
                         daily returns, × sqrt(252) to "annualize" it. It rewards
                         smooth gains and punishes a wild ride. >1 is decent;
                         most real retail strategies sit well below 1.
    3. MAX DRAWDOWN %  — the worst peak-to-trough fall along the way. This is the
                         PAIN — the number that decides whether you'd actually
                         have held on, or panic-closed at the bottom. It's what
                         blows accounts up, not the final figure.

Then the trap that kills more backtests than any other:

    IN-SAMPLE vs OUT-OF-SAMPLE. If you tune a strategy's knobs to look great on
    the data you already have, you've often just memorized that data's noise
    (overfitting / curve-fitting). On fresh, unseen data the magic evaporates.
    The fix is a discipline: reserve an out-of-sample (OOS) slice you NEVER tune
    on, and judge the strategy only there.

In the cumulative artifact (../market.py) this is the post-loop metrics block:
returns(), sharpe() and max_drawdown() computed over the daily equity_curve,
then printed beside buy-and-hold.

Run it:  python3 10_backtest.py
Then read 10_walkthrough.md.
"""

import random
from math import sqrt

random.seed(8)    # reproducible: the walkthrough's numbers match this exactly

ANN = 252         # trading days per year — the standard Sharpe annualization


# ---------------------------------------------------------------------------
# THE METRICS — pure stdlib, computed straight off an equity curve
# ---------------------------------------------------------------------------
def daily_returns(curve):
    """Day-over-day fractional change: 0.01 means the account grew 1% that day.
    These are the raw material for both total return and Sharpe."""
    return [curve[i] / curve[i - 1] - 1 for i in range(1, len(curve)) if curve[i - 1]]


def total_return(curve):
    """End-to-end growth as a fraction: 0.20 means +20% over the whole run."""
    return curve[-1] / curve[0] - 1


def sharpe(rets):
    """Mean daily return divided by its standard deviation, annualized by
    sqrt(252). High when gains are steady; low when the ride is wild. We use the
    SAMPLE std (divide by n-1) — the same formula market.py uses."""
    if len(rets) < 2:
        return 0.0
    m = sum(rets) / len(rets)
    var = sum((r - m) ** 2 for r in rets) / (len(rets) - 1)
    sd = sqrt(var)
    return (m / sd) * sqrt(ANN) if sd else 0.0


def max_drawdown(curve):
    """The worst peak-to-trough drop, as a (negative) fraction. We walk the curve
    tracking the highest point seen so far (the running peak); the drawdown at
    any day is how far below that peak we've fallen. The minimum is the worst."""
    peak, worst = curve[0], 0.0
    for v in curve:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1)
    return worst


def ascii_equity(curve, width=58, height=9):
    """A tiny ASCII line of the equity curve (no matplotlib in this course)."""
    lo, hi = min(curve), max(curve)
    span = hi - lo or 1.0
    cols = []
    for x in range(width):
        i = round(x * (len(curve) - 1) / (width - 1))
        cols.append(round((curve[i] - lo) / span * (height - 1)))
    rows = []
    for r in range(height - 1, -1, -1):
        rows.append("".join("#" if c == r else "." if c > r else " " for c in cols))
    return "\n".join("    " + row for row in rows)


# ---------------------------------------------------------------------------
# A STRATEGY THAT TURNS A PRICE PATH INTO AN EQUITY CURVE
# ---------------------------------------------------------------------------
# We don't reinvent a fancy signal here — Lesson 8 did that. We use a simple
# momentum rule with one tunable knob (LOOKBACK): go long when today's price is
# above the price `lookback` days ago, else go flat. We mark the account to
# market each day to get the equity curve the metrics feed on.
def price_path(n, seed):
    """A seeded random-walk price path — markets are ~random (Lesson 1)."""
    rng = random.Random(seed)
    p, path = 100.0, []
    for _ in range(n):
        p += rng.gauss(0.02, 1.0)   # a whisper of upward drift, lots of noise
        path.append(p)
    return path


def backtest(path, lookback, qty=10):
    """Run the momentum rule over a price path; return the daily equity curve.
    Long (hold `qty` units) when price > price `lookback` days ago, else flat."""
    eq = 1000.0
    curve = [eq]
    for t in range(1, len(path)):
        in_market = t > lookback and path[t - 1] > path[t - 1 - lookback]
        pos = qty if in_market else 0
        eq += pos * (path[t] - path[t - 1])   # mark-to-market the day's move
        curve.append(eq)
    return curve


# ===========================================================================
# PART A — read the three numbers on one strategy
# ===========================================================================
path = price_path(252, seed=8)             # one year of daily prices
curve = backtest(path, lookback=20)

tr = total_return(curve)
sh = sharpe(daily_returns(curve))
dd = max_drawdown(curve)

print("PART A — one strategy, one year, three honest numbers")
print("=" * 62)
print(ascii_equity(curve))
print(f"    start ${curve[0]:,.0f}{'':>30}end ${curve[-1]:,.0f}\n")
print(f"  total return : {tr * 100:+6.1f}%   how much the account grew end to end")
print(f"  Sharpe (ann.): {sh:6.2f}    return per unit of wobble (>1 is decent)")
print(f"  max drawdown : {dd * 100:6.1f}%   worst peak-to-trough fall along the way")
print()
print("  In plain English:")
print(f"   * It {'made' if tr >= 0 else 'lost'} {abs(tr) * 100:.1f}% over the year — but the headline hides the ride.")
sh_word = "respectable (>1)" if sh >= 1 else "mediocre — barely paid for the wobble" if sh >= 0 else "negative — it lost money AND was a rough ride"
print(f"   * A Sharpe of {sh:.2f} is {sh_word}.")
print(f"   * You'd have had to stomach a {abs(dd) * 100:.0f}% drop at the worst point.")
print("     That drawdown is the number that decides if you'd really have held on.")


# ===========================================================================
# PART B — the OOS trap: tuning on the past, judging on the future
# ===========================================================================
# Here's how backtests lie. We have TWO years of data. We split it in half:
#   IN-SAMPLE  (IS)  — the first half: the data we're allowed to tune on.
#   OUT-OF-SAMPLE    — the second half: unseen data, our honest test.
# We try several LOOKBACK values, pick the one that looks BEST in-sample, then
# check whether that "winner" still wins out-of-sample. Usually it doesn't — we
# tuned to the in-sample NOISE, not to a real edge. That gap is overfitting.
print("\n\nPART B — the in-sample / out-of-sample trap (overfitting)")
print("=" * 62)

full = price_path(504, seed=8)             # two years
split = len(full) // 2                     # tune on first half, test on second
is_path, oos_path = full[:split], full[split:]

PARAMS = [5, 10, 20, 40, 60]               # candidate lookbacks (the knob)

print(f"  Two years of prices, split at day {split}.")
print(f"  Trying {len(PARAMS)} lookback settings; tuning ONLY on the in-sample half.\n")
print(f"  {'lookback':>9}{'IS Sharpe':>12}{'OOS Sharpe':>12}")
print("  " + "-" * 33)

rows = []
for lb in PARAMS:
    is_sh = sharpe(daily_returns(backtest(is_path, lb)))
    oos_sh = sharpe(daily_returns(backtest(oos_path, lb)))
    rows.append((lb, is_sh, oos_sh))
    print(f"  {lb:>9}{is_sh:>12.2f}{oos_sh:>12.2f}")

# Pick the winner by IN-SAMPLE Sharpe — exactly what an overfitter does.
best = max(rows, key=lambda r: r[1])
print("  " + "-" * 33)
print(f"  We pick lookback={best[0]} — it has the best IN-SAMPLE Sharpe ({best[1]:.2f}).")
print(f"  On unseen out-of-sample data that same setting scores {best[2]:.2f}.")
drop = best[1] - best[2]
print(f"\n  The Sharpe fell by {drop:.2f} out-of-sample. We didn't find an edge —")
print("  we fitted the in-sample noise. THIS is why a backtest must always keep")
print("  an out-of-sample slice it never touches: it's the only honest score.")

avg_oos = sum(r[2] for r in rows) / len(rows)
print(f"\n  (Tell-tale sign: the best IS pick ({best[2]:.2f} OOS) is no better than the")
print(f"   average OOS across all settings ({avg_oos:.2f}). The 'tuning' bought nothing.)")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. SPLIT POINT. Change `split` in Part B to len(full)//3 (tune on a third,
#    test on two-thirds). Does the OOS Sharpe of the "winner" hold up any better
#    with less data to overfit, or worse? There is no free lunch here.
# 2. OVERFIT HARDER. Add more knobs to PARAMS, e.g. range(2, 80, 2). With more
#    candidates you'll almost always find one with a gorgeous IN-SAMPLE Sharpe —
#    and watch how badly it usually craters out-of-sample. More tuning = more
#    overfitting, not more edge.
# 3. RESEED. Change random.seed(10) at the top to 1, 2, 3... Re-run a few times.
#    The "best" lookback jumps around and the OOS Sharpe is all over the place —
#    proof the result is mostly luck, not skill. A number that won't sit still
#    isn't an edge.
# 4. HONEST CHECK. In Part A, try lookback=1 (trade on yesterday's move). The
#    total return might look fine, but check the max drawdown and Sharpe — a
#    twitchy rule that pays the spread constantly (Lesson 9) is rarely worth it.
