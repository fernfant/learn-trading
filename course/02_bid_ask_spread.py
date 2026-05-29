"""
LESSON 2 — Bid, ask & the spread (Track 1: trading on capital.com)

In Lesson 1 we pretended a stock had one price. It doesn't. Open capital.com
(or almost any broker) and you see TWO prices for the same thing:

    a SELL price (the "bid")  — what you get if you sell
    a BUY  price (the "ask")  — what you pay if you buy

The BUY is always a little higher than the SELL. The gap between them is the
SPREAD, and it is the first cost you will ever pay — before any strategy, before
any fees. This lesson makes you feel that cost.

Run it:  python3 02_bid_ask_spread.py
Then read 02_walkthrough.md.
"""

import random

random.seed(7)

# capital.com quotes prices around a hidden "mid" (the fair price in the middle).
SPREAD = 0.10
mid = 100.0
buy = mid + SPREAD / 2     # ask — you BUY here (the higher one)
sell = mid - SPREAD / 2    # bid — you SELL here (the lower one)

print("THE QUOTE capital.com shows you")
print(f"   SELL  ${sell:.2f}   <- you get this if you sell")
print(f"   mid   ${mid:.2f}    (fair price, halfway — you can NOT trade here)")
print(f"   BUY   ${buy:.2f}    <- you pay this if you buy")
print(f"   spread = BUY - SELL = ${buy - sell:.2f}\n")

# ---------------------------------------------------------------------------
# PART A — the instant round-trip: buy, then immediately sell
# ---------------------------------------------------------------------------
# You buy one unit and, a split second later (price hasn't moved), sell it back.
paid = buy
got = sell
print("Round-trip with NO price move (buy, then instantly sell back):")
print(f"   you pay  ${paid:.2f} to buy")
print(f"   you get  ${got:.2f} to sell")
print(f"   result   ${got - paid:+.2f}   <- you lost the whole spread\n")

# ---------------------------------------------------------------------------
# PART B — the spread is a hurdle the price must clear
# ---------------------------------------------------------------------------
# Go long at the BUY price. To get out you must SELL (at the bid). So the mid
# has to climb by a full spread before your exit price even reaches what you
# paid. Let's watch a wandering mid and see when a long FINALLY breaks even.
random.seed(7)
mid = 100.0
entry_buy = mid + SPREAD / 2
print(f"You go long at BUY ${entry_buy:.2f}. Now you wait...")
days_to_breakeven = None
for day in range(1, 16):
    mid += random.gauss(0, 1)
    exit_sell = mid - SPREAD / 2          # what you'd get if you closed today
    pnl = exit_sell - entry_buy           # profit/loss per unit
    flag = ""
    if pnl > 0 and days_to_breakeven is None:
        days_to_breakeven = day
        flag = "  <- finally above water!"
    print(f"   day {day:2d}: mid {mid:6.2f}  exit-sell {exit_sell:6.2f}  P&L {pnl:+5.2f}{flag}")

if days_to_breakeven:
    print(f"\nEven though the mid rose, you sat at a LOSS until day "
          f"{days_to_breakeven}, purely because of the spread.")
else:
    print("\nThe mid never rose enough to clear the spread — you'd still be down.")
print("Lesson: every trade starts in the red by the spread. The price must move")
print("YOUR way by more than the spread just to break even. In Track 2 you'll be")
print("on the other side — the one who COLLECTS this spread.")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. Set SPREAD = 1.00 and re-run. Does the long ever break even in 15 days?
#    Wide spreads make short-term trading much harder.
# 2. Set SPREAD = 0.02 (a tight, liquid market). Now how fast do you break even?
# 3. Change the entry to a SHORT: entry_sell = mid - SPREAD/2, and pnl =
#    entry_sell - (mid + SPREAD/2). A short profits when the mid FALLS.
# 4. Open ../market.py — the same two prices, quoted fresh every day.
