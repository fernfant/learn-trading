# How capital.com works (and how we mimic it)

The student will practise on **capital.com**, so the course models *that*
platform, not a generic stock exchange. This page is the reference: it
describes how capital.com actually operates, and how our two programs
([`../market.py`](../market.py) and [`../exchange.py`](../exchange.py)) imitate
each piece. Read it once now; each lesson points back here.

> **Start on the DEMO account.** capital.com gives you a free demo with virtual
> money that behaves exactly like the real platform — same prices, spreads,
> and order types. Everything in this course is designed to be tried on the
> demo first. No real money required to learn any of it.

## The one big thing: it's CFDs, not shares

capital.com is mostly a **CFD** broker (Contract For Difference). You are **not
buying the actual share**. You're making a contract with the broker that pays
you the *difference* in price between when you open and close. Consequences,
all of which the course teaches:

- **You can go short as easily as long.** Betting a price will *fall* is a
  first-class action, not an advanced trick. → Lesson 3.
- **Leverage.** The broker fronts most of the position's value; you post a
  small **margin**. This multiplies gains *and* losses. → Lesson 5.
- **You pay the spread, not a commission.** → Lesson 2 & 9.
- **Overnight funding** if you hold past the daily cutoff. → Lesson 9.
- It's **high-risk**: capital.com's own regulatory warning states that the
  large majority of retail CFD accounts lose money. The course leans into this
  honestly — counting costs and managing risk is the whole point, not a
  footnote. capital.com also offers a **1:1 ("1X") no-leverage** mode, which is
  the gentlest place to start.

## The mechanics, and our mimic

| capital.com concept | What it means | Where we model it |
|---|---|---|
| **Buy / Sell price** | Two prices, always. Buy (ask) is a hair above Sell (bid). | `market.py` L2 — a bid/ask around a mid price |
| **Spread** | The gap between Buy and Sell. The broker's main fee. *Half* is effectively paid when you open, half when you close. | `market.py` L2, charged in L9 |
| **Long / Short** | Buy to profit from a rise; Sell to profit from a fall. | `market.py` L3 — signed position |
| **Leverage & margin** | Open a big position with small cash. Margin = notional ÷ leverage. | `market.py` L5 |
| **Margin call / stop-out** | At 75%/100% margin used you're warned; at **50%** the platform force-closes you. | `market.py` L5 |
| **Order types** | Market, Limit, Stop, Trailing stop, Guaranteed stop (GSLO), Take-profit. | `market.py` L6 |
| **Guaranteed stop (GSLO)** | A stop that fills at your exact price even on a gap — for a fee/premium. | `market.py` L6 (note) |
| **Overnight funding (swap)** | Daily charge for holding overnight; 1:1 share positions are exempt. | `market.py` L9 |
| **How capital.com earns** | Spreads + overnight funding. It quotes you both sides — i.e. it behaves like a **market maker**. | the bridge to **Track 2** |

## Why this is the perfect bridge to HFT (Track 2)

In Track 1 you are the **customer**: you cross the spread and pay it. In Track 2
you build the other side — an **order book** and a **market maker** that
*quotes* both prices and *earns* the spread, exactly the role capital.com plays
for its users. Same number (the spread), seen from both seats. That flip from
"spread = my cost" to "spread = my revenue" is the hinge of the whole course.

## Order types cheat-sheet (capital.com)

- **Market** — fills now at the current price. Fast, no price control.
- **Limit** — fills only at your price or better. Price control, no guarantee
  it fills.
- **Stop** — becomes a market order once a trigger price is hit (used to cut
  losses or enter on breakouts).
- **Trailing stop** — a stop that follows the price as it moves your way,
  locking in profit.
- **Guaranteed stop (GSLO)** — like a stop but immune to slippage/gaps; costs a
  premium if triggered.
- **Take-profit** — auto-closes when your profit target is hit.

Sources: [capital.com — Pricing (spreads, overnight, GSLO)](https://capital.com/en-int/ways-to-trade/pricing),
[capital.com — Fees & charges](https://capital.com/en-int/ways-to-trade/fees-and-charges),
[capital.com — How capital makes money](https://capital.com/en-int/about-us/how-capital-makes-money),
[capital.com — 1:1 (1X) account](https://capital.com/en-gb/ways-to-trade/1x),
[capital.com — Order definition](https://capital.com/en-int/learn/glossary/order-definition),
[capital.com — Guaranteed stop](https://help.capital.com/hc/en-us/articles/360016602919-Guaranteed-stop-loss).
