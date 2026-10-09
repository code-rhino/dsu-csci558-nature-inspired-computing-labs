"""What a task looks like (a Level) and the collision check. Shared by every lab.

A Level says which motors may move (`free`, as joint indices 0..5), where the
target is, what is in the way, and (optionally) which way the gripper must point.
Labs define their own levels in their own folder; see labs/01-reach-search/levels.py.
"""
from dataclasses import dataclass, field

from .kinematics import FOLDED, HOME, points  # noqa: F401  (re-exported for levels.py files)

LINK_RADIUS = 0.07   # how thick the arm is, for collisions (metres)


@dataclass(frozen=True)
class Level:
    number: int                     # shown in the viewer as "Level n"
    title: str
    free: tuple                     # joint indices the search may change
    start: tuple                    # the pose every hand example starts from
    target: tuple                   # (x, y, z) the tool tip should reach
    floor: bool = False             # True: the arm may not go through the floor
    boxes: tuple = ()               # obstacles: ((xmin, ymin, zmin), (xmax, ymax, zmax))
    down: tuple = None              # level 4: the direction the gripper must point
    blurb: str = ""
    extra: dict = field(default_factory=dict)


def _seg_point_hits(p, q, level, n):
    lo_y = LINK_RADIUS if level.floor else -1e9
    for i in range(n + 1):
        t = i / n
        x, y, z = (p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t, p[2] + (q[2] - p[2]) * t)
        if y < lo_y:
            return True
        for (x0, y0, z0), (x1, y1, z1) in level.boxes:
            r = LINK_RADIUS
            if x0 - r <= x <= x1 + r and y0 - r <= y <= y1 + r and z0 - r <= z <= z1 + r:
                return True
    return False


def collides(angles, level):
    """True if any part of the arm from the shoulder outwards hits the floor or a box.

    The last 5 cm before the tool tip are ignored, so the gripper may touch what it picks up.
    """
    pts = points(angles)[1:]            # shoulder .. tool tip
    tip, before = pts[-1], pts[-2]
    d = sum((a - b) ** 2 for a, b in zip(tip, before)) ** 0.5
    if d > 0.05:                         # stop short of the fingertips
        k = (d - 0.05) / d
        pts[-1] = tuple(b + (a - b) * k for a, b in zip(tip, before))
    for p, q in zip(pts, pts[1:]):
        seg = sum((a - b) ** 2 for a, b in zip(p, q)) ** 0.5
        if _seg_point_hits(p, q, level, max(2, int(seg / 0.04))):
            return True
    return False
