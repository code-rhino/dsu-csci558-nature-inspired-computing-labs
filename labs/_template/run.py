"""Template lab: random search, the simplest possible baseline.

Copy this folder to start a new lab:

    cp -r labs/_template labs/02-my-lab
    python3 -m viewer                          # terminal 1 (repo root)
    python3 labs/02-my-lab/run.py --tries 500  # terminal 2

It shows the three things every lab does: pick a Level, score poses, and record
them with a Trace so the viewer can replay the run. Replace the search with yours.
"""
import argparse
import math
import random
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)]  # repo root + this lab

from armlab.kinematics import LIMITS, tcp
from armlab.world import collides
from levels import get_level
from viewer.trace import Trace

LAB = Path(__file__).resolve().parent.name     # traces go to traces/<this folder name>/


def score(pose, level):
    """Lower is better: metres from the target, plus 10 if the arm hits something."""
    return math.dist(tcp(pose), level.target) + (10.0 if collides(pose, level) else 0.0)


def random_search(level, tries, rng, rec):
    best, best_s = None, math.inf
    for _ in range(tries):
        pose = list(level.start)
        for j in level.free:
            pose[j] = rng.randint(*LIMITS[j])
        s = score(pose, level)
        better = s < best_s
        rec.tried(pose, s, accepted=better)    # the viewer moves the solid arm only on accepted poses
        if better:
            best, best_s = tuple(pose), s
    return best, best_s


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--level", type=int, default=1)
    p.add_argument("--tries", type=int, default=500)
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    level = get_level(args.level)
    rec = Trace(level, "random search", note=f"{args.tries} tries, seed {args.seed}", lab=LAB)
    best, s = random_search(level, args.tries, random.Random(args.seed), rec)
    print(f"best {best}  score {s:.3f}")
    rec.save(best=best)


if __name__ == "__main__":
    main()
