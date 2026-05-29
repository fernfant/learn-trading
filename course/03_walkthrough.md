# Lesson 3 — Your first trade: long and short

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`03_long_and_short.py`](03_long_and_short.py) ·
> interactive: [`html/lesson_03.html`](html/lesson_03.html)

Lessons 1 and 2 only watched a price. Now you **take** one. On capital.com you
don't buy the share itself — you trade a **CFD** (contract for difference), a
bet on which way the price moves. The first thing a bet needs is a **direction**.

## Two directions, one signed number

```python
position > 0   # LONG  — you bought first; you profit if the price RISES
position < 0   # SHORT — you sold first;  you profit if the price FALLS
position == 0  # FLAT  — no bet on the table
```

- **Long** is the obvious one: buy low, sell high.
- **Short** is the one that surprises beginners: you can **sell first** something
  you never owned, then **buy it back cheaper**. CFDs make a falling market just
  as tradeable as a rising one — that's the whole point of the product.

We track the whole bet as one signed number, the **position**. Going long 10
units is `+10`; going short 10 is `-10`. One variable, both directions.

## Which side of the spread you cross

This is the part that ties back to Lesson 2. You always open and close on the
**bad** side of the spread:

| | Open | Close |
|---|---|---|
| **Long** (+) | BUY (ask, higher) | SELL (bid, lower) |
| **Short** (−) | SELL (bid, lower) | BUY (ask, higher) |

A long buys high and sells low; a short sells low and buys high. Either way you
hand the broker a full spread for the round trip.

## A long trade

```
LONG 10 units
   open : buy  10 @ $100.05
   close: sell 10 @ $102.95   (mid 100 -> 103)
   P&L  : 10 x (102.95 - 100.05) = $+29.00
```

The mid rose a clean $3.00, but you pocketed **$29, not $30** — the spread ate a
dollar (10 units × $0.10). Profit, yes, but the toll came out first.

## A short trade

```
SHORT 10 units
   open : sell 10 @ $99.95
   close: buy  10 @ $97.05   (mid 100 -> 97)
   P&L  : -10 x (97.05 - 99.95) = $+29.00
```

The price **fell** $3 and you still made money. That's a short: you sold at
\$99.95 and bought back at \$97.05. The single P&L formula handles both:

```python
pnl = position * (exit_price - entry_price)
```

With `position = -10`, a *drop* in the exit price makes the bracket negative,
and negative × negative = a positive P&L. One formula, both directions.

## Same market, mirror outcomes

Open both a +10 long and a −10 short on the same wandering mid and mark them to
market each day:

```
   day    mid   long P&L   short P&L
     1   99.74     -3.56      +1.56
     5   98.78    -13.16     +11.16
     7   99.68     -4.17      +2.17
```

When the mid rises the long wins and the short loses, and vice versa — they're
**near-mirror images**. But look closely: they don't sum to zero, they sum to
*minus two spreads*. Both traders opened underwater. **Direction decides which
way you need the market to move; the spread is the toll you pay either way.**

## How this shows up on capital.com

- The **Buy** and **Sell** buttons *are* long and short. Tap Buy to open a long,
  Sell to open a short — same screen, same effort.
- Your open position shows a live P&L that's already slightly red the instant
  you open it (that's the spread from Lesson 2).
- A short's risk is, in theory, **unlimited**: a price can keep rising forever,
  so a short can keep losing. A long can only fall to zero. We'll put real
  guardrails on this in Lesson 6 (stops) and Lesson 7 (sizing).

## What you built

[`../market.py`](../market.py) now carries a signed `position`. On day 0 it
opens a long 10 (flip `+= 10` to `-= 10` for a short) at the correct side of the
spread, and the final line marks it to market: a long closes at the SELL, a
short at the BUY. Next lesson we stop looking at one trade in isolation and ask
the real question: **across cash and open positions, what are you actually
worth?**

## Try it (in [`03_long_and_short.py`](03_long_and_short.py))

1. In Part A set `exit_mid = 100.05`. Did the long break even? (You need the mid
   to rise a *full spread*, to 100.10, just to get back to zero.)
2. In Part C give the market a downward drift: `random.gauss(-0.3, 1)`. Which
   bet wins now? This is *why* shorts exist.
3. In Part B set `exit_mid = 101.0`. A short **loses** when the price rises —
   and there's no ceiling on how far it can rise.

---

**Next:** [Lesson 4 — P&L & equity: what are you worth?](04_pnl.py) — we fold
cash and your open position into a single number, your **equity**, the way
capital.com shows your account balance ticking in real time.
