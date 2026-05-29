# Lesson 6 — Order types: market, limit, stop, trailing, GSLO, take-profit

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`06_order_types.py`](06_order_types.py) ·
> interactive: [`html/lesson_06.html`](html/lesson_06.html)

Every trade so far filled **now, at the current price**. That's just one kind of
order — a **market** order. capital.com's order menu has six entries, and each
is a different answer to two questions: *when* should this fill, and *at what
price am I willing to take?* Picking the right one is half of trading.

## The menu, in one table

| Order | When it fills | Price you get | Used for |
|---|---|---|---|
| **Market** | immediately | whatever's quoted now | get in/out now, no fuss |
| **Limit** | only at your price *or better* | your price or better | patient entries/exits |
| **Stop** | once a trigger price is crossed | the *next* market price | cut losses · breakout entries |
| **Trailing stop** | when price falls back by your distance | next market price | lock in a running profit |
| **Take-profit** | once a profit target is reached | your target (a limit) | bank a gain automatically |
| **GSLO** | like a stop, but **guaranteed** | *exactly* your trigger | gap insurance (for a fee) |

The honest punchline of the whole lesson is hidden in that table: a **stop only
promises to *fire*, not to fill at its price**. The script proves it.

## Part A — market vs limit: the speed/price trade-off

It's day 0, mid \$100.00, and you want to go long.

```
day 0: market BUY fills immediately at the ask $100.05
LIMIT buy @ 98.50 -> filled day 9 (ask $97.50)
```

A **market** buy fills the instant you click, at the ask (\$100.05). Guaranteed
fill, zero price control. A **limit** buy at \$98.50 says "I'll only pay 98.50 or
*less*." It sat unfilled while the price climbed, and only triggered on day 9
when the market gapped down — filling at \$97.50, a much better entry.

The catch: a limit **might never fill**. If the dip hadn't come, you'd have
watched the trade go without you. Limit = price control, no guarantee. Market =
guarantee, no price control. That's the whole trade-off.

## Part B — bracket a long with take-profit + stop-loss

Once you're long (entry \$100.05) you can attach two resting orders that the
platform checks every day, so the trade manages itself while you sleep:

```
TP at mid 102.50, SL at mid 98.00
day 3: mid 103.00 hit TAKE-PROFIT -> sell @ 102.95, P&L $+29.00
```

The **take-profit** is a limit sell above you; the **stop-loss** is a stop sell
below you. Whichever the price reaches first wins. Here the market rose, the
take-profit fired on day 3, and \$29.00 of profit was banked automatically. Had
it fallen instead, the stop-loss would have capped the damage. Two triggers,
one of which will fire — your trade is now on autopilot.

## Part C — a stop *entry* (breakout) and a trailing stop

A stop isn't only for losses. Place a **buy stop** *above* the current price and
it only triggers if the market breaks out upward — a momentum entry:

```
day 1: mid 100.57 >= 100.50 -> STOP entry, buy @ 100.62
        trailing stop starts at 99.07 (high 100.57 - 1.50)
day 2: mid 101.59 new high -> trail ratchets up to 100.09
day 3: mid 103.00 new high -> trail ratchets up to 101.50
day 4: mid 103.90 new high -> trail ratchets up to 102.40
day 5: mid 101.67 <= trail 102.40 -> sell @ 101.62, P&L $+10.00 (gain locked)
```

The **trailing stop** sits a fixed distance (\$1.50) below the highest price seen
so far. As the market climbs to a new high, the stop **ratchets up** with it —
but it **never moves back down**. When the price finally pulled back through it
on day 5, we exited at \$101.62 with a \$10.00 profit *locked in*. A plain
stop-loss left at the entry would have given all of that back.

## Part D — the honest part: stops slip on gaps, GSLOs don't

This is the lesson capital.com's risk warnings are really about. You're long
from \$100.05 with a stop-loss at \$98.00. On most days the price drifts through
98.00 and you fill right about there. But markets **gap** — they jump overnight
on news, skipping prices entirely:

```
day 8 mid 103.11 -> day 9 mid 97.45 (gapped through 98.00)
PLAIN STOP : sell @ 97.40 (NOT 98.00!) -> P&L $-26.50
GSLO       : sell @ 98.00 exactly, minus $1.20 premium -> P&L $-21.70
the gap cost the plain stop $6.00 of extra slippage; the GSLO cost $1.20.
```

The plain stop *triggered* at 98.00 — but a stop only becomes a **market order**
when it fires, and the next available price was \$97.40. That extra \$6.00 loss is
**slippage**. A **GSLO** (guaranteed stop) fills at *exactly* 98.00 no matter how
violent the gap, in exchange for a premium (\$1.20) paid up front. On a calm day
the premium is wasted; on a gap day it's cheap insurance. There's no free lunch —
just a choice about who carries the gap risk, you or the broker.

## What you built in `market.py`

In [`../market.py`](../market.py), each day we now **check triggers** — a
stop-loss and a take-profit that close the position when the mark crosses them.
It's the same per-day check the script does in Part B, folded into the main loop:
before, the position only changed when *you* acted; now the market itself can
close you out at a level you set in advance. That single idea — *resting orders
the platform watches for you* — is what every order type on the menu is built on.

## How this shows up on capital.com

- The order ticket has a **Market / Limit** toggle, plus optional **Stop loss**,
  **Take profit**, and **Guaranteed stop** boxes you tick when you open.
- A **trailing stop** is a checkbox on the stop-loss: set a distance and it
  follows the price for you.
- The **GSLO premium** is shown before you confirm; you only pay it *if it
  triggers* on some products, or up front on others — always read the ticket.
- Stops are **not guaranteed** unless you pick the GSLO. The slippage in Part D
  is exactly why that checkbox exists.

## Try it (in [`06_order_types.py`](06_order_types.py))

1. In Part A, lower `limit_px` to `96.00`. Does the limit ever fill now? A limit
   that's too greedy just sits there forever — control, but no fill.
2. In Part B, set `tp_px = 101.50`. Does the take-profit fire sooner? Tightening
   a target makes it more likely to hit, but for a smaller gain.
3. In Part C, shrink `trail_dist` to `0.50`. A tight trail locks more profit but
   gets knocked out by tiny wiggles. Loosen it to `3.0` and compare.
4. In Part D, change the day-`GAP_DAY` drift from `-5.60` to `-1.0` (a normal
   day). Now the stop and GSLO fill the same — the premium was wasted. The
   guarantee only pays off when a gap actually happens.

---

**Next:** [Lesson 7 — Risk & position sizing: don't blow up](07_position_sizing.py)
— the order types decide *how* you get in and out; position sizing decides *how
much* to bet so a single bad gap can't end your account.
