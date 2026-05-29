# Lesson 17 · Market data & the tape — what an HFT actually sees

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for this
> lesson: [`17_market_data.py`](17_market_data.py) ·
> interactive: [`html/lesson_17.html`](html/lesson_17.html)

You built the matching engine (Lesson 16): crossed orders become trades. But
nobody trading on a real venue stares at the engine's internals. They stare at
a **screen** fed by two streams the exchange pumps out. This lesson is that
screen — the thing a human day-trader *and* a high-frequency bot are actually
looking at when they decide what to do.

## Two feeds, two different questions

| Feed | Also called | What it is | The question it answers |
|---|---|---|---|
| **Book / quote feed** | the **snapshot**, the **depth** | resting liquidity right now: best bid & ask plus the sizes stacked at each level | *Where can I trade, and how much is on offer?* |
| **Trade feed** | the **tape**, "time & sales" | the running list of executed trades: price, size, and which side was the aggressor | *What just happened, and who was impatient?* |

A clean way to hold the difference: **the book is a photograph of intentions;
the tape is a recording of events.** The book shows what people *say* they'll
do (resting orders they could still cancel). The tape shows what they *did* —
trades that already happened and can't be taken back.

## The two feeds in code

The teaching script trims the Lessons 13–16 engine down to exactly what's
needed to *produce* the feeds: a book to rest orders in, a `match_market` that
aggresses across it, and — the new piece — a `tape` list that records every
trade as it happens.

```python
class Book:
    def __init__(self):
        self.bids = []   # buyers, highest price first
        self.asks = []   # sellers, lowest price first
        self.tape = []   # (price, size, aggressor) in time order
```

**The book feed — `snapshot()`** just reads off the top few levels of each side:

```python
def snapshot(self, levels=3):
    return {
        "best_bid": self.best_bid(),
        "best_ask": self.best_ask(),
        "bid_depth": self.bids[:levels],   # top N levels, best first
        "ask_depth": self.asks[:levels],
    }
```

That dict *is* one frame of the quote feed. A real venue rebuilds something
like it on every single message, thousands of times a second.

**The trade feed — the tape** gets written inside `match_market`. Every time an
incoming order takes some size off a level, we append a print:

```python
take = min(remaining, avail)
self.tape.append((price, take, side))   # <-- this line is the trade feed
```

`side` is the **aggressor** — the impatient party who crossed the spread to
make the trade happen. A market BUY eats asks, so its prints are tagged `buy`;
a market SELL hits bids, tagged `sell`. That tag is the single most useful bit
on the tape, and we'll lean on it in Part C.

## Derived signals — what the eye reads off the snapshot

Nobody reads raw numbers; the eye jumps straight to a few derived figures:

```python
mid       = (best_bid + best_ask) / 2          # the fair midpoint
imbalance = bid_size / (bid_size + ask_size)   # how lopsided the top is, 0..1
microprice = (bid_size*best_ask + ask_size*best_bid) / total
```

- **mid** — the obvious "fair" price halfway across the spread.
- **imbalance** — fraction of top-of-book size sitting on the **bid**. Above
  `0.50` means buyers are stacked deeper than sellers (pressure leaning up).
- **microprice** — the mid, nudged toward the **thinner** side. Note the
  *cross*-weighting: more bid size multiplies the *ask*, pulling the estimate
  **up**. The intuition: price tends to drift toward the side with the smaller
  queue, because that side gets exhausted first.

## Part A — the opening snapshot

Six resting orders make a book; nothing has traded, so the tape is empty. This
is the pure quote feed:

```
        DEPTH (resting liquidity)
   ask   100.05  x3   ###
   ask   100.03  x6   ######
   ask   100.02  x4   ####
   ----  mid 100.000   spread 0.04  ----
   bid    99.98  x5   #####
   bid    99.97  x2   ##
   bid    99.95  x8   ########

   mid        = 100.000
   imbalance  = 0.56  (bid 5 vs ask 4 -> buyers stacked deeper)
   microprice = 100.002  (mid leaning toward the thin side)
   tape is empty — nothing has actually traded.
```

Best bid `99.98 × 5`, best ask `100.02 × 4`. Imbalance is `5 / (5+4) = 0.56` —
buyers slightly deeper, so microprice sits a hair *above* the mid at `100.002`.
The `#` bars make depth obvious at a glance, exactly like the size bars on a
real depth ladder.

## Part B — a burst of flow hits the book

We push a small scripted stream through the engine — mostly buyers today:

```python
flow = [("buy", 2), ("buy", 3), ("sell", 1), ("buy", 4), ("buy", 2)]
```

Each order aggresses and prints to the tape. Afterward both feeds have changed:

```
        DEPTH (resting liquidity)
   ask   100.05  x2   ##
   ----  mid 100.015   spread 0.07  ----
   bid    99.98  x4   ####
   bid    99.97  x2   ##
   bid    99.95  x8   ########

        TAPE (what actually traded)
   BUY <   2 @  100.02
   BUY <   2 @  100.02
   BUY <   1 @  100.03
   SELL>   1 @   99.98
   BUY <   4 @  100.03
   BUY <   1 @  100.03
   BUY <   1 @  100.05

   mid        = 100.015
   imbalance  = 0.67
   last trade = 1 @ 100.05
```

The buying eats clean through the `100.02` and `100.03` ask levels — they're
gone from the depth entirely, leaving only `100.05 × 2` as the best ask. The
mid has climbed to `100.015` and the spread widened to `0.07` because the near
asks were consumed. The tape, read top-to-bottom (oldest to newest), tells the
story: a long run of `BUY <` prints with one lone `SELL>` in the middle.

## Part C — reading the tape

Here's the payoff. We never *told* the program "buyers won." That's something
you **infer** from the feed by tallying the aggressor tags:

```
   buy-aggressor volume  = 11
   sell-aggressor volume = 1
   net pressure          = +10  (buying pressure)
   trade price walked    = 100.02 -> 100.05  (+0.03)
```

Eleven units bought aggressively against one sold, and the trade price walked
*up* the ladder. Nobody labeled this "buying pressure" — you read it off the
tape, cross-checked it against the depth imbalance (`0.67`, buyers deeper), and
inferred it. **That inference is the raw input to every trading decision** a
human or a bot makes. An HFT does exactly this, on dozens of derived signals,
updating on every message — a firehose of snapshots and tape prints. That
firehose *is* what it sees.

## How this maps back to `../exchange.py`

The cumulative artifact gains `snapshot()` (top-of-book + depth) and a `tape`
that records every executed trade with its aggressor side — the two feeds an
exchange publishes. Lessons 13–16 built the machine; Lesson 17 is the **window
into it** that every later lesson's market maker will watch to decide its
quotes.

## Try it (in [`17_market_data.py`](17_market_data.py))

1. **Skew the depth.** Add `book.add_bid(99.99, 30)` before Part B and re-print
   the opening snapshot — imbalance jumps well above `0.50` and the microprice
   leans up toward the ask.
2. **Flip the flow** to mostly sellers and watch Part C report *selling*
   pressure with the price walking down. Now the tape says sellers are in
   control.
3. **Widen the snapshot** with `book.snapshot(levels=5)` — real terminals show
   5–10 levels per side, hinting where big size is hiding.
4. **Add a signal** — spread in ticks, or the queue size at the best bid. An
   HFT watches dozens of these update on every single message.

---

**Next:** [Lesson 18 — Be the market maker: quote both sides, earn the spread](html/lesson_18.html)
— stop *reading* the feed and start *producing* it. You'll post a bid and an
ask of your own and, for the first time, the spread becomes your **revenue**.
