# Lab 00 · Start here

**Type along and build your first search in about 45 minutes.** You'll work out what a drone flight costs, write the score for a whole spraying route, watch the drone fly it in 3D, write a search that hunts for a cheaper route, and then find out honestly how good that search is. Every piece of code is on this page. Type it yourself rather than pasting; that's where the learning happens.

**What you'll end up with:** your own `my_first_search.py` (about 60 lines), a 3D replay of the drone spraying the field, and a measured result that explains why the rest of the labs exist.

## Read first

| Book | Section | Pages | Why |
|---|---|---|---|
| FNC (de Castro) | 3.1 Introduction, 3.2 Problem solving as a search task | 61–65 | The three ingredients of every search: representation, objective, evaluation. You'll write all three today. |
| CI (Eberhart & Shi) | Ch. 3, "Evolutionary Computation Overview" and "EC Paradigm Attributes" | 47–51 | Why these methods only need a score, not a formula for the answer. |

## Before you start

From the repo root, start the viewer and leave it running in its own terminal window:

```bash
python3 -m viewer
```

Your browser opens on the farm. Everything below runs in a **second** terminal, from the repo root.

---

## Step 1 · Create your file (2 min)

Create `labs/00-start-here/my_first_search.py` and type:

```python
import math
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # lets Python find farmlab/ and viewer/

from farmlab.farms import get_farm
from farmlab.flight import route_score
from viewer.trace import Trace

farm = get_farm(1)
```

The `sys.path` line tells Python to look two folders up, at the repo root, for the shared code. Run it: `python3 labs/00-start-here/my_first_search.py`. **No output is good.** An `ImportError` means the file isn't in `labs/00-start-here/`.

## Step 2 · Meet the farm (5 min)

Farm 1 is a 160 m × 100 m corn field. A soil test found **8 zones** that need fertiliser. The base station, where the drone takes off and refills, is just off the west edge at (−15, 50). Coordinates are metres: x is east, y is north.

Add this to the bottom of your file and run it:

```python
for k, z in enumerate(farm.zones):
    print(k, z.name, (z.x, z.y), z.need_l, "L")
```

<details><summary>What you should see</summary>

```
0 Z1 (130.0, 90.0) 5.0 L
1 Z2 (30.0, 30.0) 1.0 L
2 Z3 (70.0, 70.0) 3.0 L
3 Z4 (150.0, 10.0) 2.0 L
4 Z5 (50.0, 90.0) 4.0 L
5 Z6 (90.0, 30.0) 1.0 L
6 Z7 (110.0, 50.0) 2.0 L
7 Z8 (30.0, 70.0) 2.0 L
```
</details>

The zones need 20 L between them, exactly one full tank, so the drone sprays them all in **one trip**. The only decision is the **order**. A route is written as a list of zone numbers, such as `[0, 1, 2, 3, 4, 5, 6, 7]` (Z1, then Z2, then Z3...).

**Predict:** how many different orders are there for 8 zones? Delete the `for` loop before going on.

<details><summary>Answer</summary>

8! = 8 × 7 × 6 × … × 1 = **40,320**.
</details>

## Step 3 · What one leg costs (8 min)

The drone's energy model (from `farmlab/drone.json`) is deliberately simple:

> **energy (Wh) = 0.01 × mass on board (kg) × metres flown**

The drone weighs **25 kg** with an empty tank, and a litre of fertiliser weighs **1 kg**.

**By hand:** Z7 is at (110, 50) and the base at (−15, 50), so it's exactly 125 m due east.
1. What does the flight out to Z7 cost **with a full 20 L tank**?
2. What does the flight back cost **with an empty tank**?

<details><summary>Check</summary>

1. 0.01 × (25 + 20) × 125 = **56.25 Wh**.
2. 0.01 × 25 × 125 = **31.25 Wh**. A full tank makes every metre cost 80% more.
</details>

Now write it. Add this above the bottom of your file:

```python
EMPTY_KG = 25.0          # the drone with its battery and an empty tank
WH_PER_KG_M = 0.01       # energy to carry 1 kg for 1 m


def leg_energy(a, b, mass_kg):
    """Wh to fly in a straight line from point a to point b carrying mass_kg in total."""
    return WH_PER_KG_M * mass_kg * math.dist(a, b)
```

Check your hand answer: `print(leg_energy(farm.base, (110, 50), 45))` should print `56.25`.

## Step 4 · Score a whole route (10 min)

This is the **evaluation function** from FNC 3.2. The drone loads all 20 L, flies to each zone in turn, sprays it (and gets lighter), then flies home:

```python
def route_energy(route):
    """Wh to take off with all the fertiliser, spray the zones in `route` order, and fly home."""
    load = sum(farm.zones[z].need_l for z in route)       # litres, and 1 L weighs 1 kg
    here = farm.base
    total = 0.0
    for z in route:
        zone = farm.zones[z]
        total += leg_energy(here, (zone.x, zone.y), EMPTY_KG + load)
        load -= zone.need_l
        here = (zone.x, zone.y)
    total += leg_energy(here, farm.base, EMPTY_KG + load)
    return total
```

Now check yours against the shared code. `farmlab` has its own `route_score(route, farm)`, which also handles refill trips, obstacles and wind for the bigger farms. On farm 1 they must agree:

```python
r = [0, 1, 2, 3, 4, 5, 6, 7]
print(route_energy(r), route_score(r, farm))
print(route_energy(r[::-1]))
```

You should see **280.3 Wh** twice, then **268.3 Wh** for the same zones in reverse order. **Same distance, different energy.** That's the weight of the fertiliser: the order decides how far each litre gets carried before it's sprayed.

## Step 5 · Make it fly (5 min)

The viewer replays a **trace**: a record of the routes you scored. Replace your `print` lines with:

```python
if __name__ == "__main__":
    route = [0, 1, 2, 3, 4, 5, 6, 7]
    rec = Trace(farm, "my first route", lab="00-start-here")
    rec.restart(route, route_energy(route))
    rec.save(best=route)
```

Run it. The viewer picks it up by itself: the route appears as coloured lines, then the drone takes off, flies to each zone, drops down and sprays, and comes home. Watch the **battery** and **tank** gauges. The yellow corn turns green as it's sprayed: it's short of nitrogen until then.

![Farm 1 in the viewer: the base on the left, eight zones, one trip](../../docs/screenshots/farm1.jpg)

*Farm 1 in the viewer, showing the best route of all (you'll find it in the bonus step). Pale yellow zones still need fertiliser.*

**Try:** change `route` to one you think is cheaper and run it again. Can you beat 268.3 Wh by hand? Use the **Top** camera to plan.

## Step 6 · Your first search: random guessing (10 min)

The simplest possible search: try lots of random orders and keep the cheapest. Add these two functions:

```python
def random_route(rng):
    route = list(range(len(farm.zones)))
    rng.shuffle(route)
    return route


def random_search(tries, rng, rec):
    best = list(range(len(farm.zones)))
    best_score = route_energy(best)
    rec.restart(best, best_score)
    for _ in range(tries):
        route = random_route(rng)
        s = route_energy(route)
        better = s < best_score
        rec.tried(route, s, accepted=better)     # the viewer only changes the route when it's better
        if better:
            best, best_score = route, s
    return best, best_score
```

And replace your whole `__main__` block with:

```python
if __name__ == "__main__":
    rec = Trace(farm, "random search", lab="00-start-here")
    best, s = random_search(2000, random.Random(0), rec)
    print("best route:", best)
    print(f"energy: {s:.1f} Wh")
    rec.save()
```

**Why `random.Random(0)`?** The `0` is a **seed**. The same seed gives the same "random" numbers, so you and your classmates get exactly the same run and can compare results.

Run it, then watch the replay:

```
best route: [7, 4, 0, 6, 3, 2, 5, 1]
energy: 168.8 Wh
```

**What to watch:**
- The blue dashed route flickers around, one random guess at a time.
- The coloured route only changes when a guess beats the best so far.
- In the energy chart, the green "best" line drops quickly at first, then hardly at all.
- At the end the drone flies the best route it found.

## Step 7 · How good is it, really? (5 min)

One run proves nothing: maybe seed 0 was unlucky. Scientists run many trials. The best possible route for farm 1 uses **143.4 Wh** (the bonus step proves it). Add this, and call `test20()` instead of the search by temporarily replacing the `__main__` block's contents with `test20()`:

```python
class NoRecord:
    """Stands in for Trace when you don't want to record (much faster)."""
    def restart(self, *a): pass
    def tried(self, *a, **k): pass


BEST_KNOWN = 143.4


def test20(tries=2000):
    wins = 0
    for seed in range(20):
        best, s = random_search(tries, random.Random(seed), NoRecord())
        print(f"seed {seed:2}: {s:6.1f} Wh  ({100 * (s / BEST_KNOWN - 1):4.1f}% above the best)")
        wins += s <= BEST_KNOWN * 1.01
    print(f"within 1% of the best: {wins} of 20")
```

**The result:** within 1% of the best in **0 of 20** runs. With 20,000 guesses per run it's 11 of 20, but that's half of all 40,320 orders.

**Why?** Exactly **one** order out of 40,320 is within 1% of the best. Random guessing doesn't **learn** anything from its previous guesses. Every method in Chapter 3 is a way of using what you've already found to make a better next guess.

## Bonus · Rules of thumb, and the answer key (10 min)

People planning a route by hand use rules of thumb. Are they any good? `finished/rules_of_thumb.py` tries three, then checks every one of the 40,320 orders:

```bash
python3 labs/00-start-here/finished/rules_of_thumb.py
```

| Route | Energy | Distance |
|---|---|---|
| zones in name order | 280.3 Wh | 784 m |
| **heaviest first**: get light quickly | 237.4 Wh | 705 m |
| **nearest first**: always the closest zone next | 166.7 Wh | 516 m |
| **shortest loop**: fewest metres of all 40,320 | 166.6 Wh | 443 m |
| the shortest loop, **flown the other way round** | **143.4 Wh** | 443 m |
| **brute force**: the cheapest of all 40,320 | **143.4 Wh** | 443 m |

Two lessons:
1. **Weight and distance pull against each other.** "Heaviest first" ignores distance and does badly. "Shortest" ignores weight, and flying the same loop the other way round, so the heavy zones come first, saves 14%.
2. **Brute force is the answer key, and it only works because farm 1 is tiny.** It checks 40,320 orders in under a second. Farm 2 has 14 zones: 87 billion orders, weeks of computing on a laptop. Try `--farm 3`: the rules of thumb still work there, but nothing tells you how far from the best they are. That's what search is for.

---

## Check your work

If something doesn't match, compare with the finished files:

| File | What it is |
|---|---|
| `finished/my_first_search.py` | Steps 1–7, complete. Run with `--test20` for step 7. |
| `finished/rules_of_thumb.py` | The bonus, complete. `--farm N` for the other farms. |
| `finished/test_finished.py` | Checks that the finished files still give the numbers quoted on this page. |

## Where next

**Lab 01 · Route search** (being rebuilt for the drone): hill-climbing, restarts, stochastic hill-climbing and simulated annealing from FNC Chapter 3, on the same farms. You've already built the hard part: a score, a search loop, and a way to watch it.
