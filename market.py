"""
market.py — the cumulative artifact for TRACK 1 (normal trading).

You build this ONE LINE AT A TIME, one line per lesson, until it is a real
backtester: a price feed -> a strategy -> a portfolio -> P&L -> metrics.

Right now it is at the LESSON 1 stage: a price is just a number that wanders.
That wandering line IS the market. Everything else we add later reacts to it.

This mimics a capital.com DEMO account (see course/capital_com.md): two-sided
prices, long & short, leverage, the spread, real order types, and the costs.

------------------------------------------------------------------------------
BUILD MAP  (each lesson unlocks ~1 new line in the loop below)
------------------------------------------------------------------------------
  L1  price wanders          price += shock                      <-- YOU ARE HERE
  L2  two prices, a spread   buy, sell = mid + s/2, mid - s/2
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
price = 100.0          # the stock starts at $100
history = [price]      # we remember every day's price so we can look back

for day in range(DAYS):
    # ---- THE MARKET'S ONE RULE (Lesson 1) -----------------------------------
    # Each day the price gets nudged up or down by a small random "shock".
    # gauss(0, 1) means: usually a small nudge, occasionally a big one,
    # up just as often as down. Nobody knows tomorrow's shock. That is
    # the whole point of a market.
    shock = random.gauss(0, 1)
    price += shock
    # -------------------------------------------------------------------------
    history.append(price)


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


print(f"Start: ${history[0]:.2f}   End: ${history[-1]:.2f}   "
      f"High: ${max(history):.2f}   Low: ${min(history):.2f}")
print(ascii_chart(history))
print(" " * 9 + "+" + "-" * 60)
print(" " * 10 + f"day 0{' ' * 49}day {DAYS}")


# -----------------------------------------------------------------------------
# TRY IT (exercises)
# -----------------------------------------------------------------------------
# 1. Change random.seed(7) to random.seed(1). Different market, same rules.
# 2. Make the shocks bigger: random.gauss(0, 3). What happens to High/Low?
# 3. Add a "drift": price += shock + 0.1  (a tiny up-bias every day). Run it a
#    few seeds. Does the stock usually end higher now? This is roughly why
#    the stock market tends to rise over decades.
# 4. Print history[10] — what was the price on day 10?
