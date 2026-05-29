# Lesson 18 — Be the market maker: quote both sides, earn the spread

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for this
> lesson: [`18_market_maker.py`](18_market_maker.py) ·
> interactive: [`html/lesson_18.html`](html/lesson_18.html)

This is the payoff of Track 2. You built the order book (L13), watched market
orders eat it (L14), rested limit orders in a queue (L15), wired the matching
loop (L16), and read the tape an HFT sees (L17). Now you sit in the seat that
actually makes money — the one capital.com sits in for *its* users.

The promise from Lesson 12 was: **the spread flips from cost to revenue.** This
lesson is where you collect.

## The whole idea in two prices

A market maker does **not** predict direction. It posts two resting limit orders
straddling a **fair value** (the mid):

```python
bid = fair - h     # a little BELOW fair: "I'll BUY here"
ask = fair + h     # a little ABOVE fair: "I'll SELL here"
```

`h` is the **half-spread**; the full spread you quote is `2*h`. Then you wait.

- A **buyer** comes in and lifts your **ask** → you **sell** at `fair + h`.
- A **seller** comes in and hits your **bid** → you **buy** at `fair - h`.

If one of each arrives, you **bought at `fair-h` and sold at `fair+h`** — you
pocketed the full spread `2*h` without ever guessing which way the price would
go. That is the exact spread you *paid* as a customer in Lesson 2 and totted up
as a cost in Lesson 9. Same number, opposite sign.

## The three numbers that are the whole job

`MarketMaker` tracks exactly three things:

| | What it is | Sign convention |
|---|---|---|
| **cash** | money in/out so far | a **sell** adds cash, a **buy** spends it |
| **inventory** | net units held | `+` = long (bought > sold), `−` = short |
| **P&L** | `cash + inventory * fair` | cash plus open inventory marked at fair |

`pnl()` is the honest scoreboard — it's Lesson 4's *equity* idea wearing a
market-maker hat. When you're perfectly **flat** (`inventory == 0`), P&L is pure
captured spread. When you're holding inventory, P&L includes the live risk on
that position, marked at the current fair value.

```python
def on_buy(self, fair):       # taker BUYS -> lifts our ASK -> we SELL
    _, ask = self.quote(fair)
    self.cash += ask
    self.inventory -= 1       # selling makes us shorter

def on_sell(self, fair):      # taker SELLS -> hits our BID -> we BUY
    bid, _ = self.quote(fair)
    self.cash -= bid
    self.inventory += 1       # buying makes us longer
```

Note the inversion that trips everyone up the first time: when a customer
**buys**, the maker **sells** — you always take the *opposite* side of the
taker's trade. Their buy is your short.

## Part A — one clean round trip

Fair value sits flat at 100. We quote `bid 99.95 / ask 100.05` (spread 0.10). A
seller hits the bid, then a buyer lifts the ask:

```
we quote:  bid 99.95  /  ask 100.05   (spread 0.10)
a SELLER hits our bid -> we BUY 1 @ 99.95  (inv +1, cash -99.95)
a BUYER lifts our ask -> we SELL 1 @ 100.05  (inv +0, cash +0.10)

flat again (inv +0), and P&L = +0.10 — the full 0.10 spread.
```

Bought low, sold high, ended flat, **+0.10** richer — the full `2*h` spread. We
never had an opinion about the price. We just stood in the middle and got paid
for it.

## Part B — balanced flow: the spread adds up

Now let random flow arrive: each step a taker shows up, 50/50 a buyer or a
seller, while fair value slowly wanders. Because buys and sells roughly balance,
inventory stays near zero and the spread piles up:

```
   step    fair   side   inv    cash      P&L
      1   100.01  buy     -1   +100.06    +0.05
     40    99.93  sell    +4   -398.00    +1.74
     80    99.92  sell   +10   -995.98    +3.17
    120   100.05  sell   +14  -1393.39    +7.28
    160    99.98  sell   +10   -990.87    +8.95
    200    99.86  sell    +4   -390.00    +9.44

   200 fills, ending inventory +4 (near flat).
   P&L = +9.44  ~=  200 fills x half-spread 0.05 = 10.00 ideal.
```

Two things to read off this:

- **The P&L climbs steadily** — about half a spread per fill (`fills * h`). The
  ideal is `200 × 0.05 = 10.00`; we land at **+9.44**. The small shortfall is
  the live mark on whatever inventory we happen to be holding when the music
  stops (here, +4 units), plus the wander in fair value. Get flat and it
  resolves to near the ideal.
- **`cash` is wildly negative and totally misleading.** At step 120 cash reads
  −1393 — that's just because we'd been net *buying*; we're holding +14 units
  worth ~+1400. Cash alone is a trap (Lesson 4 again: balance ≠ equity). Only
  `cash + inventory*fair` tells the truth.

No prediction anywhere. We earned the **spread**, one fill at a time.

## Part C — the honest catch: one-sided flow

Here's the part the brochures skip. Run 50 **buyers in a row** — not one
seller — and let all that buying drag fair value up:

```
   step    fair   inv     cash      P&L
      1   100.03    -1   +100.08    +0.05
     20   100.60   -20  +2007.30    -4.70
     40   101.20   -40  +4026.60   -21.40
     50   101.50   -50  +5040.75   -34.25
```

Every fill lifts our ask, so we keep **selling**, and our inventory marches to
**−50** — we're badly **short**. We collected the half-spread on every single
fill (cash looks fantastic at +5040), yet **marked P&L is −34.25 and falling**.
The spread we "earned" is dwarfed by the loss on a short position we never
wanted, into a price running the wrong way.

> A market maker that ignores inventory doesn't earn the spread — it gets run
> over by it.

This is the setup for the rest of Track 2:

- **Inventory risk** — lean (skew) your quotes when you're holding too much, to
  attract the offsetting flow. **Lesson 19** (Avellaneda–Stoikov).
- **Adverse selection** — the one-sided flow in Part C isn't random bad luck; it
  can be *informed* traders (Lesson 0's signal, now your nightmare) who only
  trade with you when they're right. **Lesson 21** (Glosten–Milgrom, Kyle).

## How this maps to capital.com

This *is* capital.com's business model (see [`capital_com.md`](capital_com.md)).
It quotes you a buy and a sell, takes the other side of your trade, and earns
the spread — exactly Part A. And it manages the Part C risk across thousands of
customers whose flow mostly nets out. You're now building, in code, the machine
you traded against in Track 1.

## What this adds to `exchange.py`

The cumulative artifact grows a `MarketMaker` whose `quote(mid)` posts a
`bid = mid - h` and `ask = mid + h` as two resting limit orders, and whose fills
update `cash` and `inventory` exactly as above. The matching loop from Lesson 16
is what actually crosses an incoming taker against those resting quotes; the
maker just sits there, quoting both sides, and books the spread.

## Try it (in [`18_market_maker.py`](18_market_maker.py))

1. **Widen** the spread: `HALF_SPREAD = 0.10`, re-run Part B. More profit per
   fill — but in a real book a wider quote sits further from fair and gets hit
   *less* often. More per fill, fewer fills. The interactive page lets you feel
   that trade-off live.
2. **Narrow** it: `HALF_SPREAD = 0.01`. Thinner margin; you'd need far more flow
   to make the same money. This razor is the market maker's daily decision.
3. In Part B, tilt the flow (`0.5` → `0.6` so buyers slightly outnumber
   sellers). Inventory drifts one way and P&L wobbles — a gentle preview of
   Part C.
4. In Part C, flip to 50 **sellers** (`mm.on_sell`, `fair -= 0.03`). You go
   **long** into a falling price — the mirror-image blow-up.

---

**Next:** [Lesson 19 — Inventory risk: skew your quotes](19_inventory_skew.py)
— Part C showed the wound. Lesson 19 is the cure: when you're holding too much,
lean your bid and ask to *pull in* the flow that flattens you back out.
