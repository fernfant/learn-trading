"""
market.py — the cumulative artifact for TRACK 1 (normal trading).

You build this ONE LINE AT A TIME, one line per lesson, until it is a real
backtester: a price feed -> a strategy -> a portfolio -> P&L -> metrics.

Right now it is at the LESSON 2 stage: there isn't one price. The "true" price
(the MID) wanders, and around it capital.com quotes a BUY and a SELL price. The
gap between them is the SPREAD — the first cost you ever pay.

This mimics a capital.com DEMO account (see course/capital_com.md): two-sided
prices, long & short, leverage, the spread, real order types, and the costs.

------------------------------------------------------------------------------
BUILD MAP  (each lesson unlocks ~1 new line in the loop below)
------------------------------------------------------------------------------
  L1  price wanders          mid += shock
  L2  two prices, a spread   buy, sell = mid + s/2, mid - s/2     <-- YOU ARE HERE
  L3  long AND short         position += qty   (qty can be negative)
  L4  what are you worth      equity = cash + position * price
  L5  leverage & margin      margin = abs(position)*price / leverage
  L6  order types            trigger limit / stop / take-profit
  L7  size your bets         qty = risk_frac * equity / stop_distance
  L8  a real signal          signal = fast_avg > slow_avg
  L9  trading isn't free     cash -= half_spread + overnight_swap
  L10 measure the result     return, sharpe, max_drawdown
  L11 CAPSTONE               beat buy-and-hold on the sim, after spread + fees
------------------------------------------------------------------------------
Run it:  python3 market.py
"""

import random

# A "seed" makes the randomness repeat the same way every run, so you and I
# see the exact same wandering line. Change it to get a different market.
random.seed(7)

DAYS = 60
SPREAD = 0.10          # capital.com shows two prices; this gap is its fee (L2)
mid = 100.0            # the "true" price, halfway between Buy and Sell
history = [mid]        # we remember every day's mid so we can look back
buy = sell = mid       # today's two prices (filled in each day below)

for day in range(DAYS):
    # ---- THE MARKET'S ONE RULE (Lesson 1) -----------------------------------
    # Each day the price gets nudged up or down by a small random "shock".
    # gauss(0, 1) means: usually a small nudge, occasionally a big one,
    # up just as often as down. Nobody knows tomorrow's shock.
    shock = random.gauss(0, 1)
    mid += shock
    # ---- TWO PRICES, A SPREAD (Lesson 2) ------------------------------------
    # You can't trade at the mid. To go LONG you pay the higher Buy price; to
    # go SHORT (or close a long) you get the lower Sell price. The difference
    # is the spread, and you pay half of it each time you cross.
    buy = mid + SPREAD / 2     # ask — what you pay to buy
    sell = mid - SPREAD / 2    # bid — what you get to sell
    # -------------------------------------------------------------------------
    history.append(mid)


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


print(f"Start mid: ${history[0]:.2f}   End mid: ${history[-1]:.2f}   "
      f"High: ${max(history):.2f}   Low: ${min(history):.2f}")
print(ascii_chart(history))
print(" " * 9 + "+" + "-" * 60)
print(" " * 10 + f"day 0{' ' * 49}day {DAYS}")
print(f"\nToday's quote:  SELL ${sell:.2f}  |  mid ${mid:.2f}  |  BUY ${buy:.2f}")
print(f"Spread = ${SPREAD:.2f}. Buy now and sell instantly and you're already "
      f"down ${SPREAD:.2f} — that's the broker's fee.")


# -----------------------------------------------------------------------------
# TRY IT (exercises)
# -----------------------------------------------------------------------------
# 1. Widen the spread to SPREAD = 1.00. How much does an instant round-trip
#    (buy then sell) now cost you? (Answer: the full spread.)
# 2. capital.com spreads are tighter on big markets, wider on small ones. Which
#    SPREAD would you rather trade, 0.05 or 0.50? Why?
# 3. Print buy - sell. It always equals SPREAD — that's the definition.
# 4. A "1X" (no-leverage) share trade still pays the spread. Roughly how many
#    round-trips at SPREAD = 0.10 would cost you $1?
