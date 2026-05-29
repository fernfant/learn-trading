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

## 🟢 Track 1 — Normal trading → build [`../market.py`](../market.py)

You grow **one cumulative program**, `market.py`, adding ~one line per lesson,
until it's a real backtester: price feed → strategy → portfolio → P&L →
honest metrics.

| # | Concept | Code | Walkthrough |
|---|---------|------|-------------|
| 1 | What is a price? (the random walk; why you can't predict it) | [`01_what_is_a_price.py`](01_what_is_a_price.py) | [`01_walkthrough.md`](01_walkthrough.md) ✅ |
| 2 | Your first trade — cash, shares, position | `02_your_first_trade.py` | _soon_ |
| 3 | What are you worth? — equity & P&L | `03_pnl.py` | _soon_ |
| 4 | A strategy is just a rule — buy & hold baseline | `04_strategy.py` | _soon_ |
| 5 | Orders & fills — market vs limit | `05_orders.py` | _soon_ |
| 6 | A real signal — moving-average crossover | `06_signal.py` | _soon_ |
| 7 | Risk & position sizing — don't blow up | `07_risk.py` | _soon_ |
| 8 | Backtesting honestly — return, Sharpe, drawdown | `08_backtest.py` | _soon_ |
| 9 | Trading isn't free — fees & slippage kill strategies | `09_costs.py` | _soon_ |
| 10 | **Capstone:** beat buy-and-hold on the sim, after costs | `10_capstone.md` | _soon_ |

## 🔴 Track 2 — High-frequency trading → build [`../exchange.py`](../exchange.py)

Where did "the price" come from? From an exchange matching orders. You grow a
second cumulative program, `exchange.py`: an order book → a matching engine →
a market maker that earns the spread.

| # | Concept | Code | Walkthrough |
|---|---------|------|-------------|
| 11 | The order book — bids, asks, the spread | [`../exchange.py`](../exchange.py) (seed) | _soon_ |
| 12 | A market order eats the book | `12_market_order.py` | _soon_ |
| 13 | A limit order rests — price-time priority | `13_limit_order.py` | _soon_ |
| 14 | The matching loop — the heart of an exchange | `14_matching.py` | _soon_ |
| 15 | Market data — top of book & depth | `15_market_data.py` | _soon_ |
| 16 | A market maker — quote both sides, earn the spread | `16_market_maker.py` | _soon_ |
| 17 | Inventory risk — skew your quotes | `17_inventory.py` | _soon_ |
| 18 | Latency & the queue — why microseconds pay | `18_latency.py` | _soon_ |
| 19 | Adverse selection — getting run over by informed flow | `19_adverse_selection.py` | _soon_ |
| 20 | **Capstone:** a market maker that stays profitable *and* flat | `20_capstone.md` | _soon_ |

✅ = built · _soon_ = scaffolded, on the way

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
