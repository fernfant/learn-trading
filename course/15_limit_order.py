"""
LESSON 15 — A limit order rests: price-time priority & the queue (Track 2)

In Lesson 14 a MARKET order said "fill me NOW, at whatever price" and ate the
top of the book. A LIMIT order is the opposite kind of patience:

    LIMIT order = "fill me only at MY price or BETTER — otherwise WAIT."

If it can't trade right away it doesn't vanish; it RESTS in the book and joins a
QUEUE of other orders sitting at prices. When a market order finally arrives,
the exchange has to decide WHO gets filled first. The rule almost every real
exchange uses is PRICE-TIME PRIORITY:

    1. PRICE first  — a better price is always served first.
                      (for buyers: a HIGHER bid is better;
                       for sellers: a LOWER ask is better.)
    2. TIME second  — among orders at the SAME price, FIRST-IN-FIRST-OUT:
                      whoever arrived earlier sits ahead in the queue.

That second rule is the whole lesson. Your PLACE IN LINE — set the moment your
order arrives — decides whether you actually get filled when buyers show up, or
whether you sit there untouched while the people ahead of you trade.

One detail: we track arrival order with an incrementing SEQUENCE NUMBER, not a
wall-clock timestamp. The exchange only cares about ORDER of arrival, and a
counter is exact and reproducible (two orders can't share a nanosecond, but they
can never share a sequence number either).

Cumulative artifact: ../exchange.py will get add_limit(side, price, size) that
inserts a resting order with exactly this price-time priority.

Run it:  python3 15_limit_order.py
Then read 15_walkthrough.md.
"""


# ---------------------------------------------------------------------------
# A tiny book that REMEMBERS arrival order
# ---------------------------------------------------------------------------
# Each resting order is a dict: who posted it, the price, the size, and the
# `seq` (arrival sequence number). We keep one shared counter so every order
# that arrives gets the next number — the lower the seq, the earlier it came in.
class Book:
    def __init__(self):
        self.bids = []     # resting buyers
        self.asks = []     # resting sellers
        self.seq = 0       # arrival counter; NOT a clock

    def add_limit(self, side, who, price, size):
        self.seq += 1
        order = {"who": who, "price": price, "size": size, "seq": self.seq}
        (self.bids if side == "buy" else self.asks).append(order)
        self._sort()
        return order

    # Sort each side into PRICE-TIME PRIORITY order: index 0 is "first in line".
    # Bids: highest price first (a buyer paying more is more eager) — so we sort
    #   by price DESCENDING. Asks: lowest price first.
    # Tie-break BOTH sides by seq ASCENDING — earlier arrival sits ahead.
    def _sort(self):
        self.bids.sort(key=lambda o: (-o["price"], o["seq"]))
        self.asks.sort(key=lambda o: (o["price"], o["seq"]))

    def show_bids(self):
        print("   BID QUEUE (buyers waiting — front of line is who fills first):")
        if not self.bids:
            print("      (empty)")
        for i, o in enumerate(self.bids):
            tag = "<- FRONT" if i == 0 else ""
            print(f"      #{i+1}  {o['who']:<6} {o['price']:7.2f} x{o['size']:<3}"
                  f"  (arrived #{o['seq']}) {tag}")


# ---------------------------------------------------------------------------
# PART A — equal price: FIRST come, FIRST served
# ---------------------------------------------------------------------------
# Three buyers all want to pay the SAME price, 99.98. None is willing to pay
# more than another, so PRICE can't break the tie — TIME does. The one who
# arrived first sits at the front of the queue.
print("PART A — three buyers, same price 99.98. Who's first in line?\n")
book = Book()
book.add_limit("buy", "Ann", 99.98, 5)     # arrives 1st
book.add_limit("buy", "Bob", 99.98, 3)     # arrives 2nd
book.add_limit("buy", "Cara", 99.98, 4)    # arrives 3rd
book.show_bids()
print("\n   Same price for all three, so it's pure FIFO: Ann arrived first, so")
print("   Ann is first in line. Bob and Cara queue behind her in arrival order.\n")


# ---------------------------------------------------------------------------
# PART B — a better price JUMPS the queue
# ---------------------------------------------------------------------------
# Now Dan arrives LAST, but bids a HIGHER price (99.99). Price beats time: even
# though everyone else got here earlier, Dan's better price puts him at the very
# FRONT. Being early only matters AMONG orders at the same price.
print("PART B — Dan arrives last but bids 99.99 (a better price). He jumps the line.\n")
book.add_limit("buy", "Dan", 99.99, 2)     # arrives 4th, but best price
book.show_bids()
print("\n   Dan paid for priority with PRICE, not patience. Behind him, the 99.98")
print("   crowd is still ordered by arrival: Ann, then Bob, then Cara.\n")


# ---------------------------------------------------------------------------
# PART C — a market order arrives and eats from the FRONT
# ---------------------------------------------------------------------------
# A market SELL order shows up wanting to dump 8 units immediately. It takes
# whatever's at the front of the bid queue, in order, until it's filled. Being
# early (or paying a better price) is what gets you a trade here.
def fill_market_sell(book, size):
    print(f"   A market SELL for {size} units arrives. It fills the FRONT of the")
    print("   bid queue first, walking down the line until it's done:\n")
    remaining = size
    while remaining > 0 and book.bids:
        front = book.bids[0]
        take = min(remaining, front["size"])
        print(f"      filled {take} from {front['who']} @ {front['price']:.2f}"
              f"  (was arrival #{front['seq']})")
        front["size"] -= take
        remaining -= take
        if front["size"] == 0:
            book.bids.pop(0)             # fully filled — leaves the queue
    if remaining > 0:
        print(f"      ...market order still wants {remaining}, but the queue is empty.")
    print()

print("PART C — a market SELL for 8 units arrives. Who actually trades?\n")
fill_market_sell(book, 8)
print("   Still resting (these buyers did NOT get filled — they were too far back):")
book.show_bids()
print("\n   Dan (best price) and Ann (earliest at 99.98) traded. Bob got a partial.")
print("   Cara, last in line at 99.98, is left holding an unfilled order. Her place")
print("   in the queue — decided the instant she arrived — is why she missed out.\n")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. In PART A, add a 4th buyer at 99.98 BEFORE the others by moving the line
#    up. Re-run: the queue is still pure arrival order. Earlier seq = earlier
#    in line, every time.
# 2. To JUMP the queue, post at a better price: add book.add_limit("buy",
#    "You", 100.00, 10) in PART B. You leap straight to the front, ahead of Dan.
# 3. To get filled LAST, post LATE at the SAME price as everyone: add a buyer at
#    99.98 in PART B, then run PART C. You'll sit behind the whole 99.98 crowd
#    and the market order will run out before reaching you.
# 4. Make the market SELL bigger (size=20) in PART C. It clears the entire bid
#    queue — and any leftover would rest as a new ask. Resting leftovers is what
#    Lesson 16's matching loop handles.
