# Lesson 8 — A signal: moving-average crossover (and honest skepticism)

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`08_signal.py`](08_signal.py) ·
> interactive: [`html/lesson_08.html`](html/lesson_08.html)

Seven lessons of plumbing — a price, a spread, long/short, P&L, leverage, order
types, sizing — and we still have no rule for **when** to buy. This lesson adds
the most famous rule in charting, the **moving-average crossover**, and then
does the thing most trading content refuses to do: it checks whether the rule
actually works. Spoiler from the course's recurring theme — on a near-random
market, it mostly doesn't.

## The moving average

A **simple moving average (SMA)** is just the mean of the last *N* prices. It
smooths the daily noise so a trend can show through:

```python
def sma(prices, n):
    if len(prices) < n:
        return None          # not enough history yet
    return sum(prices[-n:]) / n
```

A **fast** MA (few days, e.g. 5) reacts quickly; a **slow** MA (more days,
e.g. 20) lags. Plot both and you get two lines that weave around the price.

## The signal — one line

```python
signal = fast_avg > slow_avg     # True -> go long, False -> go flat
```

When the fast line crosses **above** the slow line, recent prices are running
hotter than the longer-term average — chartists call it a **golden cross** and
read it as "uptrend, get long". When it crosses back below (the **death
cross**), you go flat. That single comparison is the entire signal, and it's
the exact line you add to [`../market.py`](../market.py) this lesson:
`signal = fast_avg > slow_avg`.

## Part A — drawing it

The script builds a 120-day random walk (`seed=8`), walks it day by day, and
marks every day the signal flips: `^` where the fast crosses up (open long),
`v` where it crosses down (go flat). On this market it flips **6 times** — each
`^…v` pair is one round-trip you'll pay a toll on. The arrows cluster where the
price changes direction, exactly as you'd expect a lagging average to behave:
it confirms the turn *after* it has already happened.

## Part B — the honest contest

Here's where most courses stop and yours doesn't. We run three strategies on
the **same** price path:

```
  strategy                  return   trades
  MA crossover                8.4%        8
  random coin-flip            6.5%       60
  buy & hold                 24.1%        -
```

The crossover made **+8.4%**. Sounds like a win — until you see that just
**buying and holding** made **+24.1%**, and a strategy that enters and exits on
literal **coin flips** made **+6.5%**, right next to the "smart" rule. On a
near-random walk the crossover is wrestling the same noise the coin-flip is. It
beat the coin flip *here*, on *this* seed — that's not evidence of skill, it's
the kind of thing that happens when you flip a coin a few times.

This is David Aronson's whole argument in *Evidence-Based Technical Analysis*:
a rule that "works" on one chart proves nothing. You can always find a market
where any rule looked brilliant.

## Part C — subtract a tiny cost and watch it melt

Real trades cross the spread (Lesson 2) and pay funding (Lesson 9). Charge a
modest **0.10** per trade:

```
  MA crossover, no cost   :     8.4%
  MA crossover, with cost :     7.6%   (8 trades x 0.1)
  buy & hold (1 trade)    :    24.1%
```

The cost shaved **0.8 points** off — and that's with only 8 trades on a calm
market. The crossover crosses the spread on **every** entry and exit; buy &
hold pays the toll **once**. Make the rule twitchier (a faster window) and it
trades dozens of times, and the drag compounds into something that can sink an
otherwise-positive strategy below water. **More trading is not more edge — it's
more cost.**

## Part D — many markets, one verdict: instability

The real tell is what happens when you stop cherry-picking one chart. Run the
same `(5, 20)` rule across 8 different markets:

```
   seed   crossover     +cost   buy&hold   beat B&H?
      1       -1.2%     -2.0%      -6.5%         yes
      2       13.8%     13.6%     -12.9%         yes
      3       -8.0%     -8.6%     -18.3%         yes
      4        3.0%      2.2%       9.0%          no
      5        5.6%      4.8%       4.2%         yes
      6        1.1%      0.5%      -1.7%         yes
      7       -7.4%     -8.2%      -4.1%          no
      8        8.4%      7.6%      24.1%          no
```

Sometimes the crossover wins big (seed 2: +13.8% while buy & hold *lost*
12.9%), sometimes it loses badly (seed 3), sometimes buy & hold crushes it
(seed 8 — the very market Part A drew). It beat buy & hold on **5 of 8** free
and **5 of 8** after cost, and **every** `+cost` number is lower than its free
twin. Run more seeds (try 50) and the win rate drifts toward a coin flip.

That flip-flopping **is** the finding. A genuine edge would win *consistently*
and *survive costs*. This one does neither — which is exactly what you'd expect
if the signal is reading noise.

## How this shows up on capital.com

The platform will happily draw moving averages, RSI, MACD and dozens more
indicators on your chart, with crossovers highlighted. They look authoritative.
Nothing on the screen tells you the backtest behind a "strategy" was run once,
on the one chart where it happened to work, with the spread quietly omitted.
This lesson is the antibody.

## What you built

[`../market.py`](../market.py) now computes a fast and slow SMA each day and
sets `signal = fast_avg > slow_avg`, opening a long on the golden cross and
closing on the death cross — the rule you just stress-tested, now wired into
the full leveraged, sized, cost-paying account.

## Try it (in [`08_signal.py`](08_signal.py))

1. **Windows.** Set `FAST, SLOW = (10, 50)` for a calmer system or `(2, 5)` for
   a twitchy one. The twitchy one trades far more — re-run Part C and watch the
   cost drag explode. Does any setting win on *most* seeds in Part D?
2. **Cost.** Set `COST = 0.30`. How many of the 8 markets still beat buy & hold?
   This is the single most overlooked number in amateur backtests.
3. **More seeds.** Change `range(1, 9)` to `range(1, 51)` and count the wins.
   The win rate drifts toward 50% — what you'd see if the signal had no edge.
4. **Rig it (to learn the trick).** Loop the seeds, print only the one where the
   crossover wins biggest, and present that chart alone. That's how a dishonest
   backtest is built — and why **out-of-sample** testing (Lesson 10) exists.

---

**Next:** [Lesson 9 — Costs that kill: spread + overnight funding + slippage](09_costs.py)
— we made the cost a single toy number here; next we charge it the way
capital.com really does, and see why "most retail CFD accounts lose money."

*References: John Murphy, _Technical Analysis of the Financial Markets_ (the
standard reference for crossovers) · David Aronson, _Evidence-Based Technical
Analysis_ (the skeptic's counterweight).*
