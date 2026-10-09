"""Checks that the finished Start Here files still work (they're the reference for the README).

    python3 labs/00-start-here/finished/test_finished.py
"""
import math
import random
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[3]), str(Path(__file__).resolve().parent)]

import follow_the_slope as fts
import my_first_search as mfs
from armlab.kinematics import FOLDED, tcp


def test_where_is_the_gripper():
    assert all(abs(a - b) < 1e-9 for a, b in zip(tcp((0, 0, 0, 0, 0, 0)), (2.0, 0.6, 0.0)))
    assert all(abs(a - b) < 1e-9 for a, b in zip(tcp((0, 90, 0, 0, 0, 0)), (0.0, 2.6, 0.0)))
    assert all(abs(a - b) < 1e-9 for a, b in zip(tcp((90, 0, 0, 0, 0, 0)), (0.0, 0.6, -2.0)))


def test_score_from_rest():
    assert abs(mfs.score(FOLDED) - 0.842) < 1e-3, "README step 4 says 84.2 cm"


def test_random_search_matches_readme():
    best, s = mfs.random_search(2000, random.Random(0), mfs.NoRecord())
    assert abs(s - 0.268) < 1e-3, "README step 5 says 26.8 cm for seed 0"
    wins = sum(mfs.random_search(2000, random.Random(k), mfs.NoRecord())[1] < 0.05 for k in range(20))
    assert wins == 0, "README step 6 says 0 of 20"


def test_slope_points_downhill():
    lv = fts.LEVELS[1]
    g = fts.slope(lv.start, lv)
    stepped = tuple(a - gi for a, gi in zip(lv.start, g))
    assert fts.error(stepped, lv) < fts.error(lv.start, lv)


def test_gradient_descent_matches_readme():
    best, s, e = fts.gradient_descent(fts.LEVELS[1].start, fts.LEVELS[1])
    assert s < 0.002 and e == 148, "README bonus says about 0.1 cm in 148 evaluations"
    best, s, e = fts.gradient_descent(fts.LEVELS[2].start, fts.LEVELS[2])
    assert s > 0.5, "level 2: stuck against the post"
    best, s, e = fts.with_restarts(fts.LEVELS[2], 5, random.Random(3))
    assert s < 0.01


if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_")]
    bad = 0
    for n, f in tests:
        try:
            f()
            print(f"  PASS  {n}")
        except AssertionError as e:
            bad += 1
            print(f"  FAIL  {n}: {e}")
    print(f"\n{len(tests) - bad} passed · {bad} failed")
    sys.exit(1 if bad else 0)
