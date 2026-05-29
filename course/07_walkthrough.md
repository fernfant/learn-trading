# Lesson 7 — Risk & position sizing: don't blow up

> Track 1 · cumulative artifact: [`../market.py`](../market.py) · code for this
> lesson: [`07_risk.py`](07_risk.py) ·
> interactive: [`html/lesson_07.html`](html/lesson_07.html)

You can pick a direction (L3), read your equity (L4), lever up (L5) and set a
stop-loss (L6). One question decides whether you survive long enough for any of
that to matter: **how much do you bet?**

Beginners spend all their energy on *what* to trade. The uncomfortable truth
from Van Tharp's *Trade Your Way to Financial Freedom* is that **how much** you
bet matters more. You can have a genuinely winning edge and still go broke by
betting too big — a normal run of losses wipes you out before the edge pays off.
That failure mode has a name: **risk of ruin**.

## The one rule: fixed-fractional sizing

Risk a small **fixed fraction** `R` of your *current* equity on each trade —
1% or 2%, not 25%. You decide where you'll bail (the **stop**), a distance `D`
in price units from your entry. Then size the position so that getting stopped
out loses exactly `R%` of equity:

```python
qty = risk_frac * equity / stop_distance
```

This is the single line Lesson 7 adds to `market.py` (as
`qty = int(risk_frac * equity / stop_distance)`). Everything below is why it
keeps you alive.

## Part A — size falls out of the stop

With \$10,000 and `risk_frac = 0.02`, your **risk budget** is a fixed \$200 per
trade. The *share count* then depends entirely on how far away your stop is:

```
   stop distance   qty (units)   $ at risk if stopped
   $ 0.50           400        $200.00
   $ 1.00           200        $200.00
   $ 2.00           100        $200.00
   $ 5.00            40        $200.00
```

A **tight** stop (\$0.50) lets you hold 400 units for the same \$200; a **wide**
stop (\$5.00) forces you down to 40. The dollars at risk never change — only the
size. You size *to the stop*, never to a gut feeling about how confident you
are. Confidence doesn't cap your loss; the stop does.

## Part B — same edge, two sizes, two fates

This is the part that should change how you trade. We play a betting game with a
**real positive edge**: win +1× your stake 52% of the time, lose your stake 48%
of the time. On average, you make money every single bet. We run it 200 trades
per "trader", 2000 traders each, for two bet sizes — the *only* difference being
the fraction of equity staked per trade:

```
   bet size   survival rate   median ending equity
      2%         100.0%             1.13x
     25%          20.7%             0.01x
```

(seeded with `random.seed(7)`, so you'll see these exact numbers.)

The 2% sizer **always survives** and compounds to ~1.13× the stake. The 25%
sizer — *with the identical winning edge* — busts about **4 times out of 5**,
and the median trader ends with basically nothing. Bet size, not the edge,
decided who lived. Over-betting converts a winning game into ruin.

Why does the median 25% trader end near zero even though each bet is profitable
*on average*? Because wealth **multiplies** across trades. A +25% then −25% is
not break-even — it's `1.25 × 0.75 = 0.9375`, a 6% loss. String enough of those
together and the typical path drifts to zero even while the average (dragged up
by a few lucky runaway winners) looks fine. The median trader lives on the path,
not the average.

## Part C — the drawdown trap

The deep reason over-betting kills is that **losses and gains aren't
symmetric**. Recovering a loss takes a *bigger* gain than the loss:

```python
gain_needed = loss / (1 - loss)
```

```
   drawdown   gain needed to get back to even
   - 10%       +  11%
   - 20%       +  25%
   - 50%       + 100%
   - 75%       + 300%
   - 90%       + 900%
```

Down 50%, you need **+100%** just to break even. Down 90%, a heroic **+900%**.
Big bets dig deep holes; deep holes demand exponentially bigger climbs. Keeping
each bet small keeps you in the shallow end where recovery is routine — which is
why **capital preservation is rule #1**.

## How this shows up on capital.com

- The platform lets you set a **stop-loss** when you open (Lesson 6). The
  distance from your entry to that stop *is* the `stop_distance` here.
- Your job before clicking Buy/Sell: pick the size so that the stop, if hit,
  costs only ~1–2% of your equity. capital.com won't do this for you — the size
  box defaults to whatever, and over-sizing is the single most common way demo
  graduates blow up a real account.
- The **demo account** is the place to drill this until it's a reflex: same
  prices, same stops, fake money. Practice sizing there, not with rent money.

## What you built

[`../market.py`](../market.py) now sizes every entry with
`qty = int(risk_frac * equity / stop_distance)`: it reads the live `equity`,
takes the `RISK_FRAC` knob (2%) and the stop distance implied by `STOP_FRAC`,
and never opens a position bigger than that rule allows. Equity grows → size
grows; a wider stop → smaller size. The account can take a losing streak without
detonating.

## Try it (in [`07_risk.py`](07_risk.py))

1. Drop `risk_frac` to `0.01` in Part A. Every share count halves — and so do
   the dollars at risk. The rule scales cleanly.
2. In Part B, try `0.05`, `0.10`, `0.40`. Find where survival falls off a cliff
   — the sizing beyond which a winning edge can't save you.
3. In Part B, set `WIN_PROB = 0.48` (a *losing* game). Now even 2% bleeds out —
   sizing controls how *fast* you lose, not *whether* you do. It manages a real
   edge; it can't manufacture one.
4. Open [`../market.py`](../market.py) — the live loop sizes every entry with
   exactly this line. This lesson, wired in.

---

**Next:** [Lesson 8 — A signal: moving-average crossover](08_signal.py) — for
the first time we try to *predict* direction instead of just sizing a bet. With
a healthy dose of skepticism: most "signals" are noise.
