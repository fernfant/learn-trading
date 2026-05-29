# CLAUDE.md — how this course is built

This repo is an interactive, build-it-yourself trading course. It mirrors the
structure of the author's mini-PRAGMA ML course and learn-physics course:
**teach by building one real, growing artifact, one line per lesson.**

Read this before adding or editing lessons so the course stays coherent.

## The two cumulative artifacts

There are exactly two programs that the student GROWS over the course. Never
fork them into per-lesson copies — each lesson edits the same file and updates
its in-file BUILD MAP comment.

The course mimics **capital.com** (a CFD platform: leverage, long/short,
spread, overnight funding, demo account). See `course/capital_com.md` for the
platform mechanics and `course/index.md` for the full lesson↔book↔platform map.

- **`market.py`** — Track 1 (trading on capital.com). A simulator/backtester
  behaving like a capital.com demo account. Growth ladder (one new loop line
  per lesson): `L1 price += shock` → `L2 bid/ask around a mid (spread)`
  → `L3 long AND short (signed position)` → `L4 equity = cash + position*price`
  → `L5 leverage & margin (call/stop-out)` → `L6 order types (limit/stop/TP)`
  → `L7 position sizing` → `L8 MA-crossover signal`
  → `L9 costs: half-spread + overnight swap + slippage`
  → `L10 metrics (return/Sharpe/drawdown)`
  → `L11 capstone: beat buy-and-hold after spread + fees`.
- **`exchange.py`** — Track 2 (HFT). The machine capital.com is: an order-book
  matching engine + market maker. Growth ladder: `L12 taker→maker bridge
  (concept; spread flips cost→revenue)` → `L13 book (bids/asks/spread)`
  → `L14 market order eats book` → `L15 limit order rests (price-time priority)`
  → `L16 matching loop` → `L17 market-data + trade tape`
  → `L18 market maker quotes both sides` → `L19 inventory skew`
  → `L20 latency/queue` → `L21 adverse selection`
  → `L22 capstone: profitable AND flat market maker`.

## Per-lesson files

For lesson N, in `course/`:
- `NN_topic.py` — a **standalone, runnable teaching script** (NOT the cumulative
  artifact). Self-contained, demonstrates the one new concept, ends with a
  `TRY IT` block of 2–4 exercises. Must print readable output.
- `NN_walkthrough.md` — a plain-English, **line-by-line** explanation. Links
  back to the cumulative artifact and forward to the next lesson.

## Conventions (keep these consistent)

- **Standard library only.** No pip installs. No numpy/pandas/matplotlib —
  matplotlib is NOT available in the working env. Charts are ASCII (see
  `market.py`'s `ascii_chart`). Reuse that helper; don't reinvent per lesson.
- **`random.seed(...)`** at the top of anything stochastic so output is
  reproducible and the walkthrough's numbers match what the student sees.
- **Voice:** gentle ramp, deep tail. Early lessons (1–6, 11–14) assume a smart
  ~12-year-old: concrete, intuition-first, no jargon without a plain definition.
  Later lessons (7–10, 15–20) may get technically rigorous (microstructure,
  stats), but always define terms on first use.
- **Honesty is the theme.** The recurring lesson is that markets are nearly
  random and edges are small; always include costs/risk before claiming a
  strategy "works". Never imply easy money.
- Per the author's global prefs: concise code, minimal comments EXCEPT here —
  this is teaching code, so comments that explain the *why* and *intuition* are
  the product. That's a deliberate exception to the usual "few comments" rule.
- Update `course/README.md`'s lesson table (✅ vs _soon_) when a lesson lands.

## Optional later: interactive HTML

Like the sibling courses, lessons can get a self-contained interactive HTML
page under `course/html/` (sliders, a live order book, an animated price). Not
required for a lesson to be "done"; add once the Python + walkthrough exist.

## Verify before claiming done

Run every `.py` you touch (`python3 course/NN_topic.py`, `python3 market.py`,
`python3 exchange.py`) and confirm the walkthrough's quoted numbers match the
actual output.
