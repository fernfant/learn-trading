"""
LESSON 5 — Leverage & margin: the double-edged sword (Track 1: capital.com)

You have $1000. A share costs $100. Without help you can hold 10 of them. But on
capital.com you can put down a small deposit — the MARGIN — and the broker fronts
the rest, letting you control a much BIGGER position. That is LEVERAGE.

    NOTIONAL = how big your position really is = |position| × price
    MARGIN   = the slice of cash the broker locks up   = notional / leverage

At 10x leverage, $1000 of margin controls $10,000 of notional. Sounds great —
until you remember the catch:

    leverage multiplies your gains AND your losses, measured against YOUR cash.

A 2% move on $10,000 is $200. On a 1x ($1000) position that's a 2% dent. But you
only put up $100 of margin at 100x — so the SAME $200 swing is twice your deposit.
The market barely twitched and you're wiped out.

capital.com watches one number all day, the MARGIN LEVEL:

    margin level = equity / used_margin   (as a %)

- 100% means your equity exactly equals the margin you've locked up.
- Below ~100% you get a MARGIN CALL warning (capital.com warns at 75% / 100%).
- At 50% the platform FORCE-CLOSES your trade — the "STOP-OUT". It doesn't ask.

This lesson makes that danger concrete. Leverage isn't free money; it's the same
bet with the volume turned up on both the wins and the losses.

Run it:  python3 05_leverage_margin.py
Then read 05_walkthrough.md.
"""

import random

START_CASH = 1000.0
PRICE = 100.0
QTY = 50                 # we'll hold 50 units throughout — a $5,000 position


# ---------------------------------------------------------------------------
# PART A — notional vs required margin at different leverages
# ---------------------------------------------------------------------------
# We hold the SAME 50-unit position the whole time. Its notional value never
# changes (50 × $100 = $5,000). What changes with leverage is how little of YOUR
# cash the broker makes you lock up to hold it.
notional = QTY * PRICE
print(f"Holding {QTY} units @ ${PRICE:.2f}  ->  notional = ${notional:,.2f}\n")
print("   leverage   margin required   % of your $1,000")
print("   --------   ---------------   ----------------")
for lev in (1, 5, 20):
    margin = notional / lev
    print(f"   {lev:4d}x      ${margin:11,.2f}     {margin/START_CASH*100:6.1f}%")
print()
print("At 1x you must fund the whole $5,000 — but you only HAVE $1,000, so 1x")
print("can't even open this trade. Leverage is what lets a small account hold a")
print("big position: at 20x the same position locks up just $250.\n")


# ---------------------------------------------------------------------------
# PART B — the same price move hurts more at higher leverage
# ---------------------------------------------------------------------------
# Now let the price fall a fixed 2%. The dollar loss is identical at every
# leverage — it only depends on the position, not the margin. But measured as a
# % of the MARGIN you put up, that same loss balloons as leverage rises.
move = -0.02                         # a small 2% dip
loss = QTY * (PRICE * move)          # dollars lost on the position (same for all)
print(f"The price falls {move*100:.0f}%  ->  position loses ${abs(loss):,.2f} (same at every leverage)")
print("   leverage   margin put up   loss vs that margin   what happens")
print("   --------   -------------   -------------------   ------------")
for lev in (1, 5, 20):
    margin = notional / lev
    pct = loss / margin * 100        # loss as a % of YOUR locked-up cash
    fate = "barely a scratch" if abs(pct) < 25 else "ouch" if abs(pct) < 60 else "MARGIN WIPED"
    print(f"   {lev:4d}x      ${margin:9,.2f}      {pct:7.1f}%           {fate}")
print()
print("Identical market move. At 1x it's a rounding error; at 20x that one 2% dip")
print("erased 40% of your margin. The bet didn't change — the volume knob did.\n")


# ---------------------------------------------------------------------------
# PART C — a leveraged position under a random walk, until STOP-OUT
# ---------------------------------------------------------------------------
# Now bet big: a 180-unit long at 20x. Notional is $18,000, so the broker locks
# up $900 of your $1,000 as margin — almost everything. Only $100 of free equity
# cushions the bet. Each day the price wanders and we track:
#     equity       = cash + position value   (your live net worth, Lesson 4)
#     used_margin  = |position| × price / leverage   (recomputed as price moves)
#     margin level = equity / used_margin     (the number capital.com watches)
# When margin level falls to 50%, capital.com FORCE-CLOSES the trade — the
# "stop-out". It doesn't ask, and you don't get the cushion back.
random.seed(0)
LEV = 20
position = 180
entry = PRICE
big_notional = position * entry
# We track cash as your full balance and mark the position to price (Lesson 4):
# the whole notional is debited from cash, and the position value adds it back,
# so equity starts at your real $1,000.
cash = START_CASH - position * entry
print(f"Open: LONG {position} @ ${entry:.2f} at {LEV}x  "
      f"(notional ${big_notional:,.0f}, margin ${big_notional/LEV:,.0f} of your $1,000)")
print("   day    price    equity   used_margin   margin level")
print("   ---  -------   -------   -----------   ------------")
price = PRICE
blew_up = None
for day in range(1, 21):
    price += random.gauss(0, 1.4)             # the market wanders (Lesson 1)
    equity = cash + position * price          # net worth right now (Lesson 4)
    used_margin = abs(position) * price / LEV # margin scales with notional
    level = equity / used_margin * 100        # the watched ratio, as a %
    flag = ""
    if level < 100:
        flag = "  <- margin call zone"
    if level <= 50:
        flag = "  <- STOP-OUT! force-closed"
        blew_up = day
    print(f"   {day:3d}  ${price:6.2f}   ${equity:7.2f}      ${used_margin:7.2f}      {level:6.1f}%{flag}")
    if blew_up:
        break

if blew_up:
    print(f"\nForce-closed on day {blew_up}. The price only slipped from $100.00 to "
          f"${price:.2f} —")
    print(f"a mere {(price-PRICE)/PRICE*100:.1f}% drift — yet at 20x that thin $100 cushion was")
    print("gone, and capital.com closed you out near a total loss. That is the")
    print("double-edged sword: high leverage means a tiny move decides everything.")
else:
    print("\nSurvived 20 days this time — but at 20x you were always one bad run away.")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. In Part C, set LEV = 5. The same 180-unit position now needs $3,600 margin —
#    which you can't fund. Drop position to 40 instead: margin is $200, free
#    equity is $800, and the stop-out never comes in 20 days. More cushion, more
#    room to be wrong.
# 2. Set LEV = 1 AND position = 8 (so $800 notional fits your $1,000). Now
#    used_margin == notional and a gentle wander never trips the 50% line —
#    1x can't margin-call you on a small move. Safety has a name: less leverage.
# 3. Keep position = 180 but crank LEV = 30, then re-run. Count how few days you
#    last. Then change the seed (random.seed(1), random.seed(7)) a few times —
#    sometimes you survive, mostly you don't.
# 4. Open ../market.py — it now computes `margin = abs(position)*price/leverage`
#    each day and force-closes the position if equity drops below 50% of it.
