"""
LESSON 7 — Risk & position sizing: don't blow up (Track 1: trading on capital.com)

You can now go long or short (L3), read your equity (L4), use leverage (L5) and
fire real order types with a stop-loss (L6). One huge question is still open:

    HOW MUCH do you bet on each trade?

Beginners obsess over WHAT to buy. Professionals obsess over HOW MUCH. It turns
out the second question matters MORE — you can have a genuine winning edge and
still go broke if you bet too big, because a bad run of losses can wipe you out
before the edge ever pays off. This is "risk of ruin", and the math is brutal.

The fix is boringly simple and it's what this lesson adds to market.py:

    FIXED-FRACTIONAL SIZING — risk a small fixed fraction R of your equity
    (say 1–2%) on every trade.

You decide WHERE you'll bail out (the stop), which is a distance D in price
units away from your entry. Then you size the position so that if the stop is
hit you lose exactly R% of equity:

    qty = risk_frac * equity / stop_distance

That's it. A wider stop => fewer units (same dollars at risk). A bigger account
=> bigger size (you scale with equity). You never risk the dollar amount that
ruins you.

Run it:  python3 07_risk.py
Then read 07_walkthrough.md.

Reference: Van K. Tharp, *Trade Your Way to Financial Freedom* (position sizing
& expectancy — "how much" beats "what").
"""

import random
from statistics import median


# ---------------------------------------------------------------------------
# PART A — sizing from a stop: same dollar risk, different share counts
# ---------------------------------------------------------------------------
# You have $10,000 and decide to risk 2% of it ($200) on a trade. WHERE you put
# the stop decides how many units you can hold. Risk dollars are fixed; the
# share count falls out of the stop distance.
#
#     qty = risk_frac * equity / stop_distance
#
# A tight stop (price barely has to move against you to bail) lets you hold a
# big position for the same $200. A wide stop forces a small position. Either
# way, hitting the stop costs the SAME $200 — that's the whole point.

equity = 10_000.0
risk_frac = 0.02
risk_dollars = risk_frac * equity

print("PART A — position size from a fixed risk budget")
print(f"   equity ${equity:,.0f}, risking {risk_frac:.0%} = ${risk_dollars:,.0f} per trade\n")
print("   stop distance   qty (units)   $ at risk if stopped")
for stop_distance in (0.50, 1.00, 2.00, 5.00):
    qty = int(risk_dollars / stop_distance)        # the market.py line
    at_risk = qty * stop_distance
    print(f"   ${stop_distance:>5.2f}        {qty:>6d}        ${at_risk:,.2f}")
print("\n   Wider stop -> smaller size. The risk in DOLLARS is held constant —")
print("   only the share count changes. You size to the stop, not to a hunch.\n")


# ---------------------------------------------------------------------------
# PART B — Monte Carlo: the SAME edge, two bet sizes, very different fates
# ---------------------------------------------------------------------------
# Here's the part that should scare you. We play a simple betting game with a
# REAL positive edge: each trade, you win +1x your stake 52% of the time and
# lose your stake 48% of the time. On average you make money every bet.
#
# But "on average" hides the path. We run the game 2000 times for each bet
# size. The only difference between the two sizers is HOW MUCH of equity they
# put on each trade: 2% vs 25%. Same edge, same number of trades, same coin.
#
# Watch what over-betting does: even with a winning game, the 25% sizer hits a
# run of losses that craters equity so far it can't recover. The 2% sizer
# rarely gets near zero and compounds steadily.

random.seed(7)

WIN_PROB = 0.52        # slight edge: win a hair more than half the time
PAYOFF = 1.0           # win +1x the amount risked, lose 1x (symmetric)
N_TRADES = 200         # trades per run
N_RUNS = 2000          # how many parallel "traders" we simulate
RUIN_LEVEL = 0.20      # below 20% of starting equity = effectively ruined


def run_game(risk_frac):
    """One trader: bet a fixed fraction of CURRENT equity each trade."""
    eq = 1.0
    for _ in range(N_TRADES):
        stake = risk_frac * eq                     # fraction of current equity
        if random.random() < WIN_PROB:
            eq += stake * PAYOFF
        else:
            eq -= stake
        if eq <= 0:                                 # wiped out, can't continue
            return 0.0
    return eq


def summarize(risk_frac):
    ends = [run_game(risk_frac) for _ in range(N_RUNS)]
    survived = sum(1 for e in ends if e > RUIN_LEVEL)
    return ends, survived / N_RUNS, median(ends)


print("PART B — Monte Carlo: same 52% edge, 200 trades, 2000 runs each")
print(f"   win {WIN_PROB:.0%} (+{PAYOFF:.0f}x) / lose {1-WIN_PROB:.0%} (-1x); start equity = 1.00")
print(f"   'survived' = ended above {RUIN_LEVEL:.0%} of start\n")
print("   bet size   survival rate   median ending equity")
for rf in (0.02, 0.25):
    _, survival, med = summarize(rf)
    print(f"   {rf:>5.0%}        {survival:>7.1%}         {med:>8.2f}x")
print("\n   The 2% sizer almost always survives and grows. The 25% sizer — with")
print("   the IDENTICAL winning edge — busts most of the time. Bet size, not the")
print("   edge, decided who lived. Over-betting turns a winning game into ruin.\n")


# ---------------------------------------------------------------------------
# PART C — the drawdown trap: losses and gains are not symmetric
# ---------------------------------------------------------------------------
# Why is over-betting so deadly? Because recovering from a loss takes a BIGGER
# gain than the loss itself. Lose 50% and you're not "halfway back" after +50%
# — you need +100% just to break even. The hole gets exponentially steeper.
#
#     gain needed = loss / (1 - loss)
#
# Big bets create big drawdowns; big drawdowns need heroic gains to undo. This
# is the arithmetic that makes capital preservation rule #1.

print("PART C — gain needed to recover a drawdown (the math is merciless)")
print("   drawdown   gain needed to get back to even")
for dd in (0.10, 0.20, 0.50, 0.75, 0.90):
    gain = dd / (1 - dd)
    print(f"   -{dd:>4.0%}       +{gain:>5.0%}")
print("\n   Down 50% needs +100%. Down 90% needs +900%. A trader who risks small")
print("   stays in the shallow end where recovery is easy; the one who swings big")
print("   eventually digs a hole too deep to climb out of — even while 'right'.\n")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. In Part A, drop risk_frac to 0.01 (1%). Every share count halves, but the
#    dollars at risk per trade halve too. Sizing scales cleanly with your rule.
# 2. In Part B, try risk_frac values 0.05, 0.10, 0.40. Find roughly where the
#    survival rate falls off a cliff. There's a sizing beyond which a winning
#    edge can't save you — that's the "risk of ruin" threshold.
# 3. In Part B, set WIN_PROB = 0.48 (a LOSING game) and run both sizers. Now
#    even 2% bleeds out — sizing controls how fast you lose, not whether you do.
#    Sizing manages a real edge; it can't manufacture one.
# 4. Open ../market.py — the live loop sizes every entry with exactly this rule:
#    qty = int(risk_frac * equity / stop_distance). It's this lesson, wired in.
