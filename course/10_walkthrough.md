# Lesson 10 — Backtesting honestly: return, Sharpe, drawdown & the OOS trap

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`10_backtest.py`](10_backtest.py) ·
> interactive: [`html/lesson_10.html`](html/lesson_10.html)

You have all the pieces now: a signal (Lesson 8), a size (Lesson 7), and the
costs that bite it (Lesson 9). The final question before you ever risk a cent:
**is this strategy actually any good — and how would I even know?**

A single equity curve isn't an answer. You need numbers, and you need to read
them without lying to yourself. As Ernie Chan puts it in *Quantitative Trading*:
the hardest part of backtesting isn't the math, it's not fooling yourself.

## Three numbers describe almost any strategy

All three come from one thing — the **equity curve**, your account value day by
day. In the script, `backtest()` produces that curve; the three helpers read it.

### 1. Total return — the headline (and the most over-rated number)

```python
def total_return(curve):
    return curve[-1] / curve[0] - 1
```

How much the account grew, end to end. In Part A it's **+3.6%** over a year.
Useful, but it says nothing about *how* you got there — a calm climb and a
heart-attack rollercoaster can end at the exact same number.

### 2. Sharpe ratio — return per unit of wobble

```python
def sharpe(rets):
    m = sum(rets) / len(rets)
    var = sum((r - m) ** 2 for r in rets) / (len(rets) - 1)
    sd = sqrt(var)
    return (m / sd) * sqrt(252) if sd else 0.0
```

Mean daily return divided by the standard deviation of daily returns, then
scaled by `sqrt(252)` (≈ trading days in a year) to "annualize" it. It **rewards
smooth gains and punishes a wild ride**. Rule of thumb: above 1 is decent; most
real retail strategies sit well below 1. Part A scores **0.35** — it made money,
but barely paid you for the stomach-churning it took.

### 3. Max drawdown — the pain

```python
def max_drawdown(curve):
    peak, worst = curve[0], 0.0
    for v in curve:
        peak = max(peak, v)
        worst = min(worst, v / peak - 1)
    return worst
```

Walk the curve tracking the highest point seen so far (the running `peak`); at
each day, how far below that peak have you fallen? The deepest such fall is the
max drawdown. Part A's is **-9.5%** — the worst peak-to-trough drop you'd have
had to sit through. **This is the number that decides whether you'd actually
have held on**, or panic-closed at the bottom and locked in the loss. Drawdown
is what blows accounts up, not the final figure.

## The trap that kills more backtests than anything else

Part B is the real lesson. It's called **in-sample vs out-of-sample**, and it's
where almost every beginner (and plenty of professionals) fool themselves.

Take two years of price data and split it in half:

- **In-sample (IS)** — the first half. The data you're *allowed* to tune on.
- **Out-of-sample (OOS)** — the second half. Unseen data you keep sealed.

Now do the tempting thing: try several settings of the strategy's one knob
(`lookback`), and **pick the one with the best in-sample Sharpe**. Then check
whether that "winner" still wins on the out-of-sample half:

```
 lookback   IS Sharpe  OOS Sharpe
---------------------------------
        5        0.02       -1.25
       10        1.24       -1.78
       20        0.35       -1.58
       40        0.10       -1.81
       60       -0.09       -0.94
```

We pick **lookback=10**: its in-sample Sharpe of **1.24** looks fantastic. On the
unseen out-of-sample half that exact same setting scores **-1.78** — the *worst*
of every candidate. The Sharpe fell by **3.02**.

We didn't discover an edge. We **memorized the in-sample noise** — that's
*overfitting* (or *curve-fitting*). The price path is essentially random
(Lesson 1), so with enough knobs you can always find one that happened to fit
the past beautifully and means nothing about the future.

The tell-tale sign is right there in the output: the winner's OOS Sharpe
(-1.78) is no better than the *average* OOS across all settings (-1.47). All
that "optimization" bought us exactly nothing.

> **The discipline that fixes it:** reserve an out-of-sample slice you *never*
> tune on, and judge the strategy *only* there. It's the one honest score.

## How this shows up on capital.com (and everywhere else)

Every backtesting tool will happily let you tweak parameters until the past
looks gorgeous. The platform's own warning — that the large majority of retail
CFD accounts lose money — is in part this trap in action: strategies that
sparkled on history, charged into the future, and quietly died once real spread
(Lesson 9) and unseen prices showed up.

## What you built

[`../market.py`](../market.py) now ends with a **metrics block**: `returns()`,
`sharpe()` and `max_drawdown()` computed over the daily `equity_curve`, printed
side-by-side with buy-and-hold. That's the honest scoreboard — return, Sharpe
and drawdown, *after* the Lesson 9 costs. The capstone (Lesson 11) is the OOS
test made real: can the strategy beat buy-and-hold on data it never saw?

## Try it (in [`10_backtest.py`](10_backtest.py))

1. **Move the split.** Set `split = len(full) // 3` in Part B (tune on a third,
   test on two-thirds). Does the winner's OOS Sharpe hold up better with less
   data to overfit — or worse? There's no free lunch.
2. **Overfit harder.** Widen `PARAMS` to `range(2, 80, 2)`. With more candidates
   you'll almost always find a gorgeous in-sample Sharpe — and watch how badly it
   craters out-of-sample. More tuning is more overfitting, not more edge.
3. **Reseed.** Change `random.seed(8)` to 1, 2, 3… and re-run. The "best"
   lookback jumps around and the OOS Sharpe is all over the place — proof the
   result is mostly luck. A number that won't sit still isn't an edge.
4. **Honest check.** In Part A, try `lookback=1`. The return might look fine, but
   read the drawdown and Sharpe — a twitchy rule that pays the spread constantly
   is rarely worth it.

---

**Next:** [Lesson 11 — Capstone: beat buy-and-hold, after spread & fees](11_capstone.py)
— put every lesson together and run the one test that matters: does your strategy
survive costs *and* unseen data? (It usually can't. That's the point.)
