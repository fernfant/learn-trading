# Lesson 5 — Leverage & margin: the double-edged sword

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`05_leverage_margin.py`](05_leverage_margin.py) ·
> interactive: [`html/lesson_05.html`](html/lesson_05.html)

You have \$1,000. A share costs \$100, so unaided you can hold ten of them. On
capital.com you can put down a small **margin** deposit and the broker fronts the
rest, letting you control a far bigger position. That is **leverage** — and it is
the single feature that makes CFD trading both attractive and dangerous.

## The two numbers: notional and margin

```python
notional = abs(position) * price       # how big your position really is
margin   = notional / leverage         # the slice of YOUR cash that's locked up
```

- **Notional** is the full size of the bet — 50 units at \$100 is a \$5,000
  position, whether you funded all of it or not.
- **Margin** is what the broker actually makes you put up. At 20x leverage, that
  \$5,000 position only locks \$250 of your cash. The other \$4,750 is fronted.

The same position, three leverages:

```
   leverage   margin required   % of your $1,000
   --------   ---------------   ----------------
      1x      $   5,000.00      500.0%
      5x      $   1,000.00      100.0%
     20x      $     250.00       25.0%
```

At **1x** you'd have to fund the whole \$5,000 — but you only *have* \$1,000, so
1x can't even open this trade. Leverage is precisely what lets a small account
hold a big position. That's the upside. Now the catch.

## The same move hurts more at higher leverage

Let the price fall a tiny **2%**. The dollar loss depends only on the position,
not on how you funded it — 50 units losing \$2 each is **\$100, every time**. But
measured against the **margin you put up**, that fixed loss balloons:

```
   leverage   margin put up   loss vs that margin
   --------   -------------   -------------------
      1x      $ 5,000.00         -2.0%
      5x      $ 1,000.00        -10.0%
     20x      $   250.00        -40.0%
```

Identical market move. At 1x it's a rounding error; at 20x that one 2% dip
erased **40% of your margin**. The bet never changed — leverage just turned up
the volume on both the wins and the losses. That is the double-edged sword:
leverage multiplies your gains *and* your losses as a percentage of your cash.

## Margin level — the number that decides if you survive

capital.com watches one ratio all day:

```python
margin_level = equity / used_margin * 100   # as a %
```

`equity` is your live net worth from Lesson 4 (`cash + position × price`).
`used_margin` is what's locked up, recomputed every tick as the price moves.

- **100%** means your equity exactly equals the margin you've locked.
- Below ~100% you're in the **margin-call zone** — capital.com warns you at 75%
  and 100% margin usage.
- At **50%** the platform **force-closes** your position — the **stop-out**. It
  does not ask, and you don't get the cushion back.

## Watching an account blow up

Open a *big* leveraged bet: 180 units long at 20x. Notional is \$18,000, so the
broker locks \$900 of your \$1,000 — almost everything. Only \$100 of free equity
cushions the trade. Then a perfectly ordinary, gently-drifting market:

```
   day    price    equity   used_margin   margin level
   ---  -------   -------   -----------   ------------
     1  $101.32   $1237.31      $ 911.87       135.7%
     2  $ 99.36   $ 885.37      $ 894.27        99.0%  <- margin call zone
     3  $ 98.41   $ 714.09      $ 885.70        80.6%  <- margin call zone
     4  $ 98.93   $ 807.45      $ 890.37        90.7%  <- margin call zone
     5  $ 97.51   $ 551.33      $ 877.57        62.8%  <- margin call zone
     6  $ 97.41   $ 533.16      $ 876.66        60.8%  <- margin call zone
     7  $ 97.66   $ 578.32      $ 878.92        65.8%  <- margin call zone
     8  $ 96.49   $ 368.88      $ 868.44        42.5%  <- STOP-OUT! force-closed
```

The price only slipped from \$100.00 to \$96.49 — a **3.5% drift**, the sort of
move that happens constantly. Yet at 20x that thin \$100 cushion was gone and
capital.com closed you out near a total loss of your \$1,000. Notice you were in
the warning zone from **day 2** — leverage this high leaves almost no room to be
wrong. Lower the leverage in the same market and that cushion is fat enough to
ride the dip out.

## How this shows up on capital.com

- The platform shows your **margin level** as a live percentage. Watch it, not
  the price.
- It warns at **75% and 100%** margin usage, and **stops you out at 50%** margin
  level — automatically.
- capital.com offers a **1:1 (1X) no-leverage** mode. On a gentle market 1x
  effectively can't margin-call you — it's the safest place to learn.
- The large majority of retail CFD accounts lose money, and over-leverage is a
  big reason why. Leverage is not free money; it's the same bet, amplified.

## What you built

[`../market.py`](../market.py) now computes `margin = abs(position) * price /
leverage` each day, derives the **margin level** from your Lesson-4 equity, and
**force-closes the position if margin level drops below 50%** — the stop-out.
One new line of bookkeeping turns your simulator into something that can blow up,
exactly like a real account.

## Try it (in [`05_leverage_margin.py`](05_leverage_margin.py))

1. In Part C, drop `position` to **40** at the same 20x. Margin is now \$200,
   free equity is \$800, and the stop-out never comes in 20 days — more cushion,
   more room to be wrong.
2. Set `LEV = 1` and `position = 8` (so \$800 notional fits your \$1,000). Now
   `used_margin == notional` and a gentle wander never trips the 50% line. 1x
   can't margin-call you on a small move.
3. Keep `position = 180` but crank `LEV = 30` and re-run — count how few days you
   last. Then change the seed (`random.seed(1)`, `random.seed(7)`): sometimes you
   survive, mostly you don't. That's leverage as a coin flip.

## Reference

BabyPips — *School of Pipsology*: [leverage & margin](https://www.babypips.com/learn/forex/leverage-the-double-edged-sword)
(margin, margin level, margin call and stop-out, explained for beginners).

---

**Next:** [Lesson 6 — Order types (market, limit, stop, take-profit)](06_walkthrough.md)
— so far you've opened and closed by hand at the current price. Next you place
orders that *wait* for a price and fire automatically — including the stop that
could have saved the account above.
