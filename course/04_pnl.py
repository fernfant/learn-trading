"""
LESSON 4 — P&L & equity: what are you worth? (Track 1: trading on capital.com)

You can open a long or a short now (Lesson 3). But "am I up or down?" needs real
bookkeeping. capital.com shows you two numbers that beginners confuse constantly:

    BALANCE — your settled cash. Only changes when you CLOSE a trade.
    EQUITY  — balance PLUS the live value of whatever you're still holding.

The bridge between them is your open position's profit, and it comes in two
flavours:

    UNREALIZED P&L — paper profit on a position you still hold. It moves every
                     tick. It is NOT money yet — you haven't locked it in.
    REALIZED P&L   — what you actually keep when you close. Now it's cash.

The one formula that ties it all together, and the line you add to market.py:

    equity = cash + position * price

Run it:  python3 04_pnl.py
Then read 04_walkthrough.md.
"""

SPREAD = 0.10
START_CASH = 2000.0


def quote(mid):
    return mid + SPREAD / 2, mid - SPREAD / 2     # buy (ask), sell (bid)


# ---------------------------------------------------------------------------
# PART A — opening a long spends cash; equity reveals the spread instantly
# ---------------------------------------------------------------------------
cash = START_CASH
position = 0
mid = 100.0
buy, sell = quote(mid)

# Go long 10: you BUY 10 at the ask, so cash leaves your account.
position += 10
entry = buy
cash -= position * entry                 # paid 10 x 100.05 = 1000.50

# Mark to market: a long could only CLOSE at the sell, so we value it there.
mark = sell
equity = cash + position * mark          # <-- the Lesson 4 line
print("Open LONG 10 @ $100.05")
print(f"   balance (cash) : ${cash:.2f}")
print(f"   position value : {position} x ${mark:.2f} = ${position * mark:.2f}")
print(f"   equity         : ${equity:.2f}")
print(f"   unrealized P&L : ${equity - START_CASH:+.2f}   "
      f"(down a full spread the instant you open)\n")


# ---------------------------------------------------------------------------
# PART B — equity moves with the price; balance does not
# ---------------------------------------------------------------------------
# Walk the mid up and down. Balance is frozen (trade still open); equity breathes.
print("Holding the long. Balance stays put; equity tracks the price:")
print("   mid     balance     equity   unreal P&L")
for mid in (100.0, 101.0, 102.0, 99.0, 103.0):
    buy, sell = quote(mid)
    mark = sell                          # long marks at the sell
    equity = cash + position * mark
    print(f"   {mid:6.2f}  ${cash:8.2f}  ${equity:8.2f}   ${equity - START_CASH:+7.2f}")
print("   ^ balance never moved — unrealized P&L is paper, not cash, until you close.\n")


# ---------------------------------------------------------------------------
# PART C — closing turns unrealized into realized (it lands in cash)
# ---------------------------------------------------------------------------
# Close at mid = 103: SELL 10 at the bid. Cash comes back in; position -> 0.
mid = 103.0
buy, sell = quote(mid)
close_price = sell                       # a long closes at the sell
equity_before = cash + position * close_price
cash += position * close_price           # sell the 10 units back into cash
realized = cash - START_CASH             # what you actually kept
position = 0
equity_after = cash + position * mid     # nothing held now, so equity == cash
print("Close the long: SELL 10 @ $102.95")
print(f"   equity just before close : ${equity_before:.2f}")
print(f"   balance (cash) now       : ${cash:.2f}")
print(f"   position                 : {position}  (flat)")
print(f"   equity now == balance    : ${equity_after:.2f}")
print(f"   REALIZED P&L             : ${realized:+.2f}")
print("Lesson: equity is the honest scoreboard — it already counts unrealized")
print("profit AND the spread you'd pay to get out. Balance only catches up when")
print("you close. In Lesson 5, leverage lets your position be far bigger than")
print("your cash — which is exactly when watching equity becomes survival.")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. In Part A, flip to a SHORT: position = -10, entry = sell, and mark = buy.
#    Note cash goes UP when you open (you sold first). Equity still drops a
#    spread. Does equity rise when the mid FALLS?
# 2. In Part C, close at mid = 100.0 instead. What's your realized P&L? (You
#    paid two half-spreads for nothing — a small loss.)
# 3. Compute return on equity: realized / START_CASH * 100. Tiny moves on a
#    small position barely register — foreshadowing why traders use leverage.
# 4. Open ../market.py — it now tracks cash, marks your position to market, and
#    prints your equity alongside the quote.
