"""
LESSON 17 — Market data & the tape (Track 2: inside the exchange)

Lesson 16 built the matching engine: crossed orders turn into trades. Now we
ask a different question — not "how does a trade happen?" but "what does a
trader actually SEE?" Because nobody trading on a real venue watches the raw
engine. They watch two feeds streamed out of it:

    (1) the BOOK / quote feed  — a SNAPSHOT of resting liquidity right now:
        the best bid and best ask (top-of-book) plus the DEPTH stacked at each
        price level. It answers: "where can I trade, and how much is on offer?"

    (2) the TAPE / trade feed   — the running list of trades that ACTUALLY
        executed: each one a (price, size, aggressor side). It answers: "what
        just happened, and who was the impatient one — a buyer or a seller?"

The book is a photograph of intentions; the tape is a recording of events.
"Reading the tape" while watching depth is the raw sensory input to every
trading decision a human or an HFT makes. This lesson is that screen.

From the two feeds we compute a few simple DERIVED SIGNALS — the first numbers
any trader's eye jumps to:

    mid        = (best_bid + best_ask) / 2          the fair midpoint
    imbalance  = bid_size / (bid_size + ask_size)   how lopsided the top is
    microprice = ask_size-weighted mid              mid nudged toward the
                                                    thinner side (where price
                                                    is likelier to drift)

Cumulative artifact: ../exchange.py gains `snapshot()` (top-of-book + depth)
and a `tape` list of executed trades, exactly like the Book + tape below.

Reference: Hasbrouck, *Empirical Market Microstructure* (the feeds and the
liquidity measures you read off them).

Run it:  python3 17_market_data.py
Then read 17_walkthrough.md.
"""

import random

random.seed(17)


# ---------------------------------------------------------------------------
# A standalone book + matching engine. Same machine as Lessons 13-16, trimmed
# to exactly what we need to PRODUCE the two feeds: a place for orders to rest,
# a way for incoming orders to match, and a `tape` that records every trade.
# ---------------------------------------------------------------------------
class Book:
    def __init__(self):
        self.bids = []   # buyers: (price, size), highest price first
        self.asks = []   # sellers: (price, size), lowest price first
        self.tape = []   # the trade feed: (price, size, aggressor) in time order

    def add_bid(self, price, size):
        self.bids.append((price, size))
        self.bids.sort(key=lambda o: -o[0])

    def add_ask(self, price, size):
        self.asks.append((price, size))
        self.asks.sort(key=lambda o: o[0])

    def best_bid(self):
        return self.bids[0][0] if self.bids else None

    def best_ask(self):
        return self.asks[0][0] if self.asks else None

    # --- the FEEDS ---------------------------------------------------------

    def snapshot(self, levels=3):
        """The quote/book feed: top-of-book + a few levels of depth each side.

        Returns a dict with best_bid/best_ask and the top `levels` of each
        side as [(price, size), ...]. This is the photograph of resting
        liquidity an HFT refreshes thousands of times a second.
        """
        return {
            "best_bid": self.best_bid(),
            "best_ask": self.best_ask(),
            "bid_depth": self.bids[:levels],
            "ask_depth": self.asks[:levels],
        }

    def match_market(self, side, size):
        """A market order arrives and aggresses across the book, printing
        trades onto the tape. `side` is the aggressor: 'buy' eats asks
        (cheapest first), 'sell' hits bids (highest first)."""
        remaining = size
        levels = self.asks if side == "buy" else self.bids
        while remaining > 0 and levels:
            price, avail = levels[0]
            take = min(remaining, avail)
            self.tape.append((price, take, side))   # record the trade
            remaining -= take
            if take < avail:
                levels[0] = (price, avail - take)   # partial fill, level shrinks
            else:
                levels.pop(0)                       # level fully consumed
        return size - remaining                     # how much actually traded


# ---------------------------------------------------------------------------
# Derived signals — the numbers a trader's eye reads off the snapshot.
# ---------------------------------------------------------------------------
def mid(snap):
    return (snap["best_bid"] + snap["best_ask"]) / 2


def top_sizes(snap):
    bid_size = snap["bid_depth"][0][1] if snap["bid_depth"] else 0
    ask_size = snap["ask_depth"][0][1] if snap["ask_depth"] else 0
    return bid_size, ask_size


def imbalance(snap):
    """Fraction of top-of-book size that is on the BID side, in [0, 1].
    > 0.5 means buyers are stacked deeper than sellers (pressure up)."""
    b, a = top_sizes(snap)
    return b / (b + a) if (b + a) else 0.5


def microprice(snap):
    """Mid, but weighted toward the side with LESS size — price tends to drift
    toward the thinner queue. microprice = (bid_size*ask + ask_size*bid)/total.
    Note the cross-weighting: more bid size pulls it UP toward the ask."""
    b, a = top_sizes(snap)
    if b + a == 0:
        return mid(snap)
    return (b * snap["best_ask"] + a * snap["best_bid"]) / (b + a)


def show_depth(snap):
    """Print the book the way a terminal does: asks above, bids below, with a
    visual size bar so depth is obvious at a glance."""
    print("        DEPTH (resting liquidity)")
    for price, size in reversed(snap["ask_depth"]):     # asks: worst on top
        print(f"   ask  {price:7.2f}  x{size:<3d} {'#' * size}")
    sp = snap["best_ask"] - snap["best_bid"]
    print(f"   ----  mid {mid(snap):.3f}   spread {sp:.2f}  ----")
    for price, size in snap["bid_depth"]:               # bids: best on top
        print(f"   bid  {price:7.2f}  x{size:<3d} {'#' * size}")


def show_tape(tape, n=8):
    """Print the most recent `n` trades — the tape, newest at the bottom."""
    print("        TAPE (what actually traded)")
    for price, size, side in tape[-n:]:
        arrow = "BUY <" if side == "buy" else "SELL>"   # who was the aggressor
        print(f"   {arrow}  {size:>2d} @ {price:7.2f}")


def show_signals(snap):
    b, a = top_sizes(snap)
    imb = imbalance(snap)
    lean = "buyers" if imb > 0.5 else "sellers" if imb < 0.5 else "balanced"
    print(f"   mid        = {mid(snap):.3f}")
    print(f"   imbalance  = {imb:.2f}  (bid {b} vs ask {a} -> {lean} stacked deeper)")
    print(f"   microprice = {microprice(snap):.3f}  (mid leaning toward the thin side)")
    if book.tape:
        print(f"   last trade = {book.tape[-1][1]} @ {book.tape[-1][0]:.2f}")


# ---------------------------------------------------------------------------
# PART A — what the screen shows the instant you sit down.
# A few resting orders make the book; nothing has traded yet, so the tape is
# empty. This is the pure quote feed: a snapshot of who's willing to do what.
# ---------------------------------------------------------------------------
book = Book()
book.add_bid(99.98, 5)
book.add_bid(99.97, 2)
book.add_bid(99.95, 8)
book.add_ask(100.02, 4)
book.add_ask(100.03, 6)
book.add_ask(100.05, 3)

print("=" * 56)
print("PART A — the opening snapshot (no trades yet)")
print("=" * 56)
snap = book.snapshot()
show_depth(snap)
print()
show_signals(snap)
print("   tape is empty — nothing has actually traded.\n")


# ---------------------------------------------------------------------------
# PART B — run a small stream of orders through the engine. Each market order
# aggresses the book and prints trade(s) onto the tape. After the burst we look
# at both feeds again: the depth has been eaten down, and the tape now tells
# the story of what happened and which side was the aggressor.
# ---------------------------------------------------------------------------
print("=" * 56)
print("PART B — a burst of flow hits the book")
print("=" * 56)
# A scripted little stream: mostly buyers today, so asks get eaten and the tape
# fills with BUY-side aggressors. (side, size)
flow = [("buy", 2), ("buy", 3), ("sell", 1), ("buy", 4), ("buy", 2)]
for side, size in flow:
    filled = book.match_market(side, size)
    last = book.tape[-1]
    print(f"   incoming {side.upper():4s} {size}  ->  filled {filled} "
          f"(last print {last[1]} @ {last[0]:.2f})")
print()

snap = book.snapshot()
show_depth(snap)
print()
show_tape(book.tape)
print()
show_signals(snap)
print()


# ---------------------------------------------------------------------------
# PART C — reading the tape. We never named "buying pressure" anywhere; it's
# something you INFER from the feed by tallying which side was the aggressor.
# More buy-aggressors than sell-aggressors = net buying pressure, and you can
# see it pushed the price up the ladder.
# ---------------------------------------------------------------------------
print("=" * 56)
print("PART C — reading the tape: was it buyers or sellers?")
print("=" * 56)
buy_vol = sum(s for _, s, side in book.tape if side == "buy")
sell_vol = sum(s for _, s, side in book.tape if side == "sell")
first_px = book.tape[0][0]
last_px = book.tape[-1][0]
print(f"   buy-aggressor volume  = {buy_vol}")
print(f"   sell-aggressor volume = {sell_vol}")
print(f"   net pressure          = {buy_vol - sell_vol:+d}  "
      f"({'buying' if buy_vol > sell_vol else 'selling'} pressure)")
print(f"   trade price walked    = {first_px:.2f} -> {last_px:.2f}  "
      f"({last_px - first_px:+.2f})")
print("\n   The tape never said 'buyers won' — you READ it from the feed:")
print("   more buy-aggressors, asks eaten, price walked UP. That inference,")
print("   plus the live depth imbalance, is the raw input to every decision.")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. SKEW THE DEPTH and watch imbalance move. Before Part B runs, add a big
#    resting bid: book.add_bid(99.99, 30). Re-print the opening snapshot. The
#    imbalance jumps well above 0.50 and the microprice leans UP toward the ask
#    — the engine is telling you buyers are stacked deeper than sellers.
# 2. FLIP THE FLOW to mostly sellers: flow = [("sell",3),("sell",4),("buy",1),
#    ("sell",2)]. Now bids get eaten, the tape fills with SELL aggressors, and
#    Part C reports SELLING pressure with the price walking DOWN. Reading the
#    tape, you'd infer sellers are in control.
# 3. WIDEN THE SNAPSHOT: call book.snapshot(levels=5) and show more depth. Real
#    terminals show 5-10 levels per side; deeper levels hint where big size is
#    hiding (and where a market order would slip to if it walked that far).
# 4. ADD A SIGNAL: spread in "ticks" or the queue size at the best bid. An HFT
#    watches dozens of these derived numbers update on every single message —
#    that firehose of snapshots + tape is, literally, what it sees.
