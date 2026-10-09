"""Run your GA on a level and watch it in the viewer. Provided.

    python3 run.py 1                          # level 1 with the default settings
    python3 run.py 1 --pm 0                   # no mutation
    python3 run.py 2 --N 40 --gens 100 --seed 3
    python3 run.py 3 --N 60 --gens 150

Add --runs 20 to run seeds 0..19 without recording and print a success rate.
Start the viewer first, from the repo root:  python3 -m viewer
"""
import argparse
import math
import random
import sys
import traceback
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)]  # repo root + this lab

import ga
from armlab.kinematics import tcp
from levels import get_level, success
from viewer.trace import NULL, Trace

STEP_OF = {"decode": 1, "fitness": 2, "random_population": 3, "roulette": 4, "crossover": 5,
           "crossover_pairs": 5, "mutate": 6, "hamming": 7, "diversity": 7, "run_ga": 8}


def best_of(history):
    return min(history, key=lambda e: e["best_score"])


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("level", type=int, choices=[1, 2, 3])
    p.add_argument("--N", type=int, default=30, help="population size (even numbers pair up neatly)")
    p.add_argument("--gens", type=int, default=60, help="generations after generation 0")
    p.add_argument("--pc", type=float, default=0.7, help="crossover probability per pair")
    p.add_argument("--pm", type=float, default=0.02, help="mutation probability per bit")
    p.add_argument("--elite", type=int, default=1, help="best individuals copied unchanged each generation")
    p.add_argument("--bits", type=int, default=8, help="bits per motor")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--runs", type=int, default=0, help="run seeds 0..N-1, report success, don't record")
    p.add_argument("--name", default=None, help="file name for the trace")
    a = p.parse_args()
    level = get_level(a.level)
    evals = a.N * (a.gens + 1)

    try:
        if a.runs:
            wins, finals = 0, []
            for seed in range(a.runs):
                b = best_of(ga.run_ga(level, a.N, a.pc, a.pm, a.gens, random.Random(seed), a.bits, a.elite))
                wins += success(b["best_pose"], level)
                finals.append(b["best_score"])
            finals.sort()
            print(f"Level {level.number} · GA N={a.N} gens={a.gens} pc={a.pc} pm={a.pm} elite={a.elite}: "
                  f"success {wins}/{a.runs} · {evals:,} evaluations per run · "
                  f"best {finals[0]:.3f}  median {finals[len(finals) // 2]:.3f}  worst {finals[-1]:.3f}")
            return
        rec = Trace(level, "genetic algorithm", note=" ".join(sys.argv[2:]) or "defaults", lab="02-genetic-algorithm")
        h = ga.run_ga(level, a.N, a.pc, a.pm, a.gens, random.Random(a.seed), a.bits, a.elite, rec)
    except NotImplementedError:
        fn = traceback.extract_tb(sys.exc_info()[2])[-1].name
        sys.exit(f"ga.{fn} isn't written yet. That's README Step {STEP_OF.get(fn, '?')}.")

    b = best_of(h)
    pose = b["best_pose"]
    print(f"Level {level.number} · genetic algorithm (N={a.N}, {a.gens} generations)")
    print(f"  best pose     {pose}   found in generation {b['gen']}")
    print(f"  distance      {math.dist(tcp(pose), level.target) * 100:.1f} cm   score {b['best_score']:.4f}")
    print(f"  diversity     {h[0]['diversity']:.1f} bits at the start -> {h[-1]['diversity']:.1f} at the end")
    print(f"  evaluations   {evals:,}   success: {success(pose, level)}")
    rec.save(a.name, pose)


if __name__ == "__main__":
    main()
