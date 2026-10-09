"""Forward kinematics: six joint angles -> where every part of the arm is.

Shared by every lab. `tcp(angles)` is the function labs use most.
Pure standard library: a frame is (R, p), a 3x3 rotation as nested lists and a position.
"""
import json
import math
from pathlib import Path

ARM = json.loads((Path(__file__).resolve().parent / "arm.json").read_text())
JOINTS = ARM["joints"]
N_JOINTS = len(JOINTS)
LIMITS = [(j["min"], j["max"]) for j in JOINTS]
NAMES = [j["name"] for j in JOINTS]
HOME = tuple(ARM["home"])                  # folded rest pose
FOLDED = HOME[:3] + (0, 0, 0)              # same, with the wrist straight: for levels that keep A4-A6 at 0


def _rot(axis, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    if axis == "x":
        return [[1, 0, 0], [0, c, -s], [0, s, c]]
    if axis == "y":
        return [[c, 0, s], [0, 1, 0], [-s, 0, c]]
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def _mm(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def _mv(A, v):
    return [sum(A[i][k] * v[k] for k in range(3)) for i in range(3)]


def frames(angles):
    """Every joint's world frame, then the tool tip's. Returns a list of (R, p)."""
    R = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    p = [0.0, 0.0, 0.0]
    out = []
    for joint, a in zip(JOINTS, angles):
        p = [pi + oi for pi, oi in zip(p, _mv(R, joint["offset"]))]
        R = _mm(R, _rot(joint["axis"], a))
        out.append((R, p))
    p = [pi + oi for pi, oi in zip(p, _mv(R, ARM["tool"]))]
    out.append((R, p))
    return out


def points(angles):
    """World positions of A1..A6 and the tool tip (7 points), base to tip."""
    return [tuple(p) for _, p in frames(angles)]


def tcp(angles):
    """The tool centre point: the spot between the gripper fingers, as (x, y, z)."""
    return tuple(frames(angles)[-1][1])


def tool_direction(angles):
    """Unit vector the gripper points along (the tool's +x axis in the world)."""
    R = frames(angles)[-1][0]
    return (R[0][0], R[1][0], R[2][0])
