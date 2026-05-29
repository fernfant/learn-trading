"""
LESSON 8 — A signal: the moving-average crossover (and why to distrust it)
(Track 1: trading on capital.com)

Up to now we've built the *plumbing*: a price, a spread, long/short, P&L,
leverage, order types, and how big to bet. But we've never had a RULE that
says WHEN to buy. This lesson adds the most famous rule in all of charting —
the moving-average crossover — and then does the thing most courses won't:
it checks whether the rule actually works.

THE SIGNAL
----------
A "moving average" (MA) is just the mean of the last N closing prices. It
smooths out the daily noise so you can see the trend underneath.

    fast MA = mean of the last  5 prices   (reacts quickly)
    slow MA = mean of the last 20 prices   (reacts slowly)

The classic rule:

    signal = fast_ma > slow_ma   ->  go LONG  (the "golden cross")
    when it flips back below      ->  go FLAT  (the "death cross")

The intuition: when the recent average climbs above the longer-term average,
the trend is up, so ride it. That single line — `signal = fast_avg > slow_avg`
— is exactly what we add to ../market.py this lesson.

THE SKEPTIC'S WARNING (this is the real lesson)
-----------------------------------------------
It LOOKS like wisdom. It's printed in every trading book. But David Aronson
(*Evidence-Based Technical Analysis*) spent a career showing that on a price
that's nearly a random walk, a crossover mostly trades on NOISE. A backtest
flatters itself: you can always find a market where the rule "worked", because
sometimes a coin flip comes up heads five times. The honest test is whether
the edge:
  (a) beats just buying and holding,
  (b) survives even a tiny per-trade cost, and
  (c) keeps working on data you didn't pick.

So this script doesn't just run the crossover and cheer. It pits it against
buy-and-hold AND against a strategy that enters on COIN FLIPS — on the SAME
price path — then re-runs the whole contest across several different markets
to show the result flip-flops. That instability is the point.

Run it:  python3 08_signal.py
Then read 08_walkthrough.md.
"""

import random


# ---------------------------------------------------------------------------
# THE BUILDING BLOCK — a simple moving average (stdlib only)
# ---------------------------------------------------------------------------
def sma(prices, n):
    """Mean of the last n prices, or None until we have enough history."""
    if len(prices) < n:
        return None
    return sum(prices[-n:]) / n


def random_walk(days, seed, start=100.0, vol=1.0):
    """A seeded near-random-walk price path: today = yesterday + small shock."""
    rng = random.Random(seed)
    p = start
    path = [p]
    for _ in range(days):
        p += rng.gauss(0, vol)
        path.append(p)
    return path


# ---------------------------------------------------------------------------
# THE STRATEGIES — each takes a price path, returns its total % return
# ---------------------------------------------------------------------------
# We keep the accounting deliberately simple so the comparison is clean: we're
# either fully LONG one unit or fully FLAT, we enter/exit at the day's price,
# and we charge `cost` (a per-trade toll, like crossing the spread) each time
# we change our mind. No leverage, no sizing — just: does the RULE add value?

def backtest_crossover(path, fast, slow, cost=0.0):
    pos = 0            # 1 = long, 0 = flat
    entry = 0.0
    pnl = 0.0
    trades = 0
    for t in range(len(path)):
        price = path[t]
        fast_avg = sma(path[:t + 1], fast)
        slow_avg = sma(path[:t + 1], slow)
        if fast_avg is None or slow_avg is None:
            continue
        signal = fast_avg > slow_avg          # <-- the whole "signal" (Lesson 8)
        if signal and pos == 0:               # golden cross -> open long
            pos, entry = 1, price
            pnl -= cost
            trades += 1
        elif not signal and pos == 1:         # death cross -> close
            pnl += price - entry
            pos = 0
            pnl -= cost
            trades += 1
    if pos == 1:                              # close any open trade at the end
        pnl += path[-1] - entry
        pnl -= cost
        trades += 1
    return pnl / path[0] * 100, trades


def backtest_random(path, fast, slow, cost=0.0, seed=0):
    """Same machinery, but entry/exit are COIN FLIPS — our control group.
    We flip exactly when the crossover *could* act (after the slow window
    fills), so it trades at a similar pace and the comparison is fair."""
    rng = random.Random(seed)
    pos = 0
    entry = 0.0
    pnl = 0.0
    trades = 0
    for t in range(len(path)):
        price = path[t]
        if sma(path[:t + 1], slow) is None:
            continue
        flip = rng.random() < 0.5
        if flip and pos == 0:
            pos, entry = 1, price
            pnl -= cost
            trades += 1
        elif flip and pos == 1:
            pnl += price - entry
            pos = 0
            pnl -= cost
            trades += 1
    if pos == 1:
        pnl += path[-1] - entry
        pnl -= cost
        trades += 1
    return pnl / path[0] * 100, trades


def buy_and_hold(path):
    """Buy on day 0, hold to the end. The yardstick every strategy must beat."""
    return (path[-1] - path[0]) / path[0] * 100


# ---------------------------------------------------------------------------
# PART A — see the MAs and the crossovers on ONE market
# ---------------------------------------------------------------------------
DAYS, FAST, SLOW = 120, 5, 20
path = random_walk(DAYS, seed=8)

print("PART A — the signal, drawn")
print("=" * 64)
print(f"A fast({FAST}) and slow({SLOW}) moving average over a {DAYS}-day random walk.")
print("Where fast crosses ABOVE slow we go long (^); where it crosses back")
print("below we go flat (v). Each ^v pair is one round-trip you pay a toll on.\n")

# Walk the path, find the days the crossover flips, and mark them.
marks = []
prev = None
for t in range(len(path)):
    f, s = sma(path[:t + 1], FAST), sma(path[:t + 1], SLOW)
    if f is None or s is None:
        continue
    sig = f > s
    if prev is not None and sig != prev:
        marks.append((t, "^" if sig else "v"))
    prev = sig

# A compact ASCII strip: price height, with crossover arrows underneath.
lo, hi = min(path), max(path)
span = (hi - lo) or 1.0
height = 9
for r in range(height):
    level = hi - (r + 0.5) * span / height
    row = "".join("#" if p >= level else " " for p in path)
    print(f"{level:7.2f} |{row}")
arrow_row = [" "] * len(path)
for t, a in marks:
    arrow_row[t] = a
print(" " * 8 + "+" + "-" * len(path))
print(" " * 9 + "".join(arrow_row))
print(f"\n{len(marks)} crossover flips -> roughly {len(marks)} signals on this one market.\n")


# ---------------------------------------------------------------------------
# PART B — the honest contest, on this SAME market
# ---------------------------------------------------------------------------
print("PART B — does the rule actually beat the alternatives? (same market)")
print("=" * 64)
cx, cx_tr = backtest_crossover(path, FAST, SLOW, cost=0.0)
rnd, rnd_tr = backtest_random(path, FAST, SLOW, cost=0.0, seed=99)
bh = buy_and_hold(path)
print(f"  {'strategy':22}{'return':>10}{'trades':>9}")
print(f"  {'MA crossover':22}{cx:>9.1f}%{cx_tr:>9}")
print(f"  {'random coin-flip':22}{rnd:>9.1f}%{rnd_tr:>9}")
print(f"  {'buy & hold':22}{bh:>9.1f}%{'-':>9}")
print("\n  Notice the crossover isn't reliably the winner — on a near-random")
print("  walk it's wrestling the same noise the coin-flip is.\n")


# ---------------------------------------------------------------------------
# PART C — now subtract a tiny per-trade cost. Watch the edge melt.
# ---------------------------------------------------------------------------
COST = 0.10   # ~ one spread-cross per trade, in price units (Lessons 2 & 9)
print(f"PART C — same market, but each trade now costs {COST} (the spread)")
print("=" * 64)
cx0, _ = backtest_crossover(path, FAST, SLOW, cost=0.0)
cxc, cxc_tr = backtest_crossover(path, FAST, SLOW, cost=COST)
print(f"  MA crossover, no cost   : {cx0:>7.1f}%")
print(f"  MA crossover, with cost : {cxc:>7.1f}%   ({cxc_tr} trades x {COST})")
print(f"  buy & hold (1 trade)    : {bh:>7.1f}%")
drag = cx0 - cxc
print(f"\n  Cost dragged the strategy down by {drag:.1f} points. The more it")
print("  trades, the more it bleeds — and buy & hold only pays the toll once.\n")


# ---------------------------------------------------------------------------
# PART D — run it across MANY markets. The result is unstable. That's the point.
# ---------------------------------------------------------------------------
print("PART D — the same rule on 8 different markets (seeds)")
print("=" * 64)
print(f"  {'seed':>5}{'crossover':>12}{'+cost':>10}{'buy&hold':>11}{'beat B&H?':>12}")
wins = wins_cost = 0
for seed in range(1, 9):
    p = random_walk(DAYS, seed=seed)
    c_free, _ = backtest_crossover(p, FAST, SLOW, cost=0.0)
    c_cost, _ = backtest_crossover(p, FAST, SLOW, cost=COST)
    h = buy_and_hold(p)
    if c_free > h:
        wins += 1
    if c_cost > h:
        wins_cost += 1
    verdict = "yes" if c_cost > h else "no"
    print(f"  {seed:>5}{c_free:>11.1f}%{c_cost:>9.1f}%{h:>10.1f}%{verdict:>12}")
print(f"\n  Crossover beat buy & hold on {wins}/8 markets free, {wins_cost}/8 after cost —")
print("  and every single +cost number is LOWER than its free version. The")
print("  win/loss flip-flops market to market: that's the signature of NOISE,")
print("  not an edge. A real edge would win consistently AND survive costs.")
print("  Most 'signals' do neither.\n")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. WINDOWS. Change FAST, SLOW to (10, 50) for a calmer system, or (2, 5) for
#    a twitchy one. Twitchy trades far more often — re-run Part C and watch the
#    cost drag explode. Does any window setting win on most seeds in Part D?
# 2. COST. Set COST = 0.30. How many of the 8 markets still beat buy & hold?
#    This is the single most overlooked number in amateur backtests.
# 3. MORE SEEDS. Change `range(1, 9)` to `range(1, 51)` and count the wins. As
#    you test more markets, the win rate drifts toward a coin flip — exactly
#    what you'd expect if the signal had no real edge.
# 4. RIG IT (cheat to learn). Loop over seeds and PRINT only the one where the
#    crossover wins biggest, then present that chart alone. That's how a
#    dishonest backtest is made — and why out-of-sample testing (Lesson 10)
#    exists to catch it.
# 5. Open ../market.py — the line `signal = fast_avg > slow_avg` is the exact
#    rule you just stress-tested, now wired into the full account.
