"""Template lab: random search, the simplest possible baseline.

Copy this folder to start a new lab:

    cp -r labs/_template labs/01-my-lab
    python3 -m viewer                                    # terminal 1 (repo root)
    python3 labs/01-my-lab/run.py --farm 3 --tries 500   # terminal 2

It shows the three things every lab does: pick a Farm, score routes, and record
them with a Trace so the viewer can replay the run. Replace the search with yours.
"""
import argparse
import math
import random
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)]  # repo root + this lab

from farmlab.farms import BEST_KNOWN, get_farm
from farmlab.flight import route_score
from viewer.trace import Trace

LAB = Path(__file__).resolve().parent.name     # traces go to traces/<this folder name>/


def random_search(farm, tries, rng, rec):
    best, best_s = None, math.inf
    for _ in range(tries):
        route = list(range(len(farm.zones)))
        rng.shuffle(route)
        s = route_score(route, farm)               # Wh, lower is better
        better = s < best_s
        rec.tried(route, s, accepted=better)       # the viewer changes the route only on accepted ones
        if better:
            best, best_s = route, s
    return best, best_s


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--farm", type=int, default=1)
    p.add_argument("--tries", type=int, default=500)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    farm = get_farm(args.farm)
    rec = Trace(farm, "random search", note=f"{args.tries} tries, seed {args.seed}", lab=LAB)
    best, s = random_search(farm, args.tries, random.Random(args.seed), rec)
    print(f"best {best}  {s:.1f} Wh  (best known {BEST_KNOWN.get(farm.number, '?')} Wh)")
    rec.save(best=best)


if __name__ == "__main__":
    main()
