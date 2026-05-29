"""
LESSON 18 — Be the market maker: quote both sides, earn the spread (Track 2)

This is the payoff of Track 2. Everything so far built the machine: a book
(L13), market orders eating it (L14), limit orders resting in a queue (L15),
the matching loop (L16), the tape an HFT watches (L17). Now you sit in the
seat that makes money.

A MARKET MAKER does NOT predict which way the price goes. It posts TWO resting
limit orders around a fair value:

    bid  = fair - h     (a little BELOW fair — "I'll BUY here")
    ask  = fair + h     (a little ABOVE fair — "I'll SELL here")

where `h` is the HALF-SPREAD. The full spread it quotes is `2*h`. Then it waits.

    When a BUYER comes in, they hit the ask  -> the MM SELLS  at fair+h.
    When a SELLER comes in, they hit the bid -> the MM BUYS   at fair-h.

If a buy and a sell both arrive, the MM bought at fair-h and sold at fair+h:
it pocketed the full spread `2*h` WITHOUT predicting direction. This is the
exact spread you PAID as a customer in Track 1 (Lesson 2, Lesson 9) — now you
EARN it. Cost flipped to revenue, just like Lesson 12 promised.

THE HONEST CATCH (sets up Lessons 19 & 21): this only works if buys and sells
roughly BALANCE. A burst of one-sided flow — say, everyone buying — fills your
ask again and again, and now you are short a big pile of INVENTORY at a price
that can run away from you. You wanted the fee; you got a position. Taming that
is inventory risk (L19) and adverse selection (L21).

Cumulative artifact: ../exchange.py will get a MarketMaker.quote() that posts a
bid/ask around the mid and captures the spread, exactly as modelled here.

Run it:  python3 18_market_maker.py
Then read 18_walkthrough.md.

Reference: Cartea, Jaimungal & Penalva, *Algorithmic and High-Frequency Trading*.
"""

import random

random.seed(18)            # reproducible: the numbers below match the walkthrough

HALF_SPREAD = 0.05         # h: we quote bid = fair-0.05, ask = fair+0.05
START_FAIR = 100.0         # the fair value our quotes straddle


class MarketMaker:
    """Posts a bid and an ask around `fair`, and fills passively when hit.

    We track three things, and they are the whole job:
      cash       — money in, money out. SELLS add cash, BUYS spend it.
      inventory  — net units held. +ve = long (bought more than sold),
                   -ve = short (sold more than bought). We WANT this near 0.
      P&L        — cash plus inventory marked at the current fair value.
                   This is the honest scoreboard (cf. Lesson 4's equity).
    """

    def __init__(self, half_spread):
        self.h = half_spread
        self.cash = 0.0
        self.inventory = 0
        self.fills = 0

    def quote(self, fair):
        # The two prices we stand ready to trade at, straddling fair value.
        return fair - self.h, fair + self.h     # bid, ask

    def on_buy(self, fair):
        # A taker BUYS -> they lift our ASK -> we SELL one unit at fair+h.
        _, ask = self.quote(fair)
        self.cash += ask                         # selling brings cash IN
        self.inventory -= 1                      # we are now shorter by one
        self.fills += 1
        return ask

    def on_sell(self, fair):
        # A taker SELLS -> they hit our BID -> we BUY one unit at fair-h.
        bid, _ = self.quote(fair)
        self.cash -= bid                         # buying spends cash
        self.inventory += 1                      # we are now longer by one
        self.fills += 1
        return bid

    def pnl(self, fair):
        # Realized cash PLUS the open inventory marked at fair value. If we are
        # perfectly flat (inventory == 0) this is pure spread we captured.
        return self.cash + self.inventory * fair


def walk(fair):
    # Fair value drifts a little each step — a slow random walk, like a real
    # mid price. The MM does NOT know which way it goes; that's the point.
    return fair + random.gauss(0, 0.02)


# ---------------------------------------------------------------------------
# PART A — one clean round trip: buy low, sell high, pocket the spread
# ---------------------------------------------------------------------------
# Strip everything away. Fair value sits at 100. A seller comes, then a buyer.
# We buy at 99.95 and sell at 100.05. We end flat, +0.10 richer — the full
# 2*h spread, earned without guessing direction.
print("PART A — one round trip at a flat fair value of 100.00\n")
mm = MarketMaker(HALF_SPREAD)
fair = START_FAIR
bid, ask = mm.quote(fair)
print(f"   we quote:  bid {bid:.2f}  /  ask {ask:.2f}   (spread {2*mm.h:.2f})")
px = mm.on_sell(fair)
print(f"   a SELLER hits our bid -> we BUY 1 @ {px:.2f}  "
      f"(inv {mm.inventory:+d}, cash {mm.cash:+.2f})")
px = mm.on_buy(fair)
print(f"   a BUYER lifts our ask -> we SELL 1 @ {px:.2f}  "
      f"(inv {mm.inventory:+d}, cash {mm.cash:+.2f})")
print(f"\n   flat again (inv {mm.inventory:+d}), and P&L = {mm.pnl(fair):+.2f} — "
      f"the full {2*mm.h:.2f} spread, earned by standing in the middle.\n")


# ---------------------------------------------------------------------------
# PART B — BALANCED flow over many fills: the spread adds up
# ---------------------------------------------------------------------------
# Now let real, random flow arrive: each step a taker shows up and is equally
# likely to buy or sell. Fair value wanders. Because buys and sells roughly
# balance, inventory stays near zero and we steadily bank ~half the spread per
# fill (a full spread per matched round trip). No prediction anywhere.
print("PART B — 200 balanced fills (buyer or seller, 50/50 each step)\n")
mm = MarketMaker(HALF_SPREAD)
fair = START_FAIR
print("   step    fair   side   inv    cash      P&L")
for step in range(1, 201):
    fair = walk(fair)
    if random.random() < 0.5:
        mm.on_buy(fair)
        side = "buy "
    else:
        mm.on_sell(fair)
        side = "sell"
    if step % 40 == 0 or step == 1:
        print(f"   {step:4d}  {fair:7.2f}  {side}  {mm.inventory:+4d}  "
              f"{mm.cash:+8.2f}  {mm.pnl(fair):+7.2f}")

print(f"\n   {mm.fills} fills, ending inventory {mm.inventory:+d} (near flat).")
print(f"   P&L = {mm.pnl(fair):+.2f}  ~=  {mm.fills} fills x half-spread "
      f"{mm.h:.2f} = {mm.fills*mm.h:.2f} ideal.")
print("   We never guessed direction. We earned the SPREAD, one fill at a time.\n")


# ---------------------------------------------------------------------------
# PART C — the lurking risk: ONE-SIDED flow leaves us holding inventory
# ---------------------------------------------------------------------------
# Same maker, but now the flow is toxic: 50 buyers in a row and not one seller.
# Every fill lifts our ask, so we keep SELLING — and our inventory marches
# negative (we're getting more and more SHORT). Worse, all that buying tends to
# drag fair value UP, exactly the wrong way for a short. Our marked P&L turns
# red even though we "earned the spread" on every single fill.
print("PART C — 50 buyers in a row (one-sided flow), fair drifting up\n")
mm = MarketMaker(HALF_SPREAD)
fair = START_FAIR
print("   step    fair   inv     cash      P&L")
for step in range(1, 51):
    fair += 0.03                 # one-sided buying pushes fair value up
    mm.on_buy(fair)              # every taker BUYS -> we keep SELLING (short)
    if step % 10 == 0 or step == 1:
        print(f"   {step:4d}  {fair:7.2f}  {mm.inventory:+4d}  "
              f"{mm.cash:+8.2f}  {mm.pnl(fair):+7.2f}")

print(f"\n   We collected the half-spread on all {mm.fills} fills (cash looks great),")
print(f"   but we're now SHORT {abs(mm.inventory)} units into a RISING price.")
print(f"   Marked P&L = {mm.pnl(fair):+.2f} — the spread we 'earned' is dwarfed by")
print("   the loss on inventory we never wanted. THAT is the market maker's real")
print("   enemy. Skewing quotes to fight it is Lesson 19; the informed flow that")
print("   causes it on purpose is Lesson 21.\n")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. WIDEN the spread: set HALF_SPREAD = 0.10 at the top and re-run Part B.
#    Each fill earns more, but in a real book a wider quote sits further from
#    fair and gets hit LESS often — more profit per fill, fewer fills. The
#    interactive page (html/lesson_18.html) lets you feel that trade-off live.
# 2. NARROW it: HALF_SPREAD = 0.01. Thinner margin per fill; you'd need far more
#    flow to make the same money. This is the razor real market makers walk.
# 3. In Part B, tilt the flow: change `0.5` to `0.6` so buyers slightly
#    outnumber sellers. Watch inventory drift one way and P&L wobble — a gentle
#    preview of Part C's one-sided disaster.
# 4. In Part C, flip it to 50 SELLERS (mm.on_sell, fair -= 0.03). Now you go
#    LONG into a falling price — the mirror-image inventory blow-up.
# 5. Open ../exchange.py: picture a MarketMaker.quote(mid) posting these same
#    bid/ask as two resting limit orders that the matching loop (L16) fills.
