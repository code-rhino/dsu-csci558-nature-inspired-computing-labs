"""Checks that the finished Start Here files still give the numbers quoted in the README.

    python3 labs/00-start-here/finished/test_finished.py
"""
import random
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[3]), str(Path(__file__).resolve().parent)]

import my_first_search as mfs
import rules_of_thumb as rot
from farmlab.flight import fly, route_score


def r1(x):
    return round(x, 1)


def test_one_leg():
    z7 = mfs.farm.zones[6]
    assert mfs.leg_energy(mfs.farm.base, (z7.x, z7.y), 45) == 56.25, "README step 3: 125 m with 45 kg is 56.25 Wh"


def test_route_energy_matches_readme_and_farmlab():
    r = list(range(8))
    assert r1(mfs.route_energy(r)) == 280.3 and r1(mfs.route_energy(r[::-1])) == 268.3, "README step 4"
    rng = random.Random(5)
    for _ in range(50):
        rng.shuffle(r)
        assert abs(mfs.route_energy(r) - route_score(r, mfs.farm)) < 1e-9, "your score must agree with farmlab's"


def test_random_search_matches_readme():
    best, s = mfs.random_search(2000, random.Random(0), mfs.NoRecord())
    assert r1(s) == 168.8, "README step 6 says 168.8 Wh for seed 0"
    wins = sum(mfs.random_search(2000, random.Random(k), mfs.NoRecord())[1] <= 143.4 * 1.01 for k in range(20))
    assert wins == 0, "README step 7 says 0 of 20 with 2,000 tries"


def test_rules_of_thumb_match_readme():
    farm = mfs.farm
    assert r1(route_score(rot.nearest_first(farm), farm)) == 166.7
    assert r1(route_score(rot.heaviest_first(farm), farm)) == 237.4
    shortest = rot.every_order(farm, lambda r: fly(r, farm).distance_m)
    assert r1(route_score(shortest, farm)) == 166.6 and r1(route_score(shortest[::-1], farm)) == 143.4
    assert r1(route_score(rot.every_order(farm, lambda r: route_score(r, farm)), farm)) == 143.4


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
