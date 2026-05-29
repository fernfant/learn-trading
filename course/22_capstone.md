# Lesson 22 — 🏆 Capstone: a market maker that stays profitable *and* flat

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for
> this lesson: [`22_capstone.py`](22_capstone.py) ·
> interactive: [`html/lesson_22.html`](html/lesson_22.html)

This is the boss fight for Track 2 — and the end of the course. Ten lessons ago
"the price" was one number handed to you from the sky. Now you have the whole
machine: an [order book](13_walkthrough.md) (L13) that
[market orders eat](14_walkthrough.md) (L14) and
[limit orders rest in](15_walkthrough.md) (L15), a
[matching loop](16_walkthrough.md) (L16), a [market-data feed](../exchange.py)
(L17), and a **market maker** that [quotes both sides](../exchange.py) to earn
the spread (L18), [skews by inventory](19_inventory.py) to stay flat (L19),
[wins only the flow it is fast enough](../exchange.py) to sit in front of (L20),
and [bleeds to informed flow](../exchange.py) (L21). The capstone wires the
maker's three hard lessons into one bot and asks the only question a real HFT
desk cares about:

> **Can your market maker end the session both PROFITABLE (positive P&L from
> the spread it captured) AND FLAT (inventory near zero, not a giant
> directional bet you got stuck holding) — while a slice of the flow is TOXIC,
> informed traders who know which way the price is about to jump?**

---

## The dual objective (and why both halves matter)

The whole job lives in the word **and**. Either half *alone* is easy and
worthless:

- **Profitable alone is luck.** You can post a big P&L by accident — buy a load
  of inventory right before the price rips up. That is not market making, it's
  a directional gamble that happened to win. Re-seed the world and it blows up.
- **Flat alone is doing nothing.** You can guarantee zero inventory by quoting
  so wide nobody ever hits you. Zero risk, zero profit. You didn't make a
  market, you just stood there.

The art is the **tension** between them. Adverse selection (L21) pushes you to
widen the spread and skew harder to survive; getting filled at all pushes you to
quote tight and stay near fair. A real maker lives in the narrow band where it
earns enough spread to cover the toxic flow *and* leans hard enough to keep
inventory from running away — but not so hard it stops trading. That trade-off
is the subject of Cartea, Jaimungal & Penalva, *Algorithmic and High-Frequency
Trading*.

### The rules

1. **Net of adverse selection.** ~15% of the flow is informed: the instant they
   fill you, fair value jumps against your new inventory. No frictionless
   fantasy — toxic flow is a *certain* cost, just like the spread was in Track 1.
2. **Both halves, at once.** The bar is **TOTAL P&L > 0** *and*
   **|final inventory| < 60**. Hitting one without the other is a fail.
3. **No cheating the spread.** You may only tune `HALF_SPREAD` and `SKEW`. You
   can't turn off the informed flow or the inventory mark.

---

## The reference solution

[`22_capstone.py`](22_capstone.py) condenses `exchange.py`'s `MarketMaker`
(L18 + L19) and runs it against a flow simulator for 6,000 takers. The two
levers:

```python
HALF_SPREAD = 0.07     # how far each quote sits from fair -> wider = safer, fewer fills
SKEW        = 0.012    # how hard to lean quotes by inventory -> higher = flatter, costlier
```

The maker quotes `fair ± half_spread`, then shifts **both** quotes by
`skew × inventory` so the market hands its inventory back (long ⇒ push quotes
down: sell eagerly, buy reluctantly). Every fill is split into a three-way **P&L
decomposition** that sums *exactly* to total P&L:

```
total P&L = spread_earned + adverse_loss + inventory_drift
```

- **spread earned** — the edge: each fill books `(its price − fair)`, i.e.
  +half-spread minus whatever skew you gave up.
- **adverse-selection loss** — inventory × the informed tick that moves
  *against* it the instant after a toxic fill (L21's bleed).
- **inventory drift** — inventory × fair's own random wander; pure inventory
  risk. A near-flat maker barely feels it; a maker stuck holding a big position
  lives or dies by it.

To prove the skew is doing the work, the script runs a **naive** maker — same
spread, **same flow, same seed**, but `skew = 0.0` (the L18 maker before it
learned L19) — and compares.

### What it prints (seed 22)

The reference maker's P&L climbs steadily (captured spread), and its inventory
stays pinned within a few units of flat:

```
REFERENCE maker inventory (skew ON -> mean-reverts to flat):
     +6 |      *      *
     +4 |    * *   *  *                       **
     +2 | *  * *   *  ** * *   *   *      *   **   *         *  * *
     +0 |*       *   *                 *   * *                *     0 (flat)
     -2 |  *  *   * *   * * **  **  ***  *      **  ** *  * *
     -4 |     *     *     *      *   *           *        *
     -6 |
```

```
================================================================
  REFERENCE  (skew ON)
================================================================
  fills                         1837  (267 toxic / informed)
  spread earned              +202.68  the edge: +half-spread per fill
  adverse-selection loss      -13.02  toxic ticks vs our inventory
  inventory drift              -2.38  fair's wander on what we hold
  ----------------------------------
  TOTAL P&L                  +187.28
  final inventory                 +2  units  (flat = 0)
================================================================
```

The naive maker, with no skew, lets a run of one-sided noise stack inventory
into a huge short it never chose:

```
NAIVE maker inventory (skew OFF -> wanders off and STAYS off):
   +138 |
    +92 |
    +46 |
     +0 |***** *** ** *                                             0 (flat)
    -46 |               ********************** ********************
    -92 |                        *                   **************
   -138 |                                                   *
```

```
================================================================
  NAIVE  (no skew -- same spread, same flow)
================================================================
  fills                         1805  (263 toxic / informed)
  spread earned              +249.83  the edge: +half-spread per fill
  adverse-selection loss      -29.52  toxic ticks vs our inventory
  inventory drift             +15.98  fair's wander on what we hold
  ----------------------------------
  TOTAL P&L                  +236.29
  final inventory               -101  units  (flat = 0)
================================================================
```

```
  REFERENCE: P&L +187.28, inventory +2  ->
    PROFITABLE & FLAT -- this is real market making.
  NAIVE:     P&L +236.29, inventory -101  ->
    profitable but NOT flat -- the P&L is a directional bet on leftover
    inventory, not captured spread. One bad tick erases it.
```

---

## The honest verdict

Read those two scoreboards together, because the lesson is *not* "bigger P&L
wins":

- **The reference maker ended PROFITABLE and FLAT** — **+187.28** P&L with just
  **+2** units of inventory. Look at the decomposition: **+202.68** of captured
  spread, lightly eroded by **−13.02** of adverse selection and **−2.38** of
  inventory drift. That is real market making — the money is the spread, and
  there is almost no leftover risk on the books.
- **The naive maker "won" on the headline number** — **+236.29 > +187.28** — and
  it is a *trap*. It ended on **−101** units of inventory, a short it never
  decided to put on. A chunk of that P&L is the **+15.98** inventory-drift line:
  fair happened to fall a little while it was short, so the bet paid. That
  number is a **coin-flip on the next move, not spread it earned.** Re-seed the
  world and the same −101 short can flip to a deep loss. Its higher P&L is more
  risk, not more skill.

> **Same spread, same flow, same seed — the only difference is the skew.** The
> skew didn't change *who* traded; it changed the maker's *prices* so the market
> handed its inventory back. That is the entire point of L19, and it is what
> separates a market maker from a gambler who happens to be standing at the book.

### The edge is thin — and it dies

The reference numbers are deliberately *modest*. Spread earned (+202.68) over
1,837 fills is barely **+0.11 per fill** — roughly the half-spread, minus what
the skew gives up and what toxic flow takes back. That is the honest size of the
edge. It survives at 15% informed flow; it does **not** survive everything:

- **Quote too tight** and toxic takers find your quote attractive — adverse
  selection swamps the thin spread and P&L goes negative.
- **Quote too wide** and `fills` collapses — you're flat and safe and earning
  nothing.
- **Turn informed flow up** (TRY IT #3) and past some toxicity *no* (spread,
  skew) pair stays profitable. The flow is simply poison; real desks refuse to
  quote names with too much informed flow.

There is no free money on this side of the book either. The maker's only edge is
the spread it quotes, and inventory risk and adverse selection erode it from both
sides. Owning that is the whole of Track 2.

---

## Now you try (the capstone challenge 🏆)

In [`22_capstone.py`](22_capstone.py)'s **TRY IT** block — tune only
`HALF_SPREAD` and `SKEW`, and beat the reference while staying profitable *and*
flat:

1. **Widen the spread.** Set `HALF_SPREAD = 0.12`. Spread-per-fill rises and
   adverse-selection loss shrinks — but `fills` drops. Find where wider stops
   helping.
2. **Skew harder, then not at all.** `SKEW = 0.03`, then `0.0`. Watch inventory
   pin to flat, then run away (that's the naive maker).
3. **Turn up the toxicity.** `INFORMED_FRAC = 0.30`, then `0.45`, and re-tune.
   Find roughly where the edge dies — where no quote keeps you profitable.
4. **Robustness.** Loop `SEED` over 1..10 and count how many end profitable AND
   flat. A real edge survives most worlds.
5. **The real boss.** Find one `(HALF_SPREAD, SKEW)` that ends profitable AND
   flat across a *majority* of seeds 1..10 at `INFORMED_FRAC = 0.20`. Manage it
   and you've built what an HFT market-making desk does for a living. If you
   can't — now you understand why the spread, thin as it is, is the only thing
   between the maker and ruin.

Either outcome is a pass. The capstone's job isn't to hand you a money-printer;
it's to make you understand the dual objective that defines the job.

---

## 🏆 The course is complete — both tracks, one idea

You started Track 1 as the **customer**: you *paid* the spread on every trade
and watched it, plus funding and slippage, quietly eat a thin, uncertain edge.
You ended [Lesson 11](11_capstone.md) unable to reliably beat buy-and-hold after
costs — and understanding *why* "the large majority of retail accounts lose
money."

Then you flipped seats. In Track 2 you built the **machine** — the order book,
the matching engine, the market maker — and *earned* that very spread. And here
at the end you've learned the catch: earning the spread is just as hard from
this side, eroded by inventory risk and adverse selection, with no free money
either.

The two tracks are the same coin:

- **The spread you paid in Track 1 is the spread you earned here.** Same number,
  opposite sign. Your cost was the maker's revenue; the maker's revenue is
  someone's cost.
- **The informed trader was your *signal* in Track 1** — the faint, hard-to-see
  reason markets aren't perfectly random — **and your *hazard* here**: the toxic
  flow that picks off your quotes. Same people, opposite seat. (You met this
  exact duality back in [Lesson 0](00_foundations.md); now you've built both
  ends of it.)

Markets are *nearly* random and costs are *certain* — on **both** sides of the
book. That, in one sentence, is the whole course.

---

**Next:** there is no next. 🏆 Head back to the **[course index](index.html)**,
or revisit where it all began — 🟢 **[Track 1, Lesson 1: What is a price?](lesson_01.html)** —
now that you've seen what's underneath the number.

*Reference: Á. Cartea, S. Jaimungal & J. Penalva, **Algorithmic and
High-Frequency Trading** (Cambridge, 2015).*
