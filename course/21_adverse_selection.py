"""
LESSON 21 — Adverse selection: toxic / informed flow runs you over
            (Track 2: inside the exchange / HFT)

This is the market maker's deepest problem, and the payoff of a thread that has
run through the whole course since Lesson 0.

You are the market maker (Lesson 18). You post a bid a little below fair value
and an ask a little above it, and you hope to get hit on BOTH sides: buy low,
sell high, pocket the spread, predict nothing. That captured spread is your
entire edge.

The trouble is WHO trades with you. Two kinds of taker arrive:

    NOISE traders   — uninformed. They buy and sell for reasons unrelated to the
                      next price move (rebalancing, hedging, boredom). Filling
                      them is exactly the flow you want: they pay you the spread
                      and the price wanders off randomly afterwards, so on
                      average you keep the spread. Harmless. Profitable.

    INFORMED traders — they KNOW something. The price is about to move, and they
                      trade with you right before it does. An informed BUYER
                      lifts your ask the instant before the price rises — so you
                      sold, and now you're short into a rally. An informed SELLER
                      hits your bid right before the price falls — so you bought,
                      and now you're long into a drop. Either way you are
                      systematically on the WRONG side of the move.

That systematic wrong-siding is ADVERSE SELECTION (Glosten-Milgrom 1985; Kyle
1985): the very act of someone wanting to trade with you is mild evidence that
trading with them is a bad idea. You earn small, steady spreads from the noise
majority and pay large, lumpy losses to the informed minority. As the informed
FRACTION rises, your P&L falls -- and can go negative.

The defense in this lesson: WIDEN THE SPREAD. Charge everyone (the harmless
noise majority included) a little more, so the spread you bank on noise fills
finally covers the losses to the toxic minority. The catch -- which the capstone
makes you feel -- is that a wider quote sits further from fair and wins less
flow. Too tight and toxic flow eats you; too wide and you trade with nobody.

THE BEAUTIFUL SYMMETRY (Lesson 0, made literal): the informed trader who was the
faint SIGNAL you hunted in Track 1 is the HAZARD that bleeds you in Track 2.
Same person, opposite seat.

Reference: Maureen O'Hara, *Market Microstructure Theory* (Glosten-Milgrom, Kyle).

Run it:  python3 21_adverse_selection.py
Then read 21_walkthrough.md.
"""

import random

# Seeded so the numbers here match the walkthrough exactly. Change it for a
# different (but statistically identical) market.
random.seed(21)

JUMP = 0.20   # how far fair value jumps the instant an informed trader fills us


# ---------------------------------------------------------------------------
# THE MARKET MAKER
# ---------------------------------------------------------------------------
# Minimal on purpose: a bid and an ask `half_spread` either side of fair value,
# plus the bookkeeping to track cash, inventory, and -- the whole point of this
# lesson -- to ATTRIBUTE every cent of P&L to either noise flow or informed flow.
class MarketMaker:
    def __init__(self, half_spread=0.05):
        self.half_spread = half_spread
        self.noise_pnl = 0.0     # spread captured from noise fills (the edge)
        self.informed_pnl = 0.0  # P&L bled to informed fills (the bleed)
        self.noise_fills = 0
        self.informed_fills = 0

    def quote(self, fair):
        # Symmetric quote: buy a touch below fair, sell a touch above.
        return fair - self.half_spread, fair + self.half_spread

    # We got hit. side == "buy" means the TAKER bought -> we SOLD at our ask;
    # side == "sell" means the taker SOLD -> we BOUGHT at our bid.
    #
    # We value each fill against fair value AT THE MOMENT we quoted -- the only
    # honest mark, since that's what we believed the unit was worth when we
    # traded it. The spread we banked is `edge * size`, and for ANY fill that is
    # exactly + half_spread * size (we always quote half_spread away from fair).
    #   * NOISE fill: fair then just wanders, so on average we KEEP that spread.
    #   * INFORMED fill: fair is about to jump JUMP against us, so the position
    #     we just took on is instantly underwater by JUMP * size -- a loss that
    #     dwarfs the little spread we banked. That net (spread - jump) is the
    #     bleed we book to informed_pnl.
    def on_fill(self, side, price, size, fair, informed):
        edge = (price - fair) if side == "buy" else (fair - price)
        captured = edge * size       # always +half_spread*size: the spread we banked
        if informed:
            self.informed_pnl += captured - JUMP * size
            self.informed_fills += 1
        else:
            self.noise_pnl += captured
            self.noise_fills += 1

    # The decomposed P&L: the steady edge earned from noise plus the (negative)
    # bleed paid to informed flow. By construction net = noise + informed.
    def pnl(self):
        return self.noise_pnl + self.informed_pnl


# ---------------------------------------------------------------------------
# THE FLOW SIMULATION
# ---------------------------------------------------------------------------
# Each step:
#   1. the MM quotes a bid and an ask around fair value
#   2. one taker arrives. With probability `informed_frac` it is INFORMED.
#   3. an INFORMED taker trades in the direction fair is ABOUT to move, then
#      fair jumps that way (it picked us off). A NOISE taker picks a side at
#      random and fair does NOT jump (it just wanders a little, as always).
def run_flow(mm, steps=8000, informed_frac=0.15, seed=1):
    rng = random.Random(seed)
    fair = 100.0
    for _ in range(steps):
        bid, ask = mm.quote(fair)
        size = rng.randint(1, 3)
        if rng.random() < informed_frac:
            # INFORMED: trade just before the move, in the move's direction.
            up = rng.random() < 0.5
            if up:
                mm.on_fill("buy", ask, size, fair, informed=True)   # it lifts our ask
                fair += JUMP                                        # ...then fair rises
            else:
                mm.on_fill("sell", bid, size, fair, informed=True)  # it hits our bid
                fair -= JUMP                                        # ...then fair falls
        else:
            # NOISE: uninformed, equally likely either way; no jump.
            if rng.random() < 0.5:
                mm.on_fill("buy", ask, size, fair, informed=False)
            else:
                mm.on_fill("sell", bid, size, fair, informed=False)
        fair += rng.gauss(0, 0.01)   # fair's own tiny independent wander


# ===========================================================================
# DEMO
# ===========================================================================
print("=" * 70)
print("  LESSON 21 — ADVERSE SELECTION: toxic / informed flow runs you over")
print("=" * 70)

# ---- the quote ------------------------------------------------------------
print("\nYou are the market maker. At fair = 100.00 with half-spread 0.05:")
mm0 = MarketMaker(half_spread=0.05)
b, a = mm0.quote(100.0)
print(f"    you BUY at {b:.2f}   you SELL at {a:.2f}   (you bank the 0.10 spread)")
print("You want NOISE: it pays the spread and predicts nothing. You fear")
print("INFORMED flow: it trades with you right before the price moves your way.")

# ---- decompose one run ----------------------------------------------------
print("\n" + "-" * 70)
print("ONE RUN, DECOMPOSED — where does the P&L come from?\n")
mm = MarketMaker(half_spread=0.05)
run_flow(mm, steps=8000, informed_frac=0.15, seed=1)
print(f"    fills total      : {mm.noise_fills + mm.informed_fills}")
print(f"    noise fills      : {mm.noise_fills}")
print(f"    informed fills   : {mm.informed_fills}  (the toxic minority)")
print(f"    + earned on noise: {mm.noise_pnl:+10.2f}   <- the steady edge")
print(f"    - lost to informed:{mm.informed_pnl:+10.2f}   <- the lumpy bleed")
print(f"    {'=' * 30}")
print(f"    net P&L          : {mm.pnl():+10.2f}")
print("\nThe edge is the spread earned from the harmless majority. The bleed is")
print("what the informed minority extracts -- and it is far bigger PER FILL,")
print("because each toxic fill is a position taken on right before it moves.")

# ---- sweep the informed fraction ------------------------------------------
print("\n" + "-" * 70)
print("RAISE THE INFORMED FRACTION — the edge erodes, then goes negative\n")
print(f"    {'informed %':>11} {'noise P&L':>11} {'informed P&L':>13} {'net P&L':>10}")
for frac in [0.0, 0.05, 0.10, 0.20, 0.30, 0.40]:
    m = MarketMaker(half_spread=0.05)
    run_flow(m, steps=8000, informed_frac=frac, seed=2)
    print(f"    {frac * 100:>10.0f}% {m.noise_pnl:>11.2f} {m.informed_pnl:>13.2f} "
          f"{m.pnl():>10.2f}")
print("\nWith zero informed flow the MM banks the spread cleanly. Each step up in")
print("toxicity adds more wrong-side fills; past a tipping point the bleed")
print("overwhelms the edge and the SAME bot, SAME spread, loses money.")

# ---- the defense: widen the spread ----------------------------------------
print("\n" + "-" * 70)
print("THE DEFENSE — widen the spread to survive 30% informed flow\n")
print(f"    {'half-spread':>12} {'noise P&L':>11} {'informed P&L':>13} {'net P&L':>10}")
for hs in [0.05, 0.08, 0.10, 0.13, 0.16]:
    m = MarketMaker(half_spread=hs)
    run_flow(m, steps=8000, informed_frac=0.30, seed=3)
    print(f"    {hs:>12.2f} {m.noise_pnl:>11.2f} {m.informed_pnl:>13.2f} "
          f"{m.pnl():>10.2f}")
print("\nA wider quote charges EVERYONE more -- so the spread banked on the noise")
print("majority finally covers the losses to the toxic minority, and net P&L")
print("climbs back above zero. You can't tell noise from informed in advance, so")
print("you tax all of it. (The catch, felt in the capstone: a wider quote sits")
print("further from fair and in a real book wins LESS flow. Tighten too far and")
print("toxic flow eats you; widen too far and you trade with nobody.)")

# ---- the symmetry ---------------------------------------------------------
print("\n" + "=" * 70)
print("  Lesson 0's informed trader, both seats:")
print("    Track 1 (you trade) : informed flow is the faint SIGNAL you hunt.")
print("    Track 2 (you quote) : the SAME flow is the HAZARD that bleeds you.")
print("  Same person, opposite seat. That is adverse selection.")
print("=" * 70)


# ---------------------------------------------------------------------------
# TRY IT (exercises)
# ---------------------------------------------------------------------------
# 1. PURE PROFIT. In the "ONE RUN" block set informed_frac=0.0. The informed
#    P&L line goes to 0.00 and net P&L is exactly the noise spread -- a clean,
#    riskless edge. This is the market maker's dream: only noise, no toxicity.
#
# 2. CRANK THE TOXICITY. In the same block set informed_frac=0.50. Watch net P&L
#    swing deep negative: the informed P&L (the bleed) now dwarfs the noise edge.
#    This is what "toxic order flow" does to a real desk.
#
# 3. BIGGER JUMP. At the top, change JUMP = 0.20 to 0.40 -- informed traders now
#    know about a bigger move. Re-run: even a small informed fraction is brutal,
#    because each toxic fill costs twice as much. Toxicity is about the SIZE of
#    the move the informed know about, not just how many of them there are.
#
# 4. WIDEN TO SURVIVE. In exercise 2's 50%-informed case, raise half_spread until
#    net P&L turns positive again. How wide must you quote to survive pure-ish
#    toxicity? (Hint: you must out-charge the average bleed per fill.)
#
# 5. DECOMPOSE THE DEFENSE. In the "DEFENSE" sweep, notice noise P&L RISES with
#    the half-spread (you bank more per harmless fill) while informed P&L barely
#    improves (you still get picked off; you just lose a bit less each time).
#    Widening helps mostly by taxing the noise majority, not by deterring sharks.
#
# 6. Open ../exchange.py and find run_flow(): the cumulative artifact runs this
#    exact idea inside the real matching engine, with informed traders moving
#    `fair` against the MarketMaker. Lesson 22 (the capstone) asks you to tune
#    half_spread, skew and speed so the bot stays PROFITABLE and FLAT even at
#    25% informed flow -- make money AND carry no risk. That is the real job.
