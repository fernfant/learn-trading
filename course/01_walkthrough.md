# Lesson 1 — What is a price?

> Track 1 (normal trading) · cumulative artifact: [`../market.py`](../market.py)
> · code for this lesson: [`01_what_is_a_price.py`](01_what_is_a_price.py)

You're about to learn to trade. But trade *against what*? Against a **price** —
and the first thing to understand is that a stock price is nothing like the
price of a chocolate bar. The chocolate bar is $2 today and $2 tomorrow. A
stock price changes every single time someone, somewhere, decides to buy or
sell. It is a number that is *alive*.

This lesson has one job: make you feel, in your bones, that **you cannot know
which way a price will move next.** Everything in Track 1 is a reaction to that
one hard fact.

---

## Part A — a price is a number that wanders

```python
price = 100.0
history = [price]
```

Our stock starts at \$100. `history` is a list where we'll remember every
day's price, so later we can look back and draw a chart.

```python
for day in range(20):
    shock = random.gauss(0, 1)
    price += shock
    history.append(price)
```

This little loop **is the market.** Read it slowly:

- `shock = random.gauss(0, 1)` — each day the world throws a **surprise** at
  the stock. Maybe good news, maybe bad. `random.gauss(0, 1)` draws a random
  number that is *usually* small (near 0), *occasionally* big, and just as
  likely to be negative as positive. The `0` is the average (no built-in
  up-or-down bias); the `1` is how wild the swings are.
- `price += shock` — the price simply gets **nudged** by today's surprise. Up
  on good news, down on bad. That's it. That's the only rule.

A price that moves by random nudges is called a **random walk**. It's the
simplest honest model of a market, and it's shockingly close to how real
prices behave over short horizons.

> **`random.seed(7)`** at the top means the "random" numbers come out the same
> every run, so the chart you see matches the one I see. Change the 7 and you
> get a brand-new market with the same rules.

When you run it, you watch the price stagger up and down for 20 days and end
somewhere it didn't plan to go. Nobody pushed it there. It just *wandered*.

---

## Part B — can we predict tomorrow?

Here's the trap every new trader falls into. You stare at the chart and your
brain screams *"it's been going up three days — it'll keep going up!"* That's
called a **momentum** bet. Let's test it, honestly, 10,000 times:

```python
guess_up = last_shock > 0          # predict: today moves the same way as yesterday
actually_up = shock > 0
correct += (guess_up == actually_up)
```

We predict each day will move the same direction as the previous day, then
check if we were right, and tally it up. The result:

```
Momentum guess was right 5002/9999 times = 50.0%  (a coin flip is 50%)
```

**Exactly a coin flip.** In a pure random walk, yesterday's move tells you
*nothing* about today's. Your pattern-seeing brain is fooling you — it sees
"trends" in what is really just noise.

This is the single most important idea in trading:

> Beating 50% is the entire game, and it is **hard**. Real markets aren't
> *perfectly* random — there are tiny, fleeting, hard-won edges — but they're
> close enough that most people who think they've found a pattern have found
> nothing but noise.

Track 1 is the disciplined search for a *real* edge, and the honest tools
(backtesting, costs, risk) to tell a real edge from a lucky streak.

---

## What you built

Nothing you can trade with yet — on purpose. You built the **stage**: a living
price. [`../market.py`](../market.py) is this exact wandering price drawn as a
chart, and it's the file you'll grow one line at a time across the next nine
lessons until it's a real backtester.

## Try it (answers to think about)

1. **Guess the opposite** (`guess_up = last_shock < 0`, "mean reversion"). Still
   ~50%. Randomness doesn't reward *any* fixed rule.
2. **Give the market a real edge** (`shock = random.gauss(0.3, 1)` — a built-in
   up-bias) and then `guess_up = True`. Now you beat 50%, because there's a
   *genuine* tilt to exploit. That gap — between a real edge and a made-up one
   — is the difference between investing and gambling.
3. Run [`../market.py`](../market.py) to see the same wander as a chart.

---

**Next:** [Lesson 2 — Your first trade](02_your_first_trade.py) — we give you
cash and let you buy a share. Now the wandering price starts costing or making
you money.
