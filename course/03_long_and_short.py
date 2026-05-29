"""
LESSON 3 — Your first trade: long AND short (Track 1: trading on capital.com)

So far we only watched a price. Now we TAKE one. On capital.com you trade CFDs
("contracts for difference") — you don't own the share, you just hold a bet on
which way its price moves. That bet has a DIRECTION:

    LONG  (you BUY first)  — you profit if the price goes UP.
    SHORT (you SELL first) — you profit if the price goes DOWN.

Short is the surprising one: you can sell something you never owned, then buy it
back cheaper. CFDs make falling prices just as tradeable as rising ones.

We track the bet as a single signed number, the POSITION:

    position > 0  -> long   (e.g. +10 units)
    position < 0  -> short  (e.g. -10 units)
    position == 0 -> flat   (no bet)

And the rule that haunts every trade is still here: you OPEN on the bad side of
the spread and CLOSE on the other bad side, so you pay the full spread either way.

Run it:  python3 03_long_and_short.py
Then read 03_walkthrough.md.
"""

import random

SPREAD = 0.10


def quote(mid):
    return mid + SPREAD / 2, mid - SPREAD / 2   # buy (ask), sell (bid)


# ---------------------------------------------------------------------------
# PART A — a LONG trade: buy low(er), sell high(er)
# ---------------------------------------------------------------------------
# You go long 10 units. You OPEN by BUYING at the ask. Later you CLOSE by
# SELLING at the bid. Profit when the mid has risen by more than the spread.
qty = 10
entry_mid = 100.0
buy, sell = quote(entry_mid)
entry_price = buy                      # long opens at the BUY price
print("LONG 10 units")
print(f"   open : buy  {qty} @ ${entry_price:.2f}")

exit_mid = 103.0                       # the market rose $3
xbuy, xsell = quote(exit_mid)
exit_price = xsell                     # long closes at the SELL price
pnl = qty * (exit_price - entry_price)
print(f"   close: sell {qty} @ ${exit_price:.2f}   (mid {entry_mid:.0f} -> {exit_mid:.0f})")
print(f"   P&L  : {qty} x ({exit_price:.2f} - {entry_price:.2f}) = ${pnl:+.2f}")
print(f"   note : mid rose $3.00 but you made ${pnl:.2f} — the spread ate $1.00.\n")


# ---------------------------------------------------------------------------
# PART B — a SHORT trade: sell high(er), buy back low(er)
# ---------------------------------------------------------------------------
# Same market, opposite bet. You go short 10 units (position = -10). You OPEN by
# SELLING at the bid, and CLOSE by BUYING back at the ask. Profit when the mid
# FALLS by more than the spread.
qty = -10
entry_mid = 100.0
buy, sell = quote(entry_mid)
entry_price = sell                     # short opens at the SELL price
print("SHORT 10 units")
print(f"   open : sell {abs(qty)} @ ${entry_price:.2f}")

exit_mid = 97.0                        # the market fell $3
xbuy, xsell = quote(exit_mid)
exit_price = xbuy                      # short closes at the BUY price
pnl = qty * (exit_price - entry_price)
print(f"   close: buy  {abs(qty)} @ ${exit_price:.2f}   (mid {entry_mid:.0f} -> {exit_mid:.0f})")
print(f"   P&L  : {qty} x ({exit_price:.2f} - {entry_price:.2f}) = ${pnl:+.2f}")
print(f"   note : the price FELL and you still made money — that's a short.\n")


# ---------------------------------------------------------------------------
# PART C — same wandering market, opposite bets are mirror images
# ---------------------------------------------------------------------------
# One signed formula covers both directions:
#
#     open  on the side you cross (long->buy, short->sell)
#     close on the other side
#     pnl = position * (exit_price - entry_price)
#
# Let one random market run and mark BOTH a long and a short to market each day.
# Their P&Ls are near-mirror images — but BOTH start underwater by a spread.
random.seed(7)
mid = 100.0
buy, sell = quote(mid)
long_entry, short_entry = buy, sell           # open both at day 0
print("Same market, +10 long vs -10 short, marked to market daily:")
print("   day    mid   long P&L   short P&L")
for day in range(1, 8):
    mid += random.gauss(0, 1)
    buy, sell = quote(mid)
    long_pnl = 10 * (sell - long_entry)        # close a long at the SELL
    short_pnl = -10 * (buy - short_entry)      # close a short at the BUY
    print(f"   {day:3d} {mid:7.2f}  {long_pnl:+8.2f}  {short_pnl:+9.2f}")

print("\nWhen the mid rises the long wins and the short loses, and vice versa —")
print("near-mirror images. But notice neither starts at 0: each opened a full")
print("spread underwater, so the two P&Ls sum to MINUS two spreads, not zero.")
print("Direction picks WHICH way you need the")
print("market to move; the spread is the toll you pay EITHER way.")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. In Part A, set exit_mid = 100.05. Did the long break even? (You need the
#    mid to rise a FULL spread, to 100.10, just to get back to zero.)
# 2. In Part C, make the market drift down: random.gauss(-0.3, 1). Which bet
#    wins now? This is why shorts exist — money to be made when things fall.
# 3. Flip Part B to a WINNING short that then reverses: set exit_mid = 101.0.
#    A short loses when the price rises — your risk is theoretically unlimited.
# 4. Open ../market.py — it now carries a signed `position` you open on day 0.
