"""
LESSON 16 — The matching engine loop (Track 2: inside the exchange / HFT)

This is the heart of every exchange. Strip an exchange down to one idea and
it is this: when an incoming order CROSSES the book, you MATCH it.

What does "crosses" mean? Recall the book from Lesson 13:

    bids = buyers, sorted high -> low   (the best bid is the most anyone pays)
    asks = sellers, sorted low -> high  (the best ask is the least anyone takes)

Normally there's a GAP between the best bid and the best ask — the SPREAD —
and nothing trades. An order crosses when an impatient newcomer reaches over
that gap:

    a BUY  whose price >= the best ASK   (willing to pay what a seller wants)
    a SELL whose price <= the best BID   (willing to take what a buyer offers)

When that happens the two orders TRADE. The single rule of the whole machine:

    1. Does the incoming order cross the best opposite level?
    2. If YES: make a TRADE. It prints at the RESTING order's price (the one
       that was already there — first come, first served, Lesson 15). The
       trade size is the smaller of the two. Subtract it from both. Then go
       back to step 1 — the order may still cross the NEXT level.
    3. If NO (or nothing left to cross): whatever size REMAINS RESTS as a new
       limit order in the book, and we're done.

That loop, run on every incoming order, IS the exchange. A market order
(Lesson 14) is just an order priced so aggressively it always crosses. A limit
order that doesn't cross (Lesson 15) just rests. Same loop covers both.

Run it:  python3 16_matching.py
Then read 16_walkthrough.md.
"""

import random

random.seed(16)


# ---------------------------------------------------------------------------
# The book + the matching loop
# ---------------------------------------------------------------------------
# Same two-sorted-lists book as exchange.py (Lesson 13). The new thing this
# lesson is submit(): instead of blindly appending, it first tries to MATCH.
class Engine:
    def __init__(self):
        self.bids = []        # buyers  [(price, size)], sorted high -> low
        self.asks = []        # sellers [(price, size)], sorted low  -> high
        self.trades = []      # the tape: every (price, size) that printed

    def _rest_bid(self, price, size):
        self.bids.append((price, size))
        self.bids.sort(key=lambda o: -o[0])     # best (highest) bid first

    def _rest_ask(self, price, size):
        self.asks.append((price, size))
        self.asks.sort(key=lambda o: o[0])      # best (lowest) ask first

    def submit(self, side, price, size):
        """Submit one order. Match while it crosses; rest any leftover.

        Returns the list of trades this single order produced (for printing).
        """
        fills = []
        if side == "buy":
            # A buy crosses while the BEST ask (asks[0]) is priced AT OR BELOW
            # what we're willing to pay. asks[0] is the best because the list
            # is sorted low -> high.
            while size > 0 and self.asks and self.asks[0][0] <= price:
                ask_price, ask_size = self.asks[0]
                qty = min(size, ask_size)          # trade the smaller of the two
                fills.append((ask_price, qty))     # prints at the RESTING price
                self.trades.append((ask_price, qty))
                size -= qty                        # consume the incoming order
                if qty == ask_size:
                    self.asks.pop(0)               # that level fully eaten -> gone
                else:
                    self.asks[0] = (ask_price, ask_size - qty)  # partial: shrink it
            if size > 0:                           # leftover that didn't cross
                self._rest_bid(price, size)        #   rests as a new bid
        else:  # sell
            # A sell crosses while the BEST bid (bids[0]) is priced AT OR ABOVE
            # what we'll accept. bids[0] is the best because sorted high -> low.
            while size > 0 and self.bids and self.bids[0][0] >= price:
                bid_price, bid_size = self.bids[0]
                qty = min(size, bid_size)
                fills.append((bid_price, qty))
                self.trades.append((bid_price, qty))
                size -= qty
                if qty == bid_size:
                    self.bids.pop(0)
                else:
                    self.bids[0] = (bid_price, bid_size - qty)
            if size > 0:
                self._rest_ask(price, size)
        return fills

    def best_bid(self):
        return self.bids[0][0] if self.bids else None

    def best_ask(self):
        return self.asks[0][0] if self.asks else None

    def show(self):
        print("        ASKS (sellers)")
        for price, size in reversed(self.asks):
            print(f"        {price:7.2f}  x{size}")
        bb, ba = self.best_bid(), self.best_ask()
        if bb is not None and ba is not None:
            print(f"  ----  spread = {ba - bb:.2f}  ----")
        else:
            print("  ----")
        for price, size in self.bids:
            print(f"        {price:7.2f}  x{size}")
        print("        BIDS (buyers)")


def report(label, eng, side, price, size):
    """Submit one order and narrate exactly what the loop did."""
    arrow = "BUY " if side == "buy" else "SELL"
    print(f"\n=== {label}: {arrow} {size} @ {price:.2f} ===")
    fills = eng.submit(side, price, size)
    if fills:
        total = sum(q for _, q in fills)
        for fp, fq in fills:
            print(f"   TRADE  {fq} @ {fp:.2f}")
        if len(fills) > 1:
            print(f"   ({len(fills)} fills, {total} total — it SWEPT several levels)")
        # Did any size rest? Compare what we matched to what we sent.
        if total < size:
            print(f"   leftover {size - total} did not cross -> RESTS in the book")
        else:
            print("   fully filled -> nothing rests")
    else:
        print("   no cross -> the whole order RESTS as a new limit")
    eng.show()


# ---------------------------------------------------------------------------
# A scripted sequence of orders, narrated
# ---------------------------------------------------------------------------
eng = Engine()

# Seed the book with the usual resting orders (the market when you "arrive").
for p, s in [(99.98, 5), (99.97, 2), (99.95, 8)]:
    eng._rest_bid(p, s)
for p, s in [(100.02, 4), (100.03, 6), (100.05, 3)]:
    eng._rest_ask(p, s)

print("Starting book (best bid 99.98, best ask 100.02, spread 0.04):")
eng.show()

# 1) A NON-crossing limit. 100.00 is below the best ask 100.02, so it does NOT
#    cross. It just rests as a new best bid and tightens the spread.
report("Order 1 (rests)", eng, "buy", 100.00, 3)

# 2) An EXACT-fill buy. 100.02 meets the best ask 100.02 exactly: it crosses,
#    eats all 4 there, and is fully filled. Nothing left to rest.
report("Order 2 (exact fill)", eng, "buy", 100.02, 4)

# 3) A PARTIAL fill. Sell 6 @ 100.00. The best bid is now 100.00 (from order 1,
#    size 3) which qualifies, then 99.98 x5. We hit 100.00 x3, then 99.98 takes
#    the other 3 -> a 2-level match, fully filled, nothing rests.
report("Order 3 (sweep down 2 levels)", eng, "sell", 99.98, 6)

# 4) A SWEEP that leaves a leftover. Buy 12 @ 100.05 — aggressive enough to
#    clear 100.03 x6 and 100.05 x3 (9 total), but 3 are left over with nothing
#    cheaper to buy, so they REST as a new bid at 100.05.
report("Order 4 (sweep + leftover rests)", eng, "buy", 100.05, 12)

print(f"\nTape so far: {len(eng.trades)} trades printed.")
print("Each trade printed at the RESTING order's price — first come, served first.")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. AGGRESSIVE CLEAR: after the script runs, add
#       report("mine", eng, "sell", 99.00, 50)
#    A sell priced at 99.00 crosses EVERY bid (all are >= 99.00). Watch it
#    sweep the whole bid side in one loop, then rest the remainder as an ask.
#
# 2. A RESTING LIMIT: add
#       report("mine", eng, "buy", 99.50, 4)
#    99.50 is below every ask, so it can't cross — it just rests as a bid. No
#    trade. This is the Lesson 15 "limit rests" case, handled by the same loop.
#
# 3. CHANGE THE PRICE: in Order 4 above, lower 100.05 to 100.02. Now it only
#    crosses the 100.02 level (if any remains) and rests sooner. The price you
#    pick decides how DEEP into the book you eat before you stop crossing.
#
# 4. MARKET ORDER = infinite price: call eng.submit("buy", 1e9, 5). A price so
#    high it crosses anything available is exactly a market order (Lesson 14):
#    it walks the book until filled or the book runs dry.
