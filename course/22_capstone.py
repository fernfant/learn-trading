"""
LESSON 22 — CAPSTONE: a market maker that stays PROFITABLE *and* FLAT
(Track 2: inside the exchange / HFT) · the reference solution

This is the boss fight for Track 2. Ten lessons ago "the price" was one number
handed to you from the sky. Now you have a whole machine: an order book (L13)
that market orders eat (L14) and limit orders rest in (L15), a matching loop
(L16), a market-data feed (L17), and a MARKET MAKER (L18) that quotes both
sides to earn the spread, skews by inventory to stay flat (L19), wins only the
flow it is fast enough to sit in front of (L20), and bleeds to informed /
toxic flow (L21). The capstone wires the maker's three hard lessons together
and asks the only question that matters for a real HFT desk:

  Can your market maker end the session both PROFITABLE (positive P&L from the
  spread it captured) AND FLAT (inventory near zero, not a giant directional
  bet you got stuck holding) -- while surviving a flow that contains TOXIC,
  informed traders who know which way the price is about to jump?

The dual objective is the whole job. Either half alone is easy and worthless:
  * You can be PROFITABLE by accident -- buy a load of inventory right before
    the price rips up. That is not market making, that is a directional gamble
    that happened to win. Re-run the seed and it blows up.
  * You can be FLAT by quoting so wide nobody ever hits you. Zero inventory,
    zero risk -- and zero profit. You did not make a market, you just stood
    there.
The art is the TENSION between them: widen the spread and skew harder to
survive adverse selection, but not so much that you stop getting filled and
earn nothing. (Cartea, Jaimungal & Penalva, *Algorithmic and High-Frequency
Trading* -- the rigorous treatment of exactly this trade-off.)

The honest punchline, mirrored from Track 1: the maker's only edge is the
SPREAD, and it is thin. Inventory risk and adverse selection erode it from
both sides. The reference bot below ends modestly profitable and near-flat at
a realistic toxicity -- but crank informed flow up or quote too tight and the
edge dies. There is no free money on this side of the book either.

Run it:  python3 22_capstone.py
Then read 22_capstone.md, and try to beat it.
"""

import random

# A seed makes the whole session repeat identically, so your numbers match the
# walkthrough's. Change SEED (or hit "New market" in the HTML) to see the
# verdict shift across different random worlds -- that variability IS the point.
SEED = 22
random.seed(SEED)

# ---- THE KNOBS (these define the reference market maker) ---------------------
STEPS = 6000           # how many takers arrive over the session
INFORMED_FRAC = 0.15   # fraction of flow that is TOXIC / informed (L21)
TICK = 0.06            # how far fair value jumps when an informed taker trades
NOISE = 0.02           # fair value's own small per-step random wander
INV_CAP = 60           # the challenge's "stay flat" bar: keep |inventory| under this

# The reference maker's two real levers (L18 + L19):
HALF_SPREAD = 0.07     # how far each quote sits from fair  -> wider = safer, fewer fills
SKEW = 0.012           # how hard to lean quotes by inventory -> higher = flatter, costlier


# =============================================================================
# THE MARKET MAKER  (condensed from exchange.py's MarketMaker, L18 + L19)
# =============================================================================
# It POSTS a bid and an ask around fair value and waits to get hit. A round-trip
# (a buyer lifts the ask, a seller hits the bid) banks the spread without ever
# predicting price -- that captured spread is the entire edge. The SKEW shifts
# BOTH quotes by an amount proportional to inventory so the market hands the
# inventory back: long -> push quotes down (sell eagerly, buy reluctantly).
class MarketMaker:
    def __init__(self, half_spread, skew):
        self.half_spread = half_spread
        self.skew = skew
        self.inventory = 0       # +long / -short units currently held
        self.cash = 0.0          # realized cash from fills
        self.fills = 0           # how many trades we were in
        self.toxic_fills = 0     # fills against informed flow (L21)
        # P&L DECOMPOSITION -- the heart of the capstone. Total P&L breaks into
        # exactly three pieces that SUM to it (no fudge):
        #   spread_earned  -- the edge: each fill books (its price - fair), i.e.
        #                     +half_spread minus whatever skew we gave up.
        #   adverse_loss   -- inventory * the informed tick that moves AGAINST it
        #                     the instant after a toxic fill (L21's bleed).
        #   noise_drift    -- inventory * fair's own small wander; pure inventory
        #                     risk. Near-flat makers barely feel it; the naive
        #                     maker, stuck holding a big position, lives or dies
        #                     by it. This is WHY carrying inventory is risk.
        # spread_earned + adverse_loss + noise_drift == total P&L, always.
        self.spread_earned = 0.0
        self.adverse_loss = 0.0
        self.noise_drift = 0.0
        # histories for the ASCII charts
        self.inv_hist = [0]
        self.pnl_hist = [0.0]

    def quote(self, fair):
        lean = self.skew * self.inventory
        bid = fair - self.half_spread - lean
        ask = fair + self.half_spread - lean
        return bid, ask

    def pnl(self, fair):
        # cash already booked + paper value of whatever inventory we still hold,
        # marked to fair. Flat inventory -> this is pure captured-spread profit.
        return self.cash + self.inventory * fair

    def fill(self, side, price, size, fair_before):
        # side == "buy": the taker BOUGHT from us -> we SOLD size at price
        #   (cash up, inventory down). The spread we earned is (price - fair),
        #   which is +half_spread minus any skew we gave up.
        # side == "sell": the taker SOLD to us -> we BOUGHT (cash down, inv up);
        #   the spread we earned is (fair - price).
        if side == "buy":
            self.cash += price * size
            self.inventory -= size
            self.spread_earned += (price - fair_before) * size
        else:
            self.cash -= price * size
            self.inventory += size
            self.spread_earned += (fair_before - price) * size
        self.fills += 1


# =============================================================================
# THE FLOW SIMULATION  (the world the maker trades against)
# =============================================================================
# Each step: fair takes a tiny wander; the maker quotes (skewed by inventory);
# a taker arrives wanting one side; whether it fills depends on how attractive
# (close to fair) that quote is; some takers are INFORMED and fair jumps THEIR
# way right after, so filling them is a loss. We run the SAME flow (same seed)
# against both makers so any difference is purely the skew, not luck.
def run(mm, steps=STEPS, informed_frac=INFORMED_FRAC, seed=1):
    rng = random.Random(seed)
    fair = 100.0

    def hit_prob(distance):
        # Probability a taker crosses to a quote `distance` from fair. Closer to
        # fair -> more likely to be hit. Clamped to [0.05, 0.95]. The exact
        # shape doesn't matter, only that a wider quote wins LESS flow -- that
        # is the cost of safety, and the core tension of the capstone.
        return max(0.05, min(0.95, 0.55 - distance * 3.5))

    for _ in range(steps):
        bid, ask = mm.quote(fair)
        informed = rng.random() < informed_frac
        side = rng.choice(["buy", "sell"])
        size = rng.randint(1, 3)
        dist = (ask - fair) if side == "buy" else (fair - bid)
        if rng.random() > hit_prob(dist):
            mm.inv_hist.append(mm.inventory)        # taker walked, no fill
            mm.pnl_hist.append(mm.pnl(fair))
            continue

        fair_before = fair
        if informed:
            # ADVERSE SELECTION (L21): an informed buyer lifts our ask right
            # before fair rises; an informed seller hits our bid right before
            # fair falls. Either way fair moves AGAINST our new inventory.
            move = TICK if side == "buy" else -TICK
            if side == "buy":
                mm.fill("buy", ask, size, fair_before)   # we sold the ask...
            else:
                mm.fill("sell", bid, size, fair_before)  # ...or bought the bid
            mm.toxic_fills += 1
            # the loss this toxic fill inflicts on the inventory we now hold
            mm.adverse_loss += mm.inventory * move
            fair += move
        else:
            # NOISE flow: uninformed, the flow the maker WANTS -- it pays the
            # spread and predicts nothing.
            if side == "buy":
                mm.fill("buy", ask, size, fair_before)
            else:
                mm.fill("sell", bid, size, fair_before)

        wander = rng.gauss(0, NOISE)                # fair's own wander
        mm.noise_drift += mm.inventory * wander     # inventory risk, isolated
        fair += wander
        mm.inv_hist.append(mm.inventory)
        mm.pnl_hist.append(mm.pnl(fair))
    return fair


# =============================================================================
# TINY ASCII CHARTS (stdlib only -- no matplotlib in this course)
# =============================================================================
def _sample(series, width):
    return [series[round(i * (len(series) - 1) / (width - 1))] for i in range(width)]


def pnl_chart(series, width=58, height=7):
    """P&L over time. Baseline 0 marked; rises = captured spread, dips = bleed."""
    s = _sample(series, width)
    lo, hi = min(s + [0.0]), max(s + [0.0])
    span = (hi - lo) or 1.0
    rows = []
    for r in range(height):
        top = hi - r * span / height
        bot = hi - (r + 1) * span / height
        line = "".join("*" if bot <= v < top or (r == 0 and v >= top) else
                       ("0" if bot <= 0 < top else " ") for v in s)
        rows.append(f"{top:+7.1f} |{line}")
    return "\n".join(rows)


def inv_chart(series, width=58, height=7):
    """Inventory over time, centered on zero (flat). Stays near the 0 line=good."""
    s = _sample(series, width)
    hi = max(1, max(abs(v) for v in s))
    rows = []
    for r in range(height):
        level = hi - r * (2 * hi) / (height - 1)
        flat = abs(level) < hi / height
        line = "".join("*" if (v >= level > 0) or (v <= level < 0) or
                       (flat and abs(v) < hi / height) else " " for v in s)
        rows.append(f"{level:+7.0f} |{line}{' 0 (flat)' if flat else ''}")
    return "\n".join(rows)


def scoreboard(title, mm, fair_end):
    total = mm.pnl(fair_end)
    print("\n" + "=" * 64)
    print(f"  {title}")
    print("=" * 64)
    print(f"  {'fills':24}{mm.fills:>10}  ({mm.toxic_fills} toxic / informed)")
    print(f"  {'spread earned':24}{mm.spread_earned:>+10.2f}  the edge: +half-spread per fill")
    print(f"  {'adverse-selection loss':24}{mm.adverse_loss:>+10.2f}  toxic ticks vs our inventory")
    print(f"  {'inventory drift':24}{mm.noise_drift:>+10.2f}  fair's wander on what we hold")
    print(f"  {'-'*24}{'-'*10}")
    print(f"  {'TOTAL P&L':24}{total:>+10.2f}")
    print(f"  {'final inventory':24}{mm.inventory:>+10d}  units  (flat = 0)")
    print("=" * 64)
    return total


# =============================================================================
# RUN THE CAPSTONE
# =============================================================================
print("=" * 64)
print("  TRACK 2 CAPSTONE -- a market maker that stays PROFITABLE *and* FLAT")
print("=" * 64)
print(f"  session: {STEPS} takers, {INFORMED_FRAC*100:.0f}% informed/toxic, seed {SEED}")
print(f"  the bar: end with positive P&L AND |inventory| < {INV_CAP}")

# --- THE REFERENCE MAKER: skew ON, a deliberately chosen half-spread ----------
ref = MarketMaker(half_spread=HALF_SPREAD, skew=SKEW)
fair_end = run(ref)

# --- THE NAIVE MAKER: same spread, SAME flow, but NO inventory skew -----------
# This is the L18 maker before it learned L19. It quotes symmetrically and never
# leans, so when noise hands it a run of one-sided fills it just keeps stacking
# inventory -- a giant directional bet it never chose to make.
naive = MarketMaker(half_spread=HALF_SPREAD, skew=0.0)
naive_fair_end = run(naive)

print("\nREFERENCE maker P&L over the session (0 = break-even):")
print(pnl_chart(ref.pnl_hist))
print("\nREFERENCE maker inventory (skew ON -> mean-reverts to flat):")
print(inv_chart(ref.inv_hist))
ref_pnl = scoreboard("REFERENCE  (skew ON)", ref, fair_end)

print("\nNAIVE maker inventory (skew OFF -> wanders off and STAYS off):")
print(inv_chart(naive.inv_hist))
naive_pnl = scoreboard("NAIVE  (no skew -- same spread, same flow)", naive, naive_fair_end)

# --- THE HONEST VERDICT -------------------------------------------------------
# Read off the actual numbers; don't hard-code a happy ending.
print("\n" + "-" * 64)
print("  THE VERDICT (the dual objective: profitable AND flat)")
print("-" * 64)


def verdict(mm, total):
    profitable = total > 0
    flat = abs(mm.inventory) < INV_CAP
    if profitable and flat:
        return "PROFITABLE & FLAT -- this is real market making."
    if profitable and not flat:
        return ("profitable but NOT flat -- the P&L is a directional bet on "
                "leftover inventory, not captured spread. One bad tick erases it.")
    if not profitable and flat:
        return "flat but BLEEDING -- the spread didn't cover adverse selection."
    return "BLEEDING and inventory BLEW UP -- worst of both worlds."


print(f"  REFERENCE: P&L {ref_pnl:+.2f}, inventory {ref.inventory:+d}  ->")
print(f"    {verdict(ref, ref_pnl)}")
print(f"  NAIVE:     P&L {naive_pnl:+.2f}, inventory {naive.inventory:+d}  ->")
print(f"    {verdict(naive, naive_pnl)}")
print()
print("  Same spread, same flow, same seed. The ONLY difference is the skew.")
print("  The naive maker may even show a BIGGER P&L number -- but read WHERE it")
print("  came from: it is sitting on a huge inventory whose value swings with")
print("  every tick (its 'inventory drift' line). That number is a coin-flip on")
print("  the next move, not spread it earned -- re-seed and it can flip to a deep")
print("  loss. The reference maker's P&L is almost all captured SPREAD with")
print("  inventory near flat: the same money tomorrow, with none of the risk.")
print("  Profitable is easy; profitable AND FLAT is the job.")

print("\n" + "=" * 64)
print("  The maker's only edge is the SPREAD it quotes. Quote too tight and toxic")
print("  flow eats you; too wide and you win no flow; skip the skew and inventory")
print("  risk turns you into a gambler. No free money here either -- the same")
print("  honest lesson as Track 1, seen from the other side of the book.")
print("=" * 64)


# -----------------------------------------------------------------------------
# TRY IT  /  YOUR CHALLENGE  (the Track 2 boss fight)
# -----------------------------------------------------------------------------
# Your mission: tune HALF_SPREAD and SKEW (top of file) so the REFERENCE maker
# ends both PROFITABLE (TOTAL P&L > 0) and FLAT (|final inventory| < INV_CAP),
# beating the reference P&L printed above -- WITHOUT just cranking the spread so
# wide you barely trade. Both halves must hold at once. That is the whole job.
#
# 1. WIDEN THE SPREAD. Set HALF_SPREAD = 0.12. Spread-earned per fill goes up,
#    and adverse-selection loss shrinks (toxic takers find your quote less
#    attractive) -- but `fills` drops too. Past a point you earn nothing because
#    nobody hits you. Find where wider stops helping.
# 2. SKEW HARDER, THEN NOT AT ALL. Set SKEW = 0.03, then 0.0. Watch the inventory
#    chart: more skew pins you to flat (good) but means you sometimes quote away
#    from fair to dump inventory (a cost). Zero skew is the naive maker -- flat?
# 3. TURN UP THE TOXICITY. Set INFORMED_FRAC = 0.30, then 0.45, and re-tune. At
#    some toxicity NO (spread, skew) keeps you profitable -- the flow is simply
#    poison. Find roughly where the edge dies. (This is why real desks refuse
#    to quote in names with too much informed flow.)
# 4. ROBUSTNESS. The session above is one seed. Loop SEED over 1..10, run the
#    reference maker on each, and count how many end profitable AND flat. A real
#    edge survives most worlds; a lucky one doesn't. (Hint: wrap the run in a
#    function and tally.)
# 5. THE REAL BOSS. Find ONE (HALF_SPREAD, SKEW) pair that ends profitable AND
#    flat across a MAJORITY of seeds 1..10 at INFORMED_FRAC = 0.20. If you can,
#    you have built what an HFT market-making desk actually does for a living.
#    If you can't -- now you understand why the spread, thin as it is, is the
#    only thing standing between the maker and ruin. Either way: that's Track 2.
