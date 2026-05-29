# Lesson 14 — A market order eats the book

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for this
> lesson: [`14_market_order.py`](14_market_order.py) ·
> interactive: [`html/lesson_14.html`](html/lesson_14.html)

Lesson 13 built the **order book** — two sorted lists of resting orders that
just sat there. Nobody had crossed the spread. Now someone arrives who doesn't
want to wait: they send a **market order**.

A market order names no price. It says **"fill me NOW, whatever it costs."** It
consumes the book from the best price outward. A small order is swallowed at the
top; a big order **walks the book** and pays a worse *average* price than the
top-of-book. That gap is **slippage** — and now you'll see it from the inside.

## The book we'll eat

We only need the **ask** side (the sellers), because we're going to *buy* from
it. Asks are sorted cheapest-first — a buyer always takes the cheapest seller
available first:

```
   100.02  x4      <- best ask: the price you "see"
   100.03  x6
   100.05  x3
   100.08  x10
```

The number you'd quote as "the price" is `100.02`. But that price is only good
for the **4 units** resting there. Want more? You reach up the ladder.

## Walking the book

The whole lesson is one loop. To fill a market BUY of `size` units, walk the
asks cheapest-first and eat as much of each level as you still need:

```python
def fill_market_buy(asks, size):
    remaining = size
    fills = []
    cost = 0.0                          # total money spent = sum(price * qty)
    for price, avail in asks:
        if remaining <= 0:
            break
        take = min(remaining, avail)    # eat what we need, or all of this level
        fills.append((price, take))
        cost += price * take
        remaining -= take
    filled = size - remaining
    vwap = cost / filled if filled > 0 else None
    return fills, vwap, filled
```

- `take = min(remaining, avail)` is the heart of it: if this level has enough,
  we take only what we need and stop; if not, we take all of it and move on to
  the next (worse) price.
- `vwap` is the **volume-weighted average price** — total money spent divided by
  units filled. It's the *real* price you paid, not the sticker price at the top.
- `filled` may be **less than `size`** if the book runs dry. A market order can't
  conjure liquidity that isn't there.

## A small order: no slippage

Buy 3 units. The top level has 4, so the whole order fits there:

```
SMALL ORDER
   market BUY 3 units (best ask is 100.02)
      ate  3 @ 100.02
   average fill (VWAP) = 100.0200
   slippage vs best ask = +0.0000 per unit ($+0.00 total on 3 units)
```

VWAP equals the best ask exactly. You stayed inside the top level, so you paid
the price you saw. **Slippage = 0.**

## A large order: walking down costs you

Now buy 12 units. The top level only has 4 — so the order *walks* down:

```
LARGE ORDER
   market BUY 12 units (best ask is 100.02)
      ate  4 @ 100.02
      ate  6 @ 100.03
      ate  2 @ 100.05
   average fill (VWAP) = 100.0300
   slippage vs best ask = +0.0100 per unit ($+0.12 total on 12 units)
```

Eat 4 at `100.02`, then 6 at `100.03`, then 2 of the 3 at `100.05`. Total spent
is `4×100.02 + 6×100.03 + 2×100.05 = 1200.36`, over 12 units → **VWAP 100.03**.

You *saw* `100.02` but you *paid* `100.03` on average. That extra **`+0.0100`
per unit** is slippage — `$0.12` on the whole order. Nobody charged it as a fee;
the order simply ran out of cheap sellers and reached up for more.

> **This is the Track 1 slippage, explained.** In [Lesson 9](09_walkthrough.md)
> you paid slippage as a capital.com customer and just had to accept it. Here is
> the mechanism: your fill walked the book. Same number, seen from the other seat.

## Thinner book, same order: more slippage

Halve the size at every level and refill the same 12 units:

```
THINNER BOOK (half the size at each level):
   100.02  x2
   100.03  x3
   100.05  x1
   100.08  x5
      ate  2 @ 100.02
      ate  3 @ 100.03
      ate  1 @ 100.05
      ate  5 @ 100.08
   average fill (VWAP) = 100.0527
   slippage vs best ask = +0.0327 per unit  (worse than the fat book above)
```

Same order, but now it has to walk all the way to `100.08` to fill — slippage
jumps from `+0.0100` to `+0.0327`. **Liquidity** (how much size rests near the
top) is exactly what protects a big order from slippage.

## The two rules

1. **Bigger order → walks deeper → more slippage.** (Try a 20-unit order.)
2. **Thinner book → less at each level → more slippage for the same order.**

Both are the same underlying fact: a market order trades *certainty of execution*
for *no control over price*. It will always fill (until the book runs dry), but
the price it pays depends entirely on how deep the book is.

## What you built

[`../exchange.py`](../exchange.py) gains `match_market(side, size)`, which walks
the levels exactly like `fill_market_buy` above and returns the fills plus the
VWAP. A market BUY eats the asks; a market SELL hits the bids and walks down
(slippage there is `best_bid − vwap`). The book no longer just sits — it can be
consumed.

## Try it (in [`14_market_order.py`](14_market_order.py))

1. Make the order **bigger**: `show_fill("HUGE", 20)`. It walks all four levels
   and the VWAP climbs again — bigger order, more slippage.
2. Make the book **thinner still**: set every level to `(p, 1)`, then refill 12.
   The book runs *dry* before the order fills — `filled` is less than 12.
3. Make the book **deeper**: edit `ASKS[0]` to `(100.02, 24)`. The 12-unit order
   now fits entirely at the top and slippage drops back to zero. Depth at the top
   is what kills slippage.
4. Write the mirror `fill_market_sell(bids, size)`: a market SELL hits the
   *highest* bid first and walks down. Slippage becomes `best_bid − vwap`.

---

**Next:** [Lesson 15 — A limit order rests (price-time priority)](15_limit_order_rests.py)
— instead of eating the book, you *add* to it, and discover why your place in the
queue decides whether you ever get filled.
