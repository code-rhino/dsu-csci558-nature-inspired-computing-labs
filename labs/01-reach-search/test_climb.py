"""Checks for climb.py. Run:  python3 test_climb.py   or   python3 test_climb.py 4  (steps 1-4 only)."""
import math
import random
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)]  # repo root + this lab

import climb
from armlab.kinematics import LIMITS, tcp
from levels import get_level

TESTS = []
L1, L3, L4 = get_level(1), get_level(3), get_level(4)


def step(n, name):
    def deco(fn):
        TESTS.append((n, name, fn))
        return fn
    return deco


def close(a, b, tol=1e-3):
    return abs(a - b) <= tol


class Spy:
    """A stand-in recorder that remembers what it was told."""

    def __init__(self):
        self.calls = []

    def restart(self, a, s, msg=None):
        self.calls.append(("restart", tuple(a), s))

    def tried(self, a, s, accepted=False, T=None):
        self.calls.append(("move" if accepted else "try", tuple(a), s))

    def moved(self, a, s, T=None):
        self.calls.append(("move", tuple(a), s))

    def kinds(self, k):
        return [c for c in self.calls if c[0] == k]


def l1_score(a):
    return climb.reach_score(a, L1)


# ------------------------------------------------------------- Step 1
@step(1, "planar_tip: the hand-worked values")
def _():
    for (a2, a3), (x, y) in [((0, 0), (2, 0)), ((0, 90), (1, 1)), ((90, -90), (1, 1)), ((90, 0), (0, 2))]:
        got = climb.planar_tip(a2, a3)
        assert close(got[0], x) and close(got[1], y), f"planar_tip({a2}, {a3}) should be ({x}, {y}), got {got}"


@step(1, "planar_tip agrees with the full 3D arm")
def _():
    rng = random.Random(1)
    for _ in range(50):
        a2, a3 = rng.randint(-90, 180), rng.randint(-150, 150)
        x, y, z = tcp((0, a2, a3, 0, 0, 0))
        px, py = climb.planar_tip(a2, a3)
        assert close(px, x) and close(py, y - 0.6) and close(z, 0), \
            f"A2={a2}, A3={a3}: lab says ({x:.3f}, {y - 0.6:.3f}) from the shoulder, you say ({px:.3f}, {py:.3f})"


# ------------------------------------------------------------- Step 2
@step(2, "distance and reach_score")
def _():
    assert close(climb.distance((0, 0, 0), (3, 4, 0)), 5)
    assert close(climb.distance((1, 1), (4, 5)), 5)
    assert close(climb.reach_score(L1.start, L1), math.sqrt(2)), "level 1 starts 1.414 m from the target"
    assert close(climb.reach_score((0, 0, 90, 0, 0, 0), L1), 0), "(A2, A3) = (0, 90) is exactly on the target"


# ------------------------------------------------------------- Step 3
@step(3, "neighbors: four moves, in order")
def _():
    got = climb.neighbors((0, 0, 0, 0, 0, 0), (1, 2), 10)
    want = [(0, 10, 0, 0, 0, 0), (0, -10, 0, 0, 0, 0), (0, 0, 10, 0, 0, 0), (0, 0, -10, 0, 0, 0)]
    assert list(map(tuple, got)) == want, f"expected {want}, got {got}"


@step(3, "neighbors: limits, diagonal moves, fixed joints")
def _():
    got = climb.neighbors((0, 180, 0, 0, 0, 0), (1, 2), 5)
    assert (0, 185, 0, 0, 0, 0) not in got and len(got) == 3, "A2 can't go past 180"
    assert len(climb.neighbors((0, 0, 0, 0, 0, 0), (1, 2), 10, diagonal=True)) == 8
    assert len(climb.neighbors((0, 0, 0, 0, 0, 0), (0, 1, 2), 10, diagonal=True)) == 26
    for n in climb.neighbors((5, 0, 0, 7, 8, 9), (1, 2), 1, diagonal=True):
        assert n[0] == 5 and n[3:] == (7, 8, 9), "joints not in `free` must not change"


# ------------------------------------------------------------- Step 4
@step(4, "hill_climb: the 10-degree hand walk gets stuck at (20, 60)")
def _():
    best, s, path = climb.hill_climb(L1.start, l1_score, lambda a: climb.neighbors(a, (1, 2), 10))
    assert tuple(best) == (0, 20, 60, 0, 0, 0), f"expected to stop at (0, 20, 60, 0, 0, 0), stopped at {best}"
    assert close(s, 0.3459), f"score there is 0.346, got {s}"
    assert len(path) - 1 == 12, f"12 moves in the hand walk, got {len(path) - 1}"
    assert all(l1_score(b) < l1_score(a) for a, b in zip(path, path[1:])), "every move must be strictly better"


@step(4, "hill_climb: diagonal moves reach (0, 90) in 9")
def _():
    best, s, path = climb.hill_climb(L1.start, l1_score, lambda a: climb.neighbors(a, (1, 2), 10, True))
    assert tuple(best) == (0, 0, 90, 0, 0, 0) and close(s, 0), f"expected (0, 0, 90, ...) at 0 m, got {best} at {s}"
    assert len(path) - 1 == 9, f"9 moves, got {len(path) - 1}"


@step(4, "hill_climb: records for the viewer")
def _():
    spy = Spy()
    best, s, path = climb.hill_climb(L1.start, l1_score, lambda a: climb.neighbors(a, (1, 2), 10), spy)
    assert len(spy.kinds("restart")) == 1, "call rec.restart(start, score) once"
    assert len(spy.kinds("move")) == len(path) - 1, "call rec.moved(pose, score) once per move"
    assert len(spy.kinds("try")) == 4 * len(path), "call rec.tried(pose, score) for every neighbour scored"


# ------------------------------------------------------------- Step 5
@step(5, "ik_2link: the law of cosines")
def _():
    sol = climb.ik_2link(1, 1)
    assert len(sol) == 2, "two answers: elbow down and elbow up"
    assert close(sol[0][0], 0) and close(sol[0][1], 90), f"elbow down is (0, 90), got {sol[0]}"
    assert close(sol[1][0], 90) and close(sol[1][1], -90), f"elbow up is (90, -90), got {sol[1]}"
    assert climb.ik_2link(3, 0) == [], "3 m away is out of reach"
    for a2, a3 in climb.ik_2link(0.7, 1.3):
        x, y = climb.planar_tip(a2, a3)
        assert close(x, 0.7) and close(y, 1.3), "each answer must put the tip on the point"


@step(5, "brute_force: level 1 answer key")
def _():
    best, s, n = climb.brute_force(l1_score, (1, 2), L1.start, 1)
    assert n == 271 * 301, f"A2 has 271 values and A3 301, so {271 * 301} poses; you scored {n}"
    assert close(s, 0) and tuple(best) in {(0, 0, 90, 0, 0, 0), (0, 90, -90, 0, 0, 0)}


# ------------------------------------------------------------- Step 6
@step(6, "random_pose")
def _():
    rng = random.Random(0)
    for _ in range(200):
        p = climb.random_pose(L3, rng)
        assert len(p) == 6 and p[3:] == L3.start[3:]
        assert all(LIMITS[j][0] <= p[j] <= LIMITS[j][1] for j in L3.free)
        assert all(isinstance(v, int) for v in p), "whole degrees"


@step(6, "iterated_hc finds level 1, and repeats with the same seed")
def _():
    nb = lambda a: climb.neighbors(a, (1, 2), 2)
    for seed in range(8):
        best, s, ends = climb.iterated_hc(L1, l1_score, nb, 8, random.Random(seed))
        assert len(ends) == 8 and close(s, min(l1_score(e) for e in ends), 1e-9)
        assert s < 0.05, f"8 restarts should get within 5 cm (seed {seed} got {s:.3f})"
    a = climb.iterated_hc(L1, l1_score, nb, 3, random.Random(42))
    b = climb.iterated_hc(L1, l1_score, nb, 3, random.Random(42))
    assert a == b, "use only the rng you are given"


# ------------------------------------------------------------- Step 7
@step(7, "accept_prob (minimising)")
def _():
    assert close(climb.accept_prob(0.5, 0.5, 0.1), 0.5)
    assert close(climb.accept_prob(0.6, 0.5, 0.1), 0.7311), "a better (smaller) score should be likely"
    assert close(climb.accept_prob(0.5, 0.6, 0.1), 0.2689)
    assert climb.accept_prob(0.0, 0.9, 1e-6) < 1e-9, "should be ~0 without an OverflowError"
    assert climb.accept_prob(0.9, 0.0, 1e-6) > 0.999


@step(7, "random_neighbor")
def _():
    rng = random.Random(3)
    for _ in range(300):
        a = (0, 0, 0, 0, 0, 0)
        n = climb.random_neighbor(a, (1, 2), 4, rng)
        diff = [j for j in range(6) if n[j] != a[j]]
        assert len(diff) <= 1 and set(diff) <= {1, 2}, "change exactly one free joint"
        assert all(abs(n[j] - a[j]) <= 4 for j in range(6))
    n = climb.random_neighbor((0, 180, 0, 0, 0, 0), (1,), 5, random.Random(0))
    assert n[1] <= 180, "clamp to the limits"


@step(7, "stochastic_hc: tiny T climbs, huge T wanders")
def _():
    spy = Spy()
    best, s = climb.stochastic_hc(L1.start, l1_score, (1, 2), 1e-4, 1500, random.Random(1), 5, spy)
    assert s < 0.1, f"with tiny T it should behave like hill-climbing and get close, got {s:.3f}"
    assert close(s, min(c[2] for c in spy.calls if c[0] in ("move", "restart")), 1e-9), "return the best VISITED"
    spy = Spy()
    climb.stochastic_hc(L1.start, l1_score, (1, 2), 100.0, 1000, random.Random(2), 5, spy)
    moves = len(spy.kinds("move"))
    assert 350 <= moves <= 650, f"with huge T about half the tries are accepted, got {moves}/1000"


# ------------------------------------------------------------- Step 8
@step(8, "anneal: cools down, keeps the best")
def _():
    spy = Spy()
    best, s = climb.anneal(L1.start, l1_score, (1, 2), 1e-9, 0.99, 400, random.Random(0), 10, spy)
    acc = [c[2] for c in spy.calls if c[0] in ("move", "restart")]
    assert all(b <= a + 1e-9 for a, b in zip(acc, acc[1:])), "at T ~ 0 a worse move is never accepted"
    wins = 0
    for seed in range(8):
        rng = random.Random(seed)
        _, s = climb.anneal(climb.random_pose(L1, rng), l1_score, (1, 2), 0.5, 0.998, 3000, rng, 10)
        wins += s < 0.05
    assert wins >= 6, f"annealing should solve level 1 most of the time; got {wins}/8"


# ------------------------------------------------------------- Step 9
@step(9, "penalized")
def _():
    sc = climb.penalized(lambda a: climb.reach_score(a, L3), L3, 10.0)
    assert close(sc((0, 0, 90, 0, 0, 0)), 10.0), "elbow down goes through the post: 0 m + 10"
    assert close(sc((0, 90, -90, 0, 0, 0)), 0.0), "elbow up clears it"


# ------------------------------------------------------------- Step 10
@step(10, "angle_between and pose_score")
def _():
    assert close(climb.angle_between((1, 0, 0), (0, 1, 0)), math.pi / 2)
    assert close(climb.angle_between((0, 2, 0), (0, 5, 0)), 0)
    assert close(climb.angle_between((1, 0, 0), (-3, 0, 0)), math.pi)
    down = (0, 0, 0, 0, -90, 0)                    # wrist bent straight down
    assert close(climb.pose_score(down, L4, 0.5), climb.reach_score(down, L4)), "pointing down costs nothing extra"
    flat = (0, 0, 0, 0, 0, 0)
    assert close(climb.pose_score(flat, L4, 0.5) - climb.reach_score(flat, L4), 0.5 * math.pi / 2)


# ------------------------------------------------------------- Step 11
@step(11, "decode_pose")
def _():
    assert climb.decode_pose([0] * 16, L1) == (0, -90, -150, 0, 0, 0)
    assert climb.decode_pose([1] * 16, L1) == (0, 180, 150, 0, 0, 0)
    assert climb.decode_pose([1, 0, 0, 0, 0, 0, 0, 0] + [0] * 8, L1)[1] == round(-90 + 128 * 270 / 255)


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
