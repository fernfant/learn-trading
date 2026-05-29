# CLAUDE.md — how this course is built

This repo is an interactive, build-it-yourself trading course. It mirrors the
structure of the author's mini-PRAGMA ML course and learn-physics course:
**teach by building one real, growing artifact, one line per lesson.**

Read this before adding or editing lessons so the course stays coherent.

## The two cumulative artifacts

There are exactly two programs that the student GROWS over the course. Never
fork them into per-lesson copies — each lesson edits the same file and updates
its in-file BUILD MAP comment.

- **`market.py`** — Track 1 (normal trading). A simulator/backtester. Growth
  ladder (one new loop line per lesson):
  `L1 price += shock` → `L2 cash/shares` → `L3 equity = cash + shares*price`
  → `L4 action = strategy(history)` → `L5 fills` → `L6 MA-crossover signal`
  → `L7 position sizing` → `L8 metrics (return/Sharpe/drawdown)`
  → `L9 fees + slippage` → `L10 capstone: beat buy-and-hold after costs`.
- **`exchange.py`** — Track 2 (HFT). An order-book matching engine. Growth
  ladder: `L11 book (bids/asks/spread)` → `L12 market order eats book`
  → `L13 limit order rests (price-time priority)` → `L14 matching loop`
  → `L15 market-data snapshots` → `L16 market maker quotes both sides`
  → `L17 inventory skew` → `L18 latency/queue` → `L19 adverse selection`
  → `L20 capstone: profitable AND flat market maker`.

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
