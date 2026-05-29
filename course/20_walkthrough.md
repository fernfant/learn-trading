# Lesson 20 — Latency & the queue: why microseconds pay

> Track 2 · cumulative artifact: [`../exchange.py`](../exchange.py) · code for
> this lesson: [`20_latency.py`](20_latency.py) ·
> interactive: [`html/lesson_20.html`](html/lesson_20.html)

Lesson 15 gave the order book its iron rule: **price-time priority**. Best price
wins; at the *same* price, whoever arrived *first* sits at the front of the
queue and fills first. Lesson 18 put a market maker on top, earning the spread.
Lesson 19 made it skew quotes to control inventory. This lesson asks a question
those left open: when two makers quote the **exact same price**, who actually
gets the trade?

The answer is **whoever's order got there first** — and that is decided by
**latency**. Speed is money.

## Latency, modeled as a place in line

We don't simulate wall clocks or threads. We model latency the way the queue
actually cares about it: as an **effective arrival number**. A maker with lower
latency has its quote land sooner, so it sits earlier in the queue.

```python
class Maker:
    def __init__(self, name, latency):
        self.latency = latency        # microseconds; LOWER = faster = earlier in queue
    def effective_seq(self):
        return self.latency           # the smaller this is, the closer to the front
```

That's the whole trick. `seq` in `exchange.py` was a global arrival counter;
here `latency` *is* the arrival stamp. Lower latency ⇒ earlier effective seq ⇒
front of the queue ⇒ you win the fill.

## Awarding the flow

A naive model gives every fill to the single fastest maker. That's true at one
price level with one order, but over a stream it's too harsh. The realistic
model gives each maker a **share of the flow proportional to its speed**, where
speed is just `1 / latency`:

```python
speeds = [1.0 / m.latency for m in makers]   # faster => higher speed
# pick the winner of each order with probability proportional to speed
```

This is the same shape as `exchange.py`'s L20 line, `share = speed/(speed+rival)`
— just expressed through latency instead of a raw speed number.

## Part A — same price, 10× the speed, ~10× the flow

Two makers quote `fair ± 0.05`. Identical prices. Fast has latency 1; Slow has
latency 10. Over 5000 orders:

```
    maker   latency(us)    fills     share        P&L
    Fast              1     4526     90.5%     227.54
    Slow             10      474      9.5%      28.63
```

Nobody out-quoted anyone. **The prices were identical.** A 10× lower latency
won Fast about 10× the fills and 10× the captured spread. Speed alone decided
who traded. That single fact is the entire reason HFT exists.

## Part B — halve your latency, double your share

Hold one maker at latency 1; sweep the other from 16 down to parity:

```
     our latency(us)  rival latency(us)   our fill share
                  16                  1             6.6%
                   8                  1            11.7%
                   4                  1            19.9%
                   2                  1            33.7%
                   1                  1            49.4%
```

Each halving of latency roughly **doubles** your share of the flow, until you
hit parity at 50/50. Read this table as a business case: every microsecond you
shave buys measurably more flow, and more flow means more spread captured. That
is why firms pay for **co-location** (a server rack *inside* the exchange, so the
cable is short) and **microwave links** (light through air beats light through
glass fibre) — the story Michael Lewis tells in *Flash Boys*.

## Part C — an ultra-fast maker dominates

Crank the gap to 50×: HFT at 1µs vs everyone else at 50µs.

```
    HFT  wins  4901 fills (98.0%)  P&L   236.60
    Rest wins    99 fills ( 2.0%)  P&L     0.72
```

A big enough speed edge is winner-take-almost-all. A handful of co-located firms
capturing the lion's share of market-making flow is not a conspiracy — it falls
straight out of price-time priority.

## Part D — speed also lets you RUN AWAY

Winning good flow is only half the prize. The other half is **dodging bad flow
by cancelling fast.** Fair value is about to jump +0.30; both makers are resting
a stale ask at 100.05; informed buyers are about to lift it. There are 5µs of
warning:

```
    Fast  (latency  1us): CANCELS in time -> quote pulled, dodges the hit. Loss avoided $0.00
    Slow  (latency 10us): too SLOW to cancel -> sells 100.05, fair jumps, loses $0.30
```

The fast maker pulls its quote inside the warning window and avoids the loss.
The slow maker is still sitting there and gets picked off — a preview of
**adverse selection** (Lesson 21). Both edges — *win more* good flow and *eat
less* bad flow — push the same direction: **faster is richer.**

## How this maps onto `exchange.py`

The cumulative artifact already carries the maker's `speed` field and the L20
flow-split line `share = mm.speed / (mm.speed + rival_speed)`. This lesson is
the same idea expressed as **latency** (`speed = 1/latency`), so you can see the
queue mechanism directly: lower latency ⇒ earlier in line ⇒ bigger share. Run
both and confirm the curves agree — `1/latency` here, raw `speed` there.

## The honest caveat

There is still no free money. Speed shifts *who* earns the spread, but the speed
itself costs a fortune — the racks, the fibre, the microwave towers, the
engineers. The arms race competes that edge away too: when everyone is fast,
nobody is fast. The spread is still the only edge; latency just decides whose
hand it lands in.

## Try it (in [`20_latency.py`](20_latency.py))

1. **Parity.** Set Slow's latency to 1 in Part A. Fills and P&L split ~50/50 —
   with no speed edge the spread is shared evenly.
2. **Ultra-fast.** In Part C set Rest's latency to 200. HFT's share climbs
   toward ~99%: a big enough gap is winner-take-almost-all.
3. **No warning.** In Part D set `WARN_US = 0`. Now even the fast maker can't
   cancel in time and *both* eat the move — when the jump is a surprise, only a
   wider spread protects you.
4. **Three-way race.** Pass three makers at latencies 1, 2, 4. Their shares come
   out ~ proportional to `1/latency` (4 : 2 : 1).

---

**Next:** [Lesson 21 — Adverse selection: toxic flow runs you over](21_adverse_selection.py)
— the slow maker in Part D just got picked off. Now meet the traders who do it
on *purpose*: informed flow that knows which way the price is about to jump, and
why filling them turns your spread into a loss.
