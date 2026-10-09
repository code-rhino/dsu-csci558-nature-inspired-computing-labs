"""Checks for ga.py. Run:  python3 test_ga.py   or   python3 test_ga.py 4  (steps 1-4 only)."""
import random
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)]  # repo root + this lab

import ga
from levels import get_level, score

TESTS = []
L1, L2, L3 = get_level(1), get_level(2), get_level(3)


def step(n, name):
    def deco(fn):
        TESTS.append((n, name, fn))
        return fn
    return deco


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol


class Spy:
    def __init__(self):
        self.gens = []

    def generation(self, poses, scores, diversity=None):
        self.gens.append((list(poses), list(scores), diversity))


# ------------------------------------------------------------- Step 1
@step(1, "decode: corners and the middle")
def _():
    assert ga.decode([0] * 16, L1) == (0, -90, -150, 0, 0, 0), "all zeros -> each motor's minimum"
    assert ga.decode([1] * 16, L1) == (0, 180, 150, 0, 0, 0), "all ones -> each motor's maximum"
    half = [1, 0, 0, 0, 0, 0, 0, 0]                 # 128
    assert ga.decode(half + half, L1) == (0, round(-90 + 128 * 270 / 255), round(-150 + 128 * 300 / 255), 0, 0, 0)
    p = ga.decode([0] * 48, L3)
    assert p == (-170, -90, -150, -180, -120, -180), f"level 3 frees all six motors; got {p}"


@step(1, "decode: fixed motors come from level.start, 4-bit genes work")
def _():
    p = ga.decode([1] * 24, L2)
    assert p[3:] == L2.start[3:], "motors not in level.free keep level.start's values"
    assert ga.decode([1, 1, 1, 1, 0, 0, 0, 0], L1, n_bits=4) == (0, 180, -150, 0, 0, 0)


# ------------------------------------------------------------- Step 2
@step(2, "fitness = 1 / (1 + score)")
def _():
    on_target = (0, 0, 90, 0, 0, 0)
    assert close(ga.fitness(on_target, L1), 1.0)
    p = (0, 0, 0, 0, 0, 0)
    assert close(ga.fitness(p, L1), 1 / (1 + score(p, L1)))
    assert ga.fitness((0, 0, 0, 0, 0, 0), L2) < 0.1, "a pose through the post has a tiny fitness"


# ------------------------------------------------------------- Step 3
@step(3, "random_population")
def _():
    pop = ga.random_population(10, 24, random.Random(0))
    assert len(pop) == 10 and all(len(c) == 24 and set(c) <= {0, 1} for c in pop)
    assert len({tuple(c) for c in pop}) == 10, "ten different chromosomes"
    assert pop == ga.random_population(10, 24, random.Random(0)), "same seed, same population"


# ------------------------------------------------------------- Step 4
@step(4, "roulette: slices in order")
def _():
    pop = [[0], [1], [0], [1]]
    fits = [1, 2, 3, 4]                      # slices: [0, .1) [.1, .3) [.3, .6) [.6, 1)
    pool, picked = ga.roulette(pop, fits, random.Random(0), spins=[0.05, 0.1, 0.59, 0.99])
    assert picked == [0, 1, 2, 3], f"got {picked}"
    assert pool[1] == pop[1] and pool[1] is not pop[1], "the pool holds copies"


@step(4, "roulette: fitter individuals are picked more, zero fitness doesn't crash")
def _():
    pop = [[i] for i in range(4)]
    counts = [0] * 4
    rng = random.Random(1)
    for _ in range(500):
        for i in ga.roulette(pop, [1, 1, 1, 7], rng)[1]:
            counts[i] += 1
    assert counts[3] > 3 * counts[0], f"fitness 7 vs 1 should be picked far more often: {counts}"
    pool, picked = ga.roulette(pop, [0, 0, 0, 0], random.Random(0))
    assert len(pool) == 4


# ------------------------------------------------------------- Step 5
@step(5, "crossover and crossover_pairs")
def _():
    a, b = ga.crossover([0] * 8, [1] * 8, 3)
    assert a == [0, 0, 0, 1, 1, 1, 1, 1] and b == [1, 1, 1, 0, 0, 0, 0, 0]
    pool = [[0] * 6, [1] * 6, [0] * 6, [1] * 6, [1, 0, 1, 0, 1, 0]]
    kids, used = ga.crossover_pairs(pool, 0.6, random.Random(0), rs=[0.5, 0.7], cuts=[2, 4])
    assert used == [2, None], f"pair 1 crosses (0.5 < 0.6), pair 2 doesn't; got {used}"
    assert kids[0] == [0, 0, 1, 1, 1, 1] and kids[2] == [0] * 6 and kids[2] is not pool[2]
    assert len(kids) == 5 and kids[4] == pool[4], "the odd one out is copied"
    _, used = ga.crossover_pairs([[0] * 8] * 20, 1.0, random.Random(3))
    assert all(1 <= c <= 7 for c in used), "a random cut falls between 1 and length - 1"


# ------------------------------------------------------------- Step 6
@step(6, "mutate")
def _():
    ind = [0, 1, 0, 1, 0, 1]
    keep = ind[:]
    assert ga.mutate(ind, 0.0, random.Random(0)) == ind
    assert ga.mutate(ind, 1.0, random.Random(0)) == [1, 0, 1, 0, 1, 0]
    ga.mutate(ind, 0.5, random.Random(0))
    assert ind == keep, "mutate must not change the list it was given"
    flips = sum(sum(ga.mutate([0] * 100, 0.05, random.Random(s))) for s in range(20))
    assert 60 <= flips <= 140, f"pm = 0.05 on 2,000 bits should flip about 100; got {flips}"


# ------------------------------------------------------------- Step 7
@step(7, "hamming and diversity")
def _():
    assert ga.hamming([0, 0, 1, 1], [0, 1, 1, 0]) == 2
    assert ga.diversity([[0, 1], [0, 1], [0, 1]]) == 0
    assert close(ga.diversity([[0, 0], [1, 1], [0, 1]]), 4 / 3)


# ------------------------------------------------------------- Step 8
@step(8, "run_ga: history and recording")
def _():
    spy = Spy()
    h = ga.run_ga(L1, 10, 0.7, 0.02, 12, random.Random(0), rec=spy)
    assert len(h) == 13 and len(spy.gens) == 13, "generations + 1 entries, generation 0 included"
    for e, (poses, scores, div) in zip(h, spy.gens):
        assert {"gen", "best_pose", "best_score", "mean_score", "diversity"} <= set(e)
        assert len(poses) == 10 and close(e["best_score"], min(scores), 1e-9)
        assert close(e["mean_score"], sum(scores) / 10, 1e-9) and close(e["diversity"], div, 1e-9)


@step(8, "run_ga: without mutation no bit position gains a new value; elitism never loses the best")
def _():
    from armlab.kinematics import LIMITS

    def bits_of(pose):                       # 8-bit decoding of A2 and A3 is one-to-one, so undo it
        out = []
        for j in L1.free:
            lo, hi = LIMITS[j]
            v = round((pose[j] - lo) * 255 / (hi - lo))
            out += [int(c) for c in f"{v:08b}"]
        return out

    spy = Spy()
    ga.run_ga(L1, 8, 0.9, 0.0, 25, random.Random(4), rec=spy)
    allowed = [{bits_of(p)[k] for p in spy.gens[0][0]} for k in range(16)]
    for poses, _, _ in spy.gens:
        for p in poses:
            assert all(b in allowed[k] for k, b in enumerate(bits_of(p))), \
                "with pm = 0, a bit position can only hold values it already had in generation 0 (FNC p. 91)"
    h = ga.run_ga(L2, 12, 0.7, 0.05, 20, random.Random(2), elite=1)
    bests = [e["best_score"] for e in h]
    assert all(b <= a + 1e-12 for a, b in zip(bests, bests[1:])), "with elite = 1 the best never gets worse"


@step(8, "run_ga finds level 1 most of the time")
def _():
    from levels import success
    wins = sum(success(min(ga.run_ga(L1, 30, 0.7, 0.02, 60, random.Random(s), elite=1),
                           key=lambda e: e["best_score"])["best_pose"], L1) for s in range(10))
    assert wins >= 6, f"a working GA (N 30, 60 generations, pm 0.02, elite 1) reaches level 1 in about 9 of 10 runs; yours did {wins}"


# ------------------------------------------------------------- runner
if __name__ == "__main__":
    upto = int(sys.argv[1]) if len(sys.argv) > 1 else 99
    passed = failed = todo = 0
    for n, name, fn in TESTS:
        if n > upto:
            continue
        try:
            fn()
            print(f"  PASS  step {n:>2} · {name}")
            passed += 1
        except NotImplementedError:
            print(f"  TODO  step {n:>2} · {name}")
            todo += 1
        except AssertionError as e:
            print(f"  FAIL  step {n:>2} · {name}\n        {e}")
            failed += 1
        except Exception as e:
            print(f"  ERROR step {n:>2} · {name}\n        {type(e).__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed · {failed} failed · {todo} to do")
