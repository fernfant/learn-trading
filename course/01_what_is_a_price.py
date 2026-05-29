"""
LESSON 1 — What is a price? (Track 1: normal trading)

Before you can trade, you have to know what you're trading against: a PRICE.
A price is not a fixed fact like "this chocolate bar costs $2". A stock price
is a living number that changes every time someone buys or sells. In this
lesson we don't trade yet. We just watch a price MOVE, and discover the most
important and most annoying fact in all of trading:

    you cannot know which way it will move next.

Run it:  python3 01_what_is_a_price.py
Then read 01_walkthrough.md line by line.
"""

import random

random.seed(7)

# ---------------------------------------------------------------------------
# PART A — a price is a number that wanders
# ---------------------------------------------------------------------------
price = 100.0
history = [price]

for day in range(20):
    shock = random.gauss(0, 1)   # today's surprise: small, random, fair coin-ish
    price += shock               # the price just gets nudged by the surprise
    history.append(price)
    arrow = "up  " if shock > 0 else "down"
    print(f"day {day:2d}:  shock {shock:+5.2f}  ->  price {price:7.2f}  ({arrow})")

print(f"\nAfter 20 days the price went from {history[0]:.2f} to {price:.2f}.")


# ---------------------------------------------------------------------------
# PART B — can we predict tomorrow? (a little experiment)
# ---------------------------------------------------------------------------
# A tempting "strategy": if it went up today, bet it goes up tomorrow
# ("momentum"). Let's test that guess against pure randomness and count how
# often we'd be right. With a fair random walk, the answer should be... a coin.
random.seed(7)
price = 100.0
last_shock = 0.0
correct = 0
total = 0
for _ in range(10_000):
    shock = random.gauss(0, 1)
    guess_up = last_shock > 0          # we predict: same direction as yesterday
    actually_up = shock > 0
    if last_shock != 0:
        total += 1
        correct += (guess_up == actually_up)
    last_shock = shock

print(f"\nMomentum guess was right {correct}/{total} times "
      f"= {100 * correct / total:.1f}% (a coin flip is 50%).")
print("Lesson: in a pure random walk, yesterday tells you NOTHING about today.")
print("Real markets aren't *perfectly* random — but they're close enough that")
print("beating a coin flip is the whole, hard game. That's what Track 1 is about.")


# ---------------------------------------------------------------------------
# TRY IT
# ---------------------------------------------------------------------------
# 1. Change the guess to "opposite of yesterday" (mean-reversion):
#    guess_up = last_shock < 0. Still ~50%? Yep. Randomness doesn't care.
# 2. Give the market a real edge: shock = random.gauss(0.3, 1) (up-biased).
#    Now does "always guess up" beat 50%? Try guess_up = True. This is the
#    difference between gambling and investing: a real, persistent edge.
# 3. Open ../market.py — it's the same wandering price, drawn as a chart.
