"""Checks for the shared code (armlab/ and viewer/trace.py), not for any lab.

    python3 tests/test_platform.py      (or: python3 -m pytest tests)

Run these after changing arm.json, kinematics, collisions or the trace format.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from armlab.kinematics import ARM, LIMITS, N_JOINTS, points, tcp, tool_direction  # noqa: E402
from armlab.world import Level, collides  # noqa: E402
from viewer.trace import Trace  # noqa: E402


def close(a, b, tol=1e-9):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def test_arm_definition():
    assert N_JOINTS == 6 and len(LIMITS) == 6
    for j in ARM["joints"]:
        assert j["axis"] in "xyz" and len(j["offset"]) == 3 and j["min"] < j["max"]


def test_zero_pose_points_forward():
    reach = sum(j["offset"][0] for j in ARM["joints"]) + ARM["tool"][0]
    shoulder = sum(j["offset"][1] for j in ARM["joints"])
    assert close(tcp((0,) * 6), (reach, shoulder, 0.0))
    assert close(tool_direction((0,) * 6), (1.0, 0.0, 0.0))


def test_base_turns_about_vertical():
    x, y, z = tcp((90, 0, 0, 0, 0, 0))
    assert abs(x) < 1e-9 and z < -1.9, "A1 = +90 swings the arm from +x to -z (right-hand rule about +y)"


def test_wrist_twist_does_not_move_tip():
    a, b = tcp((10, 20, 30, 0, 0, 0)), tcp((10, 20, 30, 77, 0, 0))
    assert close(a, b), "A4 turns about the forearm's own axis"


def test_points_chain():
    pts = points((0, 45, -30, 0, 0, 0))
    assert len(pts) == N_JOINTS + 1 and close(pts[-1], tcp((0, 45, -30, 0, 0, 0)))


def test_collisions():
    lv = Level(0, "t", free=(1, 2), start=(0,) * 6, target=(1, 1, 0), floor=True,
               boxes=(((0.5, 0.0, -0.25), (0.8, 1.1, 0.25)),))
    assert collides((0, 0, 0, 0, 0, 0), lv), "horizontal arm passes through the post"
    assert not collides((0, 90, -90, 0, 0, 0), lv)
    assert collides((0, -60, 0, 0, 0, 0), lv), "pointing down goes through the floor"


def test_trace_round_trip(tmp=None):
    lv = Level(0, "t", free=(1, 2), start=(0,) * 6, target=(1.0, 1.6, 0.0))
    rec = Trace(lv, "test", lab="_platform_test")
    rec.restart((0,) * 6, 1.0)
    rec.tried((0, 10, 0, 0, 0, 0), 0.9, accepted=True, T=0.5)
    path = rec.save("roundtrip")
    data = json.loads(Path(path).read_text())
    assert data["lab"] == "_platform_test" and len(data["frames"]) == 2
    assert data["frames"][1]["k"] == "move" and data["frames"][1]["T"] == 0.5
    assert data["landscape"]["joints"] == [1, 2], "2-motor levels get a landscape"
    assert close(data["frames"][0]["p"], tcp((0,) * 6), 1e-4)
    Path(path).unlink()
    Path(path).parent.rmdir()


def test_trace_generation_frames():
    lv = Level(0, "t", free=(1, 2), start=(0,) * 6, target=(1.0, 1.6, 0.0))
    rec = Trace(lv, "test", lab="_platform_test")
    rec.generation([(0, 0, 0, 0, 0, 0), (0, 0, 90, 0, 0, 0)], [1.41, 0.0], diversity=3.0)
    f = rec.frames[0]
    assert f["k"] == "gen" and f["a"] == [0, 0, 90, 0, 0, 0] and f["s"] == 0.0, "the best member leads the frame"
    assert len(f["P"]) == 2 and f["S"] == [1.41, 0.0] and abs(f["mean"] - 0.705) < 1e-9 and f["d"] == 3.0


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_")]
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
