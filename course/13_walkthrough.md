# Lesson 13 — The order book: bids, asks, depth & the spread

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for
> this lesson: [`13_order_book.py`](13_order_book.py) ·
> interactive: [`html/lesson_13.html`](html/lesson_13.html)

Lesson 12 flipped your seat: you stopped *paying* the spread and started
*earning* it. But to earn it you need the machine that produces a price in the
first place. Here it is, and it's simpler than you'd guess:

> **An order book is just two sorted lists.**

That's not a simplification for beginners — that genuinely is what an exchange
keeps. Everything else (matching, market makers, latency) is built on top of
these two lists.

## The two lists

- **BIDS** are the **buyers**. Each one is saying *"I'll buy this much, and I'll
  pay up to this price."* We sort them **highest price first**, because the
  buyer offering the most is the best one to sell into.
- **ASKS** are the **sellers**. Each says *"I'll sell this much, for at least
  this price."* We sort them **lowest price first**, because the cheapest seller
  is the best one to buy from.

In `13_order_book.py` each order is just a `(price, size)` pair, and adding one
re-sorts its list so the best price stays on top:

```python
def add_bid(self, price, size):
    self.bids.append((price, size))
    self.bids.sort(key=lambda o: -o[0])   # highest price first

def add_ask(self, price, size):
    self.asks.append((price, size))
    self.asks.sort(key=lambda o: o[0])    # lowest price first
```

The `-o[0]` is the only difference between the two: bids sort *descending* by
price, asks *ascending*. The top of each list is then trivially the best:

```python
def best_bid(self): return self.bids[0][0] if self.bids else None
def best_ask(self): return self.asks[0][0] if self.asks else None
```

## The spread and the mid

Two numbers fall straight out of the tops of the lists:

```python
def spread(self): return self.best_ask() - self.best_bid()
def mid(self):    return (self.best_bid() + self.best_ask()) / 2
```

- The **spread** is the gap you must cross to trade *right now*. To buy
  immediately you pay the best ask; to sell immediately you take the best bid.
- The **mid** is the fair point halfway between. You can **never actually trade
  at the mid** — but it's the reference everyone quotes around. And here's the
  payoff: **that mid is exactly the single "price" `market.py` used in Track 1.**
  Track 1's whole world was one number; it lived right here, dead center between
  the best buyer and the best seller.

## The book as you find it

The script seeds the same resting orders [`../exchange.py`](../exchange.py)
starts with — the stack already sitting there when you arrive — and prints an
ASCII *ladder*: asks on top, bids below, spread in the middle. The `#` bars are
**depth** (one `#` per unit of size):

```
         ASKS (sellers, cheapest nearest the spread)
     100.05  x3   ###
     100.03  x6   ######
     100.02  x4   ####
   -------- spread 0.04 · mid 100.00 --------
      99.98  x5   #####
      99.97  x2   ##
      99.95  x8   ########
         BIDS (buyers, most generous nearest the spread)
   best bid 99.98 | best ask 100.02 | spread 0.04 | mid 100.000
```

Best bid **99.98**, best ask **100.02**, so the spread is **0.04** and the mid
sits exactly at **100.00**. To trade now you cross that gap: buy at 100.02 or
sell at 99.98.

## A better bid tightens the book

Now a more generous buyer posts a bid at **100.01** — above the old best of
99.98. They jump to the top of the bids; the best ask hasn't moved, so the gap
shrinks:

```
   -------- spread 0.01 · mid 100.02 --------
     100.01  x1   #
      99.98  x5   #####
   best bid 100.01 | best ask 100.02 | spread 0.01 | mid 100.015
```

The spread fell from **0.04** to **0.01** — the book got **tighter**. The mid
nudged up to **100.015**, leaning toward the buyers. A tighter book is cheaper
to trade in, and competing to post the best quote is exactly what a market maker
does (Lesson 18).

## Depth: size matters as much as price

Two books can show the *same* best bid and ask yet behave completely
differently, because **depth** — how much size waits at each level — differs. A
thin level gets swept by one order; a deep level absorbs a big order without the
price budging. In our seeded book, 16 units want to buy and 13 want to sell.

Eating through that depth is what moves the price, and the cost of doing so is
**slippage** — the subject of Lesson 14.

## Crossed books and why they can't last

In **Try it #2** you post a bid at 100.10 — *above* the cheapest ask of 100.02.
That buyer is willing to pay more than a seller is asking, so they should trade
**instantly**. Our toy book just stacks the order and `spread()` goes
*negative* (a "crossed" book), which a real exchange never allows. Resolving a
crossed book — turning two willing orders into a trade — is exactly what the
matching engine does in Lessons 14 and 16.

## How this maps to `../exchange.py`

This script is a standalone mini-version of the `OrderBook` class in
[`../exchange.py`](../exchange.py): the same `bids`/`asks` lists,
`best_bid()`/`best_ask()`/`spread()`, and the same `show()` ladder. exchange.py
is the cumulative artifact you grow across Track 2; right now it holds this exact
book, standing still. The lessons that follow set orders flowing through it.

## Try it (in [`13_order_book.py`](13_order_book.py))

1. Add a deep seller `book.add_ask(100.02, 20)`. The best ask *price* is
   unchanged but 24 units now wait at 100.02 — depth changed, top of book
   didn't. Spread and mid stay the same.
2. Add a bid that beats the best ask: `book.add_bid(100.10, 5)`. `spread()` goes
   negative — a crossed book. See why a real book is never in this state.
3. Build a book with only bids. What do `best_ask()`, `spread()` and `mid()`
   return? (`None` — there's no two-sided market.)
4. Open [`../exchange.py`](../exchange.py) — it carries this exact book as its
   seed.

---

**Next:** [Lesson 14 — A market order eats the book](14_walkthrough.md) — send a
real order in, watch it walk down the levels of depth, and feel slippage from
the *inside* for the first time.
