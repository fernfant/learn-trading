# Learn to Trade — a two-track course

Learn how markets actually work by **building** them, one line of code at a
time. No finance degree, no heavy math to start. Each lesson is a small
runnable Python program plus a plain-English **line-by-line walkthrough**.

The course has two tracks, evenly weighted. They share one story: Track 1
treats "the price" as a number handed to you and teaches you to trade against
it. Track 2 then opens the hood and builds the *machine that makes the price* —
the exchange — and the fast bots that live inside it.

The difficulty ramps gently at the start (built so a curious 12-year-old can
follow) and gets genuinely deep by the end (real market microstructure,
latency, market making).

---

> **Built around capital.com.** The student will trade on
> [capital.com](https://capital.com), a CFD platform, so the simulator mimics
> it: two-sided prices, long *and* short, leverage, the spread, and real order
> types. See [`capital_com.md`](capital_com.md) for the platform mechanics and
> [`index.md`](index.md) for the full lesson↔book↔platform mapping. Practise on
> capital.com's free **demo account** as you go.

## 🟢 Track 1 — Trading on capital.com → build [`../market.py`](../market.py)

You grow **one cumulative program**, `market.py`, adding ~one line per lesson,
until it's a real backtester behaving like a capital.com demo account: prices →
long/short → leverage → orders → risk → honest metrics, after costs.

| # | Concept | Code | Walkthrough |
|---|---------|------|-------------|
| 1 | What is a price? (the random walk; why you can't predict it) | [`01_what_is_a_price.py`](01_what_is_a_price.py) | [`01_walkthrough.md`](01_walkthrough.md) ✅ |
| 2 | Bid, ask & the spread — there are always two prices | `02_bid_ask_spread.py` | _soon_ |
| 3 | Your first trade: long **and** short (CFDs) | `03_long_and_short.py` | _soon_ |
| 4 | P&L & equity — what are you worth? | `04_pnl.py` | _soon_ |
| 5 | Leverage & margin — the double-edged sword | `05_leverage_margin.py` | _soon_ |
| 6 | Order types — market, limit, stop, trailing, GSLO, take-profit | `06_order_types.py` | _soon_ |
| 7 | Risk & position sizing — don't blow up | `07_risk.py` | _soon_ |
| 8 | A signal — moving-average crossover (+ honest skepticism) | `08_signal.py` | _soon_ |
| 9 | Costs that kill — spread + overnight funding + slippage | `09_costs.py` | _soon_ |
| 10 | Backtesting honestly — return, Sharpe, drawdown | `10_backtest.py` | _soon_ |
| 11 | **Capstone:** beat buy-and-hold on the sim, *after* spread & fees | `11_capstone.md` | _soon_ |

## 🔴 Track 2 — Inside the exchange / HFT → build [`../exchange.py`](../exchange.py)

Where did "the price" and "the spread" come from? You flip seats and build the
machine capital.com is: an order book → a matching engine → a **market maker**
that *earns* the spread you paid in Track 1.

| # | Concept | Code | Walkthrough |
|---|---------|------|-------------|
| 12 | From price-taker to price-maker — the bridge | `12_taker_to_maker.md` | _soon_ |
| 13 | The order book — bids, asks, depth, the spread | [`../exchange.py`](../exchange.py) (seed) | _soon_ |
| 14 | A market order eats the book | `14_market_order.py` | _soon_ |
| 15 | A limit order rests — price-time priority | `15_limit_order.py` | _soon_ |
| 16 | The matching engine loop — the heart of an exchange | `16_matching.py` | _soon_ |
| 17 | Market data & the tape — top of book & depth | `17_market_data.py` | _soon_ |
| 18 | A market maker — quote both sides, earn the spread | `18_market_maker.py` | _soon_ |
| 19 | Inventory risk — skew your quotes | `19_inventory.py` | _soon_ |
| 20 | Latency & the queue — why microseconds pay | `20_latency.py` | _soon_ |
| 21 | Adverse selection — getting run over by informed flow | `21_adverse_selection.py` | _soon_ |
| 22 | **Capstone:** a market maker that stays profitable *and* flat | `22_capstone.md` | _soon_ |

✅ = built · _soon_ = planned. Full mapping with references: [`index.md`](index.md).

---

## How to use the course

For each lesson:

1. **Read** the `.py` top to bottom — don't worry if some lines are unclear.
2. **Run it**: `python3 0X_lesson.py`. Watch the output.
3. **Read** the matching `_walkthrough.md` for the line-by-line explanation.
4. **Re-run** and read the code again — now every line should click.
5. **Do the "Try it"** exercises at the bottom of the `.py`. Edit, run, observe.

## What you need

- Basic Python (variables, lists, loops, functions). That's it.
- **No external packages.** Everything uses the Python standard library, so
  there's nothing to install — just `python3`.
- No math beyond arithmetic to start. Track 2's later lessons introduce a
  little statistics, explained as we go.

## What you'll be able to do by the end

- Explain what a price *is* and why predicting it is hard.
- Write a trading strategy and **backtest it honestly** (including the costs
  that quietly kill most strategies).
- Explain how a real exchange matches orders in an order book.
- Build a **market maker** and reason about spread, inventory, latency, and
  adverse selection — the core ideas behind high-frequency trading.
