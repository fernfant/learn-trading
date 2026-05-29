# Lesson 16 — The matching engine loop: crossed orders become trades

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for
> this lesson: [`16_matching.py`](16_matching.py) ·
> interactive: [`html/lesson_16.html`](html/lesson_16.html)

Lesson 13 built the book. Lesson 14 had a market order *eat* it; Lesson 15 had a
limit order *rest* in it. Those were two halves of one machine. This lesson
welds them together into the single thing that *is* an exchange: the **matching
loop**. Every order — market or limit, aggressive or patient — runs through the
exact same handful of lines.

## The one rule

The book has two sorted sides (Lesson 13):

- **bids** = buyers, sorted **high → low**, so `bids[0]` is the *best* bid (the
  most anyone will pay).
- **asks** = sellers, sorted **low → high**, so `asks[0]` is the *best* ask (the
  least anyone will take).

Usually there's a gap between them — the **spread** — and nothing happens. A
trade only fires when an incoming order **crosses**: reaches over the gap.

```
a BUY  crosses when its price >= the best ASK   (pays what a seller wants)
a SELL crosses when its price <= the best BID   (takes what a buyer offers)
```

When it crosses, you match. The whole loop, in English:

1. Does the incoming order cross the best opposite level?
2. **Yes** → print a **TRADE** at the **resting order's price** (it was there
   first — price-time priority, Lesson 15). Trade the *smaller* of the two
   sizes. Subtract it from both. Loop back to step 1 — the order might still
   cross the *next* level.
3. **No / nothing left** → whatever size **remains rests** as a new limit, done.

That's it. There is nothing else in an exchange's core.

## The code: `submit()`

The whole lesson is one method. Here's the buy branch (the sell branch is its
mirror image):

```python
while size > 0 and self.asks and self.asks[0][0] <= price:
    ask_price, ask_size = self.asks[0]
    qty = min(size, ask_size)          # trade the smaller of the two
    fills.append((ask_price, qty))     # prints at the RESTING price
    self.trades.append((ask_price, qty))
    size -= qty                        # consume the incoming order
    if qty == ask_size:
        self.asks.pop(0)               # level fully eaten -> remove it
    else:
        self.asks[0] = (ask_price, ask_size - qty)  # partial -> shrink it
if size > 0:
    self._rest_bid(price, size)        # leftover rests as a new bid
```

Read the `while` condition slowly — it's the crossing test:

- `size > 0` — we still have something to fill.
- `self.asks` — there's a seller to fill against at all.
- `self.asks[0][0] <= price` — the **best ask is at or below what we'll pay**.
  This is "crosses". The moment the best ask climbs above our price, the loop
  stops and the leftover rests.

`qty = min(size, ask_size)` is the partial-fill engine: if we want more than
this level holds, we take all of it and loop again; if this level holds more
than we want, we take a slice and it shrinks. Either way, **trades print at
`ask_price`** — the resting order's price, never the incoming order's.

A **market order** (Lesson 14) is just this loop with a price so aggressive it
always crosses. A **non-crossing limit** (Lesson 15) skips the loop entirely and
falls straight to `_rest_bid`. Same code, both behaviours.

## Watch it run

The script seeds the usual book and narrates four orders. Run
`python3 16_matching.py`:

**Start** — best bid `99.98`, best ask `100.02`, spread `0.04`.

**Order 1 — BUY 3 @ 100.00 (rests).** `100.00` is *below* the best ask `100.02`,
so the `while` condition is false on the first check — no cross. The whole order
rests as a new best bid, and the spread tightens from `0.04` to `0.02`.

**Order 2 — BUY 4 @ 100.02 (exact fill).** Now `100.02 <= 100.02` is true: it
crosses the best ask exactly. `min(4, 4) = 4`, so it eats the entire level:

```
TRADE  4 @ 100.02
fully filled -> nothing rests
```

The `100.02` level is gone; the best ask is now `100.03`.

**Order 3 — SELL 6 @ 99.98 (sweeps down 2 levels).** A *sell* crosses while the
best **bid** is `>= 99.98`. The best bid is `100.00 x3` (from Order 1) — that
qualifies, so we take 3 there. Still 3 to go, and the loop checks again: next
best bid is `99.98 x5`, which still qualifies, so we take 3 more:

```
TRADE  3 @ 100.00
TRADE  3 @ 99.98
(2 fills, 6 total — it SWEPT several levels)
```

Notice the two trades printed at **different prices** — each at its own resting
level. The `99.98` level isn't wiped out; it had 5 and we only took 3, so it
shrinks to `x2`.

**Order 4 — BUY 12 @ 100.05 (sweep + leftover rests).** Aggressive enough to
cross both remaining asks. It eats `100.03 x6` then `100.05 x3` — 9 total — and
then the ask side is **empty**, so the loop stops with 3 unfilled:

```
TRADE  6 @ 100.03
TRADE  3 @ 100.05
(2 fills, 9 total — it SWEPT several levels)
leftover 3 did not cross -> RESTS in the book
```

Those 3 rest as a new bid at `100.05`. The book now has *no asks at all* — this
buyer cleared the entire sell side and left their leftover sitting on top.

By the end the **tape** holds 5 trades, every one printed at the price of the
order that was resting when the match happened.

## Why "resting price" matters

The incoming, aggressive order is the **taker** — it crosses the spread and
*takes* liquidity. The order already in the book is the **maker** — it *made*
the price available and waited. The trade prints at the **maker's** price. This
is the Lesson 12 flip made literal: the patient maker sets the terms, the
impatient taker pays them. In Lesson 18 you'll *be* the maker, sitting on both
sides, collecting that spread on purpose.

## What this is in `exchange.py`

This is the `match()` / `submit` core of the cumulative artifact: the loop that
crosses bids against asks into trades and rests any remainder. Lesson 13 gave
`exchange.py` a static book; from here it can *process flow*. Lesson 17 will tap
the stream of trades this loop produces and turn it into **market data** — the
top-of-book, the depth, and the **tape** that an HFT actually watches.

## Try it (in [`16_matching.py`](16_matching.py))

1. **Clear a side.** Add `report("mine", eng, "sell", 99.00, 50)` at the end. A
   sell at `99.00` is `<=` every resting bid, so one loop sweeps the whole bid
   side; the unfilled remainder rests as an ask.
2. **A resting limit.** Add `report("mine", eng, "buy", 99.50, 4)`. It's below
   every ask, can't cross, and just rests — the Lesson 15 case, same loop.
3. **Tune the aggression.** Lower Order 4's `100.05` to `100.02` and re-run: it
   crosses fewer levels and rests sooner. The price you pick decides how *deep*
   you eat before you stop crossing.
4. **Market order = infinite price.** Call `eng.submit("buy", 1e9, 5)`. A price
   that crosses anything available *is* a market order — it walks the book until
   filled or the book runs dry.

---

**Next:** [Lesson 17 — Market data & the tape](17_market_data.py) — the matching
loop spits out trades; now build the view an HFT actually trades against:
top-of-book, depth, and the running tape of prints.
