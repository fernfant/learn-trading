"""
exchange.py — the cumulative artifact for TRACK 2 (high-frequency trading).

Track 1 (market.py) treated "the price" as one number handed to you from the
sky. But where does that number come from? From an EXCHANGE matching buyers
and sellers in an ORDER BOOK. Track 2 builds that machine, then puts a fast
trading bot on top of it.

The big flip: in Track 1 you PAID the spread to capital.com. Here you build the
machine capital.com is — and you EARN the spread instead.

Right now it is at the LESSON 21 stage: a small but real MATCHING ENGINE with a
MARKET MAKER living on top of it. The book is two sides of resting limit orders
kept in PRICE-TIME PRIORITY (best price first, first-come-first-served inside a
price). A market order WALKS the book and pays SLIPPAGE; a crossing limit order
generates TRADES and the leftover rests. Every fill prints to a TAPE, and a
SNAPSHOT shows top-of-book plus depth. On top of all that sits a MarketMaker
that QUOTES a bid and an ask around fair value to earn the half-spread on each
side — but it must SKEW its quotes to control INVENTORY (Avellaneda–Stoikov:
lean to get flat), it only wins the flow it is FAST enough to sit in front of
(price-time priority, again), and it BLEEDS to ADVERSE SELECTION whenever it
fills INFORMED traders who know which way the price is about to jump.

The honest theme, mirrored from Track 1: the market maker's edge is the spread,
and that edge is constantly eroded by inventory risk and adverse selection.
There is no free money on either side of the book. In Track 1 "informed traders
are the signal you can't see"; here they are the toxic flow that runs you over.

------------------------------------------------------------------------------
BUILD MAP  (Track 2 picks up where Track 1's capstone ends)
------------------------------------------------------------------------------
  L12 taker -> maker          (concept) the spread flips from cost to revenue
  L13 the book exists         bids[], asks[], best_bid, best_ask, spread
  L14 a market order eats      match_market() walks the top, pays slippage
  L15 a limit order rests      add_limit() with price-time (FIFO) priority
  L16 the matching loop        submit() crosses bids vs asks -> trades
  L17 market data & tape       snapshot() (top-of-book + depth) + the tape
  L18 a market maker           MarketMaker.quote() captures the half-spread
  L19 inventory risk           skew quotes by inventory to lean back to flat
  L20 latency & the queue      faster maker sits ahead in line, wins more flow
  L21 adverse selection        informed flow predicts the move and runs you  <-- HERE
  L22 CAPSTONE                a market maker that stays profitable AND flat
------------------------------------------------------------------------------
Run it:  python3 exchange.py
"""

import random

# A "seed" makes every stochastic part repeat the same way each run, so the
# numbers you see match the walkthrough exactly. Change it for a new market.
random.seed(11)


# =============================================================================
# THE ORDER BOOK + MATCHING ENGINE
# =============================================================================
# A real exchange keeps, for each PRICE, a QUEUE of resting orders in the order
# they arrived. So a "level" here is (price, [orders]) where each order is a
# tiny dict carrying its size and a `seq` — a global, ever-incrementing arrival
# number. We use a counter, NOT the wall clock: it is the ORDER of arrival that
# decides the queue, and a counter is deterministic and reproducible.
class OrderBook:
    def __init__(self):
        # bids: buyers, levels sorted high -> low (best = most someone will pay)
        # asks: sellers, levels sorted low  -> high (best = least one will sell)
        # Each level is [price, [order, order, ...]] and each order is
        #   {"seq": n, "size": q, "who": tag}.
        self.bids = []
        self.asks = []
        self.seq = 0          # global arrival counter -> price-TIME priority
        self.tape = []        # every executed trade lands here (Lesson 17)

    # ---- seeding helpers (resting liquidity already on the book) ------------
    def add_bid(self, price, size, who="seed"):
        # Convenience used to seed the book; just a buy limit that we trust not
        # to cross (we place seed orders below the asks on purpose).
        self._rest("buy", price, size, who)

    def add_ask(self, price, size, who="seed"):
        self._rest("sell", price, size, who)

    # ---- L15: a limit order RESTS with price-time priority ------------------
    def _rest(self, side, price, size, who):
        # Insert `size` at `price` into the correct side. If the price level
        # already exists we APPEND to the back of its queue (FIFO: you join the
        # line behind everyone already quoting that price). Otherwise we make a
        # new level and re-sort so the best price is at index 0.
        self.seq += 1
        order = {"seq": self.seq, "size": size, "who": who}
        levels = self.bids if side == "buy" else self.asks
        for lvl in levels:
            if lvl[0] == price:
                lvl[1].append(order)            # join the BACK of the queue
                return order
        levels.append([price, [order]])
        # bids descend (best/highest first); asks ascend (best/lowest first).
        levels.sort(key=lambda l: -l[0] if side == "buy" else l[0])
        return order

    def best_bid(self):
        return self.bids[0][0] if self.bids else None

    def best_ask(self):
        return self.asks[0][0] if self.asks else None

    def spread(self):
        if self.bids and self.asks:
            return self.best_ask() - self.best_bid()
        return None

    def mid(self):
        if self.bids and self.asks:
            return (self.best_bid() + self.best_ask()) / 2
        return None

    def _level_size(self, level):
        return sum(o["size"] for o in level[1])

    # ---- L14: a MARKET order eats the book ----------------------------------
    def match_market(self, side, size):
        # A market order says "fill me NOW, whatever the price". A BUY eats the
        # ASKS from the cheapest up; a SELL eats the BIDS from the highest down.
        # We walk level by level, taking size off the FRONT of each queue
        # (price-time priority — the order that arrived first gets filled
        # first), and stop when we're full or the book runs dry.
        book = self.asks if side == "buy" else self.bids
        fills = []          # list of (price, size) we actually traded at
        need = size
        while need > 0 and book:
            level = book[0]
            price = level[0]
            queue = level[1]
            while need > 0 and queue:
                resting = queue[0]
                take = min(need, resting["size"])
                fills.append((price, take))
                resting["size"] -= take
                need -= take
                self.tape.append({"price": price, "size": take, "aggressor": side})
                if resting["size"] == 0:
                    queue.pop(0)               # this resting order is consumed
            if not queue:
                book.pop(0)                    # whole level cleared -> drop it
        filled = size - need
        # The AVERAGE price you paid. For a big order this is WORSE than the
        # top of book, because you ate deeper, pricier levels — that gap is
        # SLIPPAGE, and it is exactly what Track 1 paid as a cost.
        avg = sum(p * q for p, q in fills) / filled if filled else None
        return fills, avg, filled

    # ---- L16: the MATCHING LOOP (the heart of an exchange) ------------------
    def submit(self, side, price, size, who="taker"):
        # Submit an incoming LIMIT order. If it CROSSES the book (a buy priced
        # at-or-above the best ask, or a sell at-or-below the best bid) it trades
        # immediately against resting orders, consuming their size at THEIR
        # price (the resting order set the price; the aggressor crossed to it).
        # Whatever can't be filled at an acceptable price RESTS as a new limit.
        fills = []
        need = size
        if side == "buy":
            # cross while there is an ask we're willing to pay for
            while need > 0 and self.asks and price >= self.asks[0][0]:
                need, took = self._consume(self.asks, need, side)
                fills += took
        else:
            while need > 0 and self.bids and price <= self.bids[0][0]:
                need, took = self._consume(self.bids, need, side)
                fills += took
        if need > 0:
            self._rest(side, price, need, who)   # leftover joins the book
        return fills, need

    def _consume(self, book, need, aggressor):
        # Eat the best level of `book` for an incoming aggressor, FIFO inside
        # the level, recording each fill on the tape. Returns (remaining, fills).
        level = book[0]
        price = level[0]
        queue = level[1]
        took = []
        while need > 0 and queue:
            resting = queue[0]
            take = min(need, resting["size"])
            took.append((price, take))
            resting["size"] -= take
            need -= take
            self.tape.append({"price": price, "size": take, "aggressor": aggressor,
                              "maker": resting["who"]})
            if resting["size"] == 0:
                queue.pop(0)
        if not queue:
            book.pop(0)
        return need, took

    # ---- L17: market data — a SNAPSHOT of the book --------------------------
    def snapshot(self, depth=3):
        # What an HFT actually subscribes to: top-of-book plus a few levels of
        # DEPTH on each side (price and total size resting there).
        asks = [(l[0], self._level_size(l)) for l in self.asks[:depth]]
        bids = [(l[0], self._level_size(l)) for l in self.bids[:depth]]
        return {"bids": bids, "asks": asks,
                "best_bid": self.best_bid(), "best_ask": self.best_ask(),
                "spread": self.spread(), "mid": self.mid()}

    def show(self):
        print("        ASKS (sellers)")
        for level in reversed(self.asks):
            q = ",".join(str(o["size"]) for o in level[1])
            print(f"        {level[0]:7.2f}  x{self._level_size(level):<3} [{q}]")
        sp = self.spread()
        print(f"  ----  spread = {sp:.2f}  ----" if sp is not None else "  ----")
        for level in self.bids:
            q = ",".join(str(o["size"]) for o in level[1])
            print(f"        {level[0]:7.2f}  x{self._level_size(level):<3} [{q}]")
        print("        BIDS (buyers)")


# =============================================================================
# L18-L21: THE MARKET MAKER
# =============================================================================
# A market maker (MM) does the opposite of a Track-1 trader: instead of CROSSING
# the spread to trade now, it POSTS both a bid and an ask around fair value and
# waits to get hit. If a noise buyer lifts its ask and later a noise seller hits
# its bid, the MM has bought low and sold high — pocketing the spread without
# ever predicting the price. That captured spread is its entire edge.
#
# But the edge is fragile, and Lessons 19-21 are the three things that erode it:
#   L19 inventory risk    — fills are lumpy; you end up long or short and exposed
#   L20 latency           — you only earn the flow you are fast enough to sit in
#                           front of (price-time priority decides the queue)
#   L21 adverse selection — some takers KNOW the next move; filling them is a loss
class MarketMaker:
    def __init__(self, half_spread=0.05, skew=0.01, speed=1.0, max_inv=50):
        self.half_spread = half_spread   # how far each quote sits from fair (L18)
        self.skew = skew                 # how hard to lean quotes by inventory (L19)
        self.speed = speed               # queue priority: higher = faster (L20)
        self.max_inv = max_inv           # soft inventory cap for sizing
        self.inventory = 0               # +long / -short units we are holding
        self.cash = 0.0                  # realized cash from fills
        self.fills = 0                   # how many trades we participated in
        self.toxic_fills = 0             # fills against INFORMED flow (L21)
        self.inv_history = [0]           # inventory over time, to chart the skew

    # ---- L18 + L19: quote both sides, SKEWED by inventory -------------------
    def quote(self, fair):
        # The symmetric quote (L18) is fair +/- half_spread: sell a touch above
        # fair, buy a touch below. The SKEW (L19) shifts BOTH quotes by an
        # amount proportional to inventory. When we're long (inventory > 0) we
        # push both quotes DOWN: our ask gets cheaper (sell eagerly, offload the
        # length) and our bid gets cheaper too (buy reluctantly). This is the
        # Avellaneda-Stoikov intuition — lean your prices to pull inventory back
        # toward flat, because carrying inventory is risk, not profit.
        lean = self.skew * self.inventory
        bid = fair - self.half_spread - lean
        ask = fair + self.half_spread - lean
        return bid, ask

    # ---- the MM's value: cash already booked + paper value of inventory -----
    def pnl(self, fair):
        # Mark inventory to fair value. If we're flat (inventory == 0) this is
        # pure captured-spread profit; any inventory is unrealized risk.
        return self.cash + self.inventory * fair

    def on_fill(self, side, price, size, informed=False):
        # We got hit. If side == "buy" the taker BOUGHT from us -> we SOLD
        # `size` at `price`: cash up, inventory down. Vice versa for a sell.
        if side == "buy":
            self.cash += price * size
            self.inventory -= size
        else:
            self.cash -= price * size
            self.inventory += size
        self.fills += 1
        if informed:
            self.toxic_fills += 1


# =============================================================================
# DEMO — narrated, top to bottom, one lesson at a time
# =============================================================================

print("=" * 70)
print("  TRACK 2 — INSIDE THE EXCHANGE")
print("=" * 70)

# ---- L13: the book exists ---------------------------------------------------
print("\n[L13] THE BOOK — two sides of resting orders, a spread in between\n")
book = OrderBook()
# A handful of resting orders — the kind of thing already sitting on a real
# exchange when you arrive. The [..] after each level shows the FIFO queue.
book.add_bid(99.98, 5); book.add_bid(99.97, 2); book.add_bid(99.95, 8)
book.add_ask(100.02, 4); book.add_ask(100.03, 6); book.add_ask(100.05, 3)
book.show()
print(f"\nBest buyer pays {book.best_bid():.2f}, best seller wants "
      f"{book.best_ask():.2f}. The mid is {book.mid():.2f}; to trade now you "
      f"cross the {book.spread():.2f} spread.")

# ---- L14: a market order eats the book (slippage) ---------------------------
print("\n" + "-" * 70)
print("[L14] A MARKET ORDER EATS THE BOOK — and pays SLIPPAGE\n")
top_ask = book.best_ask()
fills, avg, filled = book.match_market("buy", 12)
print(f"You market-BUY 12 units. The book fills you level by level:")
for p, q in fills:
    print(f"    {q} @ {p:.2f}")
print(f"Top ask was {top_ask:.2f}, but your AVERAGE fill was {avg:.4f}.")
print(f"That {avg - top_ask:.4f} gap is SLIPPAGE: a big order eats past the best\n"
      f"price into deeper, worse levels. The more you take, the more it costs.")
print("\nBook after the sweep (the cheap asks are gone):")
book.show()

# ---- L15: a limit order rests with price-time priority ----------------------
print("\n" + "-" * 70)
print("[L15] A LIMIT ORDER RESTS — price-time priority, and your place in line\n")
book2 = OrderBook()
# Three buyers all want the SAME price, 100.00. They arrive in order A, B, C.
book2.submit("buy", 100.00, 5, who="Alice")
book2.submit("buy", 100.00, 5, who="Bob")
book2.submit("buy", 100.00, 5, who="Carol")
# Dana quotes a BETTER (higher) price -> she jumps to the front of the bids.
book2.submit("buy", 100.01, 5, who="Dana")
print("Four buy limits arrive: Alice, Bob, Carol at 100.00, then Dana at 100.01.")
queue_100 = next(l[1] for l in book2.bids if l[0] == 100.00)
print(f"PRICE first: Dana's 100.01 sits ahead of the whole 100.00 level.")
print(f"TIME next:  inside 100.00 the queue is "
      f"{[o['who'] for o in queue_100]} — first-in, first-out.")
# Now a seller crosses with 7 units. Dana fills first (best price), then Alice
# (first in line at 100.00), then 1 unit of Bob. Carol gets nothing yet.
fills, _ = book2.submit("sell", 100.00, 7, who="seller")
print(f"\nA seller dumps 7 units across the bids. Fills, in priority order:")
for t in book2.tape:
    print(f"    seller hits {t['maker']:<6} {t['size']} @ {t['price']:.2f}")
print("Dana (best price) and Alice (first at 100.00) fill fully; Bob partial;\n"
      "Carol — last in line — gets nothing. Your QUEUE POSITION is your edge.")

# ---- L16: the matching loop (crossed orders -> trades) ----------------------
print("\n" + "-" * 70)
print("[L16] THE MATCHING ENGINE — a stream of orders, crossing into trades\n")
book3 = OrderBook()
book3.add_bid(99.98, 5); book3.add_ask(100.02, 5)
stream = [("buy", 100.03, 3), ("sell", 99.97, 4), ("buy", 100.10, 8),
          ("sell", 100.00, 2)]
print("Resting: bid 99.98 x5, ask 100.02 x5. Now feed in an order stream:\n")
for side, price, size in stream:
    fills, rested = book3.submit(side, price, size, who="flow")
    got = sum(q for _, q in fills)
    note = (f"crossed, filled {got}" if got else "no cross")
    if rested:
        note += f", rested {rested} @ {price:.2f}"
    print(f"    {side:4} {size} @ {price:6.2f}  ->  {note}")
print("\nWhen an incoming order crosses, the engine makes a trade and consumes\n"
      "resting size; the remainder rests. That loop IS the exchange.")

# ---- L17: market data & the tape --------------------------------------------
print("\n" + "-" * 70)
print("[L17] MARKET DATA & THE TAPE — what an HFT actually sees\n")
snap = book3.snapshot()
print("SNAPSHOT (depth = top 3 levels each side):")
print(f"    asks: {snap['asks']}")
print(f"    bids: {snap['bids']}")
print(f"    best_bid={snap['best_bid']}  best_ask={snap['best_ask']}  "
      f"mid={snap['mid']}  spread={snap['spread']}")
print("\nTAPE (every execution, with the aggressor's side):")
for t in book3.tape:
    print(f"    {t['size']} @ {t['price']:.2f}  ({t['aggressor']} aggressor)")
print("The snapshot is the standing liquidity; the tape is what actually traded.\n"
      "Together they are the entire information feed a market maker reacts to.")


# =============================================================================
# L18-L21: THE MARKET MAKER vs A FLOW SIMULATION
# =============================================================================
# We now run a market maker against a stream of incoming orders. Each step:
#   1. fair value takes a small random walk (the "true" price nobody quotes)
#   2. the MM posts a bid and an ask around fair (skewed by inventory, L19)
#   3. a taker arrives wanting one side; whether it actually fills the MM
#      depends on HOW ATTRACTIVE that quote is vs fair (a quote closer to fair
#      is more likely to get hit) AND, when a rival competes, on SPEED (L20)
#   4. some takers are INFORMED — fair value jumps THEIR way right after they
#      trade, so filling them is a loss (adverse selection, L21)
#
# The key to L19: the MM's SKEW moves its quotes, which changes those fill
# probabilities. When the MM is long it skews DOWN: its ask drops toward fair
# (buyers lift it more -> the MM sells more) and its bid drops away from fair
# (sellers hit it less -> the MM buys less). Net: it sheds the length. That is
# how a price change hands inventory back, with no change to who shows up.
def run_flow(mm, steps=4000, informed_frac=0.15, seed=1, rival_speed=0.0):
    rng = random.Random(seed)
    fair = 100.0
    informed_pnl_drag = 0.0
    rival_wins = 0
    mm_wins = 0

    def hit_prob(distance):
        # Probability a taker crosses to a quote sitting `distance` away from
        # fair. At-the-fair quotes (distance 0) almost always fill; quotes far
        # from fair rarely do. Linear, clamped to [0.05, 0.95]; the exact shape
        # doesn't matter, only that CLOSER-to-fair => MORE likely to be hit.
        return max(0.05, min(0.95, 0.5 - distance * 4.0))

    for _ in range(steps):
        bid, ask = mm.quote(fair)
        # Is the next taker informed? Informed flow predicts the NEXT move.
        informed = rng.random() < informed_frac
        side = rng.choice(["buy", "sell"])     # which side the taker WANTS
        size = rng.randint(1, 3)
        # A buyer would lift our ask; a seller would hit our bid. The relevant
        # quote's distance from fair sets the fill probability (L19's lever).
        dist = (ask - fair) if side == "buy" else (fair - bid)
        if rng.random() > hit_prob(dist):
            mm.inv_history.append(mm.inventory)   # taker walked away, no fill
            continue

        # L20 — LATENCY / QUEUE: if a rival maker also quotes this price, the
        # FASTER maker sits in front and wins the fill. We give the flow to our
        # MM with probability = its speed share. A faster MM wins more flow at
        # the SAME price; that is the whole co-location arms race in one line.
        if rival_speed > 0:
            share = mm.speed / (mm.speed + rival_speed)
            if rng.random() > share:
                rival_wins += 1
                if informed:                      # rival eats it; fair still moves
                    fair += 0.06 if side == "buy" else -0.06
                mm.inv_history.append(mm.inventory)
                continue
        mm_wins += 1

        # L21 — ADVERSE SELECTION: an informed BUYER knows fair is about to rise,
        # so it lifts our ask; we sell, then fair jumps UP and our short is
        # underwater. An informed SELLER hits our bid right before fair drops.
        # Either way we end up on the wrong side of the move.
        if informed:
            move = 0.06 if side == "buy" else -0.06
            if side == "buy":
                mm.on_fill("buy", ask, size, informed=True)   # we sold the ask
            else:
                mm.on_fill("sell", bid, size, informed=True)  # we bought the bid
            fair += move                                       # ...fair moves against us
            informed_pnl_drag += -abs(move) * size            # the bleed, isolated
        else:
            # NOISE flow: uninformed, equally likely either way. This is the
            # flow the MM WANTS — it pays the spread and predicts nothing.
            if side == "buy":
                mm.on_fill("buy", ask, size)
            else:
                mm.on_fill("sell", bid, size)

        # fair value's own small random wander, independent of our fills
        fair += rng.gauss(0, 0.02)
        mm.inv_history.append(mm.inventory)
    return fair, informed_pnl_drag, mm_wins, rival_wins


def inv_chart(series, width=58, height=7):
    """Tiny ASCII chart of inventory over time, centered on zero (flat)."""
    sample = [series[round(i * (len(series) - 1) / (width - 1))] for i in range(width)]
    hi = max(1, max(abs(v) for v in sample))
    rows = []
    for r in range(height):
        level = hi - r * (2 * hi) / (height - 1)
        line = "".join("*" if (v >= level > 0) or (v <= level < 0) or
                       (abs(level) < hi / height and abs(v) < hi / height)
                       else " " for v in sample)
        tag = " 0 (flat)" if abs(level) < hi / height else ""
        rows.append(f"{level:+7.0f} |{line}{tag}")
    return "\n".join(rows)


print("\n" + "=" * 70)
print("  THE MARKET MAKER vs THE FLOW")
print("=" * 70)

# ---- L18: earning the spread ------------------------------------------------
print("\n[L18] BE THE MARKET MAKER — quote both sides, capture the half-spread\n")
mm_demo = MarketMaker(half_spread=0.05, skew=0.0)
print(f"MM quotes fair +/- {mm_demo.half_spread:.2f}. At fair=100.00 that is:")
b, a = mm_demo.quote(100.0)
print(f"    bid {b:.2f}  /  ask {a:.2f}   (it BUYS at {b:.2f}, SELLS at {a:.2f})")
print("Every round-trip (one buyer lifts the ask, one seller hits the bid)\n"
      "banks the full spread without predicting price. That is the edge.")

# ---- L19: inventory risk, skew OFF vs skew ON -------------------------------
print("\n" + "-" * 70)
print("[L19] INVENTORY RISK — skew your quotes to lean back toward flat\n")
mm_noskew = MarketMaker(half_spread=0.05, skew=0.0)
mm_skew = MarketMaker(half_spread=0.05, skew=0.01)
# Pure NOISE flow (no informed traders) so we isolate the inventory effect.
run_flow(mm_noskew, steps=4000, informed_frac=0.0, seed=2)
run_flow(mm_skew, steps=4000, informed_frac=0.0, seed=2)
print("Skew OFF — inventory wanders off and STAYS off (unbounded risk):")
print(inv_chart(mm_noskew.inv_history))
print(f"    end inventory: {mm_noskew.inventory:+d} units\n")
print("Skew ON — quotes lean against inventory, so it MEAN-REVERTS to flat:")
print(inv_chart(mm_skew.inv_history))
print(f"    end inventory: {mm_skew.inventory:+d} units")
print("\nSame flow, same seed. The skew only changes your PRICES — but a quote\n"
      "nearer fair gets hit more, so leaning quotes makes the market preferentially\n"
      "buy the side you want to sell. Inventory gets handed back toward flat.\n"
      "Carrying inventory is risk (price can move against it); skew is how you shed it.")

# ---- L20: latency & the queue -----------------------------------------------
print("\n" + "-" * 70)
print("[L20] LATENCY & THE QUEUE — a faster maker wins more of the flow\n")
print("Same price, same quotes — but a RIVAL maker competes for each order.")
print("Price-time priority means whoever is FASTER sits in front and gets hit:")
print(f"    {'our speed':>10} {'rival speed':>12} {'our fill share':>16}")
for speed in [0.5, 1.0, 2.0, 4.0]:
    mm_lat = MarketMaker(half_spread=0.05, skew=0.01, speed=speed)
    _, _, won, lost = run_flow(mm_lat, steps=4000, informed_frac=0.0,
                               seed=3, rival_speed=1.0)
    share = won / (won + lost)
    print(f"    {speed:>10.1f} {1.0:>12.1f} {share * 100:>15.1f}%")
print("\nNothing changed but speed, yet the fast maker captures most of the flow.\n"
      "That is co-location and the microsecond arms race (Flash Boys) in one\n"
      "table: at the same price, speed decides who actually trades.")

# ---- L21: adverse selection -------------------------------------------------
print("\n" + "-" * 70)
print("[L21] ADVERSE SELECTION — informed flow runs the market maker over\n")
print(f"    {'informed %':>11} {'fills':>8} {'toxic':>7} {'inventory':>11} {'P&L':>10}")
for frac in [0.0, 0.10, 0.25, 0.40]:
    mm_adv = MarketMaker(half_spread=0.05, skew=0.01)
    fair_end, drag, _, _ = run_flow(mm_adv, steps=4000, informed_frac=frac, seed=4)
    print(f"    {frac * 100:>10.0f}% {mm_adv.fills:>8d} {mm_adv.toxic_fills:>7d} "
          f"{mm_adv.inventory:>+11d} {mm_adv.pnl(fair_end):>10.2f}")
print("\nWith zero informed flow the MM earns the spread cleanly. Crank informed\n"
      "flow up and the SAME spread, SAME skew bot bleeds: every toxic fill is a\n"
      "trade where the price jumps against the MM the instant after it fills.\n"
      "It bought right before the drop, sold right before the rise. That is\n"
      "adverse selection — the mirror of Track 1's 'informed traders are the\n"
      "signal you can't see'. Here they are the toxic flow that eats your edge.")

# ---- the honest closing line ------------------------------------------------
print("\n" + "=" * 70)
mm_final = MarketMaker(half_spread=0.05, skew=0.01)
fair_end, _, _, _ = run_flow(mm_final, steps=4000, informed_frac=0.15, seed=5)
print(f"  FINAL MM (skew on, 15% informed flow): "
      f"P&L {mm_final.pnl(fair_end):+.2f}, inventory {mm_final.inventory:+d}, "
      f"{mm_final.fills} fills ({mm_final.toxic_fills} toxic)")
print("=" * 70)
print("  The market maker's only edge is the SPREAD it quotes. Inventory risk\n"
      "  and adverse selection erode it from both sides. Quote too tight and\n"
      "  toxic flow eats you; too wide and you win no flow. There is no free\n"
      "  money here either — same honest lesson, seen from the other seat.")


# -----------------------------------------------------------------------------
# TRY IT (exercises)
# -----------------------------------------------------------------------------
# 1. BIGGER market order, more slippage (L14). In the L14 block change
#    book.match_market("buy", 12) to ("buy", 25). You eat further up the asks —
#    print `avg` and watch the average fill get worse. Slippage scales with size.
# 2. QUEUE POSITION (L15). In the L15 block, change the crossing seller's size
#    from 7 to 12. Now Carol finally fills too. At what size does every resting
#    order get cleared? (Hint: total resting bid size.)
# 3. WIDEN the MM spread (L18). In the FINAL MM line set half_spread=0.10. P&L
#    on the clean flow goes UP per fill — but in a real market a wider quote
#    sits further back and wins LESS flow. Tighter vs wider is the core tradeoff.
# 4. SKEW harder (L19). In the skew-ON MM set skew=0.05 then 0.0. Watch the
#    inventory chart: more skew pins you tighter to flat but means you sometimes
#    quote away from fair to dump inventory (a cost). Find a middle ground.
# 5. SPEED race (L20). Add speed=8.0 to the L20 loop list. Your fill share keeps
#    climbing toward 100% — but in reality that last microsecond costs the most.
# 6. TURN UP THE TOXICITY (L21). In the FINAL MM line set informed_frac=0.40 and
#    re-run. Watch P&L fall (and possibly go negative): the same bot, run over
#    by informed flow. THIS is why real market makers fear toxic order flow.
# 7. Hardest (L22 capstone): tune half_spread, skew and speed so the FINAL MM
#    ends both PROFITABLE and near-FLAT (small |inventory|) even at 25% informed
#    flow. That double objective — make money AND carry no risk — is the real
#    job of an HFT market maker, and it is deliberately hard.
