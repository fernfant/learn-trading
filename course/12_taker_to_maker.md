# Lesson 12 · From price-**taker** to price-**maker** — the bridge

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) ·
> interactive: [`html/lesson_12.html`](html/lesson_12.html) ·
> **concept — no code this lesson** (the artifact already runs at its Lesson 13 stage; you'll start editing it next).

This is the hinge of the whole course. Stop. Re-read that. Everything in Track 1
happened from **one seat**; everything in Track 2 happens from the **other one**.
Lesson 12 is the moment you stand up, walk around the table, and sit down across
from your old self.

## The seat you were sitting in

In Track 1 you were the **customer** — a **price-taker**. You never *set* a
price. Two prices were handed to you (the **buy** and the **sell**, Lesson 2),
and to do anything at all you had to **cross the spread**:

- Go long? You pay the higher price (the **ask**).
- Close it? You sell at the lower price (the **bid**).

The gap between them — the **spread** — was a toll you paid on *every* round
trip, before the price moved a single tick. Lesson 4's equity curve started
*below* where you funded it for exactly this reason. Lesson 9 totted it up as a
cost that quietly decides who wins. As a taker, **the spread is your cost.**

## The seat you're moving to

Someone quoted you those two prices. Someone stood ready to sell to you at the
ask and buy from you at the bid, and **pocketed the gap**. That someone is a
**market maker** — a **price-maker**. On capital.com, that someone is
effectively *the broker*. It is the whole business model (see
[`capital_com.md`](capital_com.md)): quote both sides, capture the difference.

Now you take that seat. You post a price to buy *and* a price to sell. When a
taker crosses your spread, you take the **opposite side** of their trade — and
the same gap that was their cost becomes **your revenue**.

> Same number. Opposite sign. **Cost → revenue.** That single flip is what
> Track 2 is about.

## The flip, in one round trip

A customer wants to get in and out. Watch the spread flow:

| | The customer (taker) | The market maker (maker) |
|---|---|---|
| Opens the trade | **buys at the ask** $100.02 | **sells** to them at $100.02 |
| Closes the trade | **sells at the bid** $99.98 | **buys** it back at $99.98 |
| The 0.04 spread | **paid** it → −$0.04 | **earned** it → +$0.04 |
| The spread is… | a **cost** | **revenue** |

It's the exact same four cents. The customer's ledger shows it in red; the
maker's shows it in green. You're no longer betting on *which way* the price
goes — you're earning a fee for *standing in the middle* and providing
liquidity. (The interactive widget lets you sit in either seat and watch the
same trade re-color.)

## "So the market maker just prints money?"

No. And this is the honest catch the rest of Track 2 is about. Earning the
spread is a *fee for a service*, and the service carries two real hazards:

- **Inventory risk** (Lesson 19). When a taker buys from you, you're now
  **short**; when they sell to you, you're **long**. You didn't *want* a
  position — you wanted the fee — but you're holding one anyway, and the price
  can move against it before the next taker shows up to flatten you out.
- **Adverse selection** (Lesson 21). Some takers know something you don't.
  Remember the **informed trader** from Lesson 0 — the faint *signal* you were
  hunting in Track 1? From the maker's seat that same person is your
  *nightmare*: they only trade with you when they're right, so they pick you off
  and your "fee" turns into a loss. **Same people, opposite seat.**

A market maker that ignores these doesn't earn the spread — it gets run over by
it. Staying **profitable AND flat** at the same time is the actual job, and it's
the Lesson 22 capstone.

## The road ahead (Track 2 grows [`../exchange.py`](../exchange.py))

You'll build the machine capital.com is, one piece per lesson:

| # | You build | Why it matters |
|---|---|---|
| 13 | the **order book** — bids, asks, depth, spread | the book *is* the market; the price is just its top |
| 14 | a **market order** eats the book | slippage, seen from the inside |
| 15 | a **limit order** rests in the queue | price-time priority — why your place in line pays |
| 16 | the **matching loop** | crossed orders → trades: the heart of an exchange |
| 17 | **market data & the tape** | top-of-book, depth, trades — what an HFT actually sees |
| 18 | a **market maker** quotes both sides | the seat you took today, in code — earn the spread |
| 19 | **inventory skew** | lean your quotes when you're holding too much |
| 20 | **latency & the queue** | why being a microsecond faster pays |
| 21 | **adverse selection** | the informed flow that runs you over |
| 22 | **capstone** | a market maker that stays profitable *and* flat |

## What changed (no code yet)

Nothing in [`../exchange.py`](../exchange.py) this lesson — it already runs at
its Lesson 13 stage, printing a small resting order book. What changed is *which
side of it you're on*. From here on, the spread is the thing you **collect**, not
the thing you **pay** — and your enemies are inventory and informed flow, not the
broker's fee.

Reference: Larry Harris, *Trading and Exchanges: Market Microstructure for
Practitioners* — the backbone of Track 2, especially its treatment of dealers,
liquidity, and why someone earns the spread.

---

**Next:** [Lesson 13 — The order book (bids, asks, depth, spread)](13_order_book.py)
— stop talking about the spread and *build* the thing that has one. Two sorted
lists, and suddenly there's a market.
