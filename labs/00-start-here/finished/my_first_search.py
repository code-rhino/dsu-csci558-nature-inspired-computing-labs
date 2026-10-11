"""Start Here, finished: everything from steps 1-7 of the README in one file.

Compare it with your own labs/00-start-here/my_first_search.py.

    python3 labs/00-start-here/finished/my_first_search.py           # one search, sent to the viewer
    python3 labs/00-start-here/finished/my_first_search.py --test20  # step 7: 20 seeds
"""
import math
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # the repo root, so the imports below work

from farmlab.farms import get_farm
from farmlab.flight import route_score
from viewer.trace import Trace

farm = get_farm(1)

EMPTY_KG = 25.0          # the drone with its battery and an empty tank
WH_PER_KG_M = 0.01       # energy to carry 1 kg for 1 m


# Step 3: one leg
def leg_energy(a, b, mass_kg):
    """Wh to fly in a straight line from point a to point b carrying mass_kg in total."""
    return WH_PER_KG_M * mass_kg * math.dist(a, b)


# Step 4: a whole route (farm 1 is a single trip: everything fits in one tank)
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


# Step 6: random search
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
        rec.tried(route, s, accepted=better)
        if better:
            best, best_score = route, s
    return best, best_score


# Step 7: how good is it, really?
class NoRecord:
    """Stands in for Trace when you don't want to record (much faster)."""
    def restart(self, *a): pass
    def tried(self, *a, **k): pass


BEST_KNOWN = 143.4       # Wh: the cheapest of all 40,320 orders (the bonus step finds it)


def test20(tries=2000):
    wins = 0
    for seed in range(20):
        best, s = random_search(tries, random.Random(seed), NoRecord())
        print(f"seed {seed:2}: {s:6.1f} Wh  ({100 * (s / BEST_KNOWN - 1):4.1f}% above the best)")
        wins += s <= BEST_KNOWN * 1.01
    print(f"within 1% of the best: {wins} of 20")


if __name__ == "__main__":
    if "--test20" in sys.argv:
        test20()
    else:
        assert abs(route_energy([0, 1, 2, 3, 4, 5, 6, 7]) - route_score([0, 1, 2, 3, 4, 5, 6, 7], farm)) < 1e-9
        rec = Trace(farm, "random search", lab="00-start-here")
        best, s = random_search(2000, random.Random(0), rec)
        print("best route:", best)
        print(f"energy: {s:.1f} Wh")
        rec.save()
