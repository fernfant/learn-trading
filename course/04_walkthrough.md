# Lesson 4 — P&L & equity: what are you worth?

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`04_pnl.py`](04_pnl.py) ·
> interactive: [`html/lesson_04.html`](html/lesson_04.html)

You can open a long or a short (Lesson 3). Now the question every trader asks
fifty times a day: **am I up or down — and by how much?** capital.com answers it
with two numbers beginners constantly confuse.

## Balance vs equity

```python
balance = cash                         # settled money; only moves when you CLOSE
equity  = cash + position * price       # balance PLUS the live value of holdings
```

- **Balance** is your *settled cash*. It sits perfectly still the whole time a
  trade is open. It only changes the moment you close.
- **Equity** is your *real net worth right now* — cash plus whatever your open
  position would fetch if you closed it this instant. It moves every tick.

The single line `equity = cash + position * price` is the one you add to
`market.py` this lesson. Everything else in this lesson is just reading it.

## Realized vs unrealized P&L

The profit on an open position has two states:

| | What it is | Is it money? |
|---|---|---|
| **Unrealized** | paper profit on a position you still hold | **No** — it moves every tick and can vanish |
| **Realized** | profit locked in when you close | **Yes** — it's now cash in your balance |

`unrealized P&L = equity − starting balance`. The instant you close, that paper
number becomes realized and lands in your balance.

## Opening already shows the spread

Go long 10 at the buy of \$100.05. You spend `10 × 100.05 = $1000.50` of cash.
But a long can only *close* at the sell, so we value it there:

```
balance (cash) : $999.50
position value : 10 x $99.95 = $999.50
equity         : $1999.00
unrealized P&L : $-1.00   (down a full spread the instant you open)
```

You started with \$2000 and your equity is \$1999 before the price moved at all.
That missing dollar is the Lesson 2 spread (10 units × \$0.10), and **equity
shows it immediately** — it already knows you'd pay the toll to get out.

## Equity breathes; balance holds its breath

Hold the long and walk the mid around:

```
   mid     balance     equity   unreal P&L
   100.00  $  999.50  $ 1999.00   $  -1.00
   102.00  $  999.50  $ 2019.00   $ +19.00
    99.00  $  999.50  $ 1989.00   $ -11.00
   103.00  $  999.50  $ 2029.00   $ +29.00
```

Balance never twitches — the trade is still open, nothing is settled. Equity
rides up and down with the price. **That paper P&L is not yours until you
close.** Plenty of traders watch a fat unrealized profit evaporate because they
mistook equity for money in the bank.

## Closing turns paper into cash

Close at mid \$103 — SELL 10 at the bid \$102.95:

```
balance (cash) now    : $2029.00
position              : 0  (flat)
equity now == balance : $2029.00
REALIZED P&L          : $+29.00
```

When you're flat, `position = 0`, so `equity = cash`. The two numbers snap
together and the \$29 is finally real.

## How this shows up on capital.com

- The platform shows **Balance** and **Equity** as separate lines. Equity = the
  one that flickers; it's Balance + the live "Open P&L" of all your trades.
- A brand-new position's Open P&L starts slightly negative — that's the spread,
  exactly as our equity showed \$1999 not \$2000.
- Margin-related warnings (Lesson 5) are all driven by **equity**, not balance.
  Knowing which number matters is what keeps you in the game.

## What you built

[`../market.py`](../market.py) now carries `cash`, debits it when you open, and
each day computes `equity = cash + position * mark` — marking a long at the sell
and a short at the buy. The final lines report balance, position value and
equity together, so the whole account is visible at a glance.

## Try it (in [`04_pnl.py`](04_pnl.py))

1. Flip Part A to a **short** (`position = -10`, `entry = sell`, `mark = buy`).
   Cash goes *up* when you open (you sold first), yet equity still drops a
   spread. Does equity now rise when the mid *falls*?
2. In Part C, close at mid \$100.00 instead. What's your realized P&L? (You paid
   two half-spreads for nothing — a small loss.)
3. Compute return on equity: `realized / START_CASH * 100`. Tiny moves on a
   small position barely register — a hint at why traders reach for leverage.

---

**Next:** [Lesson 5 — Leverage & margin: the double-edged sword](05_leverage_margin.py)
— control a position far bigger than your cash. Equity becomes the number that
decides whether you survive the day.
