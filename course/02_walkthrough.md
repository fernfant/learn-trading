# Lesson 2 — Bid, ask & the spread

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`02_bid_ask_spread.py`](02_bid_ask_spread.py) ·
> interactive: [`html/lesson_02.html`](html/lesson_02.html)

Lesson 1 told a white lie: that a stock has *a* price. It doesn't. The single
most surprising thing for a new trader opening capital.com is that there are
**two** prices side by side for the same asset — and you don't get to pick the
nice one.

## Two prices, always

```python
SPREAD = 0.10
mid  = 100.0
buy  = mid + SPREAD / 2     # ask — you BUY here  (the higher one)
sell = mid - SPREAD / 2     # bid — you SELL here (the lower one)
```

- The **mid** is the fair price in the middle. It's a useful idea, but **you
  can never trade at the mid.**
- To **buy** (go long), you pay the **BUY** price (a.k.a. the *ask*) — the
  higher one.
- To **sell** (go short, or close a long), you get the **SELL** price (a.k.a.
  the *bid*) — the lower one.

The gap, `BUY − SELL`, is the **spread**. On capital.com that spread *is* the
fee — there's usually no separate commission. The broker quotes you a price
you'll *buy* at and a *worse* price you'll *sell* at, and pockets the
difference.

## You start every trade in the red

Here's the part that stings. Buy one unit, then immediately sell it back before
the price moves at all:

```
you pay  $100.05 to buy
you get  $99.95  to sell
result   $-0.10   <- you lost the whole spread
```

You did nothing wrong, the market didn't move, and you're already down the full
spread. That's because you paid half the spread crossing in, and half crossing
out. **Every position opens at a small built-in loss.**

## The spread is a hurdle, not a footnote

So a long isn't profitable when the mid ticks up — it's profitable only when
the mid rises *more than the spread*, because you'll exit at the (lower) sell
price. The lesson runs a wandering mid to show it:

```
You go long at BUY $100.05. Now you wait...
   day  1: mid  99.74  exit-sell  99.69  P&L -0.36
   day  2: mid 100.26  exit-sell 100.21  P&L +0.16  <- finally above water!
   ...
```

Even when the mid climbs, your *exit* price (the sell) lags half a spread
behind, so you sit underwater until the move is big enough. On a tiny 10-cent
spread that's a small drag; on a wide spread, or if you trade often, it's the
difference between winning and losing. This is the first appearance of the
course's recurring theme: **costs decide who wins.**

## How this shows up on capital.com

- Spreads are **dynamic**: tighter on big, liquid markets (major indices,
  popular shares), wider on small or volatile ones, and wider outside market
  hours.
- The platform quotes the spread directly; it's why your brand-new position
  shows a small red number the instant you open it.
- Trade less often and the spread costs you less. Over-trading is, mathematically,
  paying the spread again and again.

## What you built

[`../market.py`](../market.py) now quotes two prices every day: a wandering
`mid`, with `buy` and `sell` straddling it. Run it and read the last line — a
live capital.com-style quote with the spread spelled out. Next lesson you'll
actually *take* one of those prices and open your first position.

## Try it (in [`02_bid_ask_spread.py`](02_bid_ask_spread.py))

1. `SPREAD = 1.00` — does the long ever break even in 15 days? Wide spreads
   punish short-term trading.
2. `SPREAD = 0.02` — a tight, liquid market. Break-even comes much faster.
3. Flip it to a **short**: profit when the mid *falls*.

---

**Next:** [Lesson 3 — Your first trade: long and short](03_long_and_short.py) —
you take one of these prices and open a position. Because capital.com is CFDs,
betting the price will *fall* is just as easy as betting it'll rise.
