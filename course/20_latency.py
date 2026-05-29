"""
LESSON 20 — Latency & the queue: why microseconds pay (Track 2: inside the exchange)

In Lesson 15 you learned the iron rule of a limit-order book: PRICE-TIME
PRIORITY. At the same price, whoever's order ARRIVED FIRST sits at the FRONT of
the queue and gets filled first. Everyone behind them only trades if the order
in front doesn't soak up all the incoming size.

That one rule turns SPEED into money. Two market makers can quote the EXACT
same price. The faster one's order reaches the exchange sooner, so it lands
nearer the front of the queue, so it wins a bigger share of every incoming
order. Same price, same quote — but the fast maker simply trades MORE.

Speed pays a second way too: CANCELS. When fair value is about to move, a maker
wants to yank its stale quote before flow runs it over. The fast maker cancels
in time and dodges the hit; the slow maker is still sitting there and eats it.

This is the entire economic engine behind co-location (renting a rack INSIDE
the exchange so your cable is shorter) and microwave links between Chicago and
New Jersey (light through air beats light through glass). Firms spend fortunes
to shave microseconds. Michael Lewis tells the story in *Flash Boys*.

We model latency the honest way: as an effective arrival number. Lower latency
=> your order is stamped with an EARLIER effective sequence number => you sit
ahead in the queue => you win the fill. No wall clock, no threads — just a
deterministic, seeded race so the numbers match the walkthrough.

Run it:  python3 20_latency.py
Then read 20_walkthrough.md.
"""

import random

# A seed makes the random flow repeat identically every run, so the numbers
# below match the walkthrough exactly. Change it for a different market.
random.seed(20)

HALF_SPREAD = 0.05      # both makers quote fair +/- this (same price, L18)
SIZE_PER_ORDER = 1      # each incoming order is for 1 unit, kept simple


# =============================================================================
# A MARKET MAKER WITH A LATENCY
# =============================================================================
# Same idea as exchange.py's MarketMaker, trimmed to what this lesson needs.
# The new field is `latency`: a delay (in microseconds, say) between deciding
# to quote and the quote actually landing on the book. LOWER latency is better.
class Maker:
    def __init__(self, name, latency):
        self.name = name
        self.latency = latency   # microseconds of delay; lower = faster = earlier in queue
        self.fills = 0           # how many incoming orders this maker won
        self.cash = 0.0          # realized cash from fills
        self.inventory = 0       # +long / -short units held

    # When an order arrives at time `t`, a maker's quote is effectively already
    # in the queue if it was sent early enough. Its EFFECTIVE arrival stamp is
    # just its latency: the smaller the latency, the earlier it sits. So the
    # maker with the SMALLEST latency is at the FRONT of the queue.
    def effective_seq(self):
        return self.latency

    def on_fill(self, side, price, size):
        # The taker BOUGHT from us -> we SOLD: cash up, inventory down.
        # The taker SOLD to us     -> we BOUGHT: cash down, inventory up.
        if side == "buy":
            self.cash += price * size
            self.inventory -= size
        else:
            self.cash -= price * size
            self.inventory += size
        self.fills += 1

    def pnl(self, fair):
        # Realized cash plus inventory marked at fair value.
        return self.cash + self.inventory * fair


# =============================================================================
# THE RACE — a stream of marketable flow, awarded by queue position
# =============================================================================
# Each step: an order arrives wanting to trade NOW at the quoted price. Both
# makers quote that same price, so PRICE is a tie. TIME breaks the tie: the
# maker further in front of the queue (lower latency) wins. Rather than have
# the single fastest maker win EVERY order, each maker wins a SHARE of the flow
# proportional to how far in front it sits. We turn each maker's speed
# (= 1/latency) into a probability of being first to the order. That produces
# the smooth "fill share rises as you lower latency" curve, and it is exactly
# the shape of exchange.py's L20 line, share = speed/(speed+rival).
def run_race(makers, steps=5000, seed=1):
    rng = random.Random(seed)
    fair = 100.0
    speeds = [1.0 / m.latency for m in makers]   # faster (lower latency) => higher speed
    total = sum(speeds)
    for _ in range(steps):
        side = rng.choice(["buy", "sell"])
        # Pick the winner with probability proportional to speed.
        r = rng.random() * total
        acc = 0.0
        winner = makers[-1]
        for m, sp in zip(makers, speeds):
            acc += sp
            if r <= acc:
                winner = m
                break
        price = fair + HALF_SPREAD if side == "buy" else fair - HALF_SPREAD
        winner.on_fill(side, price, SIZE_PER_ORDER)
        fair += rng.gauss(0, 0.01)
    return fair


# =============================================================================
# DEMO
# =============================================================================
print("=" * 70)
print("  LESSON 20 — LATENCY & THE QUEUE (why microseconds pay)")
print("=" * 70)

# ---- Part A: two makers, same price, different latency ----------------------
print("\n[A] SAME PRICE, DIFFERENT SPEED — who sits at the front of the queue?\n")
print(f"Both makers quote fair +/- {HALF_SPREAD:.2f}. IDENTICAL prices. The only")
print("difference is latency: Fast is 1 microsecond, Slow is 10. Price-time")
print("priority means the lower-latency order sits in FRONT and wins the flow.\n")

fast = Maker("Fast", latency=1)
slow = Maker("Slow", latency=10)
fair_end = run_race([fast, slow], steps=5000, seed=1)

total_fills = fast.fills + slow.fills
print(f"    {'maker':<6} {'latency(us)':>12} {'fills':>8} {'share':>9} {'P&L':>10}")
for m in (fast, slow):
    share = m.fills / total_fills * 100
    print(f"    {m.name:<6} {m.latency:>12d} {m.fills:>8d} {share:>8.1f}% "
          f"{m.pnl(fair_end):>10.2f}")
print(f"\n    Same quote, same {total_fills} orders of flow — but Fast (10x lower")
print("    latency) wins ~10x the fills, and ~10x the captured spread. Nobody")
print("    out-quoted anybody. Speed alone decided who traded.")

# ---- Part B: lower the slow maker's latency and watch its share climb --------
print("\n" + "-" * 70)
print("[B] LOWER A MAKER'S LATENCY -> ITS FILL SHARE RISES\n")
print("Hold one maker at latency 1. Sweep the other from very slow to parity")
print("and watch its share of the flow climb toward 50%:\n")
print(f"    {'our latency(us)':>16} {'rival latency(us)':>18} {'our fill share':>16}")
for lat in [16, 8, 4, 2, 1]:
    us = Maker("us", latency=lat)
    them = Maker("them", latency=1)
    run_race([us, them], steps=5000, seed=2)
    share = us.fills / (us.fills + them.fills) * 100
    print(f"    {lat:>16d} {1:>18d} {share:>15.1f}%")
print("\n    Each halving of latency roughly doubles your share of the flow until")
print("    you reach parity (50/50). That curve IS the business case for spending")
print("    millions to shave microseconds: more speed -> more flow -> more spread.")

# ---- Part C: make one maker ultra-fast and watch it dominate -----------------
print("\n" + "-" * 70)
print("[C] AN ULTRA-FAST MAKER DOMINATES THE BOOK\n")
hft = Maker("HFT", latency=1)
rest = Maker("Rest", latency=50)
fair_end = run_race([hft, rest], steps=5000, seed=3)
hft_share = hft.fills / (hft.fills + rest.fills) * 100
print(f"    HFT at 1us vs everyone else at 50us:")
print(f"    HFT  wins {hft.fills:>5d} fills ({hft_share:4.1f}%)  P&L {hft.pnl(fair_end):>8.2f}")
print(f"    Rest wins {rest.fills:>5d} fills ({100-hft_share:4.1f}%)  P&L {rest.pnl(fair_end):>8.2f}")
print("\n    A 50x speed edge sweeps almost the entire book. This is why a handful")
print("    of co-located firms capture the lion's share of market-making flow.")

# ---- Part D: cancel speed — the fast maker dodges an adverse move ------------
print("\n" + "-" * 70)
print("[D] CANCEL SPEED — the fast maker yanks its quote before the move\n")
# Fair value is about to jump UP by 0.30. Both makers are quoting an ask at
# 100.05. A flood of informed buyers is about to lift that stale ask. The maker
# who can CANCEL inside the warning window dodges it; the slow one eats it.
JUMP = 0.30                    # the impending adverse move (fair jumps up)
WARN_US = 5                    # microseconds of warning before flow arrives
stale_ask = 100.00 + HALF_SPREAD
print(f"    Fair is about to jump +{JUMP:.2f}. Both quote a stale ask at {stale_ask:.2f}.")
print(f"    There are {WARN_US} microseconds of warning before the buyers hit.\n")
for name, lat in [("Fast", 1), ("Slow", 10)]:
    canceled = lat < WARN_US   # can you pull the quote inside the warning window?
    if canceled:
        outcome = "CANCELS in time -> quote pulled, dodges the hit. Loss avoided $0.00"
    else:
        # gets filled selling the ask, then fair jumps up against the short
        loss = JUMP * SIZE_PER_ORDER
        outcome = f"too SLOW to cancel -> sells {stale_ask:.2f}, fair jumps, loses ${loss:.2f}"
    print(f"    {name:<5} (latency {lat:>2}us): {outcome}")
print("\n    Speed isn't only about winning GOOD flow — it's about escaping BAD")
print("    flow. The fast maker cancels stale quotes before a move runs them")
print("    over; the slow maker is still resting there and gets picked off. Both")
print("    edges, win-more and lose-less, push the same way: faster is richer.")

print("\n" + "=" * 70)
print("  Same price, the queue still has a front — and speed buys you that")
print("  spot. More flow won AND fewer adverse fills eaten. That is the whole")
print("  microsecond arms race (Flash Boys) in one idea: at equal prices,")
print("  latency decides who actually trades. There is still no free money —")
print("  the speed itself costs a fortune to buy.")
print("=" * 70)


# -----------------------------------------------------------------------------
# TRY IT (exercises)
# -----------------------------------------------------------------------------
# 1. PARITY. In Part A set slow = Maker("Slow", latency=1) so both makers are
#    equally fast. Re-run: the fills and P&L should split ~50/50. With no speed
#    edge, the spread is shared evenly — speed was the only thing separating
#    them.
# 2. ULTRA-FAST. In Part C set hft = Maker("HFT", latency=1) and
#    rest = Maker("Rest", latency=200). Watch HFT's share climb toward ~99%.
#    A big enough speed gap is winner-take-almost-all.
# 3. CANCEL WINDOW (Part D). Set WARN_US = 0 (no warning at all). Now even the
#    fast maker can't cancel in time and BOTH eat the adverse move. When the
#    move is a surprise, speed can't save you — only a wider spread can.
# 4. THREE-WAY RACE. In Part A pass three makers, e.g.
#    run_race([Maker("A",1), Maker("B",2), Maker("C",4)], ...). Their
#    shares come out ~ proportional to 1/latency (4 : 2 : 1). Print each share.
# 5. Open ../exchange.py and find the [L20] block. It runs the SAME idea against
#    the real MarketMaker: a `speed` field and a fill SHARE = speed/(speed+rival).
#    Confirm our latency model (share ~ 1/latency) and its speed model agree.
