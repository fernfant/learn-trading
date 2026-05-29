"""
LESSON 6 — Order types (Track 1: trading on capital.com)

Up to now every trade filled "now, at the current price." That's only ONE kind
of order — a MARKET order. Real platforms (capital.com included) give you a menu
of orders that fill on YOUR terms, or only when the market reaches a price you
named. Each one is a different answer to: "WHEN should this fill, and at WHAT
price am I willing to take?"

The menu we'll meet:

    MARKET        fills immediately at whatever's quoted now. No price control.
    LIMIT         fills only at your price or BETTER. Control — but may never fill.
    STOP          a price trigger: once crossed it becomes a MARKET order.
                  Used to CUT LOSSES, or to ENTER on a breakout.
    TRAILING STOP a stop that follows price in your favour, ratcheting up to
                  lock in profit; it never moves back the other way.
    TAKE-PROFIT   auto-closes the position once a profit target is reached.
    GSLO          "guaranteed stop": fills at EXACTLY your trigger even on a
                  gap, for a small premium. A plain stop can fill WORSE.

The big honest idea this lesson: a STOP only promises to TURN INTO a market
order — it does NOT promise your price. If the market gaps past it overnight,
you fill at the next available price, which can be much worse (slippage). A GSLO
removes that risk — but you pay for the insurance whether or not you use it.

Run it:  python3 06_order_types.py
Then read 06_walkthrough.md.
"""

import random

SPREAD = 0.10


def quote(mid):
    return mid + SPREAD / 2, mid - SPREAD / 2   # buy (ask), sell (bid)


# ---------------------------------------------------------------------------
# A reproducible price path. We seed the RNG (house rule) but steer the story:
# the market climbs into a peak (so the breakout + trailing stop in Part C fire
# and lock a PROFIT on a normal pullback), drifts, then GAPS DOWN hard on day 9
# — that's where the stop slippage in Part D shows up. Each day's move is a
# fixed "drift" plus a small seeded jitter, so the shape is always the same and
# the walkthrough's numbers match exactly.
# ---------------------------------------------------------------------------
random.seed(6)
GAP_DAY = 9
drift = [0.55, 1.10, 1.45, 0.90, -2.30, 0.40, 0.60, 0.50, -5.60, 0.30, -0.40, 0.70]
mid = 100.0
path = [mid]
for day, dft in enumerate(drift, start=1):
    jitter = random.gauss(0, 0.05)         # tiny noise; never disturbs the levels
    mid += dft + jitter
    path.append(round(mid, 2))

print("The price path we'll trade against (mid each day):")
print("   day  mid")
for d, m in enumerate(path):
    tag = "   <- big gap down" if d == GAP_DAY else ""
    print(f"   {d:3d} {m:7.2f}{tag}")
print()


# ---------------------------------------------------------------------------
# PART A — MARKET vs LIMIT entry
# ---------------------------------------------------------------------------
# It's day 0, mid = 100.00. You want to go long.
#   - A MARKET buy fills NOW at the ask (100.05). Guaranteed fill, no price say.
#   - A LIMIT buy at 98.50 fills ONLY if the ask drops to 98.50 or lower. You
#     get a better price IF it triggers — but it might never come.
print("PART A — entry: MARKET fills now, LIMIT waits for your price")
buy0, sell0 = quote(path[0])
print(f"   day 0: market BUY fills immediately at the ask ${buy0:.2f}")

limit_px = 98.50
limit_filled = None
for d in range(1, len(path)):
    ask, bid = quote(path[d])
    if ask <= limit_px:                    # ask reached our limit or better
        limit_filled = d
        print(f"   LIMIT buy @ {limit_px:.2f} -> filled day {d} (ask ${ask:.2f})")
        break
if limit_filled is None:
    print(f"   LIMIT buy @ {limit_px:.2f} -> NEVER filled (ask never fell that far)")
print("   lesson: the limit got you a better price — but only because the dip came.\n")


# ---------------------------------------------------------------------------
# PART B — once LONG: a TAKE-PROFIT above and a STOP-LOSS below
# ---------------------------------------------------------------------------
# Assume the market entry from Part A: long, entry at the ask 100.05.
# We bracket the trade with two resting orders that the platform checks daily:
#   TAKE-PROFIT at mid 102.50  -> close for a gain if we reach it
#   STOP-LOSS   at mid  98.00  -> close for a small loss if we fall through it
# Whichever the price hits FIRST wins. A long is marked/closed at the SELL.
print("PART B — bracket the long: take-profit above, stop-loss below")
entry = buy0
tp_px, sl_px = 102.50, 98.00
print(f"   long entry ${entry:.2f}; TP at mid {tp_px:.2f}, SL at mid {sl_px:.2f}")
closed = False
for d in range(1, len(path)):
    m = path[d]
    if m >= tp_px:
        ask, bid = quote(m)
        pnl = 10 * (bid - entry)
        print(f"   day {d}: mid {m:.2f} hit TAKE-PROFIT -> sell @ {bid:.2f}, P&L ${pnl:+.2f}")
        closed = True
        break
    if m <= sl_px:
        ask, bid = quote(m)
        pnl = 10 * (bid - entry)
        print(f"   day {d}: mid {m:.2f} hit STOP-LOSS -> sell @ {bid:.2f}, P&L ${pnl:+.2f}")
        closed = True
        break
if not closed:
    print("   neither trigger hit in the window — position still open")
print("   lesson: triggers let the trade manage itself while you're away.\n")


# ---------------------------------------------------------------------------
# PART C — a STOP entry (breakout) + a TRAILING STOP that ratchets
# ---------------------------------------------------------------------------
# A STOP isn't only for losses. Place a BUY stop ABOVE the price to enter only
# if the market breaks out upward (momentum traders love this). Once we're long,
# attach a TRAILING stop: it sits a fixed distance BELOW the high-water mark and
# only ever moves UP, locking in profit as the price climbs.
print("PART C — STOP entry (breakout) + a TRAILING stop that locks profit")
breakout = 100.50
trail_dist = 1.50
entered, entry_c, trail_stop, high = None, None, None, None
for d in range(1, len(path)):
    m = path[d]
    if entered is None:
        if m >= breakout:
            ask, bid = quote(m)
            entered = d
            entry_c = ask
            high = m
            trail_stop = m - trail_dist
            print(f"   day {d}: mid {m:.2f} >= {breakout:.2f} -> STOP entry, buy @ {ask:.2f}")
            print(f"           trailing stop starts at {trail_stop:.2f} (high {high:.2f} - {trail_dist:.2f})")
    else:
        if m > high:                       # new high -> ratchet the stop UP
            high = m
            new_stop = m - trail_dist
            if new_stop > trail_stop:
                trail_stop = new_stop
                print(f"   day {d}: mid {m:.2f} new high -> trail ratchets up to {trail_stop:.2f}")
        elif m <= trail_stop:              # pulled back to the stop -> exit
            ask, bid = quote(m)
            pnl = 10 * (bid - entry_c)
            print(f"   day {d}: mid {m:.2f} <= trail {trail_stop:.2f} -> sell @ {bid:.2f}, P&L ${pnl:+.2f} (gain locked)")
            break
        else:
            print(f"   day {d}: mid {m:.2f} drifting, trail holds at {trail_stop:.2f}")
if entered is None:
    print(f"   price never broke {breakout:.2f} — stop entry never fired")
print("   lesson: the trail only moves one way; it can't give back its locked gains.\n")


# ---------------------------------------------------------------------------
# PART D — the honest one: STOP slippage on a gap vs a GSLO
# ---------------------------------------------------------------------------
# You're long from 100.05 with a stop-loss at 98.00. Most days the price would
# touch 98.00 on its way down and you'd fill right about there. But day 9 GAPS:
# the mid leaps from path[GAP_DAY-1] straight to path[GAP_DAY], skipping 98.00.
#   - A PLAIN STOP becomes a market order at the OPEN after the gap — it fills at
#     the SELL price of the gapped mid, far below 98.00. That extra loss is
#     SLIPPAGE.
#   - A GSLO fills at EXACTLY 98.00 no matter the gap — but you paid a premium
#     up front for that guarantee.
print("PART D — gap day: a plain STOP slips, a GSLO does not")
entry = buy0
stop_trigger = 98.00
gslo_premium = 1.20                        # paid up front for the guarantee
print(f"   long entry ${entry:.2f}, stop trigger {stop_trigger:.2f}")
print(f"   day {GAP_DAY-1} mid {path[GAP_DAY-1]:.2f} -> day {GAP_DAY} mid {path[GAP_DAY]:.2f} (gapped through 98.00)")

askG, bidG = quote(path[GAP_DAY])
plain_fill = bidG                          # plain stop = market sell at the gapped bid
plain_pnl = 10 * (plain_fill - entry)
print(f"   PLAIN STOP : sell @ {plain_fill:.2f} (NOT 98.00!) -> P&L ${plain_pnl:+.2f}")

gslo_fill = stop_trigger                   # GSLO honours the exact trigger
gslo_pnl = 10 * (gslo_fill - entry) - gslo_premium
print(f"   GSLO       : sell @ {gslo_fill:.2f} exactly, minus ${gslo_premium:.2f} premium -> P&L ${gslo_pnl:+.2f}")
slip = 10 * (stop_trigger - plain_fill)
print(f"   the gap cost the plain stop ${slip:.2f} of extra slippage; the GSLO cost ${gslo_premium:.2f}.")
print("   lesson: a stop promises to FIRE, not to fill at its price. GSLO buys that promise.\n")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. In PART A, lower limit_px to 96.00. Does the limit ever fill now? A limit
#    that's too greedy just sits there forever — control, but no fill.
# 2. In PART B, set tp_px = 101.50. Does the take-profit fire BEFORE the stop?
#    Tightening a target makes it more likely to hit — but for a smaller gain.
# 3. In PART C, shrink trail_dist to 0.50. A tight trail locks more profit but
#    gets knocked out by tiny wiggles. Loosen it to 3.0 and compare.
# 4. In PART D, change the day-5 gap in the path builder to -1.0 (a normal day).
#    Now the stop and GSLO fill the same — the GSLO premium was wasted. The
#    guarantee only pays off when a gap actually happens.
