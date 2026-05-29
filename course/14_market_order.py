"""
LESSON 14 — A market order eats the book (Track 2: inside the exchange)

Lesson 13 built the order book: two sorted lists of resting orders. The asks
are sellers, cheapest first; the bids are buyers, highest first. Nobody had
crossed the spread yet — the book just sat there.

Now someone arrives in a hurry. A MARKET order says: "fill me NOW, whatever the
price." It does not name a price. It just takes whatever the book is offering,
starting from the best level and working outward:

    a market BUY  eats the cheapest ASK first, then the next ask, then the next
    a market SELL hits the highest BID first, then the next bid, then the next

A SMALL order is fully filled at the top level — you pay (about) the best price.
A BIG order exhausts the top level and has to "walk" down to worse prices to get
the rest. Its AVERAGE fill price ends up worse than the price you saw at the top.

That gap — (average fill price) minus (best price you started from) — is
SLIPPAGE. In Track 1 you paid slippage as a customer (Lesson 9) without seeing
why. Here is the mechanism, from the inside: a big order simply runs out of
cheap sellers and reaches up the ladder for more.

Two rules fall out, and they are the whole lesson:
    1. Bigger order  -> walks deeper -> more slippage.
    2. Thinner book   -> less size at each level -> more slippage for the same order.

Cumulative artifact: ../exchange.py gets `match_market(side, size)`, which walks
the levels exactly like fill_market_buy below, returning the fills and the
volume-weighted average price (VWAP).

Run it:  python3 14_market_order.py
Then read 14_walkthrough.md.
"""


# ---------------------------------------------------------------------------
# A standalone book — just the ASK side (the sellers), since we'll buy from it.
# Each level is (price, size): a price, and how many units rest there.
# Asks are sorted cheapest-first, because a buyer always takes the cheapest
# seller available first.
# ---------------------------------------------------------------------------
ASKS = [
    (100.02, 4),   # best ask: 4 units for sale at 100.02
    (100.03, 6),   # next level up
    (100.05, 3),   # and the next
    (100.08, 10),  # a deeper, larger level
]

BEST_ASK = ASKS[0][0]   # the price you "see" at the top of the book


def fill_market_buy(asks, size):
    """Fill a market BUY of `size` units by walking the asks cheapest-first.

    Returns (fills, vwap, filled):
      fills  - list of (price, qty) we actually traded at each level
      vwap   - volume-weighted average price we paid (None if nothing filled)
      filled - how many units we managed to fill (may be < size if the book
               runs dry)
    """
    remaining = size
    fills = []
    cost = 0.0           # total money spent = sum(price * qty)
    for price, avail in asks:
        if remaining <= 0:
            break
        take = min(remaining, avail)   # eat as much of this level as we need
        fills.append((price, take))
        cost += price * take
        remaining -= take
    filled = size - remaining
    vwap = cost / filled if filled > 0 else None
    return fills, vwap, filled


def show_fill(label, size):
    fills, vwap, filled = fill_market_buy(ASKS, size)
    print(label)
    print(f"   market BUY {size} units (best ask is {BEST_ASK:.2f})")
    for price, qty in fills:
        print(f"      ate {qty:>2} @ {price:.2f}")
    if filled < size:
        print(f"      !! only {filled} of {size} filled — the book ran dry")
    # slippage = how much worse the average price is than the top of the book.
    slip = vwap - BEST_ASK
    print(f"   average fill (VWAP) = {vwap:.4f}")
    print(f"   slippage vs best ask = {slip:+.4f} per unit "
          f"(${slip * filled:+.2f} total on {filled} units)\n")


print("THE BOOK (asks / sellers, cheapest first):")
for price, size in ASKS:
    print(f"   {price:.2f}  x{size}")
print()

# A SMALL order: 3 units fits entirely inside the top level (4 available).
# You pay exactly the best ask. No walking, so ~zero slippage.
show_fill("SMALL ORDER", 3)

# A LARGE order: 12 units. The top level only has 4, so it walks down through
# 100.03 and 100.05 to find the rest. The average price you pay is now clearly
# worse than the 100.02 you saw at the top — that's slippage, from the inside.
show_fill("LARGE ORDER", 12)


# ---------------------------------------------------------------------------
# Same large order, but a THINNER book — half the size at each level. The order
# now has to walk EVEN deeper to fill, so slippage gets worse. Liquidity (how
# much rests near the top) is what protects a big order from slippage.
# ---------------------------------------------------------------------------
THIN = [(p, max(1, s // 2)) for p, s in ASKS]
print("THINNER BOOK (half the size at each level):")
for price, size in THIN:
    print(f"   {price:.2f}  x{size}")
fills, vwap, filled = fill_market_buy(THIN, 12)
for price, qty in fills:
    print(f"      ate {qty:>2} @ {price:.2f}")
slip = vwap - THIN[0][0]
print(f"   average fill (VWAP) = {vwap:.4f}")
print(f"   slippage vs best ask = {slip:+.4f} per unit  "
      f"(worse than the fat book above)\n")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. Make the order BIGGER: call show_fill("HUGE", 20). It walks all four
#    levels and the VWAP climbs again — bigger order, more slippage.
# 2. Make the book THINNER still: change THIN to (p, 1) for every level, then
#    refill 12 units. With only 1 unit per level the book runs DRY before the
#    order fills — `filled` is less than 12. A market order can't conjure
#    liquidity that isn't there.
# 3. Make the book DEEPER: add (100.02, 20) worth of size at the top by editing
#    ASKS[0] to (100.02, 24). Now the 12-unit order fits entirely at the top —
#    slippage drops back to zero. Depth at the top is what kills slippage.
# 4. Write the mirror, fill_market_sell(bids, size): a market SELL hits the
#    HIGHEST bid first and walks DOWN. Slippage is then (best_bid - vwap) — the
#    average you receive is LOWER than the top bid. Same idea, other side.
