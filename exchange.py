"""
exchange.py — the cumulative artifact for TRACK 2 (high-frequency trading).

Track 1 (market.py) treated "the price" as one number handed to you from the
sky. But where does that number come from? From an EXCHANGE matching buyers
and sellers in an ORDER BOOK. Track 2 builds that machine, then puts a fast
trading bot on top of it.

Right now it is at the LESSON 11 stage: an order book is just two sorted
lists — people willing to BUY (bids) and people willing to SELL (asks). The
gap between the best of each is the SPREAD, and the spread is where an HFT
market maker earns its living.

------------------------------------------------------------------------------
BUILD MAP  (Track 2 picks up where Track 1's capstone ends)
------------------------------------------------------------------------------
  L11 the book exists        bids[], asks[], best_bid, best_ask, spread   <-- HERE
  L12 a market order eats     fill against the top of the book
  L13 a limit order rests     insert with price-time priority
  L14 the matching loop       cross bids vs asks -> trades
  L15 market data feed        top-of-book + depth snapshots
  L16 a market maker          quote both sides, capture the spread
  L17 inventory risk          skew quotes when you hold too much
  L18 latency & the queue     why being 1 microsecond faster pays
  L19 adverse selection       getting run over by informed flow
  L20 CAPSTONE               a market maker that stays profitable AND flat
------------------------------------------------------------------------------
Run it:  python3 exchange.py
"""


class OrderBook:
    def __init__(self):
        # Each entry is (price, size). Kept sorted so the BEST price is easy
        # to find. Bids: highest price first (the most someone will pay).
        # Asks: lowest price first (the least someone will sell for).
        self.bids = []  # buyers, sorted high -> low
        self.asks = []  # sellers, sorted low -> high

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

    def spread(self):
        if self.bids and self.asks:
            return self.best_ask() - self.best_bid()
        return None

    def show(self):
        print("        ASKS (sellers)")
        for price, size in reversed(self.asks):
            print(f"        {price:7.2f}  x{size}")
        sp = self.spread()
        print(f"  ----  spread = {sp:.2f}  ----" if sp is not None else "  ----")
        for price, size in self.bids:
            print(f"        {price:7.2f}  x{size}")
        print("        BIDS (buyers)")


book = OrderBook()
# A handful of resting orders — the kind of thing already sitting on a real
# exchange when you arrive.
book.add_bid(99.98, 5)
book.add_bid(99.97, 2)
book.add_bid(99.95, 8)
book.add_ask(100.02, 4)
book.add_ask(100.03, 6)
book.add_ask(100.05, 3)

book.show()
print(f"\nBest buyer pays {book.best_bid():.2f}, best seller wants "
      f"{book.best_ask():.2f}. To trade RIGHT NOW you cross the "
      f"{book.spread():.2f} spread.")


# -----------------------------------------------------------------------------
# TRY IT (exercises)
# -----------------------------------------------------------------------------
# 1. Add a new bid at 100.01 (book.add_bid(100.01, 1)). It's now the best bid.
#    What is the spread? It got smaller — the book got "tighter".
# 2. Add a bid at 100.04. That buyer is willing to pay MORE than the best
#    seller wants. They should trade immediately! Right now the book just
#    holds it. Fixing that — matching crossed orders — is Lesson 12-14.
# 3. The "mid price" is (best_bid + best_ask) / 2. Print it. That single
#    number is what Track 1's market.py was secretly using all along.
