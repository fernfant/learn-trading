# Course index

The master catalog. Two tracks, evenly weighted (10 teaching lessons + a
capstone each). Each row maps a lesson to: the **concept**, the **line it adds**
to the cumulative program, the **capital.com feature** it mirrors (see
[`capital_com.md`](capital_com.md)), and a **primary reference** (full
bibliography at the bottom). Difficulty ramps gently early, deep late.

Legend: ✅ built · ◻︎ planned · 📈 grows `../market.py` · 📕 grows `../exchange.py`

---

## 🟢 Track 1 — Trading on capital.com (you are the customer) · grows `../market.py`

You learn to trade *against* a price, on a simulator built to behave like a
capital.com **demo** account: two-sided prices, long & short, leverage, the
spread, real order types, and the costs that quietly decide who wins.

| # | Lesson | Adds to `market.py` | capital.com mirror | Primary reference |
|---|--------|--------------------|--------------------|-------------------|
| 1 ✅ | What is a price? (random walk; why you can't predict it) | `price += shock` | the live price chart | Malkiel, *Random Walk Down Wall Street* |
| 2 ◻︎ | Bid, ask & the spread (there are always two prices) | `buy/sell` around a mid | Buy/Sell price; the spread | BabyPips, *School of Pipsology* |
| 3 ◻︎ | Your first trade: long **and** short | signed `position`, `cash` | Buy = long, Sell = short (CFD) | capital.com — CFD basics |
| 4 ◻︎ | P&L & equity (realized vs unrealized) | `equity = cash + position*price` | open P&L, account equity | Investopedia — P&L |
| 5 ◻︎ | Leverage & margin (the double-edged sword) | `margin = notional/leverage` | leverage; 75/100% call, 50% stop-out | BabyPips — leverage & margin |
| 6 ◻︎ | Order types (market, limit, stop, trailing, GSLO, take-profit) | trigger checks each step | capital.com's order menu | Harris, *Trading & Exchanges* (ch. on orders) |
| 7 ◻︎ | Risk & position sizing (don't blow up) | `qty = risk_frac*equity/stop_dist` | risk per trade; the demo as practice | Van Tharp, *Trade Your Way…* |
| 8 ◻︎ | A signal: moving-average crossover (+ honest skepticism) | `signal = fast_ma > slow_ma` | indicators on the chart | Murphy, *Technical Analysis…* / Aronson |
| 9 ◻︎ | Costs that kill (spread + overnight funding + slippage) | `cash -= half_spread + swap` | why most retail CFD accounts lose | capital.com — Pricing & fees |
| 10 ◻︎ | Backtesting honestly (return, Sharpe, max drawdown, OOS) | metrics over `history` | — | Chan, *Quantitative Trading* |
| 11 ◻︎ | **Capstone:** beat buy-and-hold on the sim, *after* spread & fees | full loop | a demo-account challenge | Chan + Tharp |

## 🔴 Track 2 — Inside the exchange / HFT (you are the market maker) · grows `../exchange.py`

Now flip seats. Where did the price and the spread come from? You build the
**order book** and the **market-making bot** that quotes both sides and *earns*
the spread — the very role capital.com plays for its users.

| # | Lesson | Adds to `exchange.py` | Idea | Primary reference |
|---|--------|----------------------|------|-------------------|
| 12 ◻︎ | From price-**taker** to price-**maker** (the bridge) | — (concept) | the spread flips from cost → revenue | Harris, *Trading & Exchanges* |
| 13 ◻︎ | The order book (bids, asks, depth, spread) | `OrderBook`, `spread()` | the book is the market | Harris |
| 14 ◻︎ | A market order eats the book (slippage, from the inside) | `match_market()` | walking the book | Harris |
| 15 ◻︎ | A limit order rests (price-time priority, the queue) | `add_limit()` w/ priority | why your place in line matters | Harris |
| 16 ◻︎ | The matching engine loop (crossed orders → trades) | `match()` core | the heart of an exchange | Hasbrouck, *Empirical Market Microstructure* |
| 17 ◻︎ | Market data & the tape (top-of-book, depth, trades) | `snapshot()`, `tape` | what an HFT actually sees | Hasbrouck |
| 18 ◻︎ | Be the market maker (quote both sides, earn the spread) | `quote()` bot | capital.com's business model | Cartea/Jaimungal/Penalva |
| 19 ◻︎ | Inventory risk (skew your quotes) | skew by `inventory` | Avellaneda–Stoikov intuition | Avellaneda & Stoikov (2008) |
| 20 ◻︎ | Latency & the queue (why microseconds pay) | per-order latency | co-location, speed races | Lewis, *Flash Boys* |
| 21 ◻︎ | Adverse selection (toxic / informed flow runs you over) | informed traders in the sim | Glosten–Milgrom, Kyle | O'Hara, *Market Microstructure Theory* |
| 22 ◻︎ | **Capstone:** a market maker that stays profitable **and** flat | full bot vs flow sim | the real HFT objective | Cartea et al. |

---

## References

### Books — Track 1 (trading & investing)
- **Burton G. Malkiel — _A Random Walk Down Wall Street_** — random walks, why
  prediction is hard, efficient markets. (L1)
- **BabyPips — _School of Pipsology_** (free, online) — the friendliest intro to
  spread, pips, leverage and margin; written for total beginners. (L2–L6)
- **Alexander Elder — _The New Trading for a Living_** — risk, discipline, the
  psychology of trading. (L7)
- **Van K. Tharp — _Trade Your Way to Financial Freedom_** — position sizing &
  expectancy: *how much* to bet is more important than *what*. (L7)
- **John J. Murphy — _Technical Analysis of the Financial Markets_** — the
  standard reference for chart signals like moving averages. (L8)
- **David Aronson — _Evidence-Based Technical Analysis_** — the skeptic's
  counterweight: most "signals" are noise. (L8)
- **Ernest P. Chan — _Quantitative Trading_ / _Algorithmic Trading_** — how to
  backtest a strategy honestly. (L10–L11)
- *Optional classics:* Edwin Lefèvre, _Reminiscences of a Stock Operator_;
  Jack Schwager, _Market Wizards_; Benjamin Graham, _The Intelligent Investor_.

### Books & papers — Track 2 (market microstructure & HFT)
- **Larry Harris — _Trading and Exchanges: Market Microstructure for
  Practitioners_** — *the* book on order books, order types, priority and
  market makers. The backbone of Track 2. (L12–L16)
- **Joel Hasbrouck — _Empirical Market Microstructure_** — market data, the
  tape, measuring liquidity. (L16–L17)
- **Á. Cartea, S. Jaimungal & J. Penalva — _Algorithmic and High-Frequency
  Trading_** — rigorous market-making and inventory control. (L18–L19, L22)
- **Maureen O'Hara — _Market Microstructure Theory_** — adverse selection and
  informed trading. (L21)
- **Michael Lewis — _Flash Boys_** (narrative) — why latency and co-location
  matter, told as a story. (L20)
- **Papers:** Avellaneda & Stoikov (2008), *High-frequency trading in a limit
  order book* (L19); Glosten & Milgrom (1985), *Bid, ask and transaction
  prices…* (L21); Kyle (1985), *Continuous auctions and insider trading* (L21).

### Online resources
- **[capital.com — Learn & Help Centre](https://capital.com/en-int/learn)** —
  platform-specific mechanics; the thing we mimic. See also
  [`capital_com.md`](capital_com.md).
- **[BabyPips](https://www.babypips.com/learn/forex)** — free beginner course;
  best for CFD/leverage/spread intuition.
- **[Investopedia](https://www.investopedia.com)** — quick, reliable
  definitions for any term in the course.
- **[Khan Academy — Finance & Capital Markets](https://www.khanacademy.org/economics-finance-domain/core-finance)**
  — gentle video foundations, good for the youngest learners.
- **[QuantStart](https://www.quantstart.com)** — practical backtesting and
  quant-trading articles (L10).
