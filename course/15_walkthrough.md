# Lesson 15 — A limit order rests: price-time priority & the queue

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for this
> lesson: [`15_limit_order.py`](15_limit_order.py) ·
> interactive: [`html/lesson_15.html`](html/lesson_15.html)

Lesson 14's **market order** was impatient: *fill me now, at any price.* It ate
the top of the book and paid whatever it had to. A **limit order** is the
opposite temperament:

> **Limit order** = "fill me only at MY price or better — otherwise, wait."

If it can't trade the instant it arrives, it doesn't disappear. It **rests** in
the book and joins a **queue** of orders waiting at prices. The moment a market
order shows up, the exchange must decide *who trades first*. That rule is the
heart of this lesson.

## Price-time priority

Almost every exchange serves resting orders by **price-time priority** — two
rules, in order:

1. **Price first.** A better price is always served first. For buyers, a
   *higher* bid is better (you'll pay more, so you're more eager). For sellers,
   a *lower* ask is better.
2. **Time second.** Among orders at the *same* price, it's **first-in-first-out**
   (FIFO): whoever arrived earlier sits ahead in line.

Rule 2 is the one beginners miss. Your **place in line** — fixed the instant
your order arrives — decides whether you actually get filled, or whether you sit
untouched while the people ahead of you trade.

## Arrival is a counter, not a clock

```python
self.seq = 0
...
self.seq += 1
order = {"who": who, "price": price, "size": size, "seq": self.seq}
```

We stamp each order with an incrementing **sequence number**, not a wall-clock
time. The exchange only cares about the *order* of arrival, and a counter is
exact: two orders can't share a sequence number, so ties are impossible. (Real
matching engines do exactly this — sequence numbers, not timestamps.)

## The one sort that encodes both rules

```python
def _sort(self):
    self.bids.sort(key=lambda o: (-o["price"], o["seq"]))
    self.asks.sort(key=lambda o: (o["price"], o["seq"]))
```

A single tuple key does the whole job. For **bids**, `-price` puts the *highest*
price first; for **asks**, `price` puts the *lowest* first. Then `seq` breaks
ties by arrival, ascending — earliest in front. Index `0` of each list is "first
in line."

## Part A — same price, pure FIFO

Three buyers all bid `99.98`. Price can't separate them, so time does:

```
   #1  Ann   99.98 x5  (arrived #1) <- FRONT
   #2  Bob   99.98 x3  (arrived #2)
   #3  Cara  99.98 x4  (arrived #3)
```

Ann arrived first, so Ann is first in line. Bob and Cara queue behind her in the
order they showed up. Nothing about size or luck matters — only arrival.

## Part B — a better price jumps the queue

Dan arrives **last** but bids `99.99` — a better price. Price beats time, so he
leaps to the very front, ahead of everyone who got there earlier:

```
   #1  Dan   99.99 x2  (arrived #4) <- FRONT
   #2  Ann   99.98 x5  (arrived #1)
   #3  Bob   99.98 x3  (arrived #2)
   #4  Cara  99.98 x4  (arrived #3)
```

Dan bought priority with **price**, not patience. Notice the `99.98` crowd
behind him is *still* in arrival order — being early only matters among orders
at the same price.

## Part C — a market order eats from the front

A market **sell** for 8 units arrives and walks down the bid queue from the
front until it's filled:

```
   filled 2 from Dan @ 99.99  (was arrival #4)
   filled 5 from Ann @ 99.98  (was arrival #1)
   filled 1 from Bob @ 99.98  (was arrival #2)
```

```python
front = book.bids[0]
take = min(remaining, front["size"])
front["size"] -= take
remaining -= take
if front["size"] == 0:
    book.bids.pop(0)            # fully filled — leaves the queue
```

Dan (best price) fills completely; Ann (earliest at `99.98`) fills completely;
Bob gets a **partial** — 1 of his 3 — then the order runs dry. What's left:

```
   #1  Bob   99.98 x2  (arrived #2) <- FRONT
   #2  Cara  99.98 x4  (arrived #3)
```

**Cara never traded.** Same price as Ann and Bob, but she arrived last and the
market order ran out before reaching her. Her miss was decided the instant she
posted — by her place in the queue. That's price-time priority made tangible,
and it's why HFTs fight over microseconds (Lesson 20): a better spot in line is
the difference between trading and waiting.

## How this shows up on capital.com

When you place a **limit order** on capital.com (Lesson 6's order menu), this is
where it goes — it rests in the exchange's book until the price comes to it. The
platform doesn't show you the queue, but you're in one, and your place decides
whether a touch on your price actually fills you.

## What you built

[`../exchange.py`](../exchange.py) gets `add_limit(side, price, size)`: it stamps
each resting order with the next sequence number and inserts it into `bids` or
`asks` in price-time priority — the exact sort above. The book now *remembers
arrival order*, which is everything the matching loop needs next.

## Try it (in [`15_limit_order.py`](15_limit_order.py))

1. Add a 4th buyer at `99.98` and re-run — the queue stays in pure arrival
   order. Earlier `seq` = earlier in line, every time.
2. Post at a *better* price (`book.add_limit("buy", "You", 100.00, 10)`) to leap
   to the front, ahead of Dan.
3. Post *late* at the *same* price as the crowd, then run Part C — you sit at the
   back and the market order runs out before it reaches you.
4. Make the market sell bigger (`size=20`) — it clears the whole bid queue, and
   any leftover would rest as a new ask. Resting leftovers is exactly what the
   matching loop handles next.

---

**Next:** [Lesson 16 — The matching engine loop](16_matching.py) — stop hand-firing
orders. Crossed bids and asks meet automatically and turn into trades: the
beating heart of an exchange.
