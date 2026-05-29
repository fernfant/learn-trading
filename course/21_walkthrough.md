# Lesson 21 — Adverse selection: toxic / informed flow runs you over

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for
> this lesson: [`21_adverse_selection.py`](21_adverse_selection.py) ·
> interactive: [`html/lesson_21.html`](html/lesson_21.html)

This is the market maker's deepest problem — and the payoff of a thread that has
run through the whole course since [Lesson 0](00_foundations.md). You've built
the book (L13–L17), become the market maker (L18), learned to skew quotes
against inventory (L19), and learned that speed wins you the queue (L20). Each of
those eroded the spread edge a little. This one can wipe it out entirely.

## The edge, and who threatens it

You quote a bid a touch below fair value and an ask a touch above it (L18). When
a buyer lifts your ask and later a seller hits your bid, you bought low and sold
high and banked the **spread** without predicting anything. That captured spread
is your *entire* edge.

The danger is **who** trades with you. Two kinds of taker arrive:

- **Noise traders** — uninformed. They trade for reasons unrelated to the next
  move (rebalancing, hedging, boredom). They pay you the spread and the price
  wanders off randomly afterwards, so on average you *keep* it. This is the flow
  you want. Harmless. Profitable.
- **Informed traders** — they *know something*. The price is about to move, and
  they trade with you right before it does. An informed **buyer** lifts your ask
  the instant before the price rises — so you sold, and now you're short into a
  rally. An informed **seller** hits your bid right before the price falls — so
  you bought, and now you're long into a drop. Either way you end up
  **systematically on the wrong side of the move.**

That systematic wrong-siding is **adverse selection** (Glosten–Milgrom 1985;
Kyle 1985). The unsettling core of it: the very fact that someone *wants* to
trade with you is mild evidence that trading with them is a bad idea.

## The one line that books the bleed

The market maker values every fill against fair value **at the moment it
quoted** — the only honest mark, since that's what it believed the unit was
worth when it traded. The spread it banks is the same for *every* fill:

```python
edge = (price - fair) if side == "buy" else (fair - price)
captured = edge * size      # always +half_spread*size
```

The difference is what happens **next**:

```python
if informed:
    self.informed_pnl += captured - JUMP * size   # spread banked, minus the jump against us
    self.informed_fills += 1
else:
    self.noise_pnl += captured                    # just the spread; fair wanders off
    self.noise_fills += 1
```

A **noise** fill banks `half_spread * size` and that's the end of it. An
**informed** fill banks the same little spread, but `fair` immediately jumps
`JUMP` *against* the position you just took on — so that fill is really worth
`(half_spread − JUMP) * size`. With `half_spread = 0.05` and `JUMP = 0.20`, a
noise fill is worth `+0.05/unit` and an informed fill is worth `−0.15/unit`. One
toxic fill undoes *three* good ones.

## Decomposing one run

`run_flow` sends 8000 takers past the MM; 15% of them are informed. Run
`python3 21_adverse_selection.py`:

```
    fills total      : 8000
    noise fills      : 6836
    informed fills   : 1164  (the toxic minority)
    + earned on noise:    +681.50   <- the steady edge
    - lost to informed:   -346.80   <- the lumpy bleed
    ==============================
    net P&L          :    +334.70
```

Read the two middle lines. The MM banks **+681.50** from 6836 harmless noise
fills — its edge. It bleeds **−346.80** to just 1164 informed fills — a minority
of one fill in seven that costs *half* the entire edge. The bleed is enormous
**per fill** precisely because each toxic fill is a position taken on right
before the price moves against it.

## Crank the toxicity and the edge dies

The MM can't tell a noise order from an informed one *in advance* — both just
look like someone lifting the ask or hitting the bid. So as the informed
fraction rises, it keeps getting picked off more often, same spread, same bot:

```
     informed %   noise P&L  informed P&L    net P&L
             0%      798.55          0.00     798.55
             5%      761.35       -111.60     649.75
            10%      723.15       -226.20     496.95
            20%      645.50       -459.15     186.35
            30%      566.90       -694.95    -128.05
            40%      487.70       -932.55    -444.85
```

With **zero** informed flow it's pure profit — a clean, riskless spread. Each
step up in toxicity does two things: it shrinks the noise edge (fewer fills are
harmless) *and* it grows the bleed. Somewhere between 20% and 30% the two cross,
and past that tipping point the **same bot, quoting the same spread, loses
money.** That is what "toxic order flow" means on a real desk.

## The defense: widen the spread

You can't identify the sharks, so you do the only thing you can — **charge
everyone more.** Hold the toxicity at a brutal 30% and widen the half-spread:

```
     half-spread   noise P&L  informed P&L    net P&L
            0.05      556.50       -721.65    -165.15
            0.08      890.40       -577.32     313.08
            0.10     1113.00       -481.10     631.90
            0.13     1446.90       -336.77    1110.13
            0.16     1780.80       -192.44    1588.36
```

At the tight `0.05` quote the MM is underwater (**−165**). Widen it and net P&L
climbs back above zero and keeps rising. Look at *why*: the **noise P&L roughly
triples** (you bank more on every harmless fill), while the informed P&L improves
only modestly (you still get picked off — you just lose a bit less each time
because the jump now has to overcome a wider spread). **Widening works mainly by
taxing the harmless majority** to pay for the toxic minority. You charge the many
for the sins of the few.

The catch — which the capstone makes you *feel* — is that this script lets you
widen for free. In a real book (and in `exchange.py`) a wider quote sits further
from fair and **wins less flow**: other makers undercut you. Quote too tight and
toxic flow eats you; quote too wide and you trade with nobody. The market maker
lives on that knife edge. Real desks add more weapons — **skew/step away** when
they *detect* toxicity (a burst of one-sided fills), and tight **inventory
management** (L19) — but the spread is the first and bluntest defense.

## The symmetry that closes the course

```
    Track 1 (you trade) : informed flow is the faint SIGNAL you hunt.
    Track 2 (you quote) : the SAME flow is the HAZARD that bleeds you.
```

This is the promise [Lesson 0](00_foundations.md) made, now paid in full. Markets
are *nearly* random; the small real edges come from people who **know
something** — informed traders. In Track 1 you were the customer trying to *find*
their footprints (the reason a price isn't a perfect coin flip). In Track 2,
quoting prices, those exact same traders are your nightmare: they pick you off,
and the damage has a name. **Same person, opposite seat.** That is adverse
selection.

## What this is in `exchange.py`

The cumulative artifact runs this idea *inside the real matching engine*. In
[`../exchange.py`](../exchange.py), `run_flow()` sends informed takers at the
`MarketMaker`, and `fair` jumps against it on each toxic fill — the L21 line in
the build map. There the bleed shows up as a growing `toxic_fills` count and a
falling `pnl()`, on top of the inventory and latency effects from L19–L20.

## Try it (in [`21_adverse_selection.py`](21_adverse_selection.py))

1. **Pure profit.** In the "ONE RUN" block set `informed_frac=0.0`. The informed
   bleed goes to `0.00` and net P&L is exactly the noise spread — riskless.
2. **Crank the toxicity.** Set `informed_frac=0.50` and watch net P&L swing deep
   negative: the bleed now dwarfs the edge.
3. **Bigger jump.** Change `JUMP = 0.20` to `0.40` — the informed now know about a
   bigger move, so each toxic fill costs twice as much. Even a small fraction is
   brutal. Toxicity is about the *size* of the move, not just the head-count.
4. **Widen to survive.** In exercise 2's 50%-informed case, raise `half_spread`
   until net P&L turns positive again. You must out-charge the average bleed.
5. **Decompose the defense.** In the DEFENSE sweep, watch noise P&L *rise* with
   the half-spread while informed P&L barely improves. Widening taxes the noise
   majority more than it deters the sharks.

---

**Next:** [Lesson 22 — Capstone: a market maker that stays profitable *and*
flat](lesson_22.html) — put L18–L21 together. Tune `half_spread`, `skew` and
`speed` so the bot makes money **and** carries no inventory even at 25% informed
flow. Make money *and* hold no risk — the real job of an HFT market maker, and
deliberately hard.
