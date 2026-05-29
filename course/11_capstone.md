# Lesson 11 — 🏆 Capstone: beat buy-and-hold, *after* costs

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`11_capstone.py`](11_capstone.py) ·
> interactive: [`html/lesson_11.html`](html/lesson_11.html)

This is the boss fight. Ten lessons ago you had a price that wandered. Now you
have a real backtester: a [random-walk price](../market.py) (L1) with
[two quotes and a spread](02_bid_ask_spread.py) (L2), [long & short](03_long_and_short.py)
(L3), [equity](04_pnl.py) (L4), [leverage & margin](05_leverage_margin.py) (L5),
[stop-loss / take-profit](06_order_types.py) (L6), [risk-based sizing](07_risk.py)
(L7), a [moving-average signal](../market.py) (L8), [real costs](../market.py)
(L9), and [honest metrics](../market.py) (L10). The capstone wires all of it
into one program and asks the only question that matters:

> **Can you beat simply buying and holding the asset — after the spread,
> overnight funding, and slippage — and prove it on data your strategy never
> saw while you tuned it?**

---

## The challenge (and the rules)

Anyone can produce a backtest that prints a big number. An *honest* one obeys
three rules (Chan, *Quantitative Trading*; Van Tharp on sizing):

1. **Net of costs.** Every fill pays half the spread **plus slippage**; every
   held day pays the overnight swap. No frictionless fantasy.
2. **Split the data.** Tune the knobs on the **in-sample (IS)** half only. Then
   run the frozen strategy **once** on the **out-of-sample (OOS)** half. The OOS
   number is the only one you're allowed to believe.
3. **No peeking.** You don't get to re-tune after seeing OOS. Do that and you've
   "fitted the noise" — your real, live results will look like the OOS, not the
   pretty IS.

The benchmark — **buy-and-hold** — is deliberately tough: the simulated market
has a small upward **drift** baked in (`gauss(0.02, 1.0)` per day), just like
real stock indices tend to drift up. B&H pays the spread exactly once and then
rides that drift for free. Beating it after you cross the spread on every trade
is genuinely hard. That's the point.

---

## The reference solution

[`11_capstone.py`](11_capstone.py) packages `market.py`'s loop into a function
you can run on any price slice:

```python
def run_strategy(prices, costs=True):
    # long-only MA crossover (L8), risk-sized (L7), stop/TP (L6),
    # leverage + 50% stop-out (L5), paying half-spread + slippage on every
    # fill (L9) and a swap every held day (L9). returns the daily equity curve.
```

```python
def buy_and_hold(prices, costs=True):
    entry = prices[0] + SPREAD/2     # buy at the ask, pay the spread ONCE
    units = START_CASH / entry
    return [units * (p - SPREAD/2) for p in prices]   # mark out at the bid
```

We generate **500 days** once and split down the middle: days `0..250` are
in-sample (where the knobs `FAST,SLOW = 10,40` etc. were chosen), days
`250..500` are out-of-sample (judged once). Knobs live at the top of the file.

### What it prints (seed 11)

**In-sample** — where the knobs were tuned:

```
                        strategy      buy & hold
  total return             11.1%           30.4%
  Sharpe (ann.)             2.28            2.02
  max drawdown             -2.3%           -8.0%
  round-trips                  5               1
  Verdict: strategy LOST to buy-and-hold (by return).
```

**Out-of-sample** — the only result that counts:

```
                        strategy      buy & hold
  total return              0.1%           -8.8%
  Sharpe (ann.)             0.05           -0.68
  max drawdown             -2.4%          -10.9%
  round-trips                  4               1
  Verdict: strategy BEAT buy-and-hold (by return).
```

---

## The honest verdict

Read those two tables carefully, because the story is *not* a clean victory:

- **In-sample, the strategy LOST** (+11.1% vs +30.4%). The market drifted hard
  up on the first half; a long-only system that ducks out on every dip simply
  can't keep up with sitting in the whole rally.
- **Out-of-sample, the strategy "BEAT" B&H** (+0.1% vs −8.8%) — but look *why*.
  The second half fell. The strategy spent most of it **flat**, dodging the
  drop, so it lost almost nothing while B&H bled −8.8% with a −10.9% drawdown.
  That's **risk avoidance, not prediction.** It didn't foresee the fall; it just
  wasn't holding. On a random walk, that kind of luck reverses.

The script even prints this read-out for you, derived from the actual numbers
rather than a canned happy ending:

```
  * But look WHY it 'won': it mostly sat FLAT through a falling
    market while buy-and-hold bled (its DD -11% vs the
    strategy's -2%). Dodging a drop is risk control,
    not a predictive edge — and on a random walk that luck reverses.
```

### The real test: does it survive *other* worlds?

One split proves nothing. TRY IT #1 asks you to re-run across seeds 1..10 and
**count** the OOS wins. Here's that tally for the reference knobs:

| seeds tested | OOS wins vs B&H |
|---|---|
| 1 – 10 | **2 / 10** |

**Two out of ten.** Worse than a coin flip. The seed `11` shipped as the default
is simply one of the lucky splits — which is exactly why a single backtest is
so dangerous, and why honest quants demand robustness across many samples. The
strategy has **no durable edge**. After the spread on every crossing, the swap
on every held day, and slippage on every fill, the small MA signal isn't worth
the friction it costs.

> This is the regulatory warning made concrete: *"the large majority of retail
> CFD accounts lose money."* You just built the machine that shows why. It isn't
> that the strategy is stupid — it's that markets are *nearly* random and costs
> are *certain*, so a thin, uncertain edge gets eaten by a thick, guaranteed
> cost. Owning that is the whole of Track 1.

---

## Now you try (the capstone challenge 🏆)

In [`11_capstone.py`](11_capstone.py)'s **TRY IT** block:

1. **Robustness.** Sweep `SEED` 1..10, tally OOS wins. ~5/10 = no edge. (Default
   knobs: 2/10.)
2. **Overfit on purpose.** Maximize *in-sample* return by tuning `FAST/SLOW`,
   then look at OOS. Watch the IS win evaporate. That's curve-fitting, caught
   red-handed.
3. **Costs off.** Run with `costs=False`. How much of the gap was just the
   spread + swap?
4. **Add shorts.** Let it go short when `fast < slow`. Does trading both
   directions beat a drifting-up B&H — or does doubling your spread-crossings
   cost more than it earns?
5. **The real boss.** Find one set of knobs that beats B&H out-of-sample across
   a *majority* of seeds 1..10, after costs. If you can, you've done what most
   retail traders never do. If you can't — now you *understand* the warning.

Either outcome is a pass. The capstone's job isn't to hand you a money-printer;
it's to make you the kind of trader who knows the difference between an edge and
a lucky split.

---

**Next:** 🔴 **Track 2 begins — [Lesson 12: from price-*taker* to price-*maker*](lesson_12.html).**
You've spent Track 1 *paying* the spread on every trade and watching it eat your
edge. Now flip seats. In Track 2 you build the **order book** and the
**market maker** that *quotes* both prices and **earns** that very spread — the
role capital.com plays for you. Same number, opposite sign: the spread that was
your cost becomes your revenue. That hinge is the whole second half of the
course. 🏆 → 📕
