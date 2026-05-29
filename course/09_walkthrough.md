# Lesson 9 — Costs that kill: spread + overnight funding + slippage

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`09_costs.py`](09_costs.py) ·
> interactive: [`html/lesson_09.html`](html/lesson_09.html)

You have a signal now (Lesson 8). On paper it makes money. So why does
capital.com's own regulator-mandated warning say the **large majority of retail
CFD accounts lose money?** This is the lesson the whole honesty theme has been
walking toward, and the answer is blunt: **costs decide who wins.** Three quiet
costs, none dramatic alone, that a "gross" backtest never shows you.

## The three quiet costs

| Cost | What it is | When you pay it |
|---|---|---|
| **Spread** | the gap between Buy and Sell (Lesson 2) | a *full* spread per round trip — half on open, half on close |
| **Overnight swap** | a daily funding charge for holding a leveraged position past the cutoff | every day you're still holding |
| **Slippage** | a market order fills a hair *worse* than the quoted price | on every fill — twice per round trip |

Each one is small. The point of this lesson is what happens when you **stack
them**.

## Part A — peel the costs off, one layer at a time

We don't model a fancy signal here. We just *grant* ourselves a small, real
edge — `gauss(EDGE, WOBBLE)` per round trip, a positive average with noise —
and trade it 40 times. Then we admit one more real cost per row, on the
**exact same 40 trades**, and watch equity sink:

```
  cost layer                    final equity
  0. gross (no costs)               2,710.59
  1. + spread (per round trip)      2,310.59
  2. + overnight swap (per day)     2,070.59
  3. + slippage (per fill)          1,830.59
```

Read it top to bottom. The strategy is genuinely good *gross*: it turns \$2,000
into \$2,710.59, a **+\$710.59** profit. Then:

- **Spread** (\$0.10 × 100 units × 40 trips = \$400) drops it to \$2,310.59.
- **Overnight swap** (\$0.02 × 100 × 3 days × 40 = \$240) drops it to \$2,070.59.
- **Slippage** (\$0.03 × 100 × 2 fills × 40 = \$240) drops it to \$1,830.59.

Costs ate **\$880.00** total and flipped a **+\$710.59 winner into a −\$169.41
loser.** Nothing about the edge changed — only the costs we were honest about.

The script also prints an ASCII bar so you can *see* the bar slide from deep
green (gross) down across the start line into red (net). That picture is the
whole lesson.

## Part B — frequency is a multiplier on the spread

The spread is paid **per round trip**. So the same total edge, chopped into
more trades, pays the toll more times. Here we hold the *total gross edge*
fixed at \$720 and only change how many trades we slice it into:

```
  plan                    trips   spread paid    net equity
  trade rarely                5           50       2,610.00
  trade often               100        1,000         520.00
```

Identical gross edge. The patient 5-trade plan keeps almost all of it. The busy
100-trade plan pays \$1,000 in spread alone (plus slippage on all 200 fills) and
hands nearly the whole edge back. **Overtrading is how a real edge dies** — you
pay the toll twenty times to earn it once. This is the single most common way a
"profitable on paper" retail strategy bleeds out.

## How this shows up in `market.py`

The cumulative artifact charges all of this inside the trading loop. The
load-bearing line is:

```python
cash -= position * entry + half_spread * position    # pay + half the spread on the fill
...
if position != 0:
    cash -= OVERNIGHT_SWAP * abs(position)           # the tax on patience, every held day
```

Half the spread is debited on the open fill and again on the close fill (a full
spread per round trip), and the overnight swap is charged every day a position
is still open. Slippage, in the full artifact, is folded into the fill price
(you fill a touch worse than quoted). Those few subtractions are why `market.py`
prints "after spread + overnight swap" on its scoreboard — and why the strategy
there can *lose* to buy-and-hold even when it looks clever.

## On capital.com

- The **spread** is capital.com's main fee — there's no separate commission on
  most instruments. A tight spread on a liquid market; a wide one on something
  thin. You pay it coming and going.
- **Overnight funding (swap)** is charged daily on leveraged positions held past
  the platform's cutoff. The 1:1 ("1X") no-leverage share mode is exempt — one
  reason it's the gentlest place to start.
- **Slippage** hits market orders, especially in fast or thin conditions. A
  **guaranteed stop (GSLO)** removes slippage on a stop — for a premium (Lesson
  6). You either pay slippage or pay to insure against it.

See [`../capital_com.md`](../capital_com.md) and capital.com's
[Pricing & fees](https://capital.com/en-int/ways-to-trade/pricing) page.

## What you built

[`../market.py`](../market.py) now subtracts `half_spread * abs(position)` on
every fill and `OVERNIGHT_SWAP * abs(position)` on every held day, so its final
equity and Sharpe are reported **net of costs** — the only honest way to score a
strategy.

## Try it (in [`09_costs.py`](09_costs.py))

1. Lower `SPREAD` to `0.04` (a tight, liquid market) and re-run Part A. Does the
   net flip back to positive? The spread is usually the single biggest bite.
2. Cut `HOLD_DAYS` from 3 to 1 (in and out same-day). How much overnight swap do
   you save? Swap only bites while you're still holding past the cutoff.
3. In Part B, change the rare plan from 5 to 1 trip and the busy one to 250.
   Watch the gap widen — frequency multiplies every per-trip cost.
4. Set `EDGE = 0.30` (a fat, unrealistic edge). Even a strong edge has a
   break-even trade count: beyond it, costs win. Find where the busy plan goes
   red.

---

**Next:** [Lesson 10 — Backtesting honestly (return, Sharpe, max drawdown, OOS)](10_backtesting.py)
— now that costs are in, learn to *score* a strategy without fooling yourself:
the three numbers every backtest must report, and the traps that make a dead
edge look alive.
