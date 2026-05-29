"""
market.py — the cumulative artifact for TRACK 1 (normal trading).

You build this ONE LINE AT A TIME, one line per lesson, until it is a real
backtester: a price feed -> a signal -> a sized position -> P&L -> metrics.

Right now it is at the LESSON 10 stage: a small, honest, runnable MA-crossover
backtester that behaves like a capital.com DEMO account. A "true" price (the
MID) wanders; around it the platform quotes a BUY and a SELL whose gap is the
SPREAD. A fast and a slow moving average drive a long-only signal: when the
fast crosses above the slow we open a LONG, sized from how much equity we're
willing to RISK; when it crosses back below we close. Every position runs on
LEVERAGE (a small margin backs a big notional), carries a STOP-LOSS and a
TAKE-PROFIT, gets force-closed if margin runs out (50% stop-out), and pays its
costs: half the spread on every fill plus an overnight SWAP each day held.
After the loop we score it honestly — total return, a Sharpe ratio, and the
worst drawdown — and compare it to simply buying and holding.

The honest theme runs through the whole thing: the market is ~random, any edge
is small, and costs quietly eat it. Don't expect easy money — after the spread
and the swap this strategy may barely beat, or even lose to, buy-and-hold.
That's the lesson, not a bug.

This mimics a capital.com DEMO account (see course/capital_com.md): two-sided
prices, long & short, leverage, the spread, real order types, and the costs.

------------------------------------------------------------------------------
BUILD MAP  (each lesson unlocks ~1 new idea in the loop below)
------------------------------------------------------------------------------
  L1  price wanders          mid += shock
  L2  two prices, a spread   buy, sell = mid + s/2, mid - s/2
  L3  long AND short         position += qty   (qty can be negative)
  L4  what are you worth      equity = cash + position * price
  L5  leverage & margin      margin = abs(position)*price / leverage
  L6  order types            stop-loss / take-profit triggers
  L7  size your bets         qty = int(risk_frac * equity / stop_distance)
  L8  a real signal          signal = fast_avg > slow_avg
  L9  trading isn't free     cash -= half_spread + overnight_swap
  L10 measure the result     return, sharpe, max_drawdown                <-- HERE
  L11 CAPSTONE               beat buy-and-hold on the sim, after spread + fees
------------------------------------------------------------------------------
Run it:  python3 market.py
"""

import random
from math import sqrt

# A "seed" makes the randomness repeat the same way every run, so you and I
# see the exact same wandering line. Change it to get a different market.
random.seed(7)

# ---- THE KNOBS (everything you can tune lives here) -------------------------
DAYS = 250             # ~one trading year, so the annualized Sharpe is honest
SPREAD = 0.10          # capital.com shows two prices; this gap is its fee (L2)
LEVERAGE = 5           # broker fronts most of the notional; you post 1/5 (L5)
RISK_FRAC = 0.02       # risk at most 2% of equity per trade (L7)
STOP_FRAC = 0.04       # stop-loss 4% below entry; take-profit 8% above (L6)
TAKE_FRAC = 0.08
FAST, SLOW = 5, 20     # moving-average windows for the signal (L8)
OVERNIGHT_SWAP = 0.02  # charged every day a position is held overnight (L9)

mid = 100.0            # the "true" price, halfway between Buy and Sell
history = [mid]        # we remember every day's mid so we can look back
buy = sell = mid       # today's two prices (filled in each day below)
position = 0           # signed bet: +long, -short, 0 flat (L3)
entry = 0.0            # the price we opened that position at
stop = take = 0.0      # this position's stop-loss / take-profit levels (L6)
cash = 2000.0          # settled balance; only moves when we trade (L4)
equity = cash          # balance + live value of the open position (L4)
equity_curve = [cash]  # equity at the end of each day, for the metrics (L10)
trades = 0             # how many round-trips we did, to see the cost drag


def avg(xs):
    return sum(xs) / len(xs)


for day in range(DAYS):
    # ---- THE MARKET'S ONE RULE (Lesson 1) -----------------------------------
    # Each day the price gets nudged up or down by a small random "shock".
    # gauss(0, 1) means: usually a small nudge, occasionally a big one, up just
    # as often as down. Nobody knows tomorrow's shock — the price is a random
    # walk, and that is exactly why a "signal" is so hard to beat.
    shock = random.gauss(0, 1)
    mid += shock
    history.append(mid)
    # ---- TWO PRICES, A SPREAD (Lesson 2) ------------------------------------
    # You can't trade at the mid. To go LONG you pay the higher Buy price; to
    # close a long you get the lower Sell price. The gap is the spread, and you
    # pay half of it each time you cross — once in, once out (charged in L9).
    buy = mid + SPREAD / 2     # ask — what you pay to buy
    sell = mid - SPREAD / 2    # bid — what you get to sell
    half_spread = SPREAD / 2
    # The price we could CLOSE the current position at: a long exits at the
    # sell, a short at the buy, flat marks at the mid (Lesson 4).
    mark = sell if position > 0 else buy if position < 0 else mid

    # ---- THE SIGNAL: A MOVING-AVERAGE CROSSOVER (Lesson 8) -------------------
    # A moving average is just the mean of the last N prices — it smooths the
    # noise. When the FAST average is above the SLOW one the recent trend is up
    # ("golden cross"); when it's below, down ("death cross"). We only act once
    # we have enough history to fill the slow window.
    signal = False
    if len(history) > SLOW:
        fast_avg = avg(history[-FAST:])
        slow_avg = avg(history[-SLOW:])
        signal = fast_avg > slow_avg

    # ---- ORDER TRIGGERS: STOP-LOSS & TAKE-PROFIT (Lesson 6) ------------------
    # capital.com lets you attach a stop (cut the loss) and a take-profit (bank
    # the win) to a position; the platform watches the mark and closes you when
    # either is hit. We check the same two levels here every single day.
    hit_stop = position > 0 and mark <= stop
    hit_take = position > 0 and mark >= take

    # ---- LEVERAGE, MARGIN & THE STOP-OUT (Lesson 5) -------------------------
    # On leverage you control a big NOTIONAL (position * price) with a small
    # MARGIN = notional / LEVERAGE. The margin LEVEL is equity / used-margin.
    # capital.com warns at 75%/100% and FORCE-CLOSES ("stop-out") at 50%. We
    # mirror the 50% rule: if a losing trade burns through half its margin,
    # the platform shuts it for you — no choice, no mercy.
    used_margin = abs(position) * mark / LEVERAGE
    stopped_out = position != 0 and equity < 0.5 * used_margin

    # ---- ACT ON ALL OF THE ABOVE -------------------------------------------
    if position != 0 and (hit_stop or hit_take or stopped_out or not signal):
        # CLOSE the position. We sell our units back at the mark and pay half
        # the spread on this fill (Lesson 9). Whatever we get lands in cash.
        cash += position * mark - half_spread * abs(position)
        why = ("stop-out" if stopped_out else "stop-loss" if hit_stop
               else "take-profit" if hit_take else "signal flipped down")
        if stopped_out:
            print(f"day {day:>3}: FORCED CLOSE — margin level hit 50% "
                  f"(equity ${equity:.0f} < ${0.5 * used_margin:.0f}); reason: {why}")
        position, entry, stop, take = 0, 0.0, 0.0, 0.0
        trades += 1
    elif position == 0 and signal:
        # OPEN a long. SIZE IT FROM RISK (Lesson 7): we're willing to lose
        # RISK_FRAC of equity if the stop is hit, and the stop sits STOP_FRAC
        # below entry, so qty = risk_dollars / stop_distance. Leverage caps how
        # big a notional our cash can back, so we never size past our margin.
        entry = buy                       # we open at the ask
        stop = entry * (1 - STOP_FRAC)    # stop-loss level (Lesson 6)
        take = entry * (1 + TAKE_FRAC)    # take-profit level (Lesson 6)
        stop_distance = entry - stop
        qty = int(RISK_FRAC * equity / stop_distance)
        max_qty = int(equity * LEVERAGE / entry)   # margin ceiling (Lesson 5)
        qty = max(1, min(qty, max_qty))
        position += qty                   # signed position (Lesson 3)
        cash -= position * entry + half_spread * position   # pay + half spread

    # ---- CARRYING COST: THE OVERNIGHT SWAP (Lesson 9) -----------------------
    # Hold a CFD past the daily cutoff and capital.com charges overnight funding
    # ("swap"). It's small per day but it never stops — the tax on patience.
    if position != 0:
        cash -= OVERNIGHT_SWAP * abs(position)

    # ---- WHAT ARE YOU WORTH? P&L & EQUITY (Lesson 4) ------------------------
    # Re-mark after acting, then equity = cash + live value of the position.
    mark = sell if position > 0 else buy if position < 0 else mid
    equity = cash + position * mark
    equity_curve.append(equity)


def ascii_chart(series, width=60, height=12):
    """A tiny no-dependencies line chart so we can SEE the price wander."""
    lo, hi = min(series), max(series)
    span = (hi - lo) or 1.0
    # sample the series down to `width` columns
    cols = [series[round(i * (len(series) - 1) / (width - 1))] for i in range(width)]
    rows = []
    for r in range(height):
        level = hi - (r + 0.5) * span / height
        line = "".join("█" if c >= level else " " for c in cols)
        rows.append(f"{level:8.2f} |{line}")
    return "\n".join(rows)


# ---- MEASURE THE RESULT, HONESTLY (Lesson 10) -------------------------------
# Three numbers a backtest must report, computed from the daily equity curve:
#   * total return %     — how much the account grew (or shrank) end to end.
#   * Sharpe ratio       — return per unit of wobble: mean daily return over its
#                          std, scaled by sqrt(252) to "annualize" it. >1 is
#                          decent; most real retail strategies sit below 1.
#   * max drawdown %     — the worst peak-to-trough fall along the way; the pain
#                          you'd have had to sit through. This is what blows
#                          accounts up, not the final number.
def returns(curve):
    return [(curve[i] / curve[i - 1] - 1) for i in range(1, len(curve)) if curve[i - 1]]


def sharpe(rets):
    if len(rets) < 2:
        return 0.0
    m = avg(rets)
    var = sum((r - m) ** 2 for r in rets) / (len(rets) - 1)
    sd = sqrt(var)
    return (m / sd) * sqrt(252) if sd else 0.0


def max_drawdown(curve):
    peak, worst = curve[0], 0.0
    for v in curve:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1)
    return worst


start_eq = equity_curve[0]
total_return = equity / start_eq - 1
strat_sharpe = sharpe(returns(equity_curve))
strat_dd = max_drawdown(equity_curve)

# The honest yardstick: what if you'd done NOTHING but buy and hold the asset?
# Same starting cash, same one round-trip spread, no signal, no leverage games.
bh_units = (start_eq / history[0])
bh_curve = [bh_units * p for p in history]
bh_return = history[-1] / history[0] - 1
bh_sharpe = sharpe(returns(bh_curve))
bh_dd = max_drawdown(bh_curve)


print(f"Start mid: ${history[0]:.2f}   End mid: ${history[-1]:.2f}   "
      f"High: ${max(history):.2f}   Low: ${min(history):.2f}")
print(ascii_chart(history))
print(" " * 9 + "+" + "-" * 60)
print(" " * 10 + f"day 0{' ' * 49}day {DAYS}")

print(f"\nToday's quote:  SELL ${sell:.2f}  |  mid ${mid:.2f}  |  BUY ${buy:.2f}")
side = "LONG" if position > 0 else "SHORT" if position < 0 else "FLAT"
print(f"End state: {side} {abs(position)} units   cash ${cash:.2f}   "
      f"equity ${equity:.2f}   ({trades} round-trips)")

# ---- THE SCOREBOARD (Lesson 10) ---------------------------------------------
print("\n" + "=" * 62)
print("  BACKTEST RESULT (after spread + overnight swap)")
print("=" * 62)
print(f"  {'':14}{'MA-crossover':>16}{'buy & hold':>16}")
print(f"  {'total return':14}{total_return * 100:>15.1f}%{bh_return * 100:>15.1f}%")
print(f"  {'Sharpe (ann.)':14}{strat_sharpe:>16.2f}{bh_sharpe:>16.2f}")
print(f"  {'max drawdown':14}{strat_dd * 100:>15.1f}%{bh_dd * 100:>15.1f}%")
print("=" * 62)
verdict = "beat" if total_return > bh_return else "LOST to"
print(f"  After costs, the strategy {verdict} buy-and-hold here. Markets are\n"
      f"  ~random and the spread + swap are a constant drag — an edge this\n"
      f"  small is exactly what 'most retail CFD accounts lose money' means.")


# -----------------------------------------------------------------------------
# TRY IT (exercises)
# -----------------------------------------------------------------------------
# 1. LEVERAGE cuts both ways. Bump LEVERAGE from 5 to 30 and re-run. Does the
#    return get better — or do you trigger a "FORCED CLOSE" stop-out line?
# 2. RISK_FRAC is your bet size. Try 0.01 (timid) and 0.10 (reckless). Watch
#    what 0.10 does to max drawdown — that number is the pain, not the return.
# 3. The signal lives in FAST, SLOW. Try (10, 50) for a slower, calmer system
#    and (2, 5) for a twitchy one. Count the round-trips printed at the end:
#    more trades means more spread paid. Does trading more ever help?
# 4. Set OVERNIGHT_SWAP = 0.0 (pretend funding is free) and re-run. How much of
#    the result was just the swap quietly bleeding you each held day?
# 5. Set SPREAD = 0.50 and re-run. The strategy crosses the spread on every
#    fill — does a wider spread flip "beat" into "LOST to" buy-and-hold?
# 6. Hardest: can you make the strategy beat buy-and-hold AND keep drawdown
#    smaller than it, after costs? That's Lesson 11, the capstone — and it's
#    deliberately hard, because on a random market it usually can't be done.
