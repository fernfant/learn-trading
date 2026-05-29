# Learn to Trade

A hands-on, build-it-yourself course on how markets work — from "what is a
stock price?" all the way to **high-frequency trading**. You learn by writing
two small programs, one line per lesson, until they're the real thing.

No finance background needed. No external packages — just `python3` and the
standard library. The early lessons are gentle enough for a curious kid; the
later ones go deep into real market microstructure.

## The two things you build

- **[`market.py`](market.py)** — a trading **simulator + backtester** (Track 1).
  A wandering price, a portfolio, a strategy, and honest metrics. You grow it
  across Lessons 1–10 until it can prove whether a strategy actually beats
  buy-and-hold *after costs*.

- **[`exchange.py`](exchange.py)** — an **order-book matching engine** (Track 2).
  The machine that *makes* a price by matching buyers and sellers. You grow it
  across Lessons 11–20 until a **market-maker bot** earns the spread while
  managing inventory and latency — the heart of HFT.

## Quick start

```bash
python3 market.py     # Track 1: watch a price wander, as a chart
python3 exchange.py   # Track 2: see an order book and its spread
```

Then open [`course/README.md`](course/README.md) and start with Lesson 1.

## Why two tracks?

Most trading courses teach one or the other. They're really two ends of the
same thing. Track 1 stands *outside* the market and asks "given prices, how do
I trade well?" Track 2 stands *inside* the market and asks "how is the price
made, and how do I profit from being the one who makes it?" Doing both, in
order, is what makes high-frequency trading finally make sense instead of
sounding like magic.

## License

[MIT](LICENSE) — use it, fork it, remix it, teach with it.

## Author

Built by [@fernfant](https://github.com/fernfant) in the same spirit as the
mini-PRAGMA ML course and the learn-physics course: teach by building the real
thing, one line at a time.
