"""Start Here, bonus step, finished: gradient descent ("follow the slope"), plus restarts.

    python3 labs/00-start-here/finished/follow_the_slope.py 1          # your first target
    python3 labs/00-start-here/finished/follow_the_slope.py 2          # a post in the way: it gets stuck
    python3 labs/00-start-here/finished/follow_the_slope.py 2 --restarts 5 --seed 3
    python3 labs/00-start-here/finished/follow_the_slope.py 3          # all six motors, gripper pointing down
    python3 labs/00-start-here/finished/follow_the_slope.py 1 --runs 20

This is NOT a Chapter 3 method: it needs the slope of the landscape, not just the score.
It's here as a contrast with lab 01, and as a complete example of a lab's moving parts.
"""
import argparse
import math
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # the repo root

from armlab.kinematics import FOLDED, HOME, LIMITS, tcp, tool_direction
from armlab.world import Level, collides
from viewer.trace import NULL, Trace

LEVELS = {
    1: Level(1, "My first target", free=(0, 1, 2), start=FOLDED, target=(1.2, 1.0, 0.5), floor=True,
             blurb="The Start Here target. Smooth and open: the slope points the way."),
    2: Level(2, "Around the post · 3 motors", free=(0, 1, 2), start=(0, 60, 30, 0, 0, 0), target=(1.0, 1.6, 0.0),
             floor=True, boxes=(((0.5, 0.0, -0.25), (0.8, 1.1, 0.25)),),
             blurb="The slope points straight at the post. Following it gets you stuck against the wall."),
    3: Level(3, "Pick from above · 6 motors", free=(0, 1, 2, 3, 4, 5), start=HOME, target=(1.1, 0.25, 0.4),
             floor=True, down=(0.0, -1.0, 0.0), boxes=(((0.95, 0.0, 0.25), (1.25, 0.12, 0.55)),),
             blurb="Six motors, gripper pointing down. Too many poses to guess; the slope still works."),
}


def error(pose, level, w=0.5):
    """Metres from the target, plus (level 3) w metres per radian the gripper is off vertical."""
    e = math.dist(tcp(pose), level.target)
    if level.down:
        cos = sum(a * b for a, b in zip(tool_direction(pose), level.down))
        e += w * math.acos(max(-1.0, min(1.0, cos)))
    return e


def score(pose, level, w=0.5):
    """What the search minimises. A pose that hits something isn't allowed at all (infinite)."""
    return math.inf if collides(pose, level) else error(pose, level, w)


def clamp(pose):
    return tuple(max(lo, min(hi, a)) for a, (lo, hi) in zip(pose, LIMITS))


def slope(pose, level, w=0.5, h=0.5):
    """How the error changes per degree of each free motor: nudge it +h and -h degrees and compare."""
    g = [0.0] * len(pose)
    for j in level.free:
        up, dn = list(pose), list(pose)
        up[j] += h
        dn[j] -= h
        g[j] = (error(up, level, w) - error(dn, level, w)) / (2 * h)
    return g


def gradient_descent(start, level, rec=NULL, w=0.5, step=20.0, iters=300, tol=0.002):
    """Step `step` degrees downhill; if that fails, halve the step; if it works, grow it 20%.

    Returns (best_pose, best_score, evaluations). Evaluations include the slope measurements.
    """
    pose = clamp(start)
    s = score(pose, level, w)
    evals = 1
    rec.restart(pose, min(s, 99))
    for _ in range(iters):
        if s < tol or step < 0.01:
            break
        g = slope(pose, level, w)
        evals += 2 * len(level.free)
        norm = math.sqrt(sum(x * x for x in g)) or 1.0
        cand = clamp(tuple(a - step * gi / norm for a, gi in zip(pose, g)))
        cs = score(cand, level, w)
        evals += 1
        if cs < s:
            pose, s = cand, cs
            rec.moved(pose, s)
            step *= 1.2
        else:
            rec.tried(cand, min(cs, 99))
            step *= 0.5
    return pose, s, evals


def random_pose(level, rng):
    return tuple(rng.uniform(*LIMITS[j]) if j in level.free else v for j, v in enumerate(level.start))


def with_restarts(level, n, rng, rec=NULL, w=0.5):
    """Gradient descent from n random poses; keep the best. The same idea as iterated hill-climbing."""
    best, best_s, evals = None, math.inf, 0
    for _ in range(n):
        p, s, e = gradient_descent(random_pose(level, rng), level, rec, w)
        evals += e
        if s < best_s:
            best, best_s = p, s
    return best, best_s, evals


def success(pose, level, s):
    """Within 5 cm, not colliding, and (level 3) within 10 degrees of straight down."""
    if s == math.inf or math.dist(tcp(pose), level.target) >= 0.05:
        return False
    if level.down:
        cos = sum(a * b for a, b in zip(tool_direction(pose), level.down))
        return math.degrees(math.acos(max(-1.0, min(1.0, cos)))) < 10
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("level", type=int, choices=sorted(LEVELS), nargs="?", default=1)
    p.add_argument("--restarts", type=int, default=0, help="run from this many random poses instead of the start pose")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--runs", type=int, default=0, help="run seeds 0..N-1 from random poses; print a success rate")
    args = p.parse_args()
    level = LEVELS[args.level]

    if args.runs:
        wins, evals = 0, 0
        for seed in range(args.runs):
            rng = random.Random(seed)
            if args.restarts:
                best, s, e = with_restarts(level, args.restarts, rng)
            else:
                best, s, e = gradient_descent(random_pose(level, rng), level)
            wins += success(best, level, s)
            evals += e
        print(f"Level {level.number}: within 5 cm in {wins}/{args.runs} runs · avg evaluations {evals / args.runs:,.0f}")
        return

    name = "gradient descent" + (f" + {args.restarts} restarts" if args.restarts else "")
    rec = Trace(level, name, note=" ".join(sys.argv[1:]), lab="00-start-here")
    if args.restarts:
        best, s, e = with_restarts(level, args.restarts, random.Random(args.seed), rec)
    else:
        best, s, e = gradient_descent(level.start, level, rec)
    print(f"Level {level.number} · {name}")
    print(f"  best pose   ({', '.join(f'{a:.1f}' for a in best)})")
    print(f"  distance    {math.dist(tcp(best), level.target) * 100:.1f} cm" + ("   (every pose collided)" if s == math.inf else ""))
    print(f"  evaluations {e:,}   success: {success(best, level, s)}")
    rec.save(best=best)


if __name__ == "__main__":
    main()
