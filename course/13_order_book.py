"""
LESSON 13 — The order book: bids, asks, depth & the spread (Track 2: HFT)

Track 1 handed you "the price" as one number from the sky. Lesson 12 flipped your
seat: you're no longer the customer paying the spread, you're the machine that
EARNS it. But what machine? This one. An exchange is, at its heart, almost
embarrassingly simple:

    AN ORDER BOOK IS JUST TWO SORTED LISTS.

    BIDS = buyers.  Each says "I'll BUY this much, up to this price."
                    Sorted HIGHEST price first — the most anyone will pay.
    ASKS = sellers. Each says "I'll SELL this much, down to this price."
                    Sorted LOWEST price first — the least anyone will accept.

The top of each list is the BEST BID and BEST ASK. The gap between them is the
SPREAD. Their average is the MID — and that single mid number is exactly the
"price" market.py used in Track 1 all along. DEPTH is just how much size sits
waiting at each price level.

That's the whole lesson: the book IS the market. Nobody hands down a price;
it emerges from this stack of resting orders.

This standalone script is a mini-version of the OrderBook in ../exchange.py
(same bids/asks/best_bid/best_ask/spread, same ASCII ladder). exchange.py is the
real cumulative artifact you grow; this file is a sandbox to poke at the idea.

Run it:  python3 13_order_book.py
Then read 13_walkthrough.md.
"""


class OrderBook:
    def __init__(self):
        # Each resting order is just (price, size). We keep the lists sorted so
        # the BEST price is always at index 0 — no searching required.
        self.bids = []  # buyers,  sorted high -> low  (best = highest price)
        self.asks = []  # sellers, sorted low  -> high (best = lowest price)

    def add_bid(self, price, size):
        # A new buyer joins. Re-sort so the most generous buyer stays on top.
        self.bids.append((price, size))
        self.bids.sort(key=lambda o: -o[0])

    def add_ask(self, price, size):
        # A new seller joins. Re-sort so the cheapest seller stays on top.
        self.asks.append((price, size))
        self.asks.sort(key=lambda o: o[0])

    def best_bid(self):
        return self.bids[0][0] if self.bids else None

    def best_ask(self):
        return self.asks[0][0] if self.asks else None

    def spread(self):
        # The gap you must cross to trade RIGHT NOW. None if one side is empty.
        if self.bids and self.asks:
            return self.best_ask() - self.best_bid()
        return None

    def mid(self):
        # The fair "price" halfway between the best buyer and best seller.
        # THIS is the number Track 1 quietly called "the price".
        if self.bids and self.asks:
            return (self.best_bid() + self.best_ask()) / 2
        return None

    def show(self):
        # An ASCII ladder: asks stacked on top (you read prices DOWN toward the
        # spread), bids below. The '#' bars show DEPTH — more size, longer bar.
        print("         ASKS (sellers, cheapest nearest the spread)")
        for price, size in reversed(self.asks):
            print(f"   {price:8.2f}  x{size:<3d} {'#' * size}")
        sp, md = self.spread(), self.mid()
        if sp is not None:
            print(f"   -------- spread {sp:.2f} · mid {md:.2f} --------")
        else:
            print("   -------- (one side empty) --------")
        for price, size in self.bids:
            print(f"   {price:8.2f}  x{size:<3d} {'#' * size}")
        print("         BIDS (buyers, most generous nearest the spread)")


def report(book, label):
    print(f"\n=== {label} ===")
    book.show()
    bb, ba = book.best_bid(), book.best_ask()
    print(f"   best bid {bb:.2f} | best ask {ba:.2f} | "
          f"spread {book.spread():.2f} | mid {book.mid():.3f}")


# ---------------------------------------------------------------------------
# PART A — seed the book and read it
# ---------------------------------------------------------------------------
# These are the SAME resting orders ../exchange.py starts with: the kind of
# stack already sitting on a real exchange the moment you arrive.
book = OrderBook()
book.add_bid(99.98, 5)
book.add_bid(99.97, 2)
book.add_bid(99.95, 8)
book.add_ask(100.02, 4)
book.add_ask(100.03, 6)
book.add_ask(100.05, 3)
report(book, "the book as you find it")
print("   To trade NOW you cross the spread: buy at 100.02 or sell at 99.98.")


# ---------------------------------------------------------------------------
# PART B — a tighter bid SHRINKS the spread
# ---------------------------------------------------------------------------
# Someone posts a more generous buy order at 100.01 — above the old best bid of
# 99.98. They jump to the top of the bids. The best ask hasn't moved, so the gap
# between best bid and best ask gets SMALLER. A tighter book is a cheaper book
# to trade in — and exactly what a market maker competes to provide.
book.add_bid(100.01, 1)
report(book, "after a better bid at 100.01")
print("   The spread fell from 0.04 to 0.01 — the book got TIGHTER.")
print(f"   The mid moved too: it's now {book.mid():.3f}, nudged up toward the buyers.")


# ---------------------------------------------------------------------------
# PART C — depth: size matters as much as price
# ---------------------------------------------------------------------------
# Two books can show the SAME best bid/ask yet behave very differently. Depth is
# how much size waits at each level. A thin level is easily swept; a deep one
# absorbs big orders without the price moving. (Eating through depth = slippage,
# which is Lesson 14.)
print("\n=== depth at each price level ===")
for price, size in book.asks:
    print(f"   ask {price:8.2f}: {size} unit(s) waiting")
for price, size in book.bids:
    print(f"   bid {price:8.2f}: {size} unit(s) waiting")
total_bid = sum(s for _, s in book.bids)
total_ask = sum(s for _, s in book.asks)
print(f"   total resting: {total_bid} units want to BUY, {total_ask} want to SELL.")


# ---------------------------------------------------------------------------
# PART D — the mid IS Track 1's "price"
# ---------------------------------------------------------------------------
# In market.py the whole world was one number. Here you can see where it lived:
# dead center between the best buyer and best seller. It isn't a real tradeable
# price — you can never buy OR sell at the mid — but it's the fair reference
# everyone quotes around.
print("\n=== the mid is the single 'price' from Track 1 ===")
print(f"   best bid {book.best_bid():.2f}  (you could SELL here)")
print(f"   best ask {book.best_ask():.2f}  (you could BUY here)")
print(f"   mid      {book.mid():.3f}  (nobody trades here — it's the reference)")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. Add a deep seller: book.add_ask(100.02, 20). The best ask price doesn't
#    change, but now 24 units sit at 100.02. Re-run report(book, "..."). The
#    spread and mid are identical — DEPTH changed, the top of book didn't.
#
# 2. Add a bid that BEATS the best ask: book.add_bid(100.10, 5). That buyer will
#    pay MORE than the cheapest seller asks — they should trade instantly! Our
#    book just stacks it (a "crossed" book). Notice spread() goes NEGATIVE.
#    Actually matching those two is Lesson 14 (market orders) and Lesson 16
#    (the matching loop). For now, see why a real book is NEVER crossed.
#
# 3. Empty one side: build a fresh OrderBook with only bids. What do best_ask(),
#    spread() and mid() return? (None — there's no two-sided market to quote.)
#
# 4. Open ../exchange.py — it carries this exact OrderBook as its seed. This
#    lesson is that book standing still; the next few make orders flow through
#    it.
