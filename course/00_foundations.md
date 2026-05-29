# Lesson 0 · Foundations — what are we even trading?

> **Read this once before Lesson 1.** It's the only lesson with *no code* and
> *no line added to `market.py`* — it's the map of the whole journey. It answers
> the question a thoughtful person asks before risking a cent: *what is this
> thing, where does its price come from, and what game am I actually playing?*

---

## 1. What is an "asset"?

An **asset** is anything you can own that might be worth something later: a share
of a company, an ounce of gold, a barrel of oil, a currency, a bar of chocolate.
On capital.com the menu is stocks, indices, commodities, forex and crypto — but
the idea is the same for all of them.

Two things are true about every asset, and holding both in your head at once is
the start of understanding markets:

1. It has some **underlying value** — a share is a slice of a real business that
   earns real money; gold is a metal people actually want.
2. It has a **price** — the number on the screen *right now* — and that price is
   **not** the same thing as the value. The price is just **the last number two
   people agreed to trade at.**

The gap between *value* and *price* is where this entire course lives.

## 2. Where does a price come from? Supply meets demand

A price isn't announced by anyone. It **emerges** from a crowd of buyers and
sellers, each with a number in their head:

- **Buyers** post the most they're willing to *pay* (the **bids**).
- **Sellers** post the least they're willing to *accept* (the **asks**).

A trade happens at the point where an eager buyer meets an eager seller. When
buyers crowd in, the price gets pulled **up**; when sellers pile on, it's pushed
**down**. That's it. The price is a running tally of that tug-of-war.

> This is a sneak peek at **Track 2**. The list of all those bids and asks has a
> name — the **order book** — and in Lesson 13 you'll *build* it. The price
> you'll trade against in Track 1 is literally the top of a book someone else is
> running.

## 3. Two ways to make money: valuation vs trading

There are two fundamentally different jobs people do in markets. They sound
similar and they are *not*.

| | **Investing / valuation** | **Trading / speculation** |
|---|---|---|
| Core question | "What is this *worth*?" | "Which way will the *price* move?" |
| Time horizon | Years | Seconds to weeks |
| You make money when | Value > price, and the world notices | You bought before it rose / sold before it fell |
| Tools | Earnings, cash flow, the business | Price action, orders, risk, costs |
| Hero | Warren Buffett | a market maker / quant |

**Investing** is estimating an asset's true worth and buying when the price is
below it — then waiting, sometimes for years, for everyone else to catch up.
That's a deep skill, and it's a *different course*.

**Trading** — what *this* course teaches — mostly sets the "what is it worth?"
question aside and asks the narrower one: **over my short horizon, which way does
the price move, and can I capture that move after costs?**

## 4. So… do we trade blind, with no idea what the asset is worth?

Almost — and on purpose. Here's the honest reasoning:

- Over a **short** horizon, price moves are dominated by *flow* (who's buying and
  selling right now), not by slow changes in fundamental value. A great company's
  stock can fall all afternoon because a big fund needed cash.
- We're on **capital.com using CFDs** (next section), which are *built* for
  short-horizon directional bets, not for owning a business for a decade.
- And the course's spine is a **random walk** (Lesson 1): a model that *assumes*
  you can't predict value at all, so every edge has to be earned against pure
  chance — and after costs.

So we don't ignore value out of laziness. We set it aside because, over our
horizon and with our tools, the *price's own behaviour* — and the costs of
trading it — matter more. **That is a deliberate, explained choice, not a gap.**

## 5. Why a CFD is *not* the same as investing

On capital.com you don't usually *buy the share*. You trade a **CFD** (Contract
for Difference) — a bet with the broker on the price *difference* between when you
open and when you close. Consequences, all of which later lessons make concrete:

- You can go **short** (profit when the price falls) just as easily as long
  (Lesson 3) — impossible if you simply *own* the thing.
- You use **leverage** — control a big position with a small deposit, which
  magnifies both gains *and* losses (Lesson 5).
- You **don't own** the asset, collect no dividend, get no vote. You hold a
  position, not a slice of a business.
- You pay to play: the **spread** on every trade (Lesson 2) and **overnight
  funding** to hold positions (Lesson 9).

CFDs are a *trading* instrument, full stop. That's why this is a trading course.

## 6. "But you said markets are random — so it's hopeless?"

Lesson 1 will hammer the point that a price is *close* to a random walk, and that
predicting the next tick beats a coin flip only by a hair. So why bother?

Because markets aren't *perfectly* random. Prices are tugged — gently, noisily —
back toward value by people who **know something**: a fund that's read the
earnings, an insider, a faster bot. They're called **informed traders**, and
their footprints are the small, real edges a good trader hunts.

Here's the beautiful symmetry that ties the whole course together: in **Track 1**
those informed traders are the faint signal you're trying to find. In **Track 2**,
once you're the **market maker** quoting prices, those same informed traders are
your *nightmare* — they pick you off, and the damage has a name: **adverse
selection** (Lesson 21). Same people, opposite seat.

---

## ✅ After this primer you can say…

- An asset has a **value** (what it's worth) and a **price** (the last number two
  people traded at) — and they are not the same.
- A price **emerges** from buyers' bids and sellers' asks meeting — supply vs
  demand — which is the **order book** you'll build in Track 2.
- **Investing** asks *what is it worth?*; **trading** asks *which way does the
  price move?* — and this course is firmly in the **trading** camp.
- A **CFD** is a leveraged, two-directional bet on price *difference*, not
  ownership — which is *why* deep valuation is out of scope here.
- Markets are *nearly* random; the small real edges come from **informed
  traders**, who are Track 1's signal and Track 2's hazard.

Next: stop reading, start building. **Lesson 1 — what is a price?**
