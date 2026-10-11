"""Start Here, bonus step, finished: rules of thumb, and the answer key by brute force.

    python3 labs/00-start-here/finished/rules_of_thumb.py            # farm 1: every rule, then all 40,320 orders
    python3 labs/00-start-here/finished/rules_of_thumb.py --farm 3   # bigger farms: rules only (too many orders)

A rule of thumb (a "heuristic") builds one route straight away, with no searching:
  * nearest first: always fly to the closest zone not yet sprayed;
  * heaviest first: spray the zones that need the most fertiliser first, to get light quickly;
  * shortest loop: the order with the fewest metres (found by trying them all, so farm 1 only).

Brute force tries every order, so it's guaranteed to find the best one. It's the answer key that
lets you judge everything else, and it only works because farm 1 is small.
"""
import argparse
import itertools
import math
import sys
import time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # the repo root

from farmlab.farms import BEST_KNOWN, get_farm
from farmlab.flight import fly, route_score
from farmlab.world import flight_distance
from viewer.trace import Trace


def nearest_first(farm):
    route, here, left = [], -1, set(range(len(farm.zones)))
    while left:
        z = min(left, key=lambda k: (flight_distance(here, k, farm), k))
        route.append(z)
        left.remove(z)
        here = z
    return route


def heaviest_first(farm):
    return sorted(range(len(farm.zones)), key=lambda k: (-farm.zones[k].need_l, k))


def every_order(farm, key):
    """The route with the lowest key(route) out of every possible order. Farm 1 only: 8! = 40,320."""
    return list(min(itertools.permutations(range(len(farm.zones))), key=key))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--farm", type=int, default=1)
    args = p.parse_args()
    farm = get_farm(args.farm)
    n = len(farm.zones)
    rec = Trace(farm, "rules of thumb", note=f"farm {farm.number}", lab="00-start-here")

    rules = [("zones in name order", list(range(n))), ("nearest first", nearest_first(farm)),
             ("heaviest first", heaviest_first(farm))]
    if n <= 8:
        shortest = every_order(farm, lambda r: fly(r, farm).distance_m)
        rules += [("shortest loop", shortest), ("shortest loop, flown the other way", shortest[::-1])]

    best, best_s = None, math.inf
    for k, (name, route) in enumerate(rules):
        f = fly(route, farm)
        print(f"{name:<36} {f.energy_wh:6.1f} Wh  {f.distance_m:5.0f} m  {len(f.trips)} trip(s)  "
              f"{' '.join(farm.zones[z].name for z in route)}")
        (rec.restart if k == 0 else rec.tried)(route, f.score)
        rec.note_text(f"{name}: {f.energy_wh:.1f} Wh, {f.distance_m:.0f} m")
        if f.score < best_s:
            best, best_s = route, f.score

    if n <= 8:
        t = time.time()
        answer = every_order(farm, lambda r: route_score(r, farm))
        f = fly(answer, farm)
        print(f"{'brute force: the best of all ' + format(math.factorial(n), ',') + ' orders':<36} {f.energy_wh:6.1f} Wh  "
              f"{f.distance_m:5.0f} m  {len(f.trips)} trip(s)  {' '.join(farm.zones[z].name for z in answer)}"
              f"   ({time.time() - t:.1f} s)")
        rec.tried(answer, f.score, accepted=True)
        rec.note_text(f"Brute force, the answer key: {f.energy_wh:.1f} Wh. Every one of the {math.factorial(n):,} orders was tried.")
        best = answer
    else:
        print(f"\n{n} zones: {math.factorial(n):,} orders, far too many to try them all. "
              f"Best known for this farm: {BEST_KNOWN[farm.number]} Wh.")
    rec.save(best=best)


if __name__ == "__main__":
    main()
