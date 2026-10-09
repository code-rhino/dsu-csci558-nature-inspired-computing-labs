"""Run one of your algorithms on a level and send it to the 3D viewer. Provided.

    python3 run.py 1 hc --step 10                 # Step 4's hand walk
    python3 run.py 1 hc --step 10 --diagonal
    python3 run.py 1 brute                        # the answer key, 2-degree grid
    python3 run.py 3 ihc --restarts 8 --seed 4
    python3 run.py 3 sa --T0 0.5 --beta 0.998 --iters 4000
    python3 run.py 4 sa --w 0.2

Add --runs 20 to run seeds 0..19 without recording and print a success rate instead.
Start the viewer first, from the repo root:  python3 -m viewer
"""
import argparse
import math
import random
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)]  # repo root + this lab

import climb
from armlab.kinematics import tcp, tool_direction
from armlab.world import collides
from levels import get_level
from viewer.trace import NULL, Trace

ALGOS = {"hc": "hill-climbing", "ihc": "iterated hill-climbing", "shc": "stochastic hill-climbing",
         "sa": "simulated annealing", "brute": "brute force"}
STEP_OF = {"planar_tip": 1, "distance": 2, "reach_score": 2, "neighbors": 3, "hill_climb": 4,
           "ik_2link": 5, "brute_force": 5, "random_pose": 6, "iterated_hc": 6, "accept_prob": 7,
           "random_neighbor": 7, "stochastic_hc": 7, "anneal": 8, "penalized": 9,
           "angle_between": 10, "pose_score": 10}
REACH_OK, ANGLE_OK = 0.05, 10.0   # success = within 5 cm (and, on level 4, within 10 degrees)


class Counted:
    def __init__(self, fn):
        self.fn, self.calls = fn, 0

    def __call__(self, a):
        self.calls += 1
        return self.fn(a)


def make_score(level, args):
    if level.down:
        base = lambda a: climb.pose_score(a, level, args.w)
    else:
        base = lambda a: climb.reach_score(a, level)
    if level.floor or level.boxes:
        return climb.penalized(base, level, args.penalty)
    return base


def success(pose, level):
    ok = climb.reach_score(pose, level) < REACH_OK and not collides(pose, level)
    if level.down:
        ok = ok and math.degrees(climb.angle_between(tool_direction(pose), level.down)) < ANGLE_OK
    return ok


def run_once(level, args, rng, score, rec):
    free = level.free
    max_step = args.max_step
    nb = lambda a: climb.neighbors(a, free, args.step, args.diagonal)
    start = climb.random_pose(level, rng) if args.start == "random" else level.start
    if args.algo == "hc":
        best, s, _ = climb.hill_climb(start, score, nb, rec)
    elif args.algo == "ihc":
        best, s, _ = climb.iterated_hc(level, score, nb, args.restarts, rng, rec)
    elif args.algo == "shc":
        best, s = climb.stochastic_hc(start, score, free, args.T, args.iters, rng, max_step or 5, rec)
    elif args.algo == "sa":
        best, s = climb.anneal(start, score, free, args.T0, args.beta, args.iters, rng, max_step or 10, rec)
    else:
        if len(free) > 2:
            sys.exit(f"brute force on {len(free)} joints is {360 ** len(free):,} poses. Levels 1 only, please.")
        state = {"best": math.inf, "n": 0}

        def watched(a):
            v = score(a)
            state["n"] += 1
            if v < state["best"]:
                state["best"] = v
                rec.moved(a, v)
            elif state["n"] % 25 == 0:
                rec.tried(a, v)
            return v

        best, s, _ = climb.brute_force(watched, free, level.start, args.step)
    return tuple(best), s


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("level", type=int, choices=[1, 2, 3, 4])
    p.add_argument("algo", choices=list(ALGOS))
    p.add_argument("--step", type=int, default=None, help="degrees per move for hc/ihc/brute (default 1; brute 2)")
    p.add_argument("--diagonal", action="store_true", help="hc/ihc: let several motors move at once")
    p.add_argument("--start", choices=["level", "random"], default=None,
                   help="hc/shc/sa start pose (default: level for one run, random for --runs)")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--restarts", type=int, default=8)
    p.add_argument("--T", type=float, default=0.02, help="stochastic hc temperature")
    p.add_argument("--T0", type=float, default=0.5, help="annealing start temperature")
    p.add_argument("--beta", type=float, default=0.998, help="annealing cooling factor")
    p.add_argument("--iters", type=int, default=4000)
    p.add_argument("--max-step", type=int, default=None, help="shc/sa biggest random move (5 / 10)")
    p.add_argument("--penalty", type=float, default=10.0, help="score added for a collision")
    p.add_argument("--w", type=float, default=0.5, help="level 4: metres per radian of gripper error")
    p.add_argument("--runs", type=int, default=0, help="run seeds 0..N-1, report success, don't record")
    p.add_argument("--name", default=None, help="file name for the trace")
    args = p.parse_args()
    if args.step is None:
        args.step = 2 if args.algo == "brute" else 1
    if args.start is None:
        args.start = "random" if args.runs else "level"

    level = get_level(args.level)
    label = ALGOS[args.algo]
    try:
        if args.runs:
            wins, evals, scores = 0, 0, []
            for seed in range(args.runs):
                score = Counted(make_score(level, args))
                best, s = run_once(level, args, random.Random(seed), score, NULL)
                wins += success(best, level)
                evals += score.calls
                scores.append(s)
            scores.sort()
            print(f"Level {level.number} · {label}: success {wins}/{args.runs} "
                  f"· avg evaluations {evals / args.runs:,.0f} "
                  f"· best {scores[0]:.3f}  median {scores[len(scores) // 2]:.3f}  worst {scores[-1]:.3f}")
            return
        rec = Trace(level, label, note=" ".join(sys.argv[2:]), lab="01-reach-search")
        score = Counted(make_score(level, args))
        best, s = run_once(level, args, random.Random(args.seed), score, rec)
    except NotImplementedError:
        import traceback
        fn = traceback.extract_tb(sys.exc_info()[2])[-1].name
        sys.exit(f"climb.{fn} isn't written yet. That's README Step {STEP_OF.get(fn, '?')}.")

    x, y, z = tcp(best)
    print(f"Level {level.number} · {label}")
    print(f"  best pose   {best}")
    print(f"  score       {s:.4f}")
    print(f"  tool tip    ({x:.3f}, {y:.3f}, {z:.3f})   target {level.target}")
    print(f"  evaluations {score.calls:,}   collides: {collides(best, level)}   success: {success(best, level)}")
    rec.save(args.name, best)


if __name__ == "__main__":
    main()
