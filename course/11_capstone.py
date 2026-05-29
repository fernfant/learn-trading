"""
LESSON 11 — CAPSTONE: beat buy-and-hold on the sim, AFTER spread & fees
(Track 1: trading on capital.com) · the reference solution

This is the boss fight. Everything you built in Track 1 — a wandering price
(L1), two prices and a spread (L2), long & short (L3), equity (L4), leverage &
margin (L5), stop-loss / take-profit (L6), risk-based position sizing (L7), a
moving-average signal (L8), real costs (L9), honest metrics (L10) — all of it
comes together here into ONE honest backtest.

The challenge: build a strategy that beats simple BUY-AND-HOLD on the simulator
AFTER paying the spread, overnight funding, and slippage — and prove it with
proper metrics (return, Sharpe, max drawdown) on data the strategy has NEVER
seen while it was being tuned: the OUT-OF-SAMPLE (OOS) split.

The rules of an honest backtest (Chan, *Quantitative Trading*):
  1. Net of costs. Every fill pays half the spread + slippage; every held day
     pays the overnight swap. No frictionless fantasy numbers.
  2. Split the data. Tune ONLY on the IN-SAMPLE half. Then run the frozen
     strategy ONCE on the OOS half. The OOS number is the only one you trust.
  3. No peeking. You don't get to re-tune after seeing OOS. (Do that and you've
     just "fitted" the noise — your live results will be the OOS, not the IS.)

The honest punchline (and the whole theme of Track 1): on a near-random walk,
after costs, beating buy-and-hold *reliably* is RARE. The reference strategy
below is realistic — it may win on the in-sample half and then only marginally
beat, or even LOSE to, buy-and-hold out-of-sample. That gap between IS and OOS
is the most important lesson in trading. We own it; we don't fake a win.

Run it:  python3 11_capstone.py
Then read 11_capstone.md, and try to beat it.
"""

import random
from math import sqrt

# A seed makes the whole market repeat identically, so your numbers match the
# walkthrough's. Change SEED (or hit "New market" in the HTML) to see the
# verdict flip across different random worlds — that variability IS the point.
SEED = 11
random.seed(SEED)

# ---- THE KNOBS (these were tuned ONLY on the in-sample half) -----------------
DAYS = 500             # two "years"; we split it down the middle (L10)
SPLIT = DAYS // 2      # first half = in-sample (tune), second half = OOS (judge)
SPREAD = 0.10          # the platform's two-price gap; its fee (L2)
SLIPPAGE = 0.02        # extra price you lose to motion on each fill (L9)
LEVERAGE = 5           # margin = notional / leverage (L5)
RISK_FRAC = 0.02       # risk 2% of equity per trade (L7)
STOP_FRAC = 0.04       # stop 4% below entry; take-profit 8% above (L6)
TAKE_FRAC = 0.08
FAST, SLOW = 10, 40    # the signal's MA windows — tuned on IS only (L8)
OVERNIGHT_SWAP = 0.02  # charged every held day (L9)
START_CASH = 2000.0


def avg(xs):
    return sum(xs) / len(xs)


# -----------------------------------------------------------------------------
# 1) THE MARKET — one random walk, generated once, then SPLIT in two.
# -----------------------------------------------------------------------------
# We build the whole price path up front so the in-sample and out-of-sample
# halves are two slices of the SAME world. A faint upward drift (0.02/day) is
# deliberately baked in — it gives buy-and-hold a real tailwind, making it a
# genuinely hard benchmark to beat (which is honest: stocks drift up over time).
def make_prices(days, drift=0.02):
    mid = 100.0
    path = [mid]
    for _ in range(days):
        mid += random.gauss(drift, 1.0)
        path.append(mid)
    return path


# -----------------------------------------------------------------------------
# 2) THE STRATEGY — the full Track-1 loop, runnable on ANY price slice.
# -----------------------------------------------------------------------------
# This is market.py, packaged as a function so we can run it on the in-sample
# slice and (separately) the out-of-sample slice. Long-only MA crossover, risk-
# sized, with a stop/TP, leverage + 50% stop-out, paying half-spread + slippage
# on every fill and a swap every held day. Returns the daily equity curve.
def run_strategy(prices, costs=True):
    half_spread = (SPREAD / 2) if costs else 0.0
    slip = SLIPPAGE if costs else 0.0
    swap = OVERNIGHT_SWAP if costs else 0.0

    cash = START_CASH
    equity = cash
    position = 0
    entry = stop = take = 0.0
    history = [prices[0]]
    curve = [cash]
    trades = 0

    for i in range(1, len(prices)):
        mid = prices[i]
        history.append(mid)
        buy = mid + SPREAD / 2     # ask (L2)
        sell = mid - SPREAD / 2    # bid (L2)
        mark = sell if position > 0 else buy if position < 0 else mid

        # SIGNAL: fast MA above slow MA = uptrend, go/stay long (L8)
        signal = False
        if len(history) > SLOW:
            signal = avg(history[-FAST:]) > avg(history[-SLOW:])

        # ORDER TRIGGERS (L6) and the 50% margin STOP-OUT (L5)
        hit_stop = position > 0 and mark <= stop
        hit_take = position > 0 and mark >= take
        used_margin = abs(position) * mark / LEVERAGE
        stopped_out = position != 0 and equity < 0.5 * used_margin

        if position != 0 and (hit_stop or hit_take or stopped_out or not signal):
            # CLOSE: sell back at the mark, pay half-spread + slippage (L9)
            cash += position * mark - (half_spread + slip) * abs(position)
            position, entry, stop, take = 0, 0.0, 0.0, 0.0
            trades += 1
        elif position == 0 and signal:
            # OPEN a long, sized from risk (L7), capped by leverage (L5)
            entry = buy
            stop = entry * (1 - STOP_FRAC)
            take = entry * (1 + TAKE_FRAC)
            stop_distance = entry - stop
            qty = int(RISK_FRAC * equity / stop_distance)
            max_qty = int(equity * LEVERAGE / entry)
            qty = max(1, min(qty, max_qty))
            position += qty
            cash -= position * entry + (half_spread + slip) * position

        if position != 0:
            cash -= swap * abs(position)   # overnight funding (L9)

        mark = sell if position > 0 else buy if position < 0 else mid
        equity = cash + position * mark
        curve.append(equity)

    return curve, trades


# -----------------------------------------------------------------------------
# 3) BUY-AND-HOLD — the benchmark. Buy on day 0, hold to the end. One spread.
# -----------------------------------------------------------------------------
# The honest yardstick. Same starting cash, one round-trip spread paid up front
# (you cross to buy), then just ride the asset. No leverage, no signal, no swap
# (a 1:1 share-style hold is swap-exempt on capital.com — the gentlest case).
def buy_and_hold(prices, costs=True):
    entry = prices[0] + (SPREAD / 2 if costs else 0.0)    # buy at the ask
    units = START_CASH / entry
    # mark each day at the sell (what you'd actually get out at)
    return [units * (p - (SPREAD / 2 if costs else 0.0)) for p in prices]


# -----------------------------------------------------------------------------
# 4) THE METRICS (Lesson 10) — return, annualized Sharpe, max drawdown.
# -----------------------------------------------------------------------------
def returns(curve):
    return [curve[i] / curve[i - 1] - 1 for i in range(1, len(curve)) if curve[i - 1]]


def sharpe(curve):
    rets = returns(curve)
    if len(rets) < 2:
        return 0.0
    m = avg(rets)
    var = sum((r - m) ** 2 for r in rets) / (len(rets) - 1)
    sd = sqrt(var)
    return (m / sd) * sqrt(252) if sd else 0.0


def total_return(curve):
    return curve[-1] / curve[0] - 1


def max_drawdown(curve):
    peak, worst = curve[0], 0.0
    for v in curve:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1)
    return worst


# -----------------------------------------------------------------------------
# 5) A TINY ASCII EQUITY CHART that overlays TWO curves (strategy vs B&H).
# -----------------------------------------------------------------------------
# 'S' = strategy, 'H' = buy-and-hold, ':' = where they overlap on a row.
def ascii_two(a, b, width=58, height=12):
    lo = min(min(a), min(b))
    hi = max(max(a), max(b))
    span = (hi - lo) or 1.0

    def sample(s):
        return [s[round(i * (len(s) - 1) / (width - 1))] for i in range(width)]

    ca, cb = sample(a), sample(b)
    rows = []
    for r in range(height):
        top = hi - r * span / height
        bot = hi - (r + 1) * span / height
        line = []
        for x in range(width):
            ina = bot <= ca[x] < top or (r == 0 and ca[x] >= top)
            inb = bot <= cb[x] < top or (r == 0 and cb[x] >= top)
            line.append(":" if ina and inb else "S" if ina else "H" if inb else " ")
        rows.append(f"{top:8.0f} |{''.join(line)}")
    return "\n".join(rows)


def scoreboard(title, strat_curve, bh_curve, trades=None):
    sr, br = total_return(strat_curve), total_return(bh_curve)
    print("\n" + "=" * 62)
    print(f"  {title}")
    print("=" * 62)
    print(f"  {'':14}{'strategy':>16}{'buy & hold':>16}")
    print(f"  {'total return':14}{sr * 100:>15.1f}%{br * 100:>15.1f}%")
    print(f"  {'Sharpe (ann.)':14}{sharpe(strat_curve):>16.2f}{sharpe(bh_curve):>16.2f}")
    print(f"  {'max drawdown':14}{max_drawdown(strat_curve) * 100:>15.1f}%"
          f"{max_drawdown(bh_curve) * 100:>15.1f}%")
    if trades is not None:
        print(f"  {'round-trips':14}{trades:>16}{'1':>16}")
    print("=" * 62)
    verdict = "BEAT" if sr > br else "LOST to"
    print(f"  Verdict: strategy {verdict} buy-and-hold (by return).")
    return sr, br


# -----------------------------------------------------------------------------
# RUN THE CAPSTONE
# -----------------------------------------------------------------------------
prices = make_prices(DAYS)
in_sample = prices[:SPLIT + 1]          # day 0..250  — you tuned the knobs here
out_sample = prices[SPLIT:]             # day 250..500 — judged here, ONCE

print(f"Capstone market (seed {SEED}):  start ${prices[0]:.2f}  "
      f"end ${prices[-1]:.2f}  high ${max(prices):.2f}  low ${min(prices):.2f}")
print(f"Split: in-sample = days 0..{SPLIT}, out-of-sample = days {SPLIT}..{DAYS}\n")

# --- IN-SAMPLE: where the knobs were chosen. Looks good — it always does. ---
is_strat, is_trades = run_strategy(in_sample)
is_bh = buy_and_hold(in_sample)
print("IN-SAMPLE equity (S = strategy, H = buy & hold, : = both):")
print(ascii_two(is_strat, is_bh))
scoreboard("IN-SAMPLE  (after spread + slippage + swap)", is_strat, is_bh, is_trades)

# --- OUT-OF-SAMPLE: the honest test. The strategy has never seen this. ---
oos_strat, oos_trades = run_strategy(out_sample)
oos_bh = buy_and_hold(out_sample)
print("\nOUT-OF-SAMPLE equity (S = strategy, H = buy & hold, : = both):")
print(ascii_two(oos_strat, oos_bh))
oos_sr, oos_br = scoreboard("OUT-OF-SAMPLE  (the only result that counts)",
                            oos_strat, oos_bh, oos_trades)

# --- THE HONEST VERDICT ------------------------------------------------------
# We don't hard-code a triumphant story — we read it off the actual numbers,
# because on a random walk the verdict genuinely flips from seed to seed.
print("\n" + "-" * 62)
is_sr, is_br = total_return(is_strat), total_return(is_bh)
oos_dd, bh_dd = max_drawdown(oos_strat), max_drawdown(oos_bh)
print("  THE HONEST READ:")
print(f"  * In-sample, the strategy {'beat' if is_sr > is_br else 'LOST to'} "
      f"buy-and-hold on return.")
print(f"  * Out-of-sample — the only test that counts — it "
      f"{'BEAT' if oos_sr > oos_br else 'LOST to'} buy-and-hold")
print(f"    ({oos_sr * 100:+.1f}% vs {oos_br * 100:+.1f}%).")
if oos_sr > oos_br and oos_sr < is_br:
    print(f"  * But look WHY it 'won': it mostly sat FLAT through a falling")
    print(f"    market while buy-and-hold bled (its DD {bh_dd * 100:.0f}% vs the")
    print(f"    strategy's {oos_dd * 100:.0f}%). Dodging a drop is risk control,")
    print(f"    not a predictive edge — and on a random walk that luck reverses.")
else:
    print(f"  * The strategy paid the spread on every fill and a swap on every")
    print(f"    held day; that constant drag is exactly what eats a thin edge.")
print(f"  * Bottom line: on a near-random walk, after spread + swap + slippage,")
print(f"    a DURABLE edge over buy-and-hold is genuinely rare. Re-run with")
print(f"    SEED 1..10 (TRY IT #1) and count the wins — that honest tally, not")
print(f"    one lucky split, is the whole lesson of Track 1.")


# -----------------------------------------------------------------------------
# TRY IT  /  YOUR CHALLENGE  🏆
# -----------------------------------------------------------------------------
# This is the capstone. Your mission: make the strategy beat buy-and-hold
# OUT-OF-SAMPLE, after costs — honestly. The rules:
#
#   * Tune knobs using ONLY the in-sample scoreboard. Never look at the OOS
#     numbers while changing FAST/SLOW/RISK_FRAC/STOP_FRAC/TAKE_FRAC.
#   * Then run once and read the OOS scoreboard. That's your real score.
#   * It must stay net of SPREAD, SLIPPAGE and OVERNIGHT_SWAP. No cheating those.
#
# 1. ROBUSTNESS: change SEED to 1, 2, 3, … 10 and tally how many seeds the
#    strategy beats B&H out-of-sample. If it's ~5/10, you have no edge — you're
#    flipping a coin. A real edge wins clearly across MOST seeds.
# 2. OVERFIT ON PURPOSE: tune FAST/SLOW to maximize the IN-SAMPLE return, then
#    look at OOS. Watch the IS win turn into an OOS loss. That's curve-fitting,
#    the trap this whole lesson is built to expose.
# 3. COSTS OFF: call run_strategy(out_sample, costs=False) and B&H with
#    costs=False. How much of the gap to B&H was just the spread + swap?
# 4. ADD SHORTS: right now the strategy is long-only, so in a downtrend it just
#    sits flat while B&H bleeds. Let it go SHORT when fast < slow. Does trading
#    both directions finally beat a drifting-up B&H — or does doubling your
#    spread-crossings cost more than it earns?
# 5. THE REAL BOSS: find ONE set of knobs that beats B&H out-of-sample across a
#    MAJORITY of seeds 1..10, after costs. If you manage it, you've done what
#    most retail CFD traders never do. If you can't — now you understand the
#    regulatory warning. Either way: that's Track 1. 🏆  Next, Track 2.
