"""Checks for the shared code (farmlab/ and viewer/trace.py), not for any lab.

    python3 tests/test_platform.py      (or: python3 -m pytest tests)

Run these after changing drone.json, the farms, the energy model or the trace format.
"""
import itertools
import json
import math
import random
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import viewer.trace as trace  # noqa: E402
from farmlab.farms import BEST_KNOWN, FARMS, get_farm  # noqa: E402
from farmlab.flight import fly, leg_energy, plan_trips, route_score, trip_energy  # noqa: E402
from farmlab.world import DRONE, blocked, flight_distance, inside_obstacle, path  # noqa: E402


def close(a, b, tol=1e-9):
    return abs(a - b) <= tol


def test_drone_numbers_are_hand_friendly():
    assert DRONE["wh_per_kg_m"] == 0.01 and DRONE["empty_mass_kg"] == 25 and DRONE["kg_per_l"] == 1
    assert DRONE["spray_alt_m"] < DRONE["cruise_alt_m"]


def test_farms_are_well_formed():
    for n, farm in FARMS.items():
        assert farm.number == n
        assert all(z.need_l <= farm.tank for z in farm.zones), "every zone must fit in one tank"
        assert not inside_obstacle(farm.base, farm), f"farm {n}: the base is inside an obstacle"
        for z in farm.zones:
            assert not inside_obstacle((z.x, z.y), farm), f"farm {n}: {z.name} is inside an obstacle"
            assert trip_energy([farm.zones.index(z)], farm) <= farm.battery, f"farm {n}: {z.name} is out of battery range"
    assert sum(z.need_l for z in get_farm(1).zones) == get_farm(1).tank, "farm 1 is exactly one tank"


def test_one_leg_by_hand():
    farm = get_farm(1)
    z7 = farm.zones[6]
    assert (z7.x - farm.base[0], z7.y - farm.base[1]) == (125.0, 0.0), "Z7 is 125 m due east of the base"
    assert close(leg_energy(-1, 6, 45.0, farm), 0.01 * 45 * 125)


def test_route_energy_by_hand():
    farm = get_farm(1)
    route = list(range(8))
    load, here, wh = 20.0, farm.base, 0.0
    for z in route:
        p = (farm.zones[z].x, farm.zones[z].y)
        wh += 0.01 * (25 + load) * math.dist(here, p)
        load -= farm.zones[z].need_l
        here = p
    wh += 0.01 * 25 * math.dist(here, farm.base)
    assert close(route_score(route, farm), wh, 1e-9)


def test_weight_makes_direction_matter():
    farm = get_farm(1)
    r = [7, 4, 2, 0, 6, 3, 5, 1]
    assert close(fly(r, farm).distance_m, fly(r[::-1], farm).distance_m, 1e-9), "same loop, same metres"
    assert route_score(r, farm) < route_score(r[::-1], farm) - 20, "...but not the same energy"


def test_fast_score_matches_full_flight():
    rng = random.Random(0)
    for farm in FARMS.values():
        for _ in range(30):
            r = list(range(len(farm.zones)))
            rng.shuffle(r)
            f = fly(r, farm)
            assert close(route_score(r, farm), f.score, 1e-6)
            assert close(sum(leg["wh"] for leg in f.legs), f.energy_wh, 1e-6)
            assert [z for t in f.trips for z in t] == r, "trips keep the route's order"


def test_trips_respect_tank_and_battery():
    rng = random.Random(1)
    for farm in (get_farm(2), get_farm(4)):
        for _ in range(30):
            r = list(range(len(farm.zones)))
            rng.shuffle(r)
            for t in plan_trips(r, farm):
                assert sum(farm.zones[z].need_l for z in t) <= farm.tank + 1e-9
                assert trip_energy(t, farm) <= farm.battery + 1e-9
    assert len(plan_trips(list(range(14)), get_farm(2))) >= 3, "59 L needs at least 3 tank loads"


def test_paths_go_round_obstacles():
    farm = get_farm(3)
    detours = 0
    for i in range(-1, len(farm.zones)):
        for j in range(-1, len(farm.zones)):
            if i == j:
                continue
            p = path(i, j, farm)
            assert all(not blocked(a, b, farm) for a, b in zip(p, p[1:])), f"path {i}->{j} cuts an obstacle"
            straight = math.dist(farm.spot(i), farm.spot(j))
            assert flight_distance(i, j, farm) >= straight - 1e-9
            detours += len(p) > 2
    assert detours > 20, "farm 3's obstacles should force plenty of detours"
    assert all(len(path(i, j, get_farm(2))) == 2 for i in range(-1, 14) for j in range(-1, 14) if i != j), "farm 2 is open"


def test_wind_is_one_way():
    calm, windy = get_farm(3), get_farm(4)
    assert close(leg_energy(-1, 7, 30, calm), leg_energy(7, -1, 30, calm), 1e-9), "no wind: there and back cost the same"
    # the wind blows from the north-east, so flying north-east (out to Z8) is into it
    assert leg_energy(-1, 7, 30, windy) > leg_energy(7, -1, 30, windy)


def test_farm1_answer_key():
    farm = get_farm(1)
    best = min(route_score(r, farm) for r in itertools.permutations(range(8)))
    assert round(best, 1) == BEST_KNOWN[1]


def test_trace_round_trip():
    farm = get_farm(3)
    old = trace.ROOT
    with tempfile.TemporaryDirectory() as tmp:
        trace.ROOT = Path(tmp)               # never touch the real traces/latest.json the viewer is watching
        try:
            rec = trace.Trace(farm, "test", lab="_platform_test")
            r = list(range(14))
            rec.restart(r, route_score(r, farm))
            rec.tried(r[::-1], route_score(r[::-1], farm), accepted=True, T=0.5)
            rec.moved(r, route_score(r, farm))
            out = rec.save("roundtrip")
            data = json.loads(Path(out).read_text())
            assert (Path(tmp) / "traces" / "latest.json").exists()
        finally:
            trace.ROOT = old
    assert data["lab"] == "_platform_test" and len(data["frames"]) == 3 and data["evaluations"] == 2, \
        "moved() re-records a route already scored, so it isn't an evaluation"
    assert data["frames"][1]["k"] == "move" and data["frames"][1]["T"] == 0.5
    assert data["frames"][0]["t"] == plan_trips(r, farm)
    assert data["farm"]["best_known_wh"] == BEST_KNOWN[3] and data["farm"]["paths"], "detours go to the viewer"
    assert close(data["best"]["energy_wh"], route_score(data["best"]["route"], farm), 1e-3)


def test_trace_generation_frames():
    farm = get_farm(1)
    rec = trace.Trace(farm, "test", lab="_platform_test")
    a, b = list(range(8)), [7, 4, 2, 0, 6, 3, 5, 1]
    rec.generation([a, b], [route_score(a, farm), route_score(b, farm)], diversity=3.0)
    f = rec.frames[0]
    assert f["k"] == "gen" and f["o"] == b and len(f["P"]) == 2 and len(f["PT"]) == 2 and f["d"] == 3.0
    assert rec.evaluations == 2


if __name__ == "__main__":
    tests = [(n, f) for n, f in globals().items() if n.startswith("test_")]
    bad = 0
    for n, f in tests:
        try:
            f()
            print(f"  PASS  {n}")
        except Exception as e:
            bad += 1
            print(f"  FAIL  {n}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - bad} passed · {bad} failed")
    sys.exit(1 if bad else 0)
