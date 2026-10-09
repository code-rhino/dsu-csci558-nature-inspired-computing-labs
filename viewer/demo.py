"""Check the viewer works. Needs no lab code.

    python3 -m viewer        # in one terminal
    python3 -m viewer.demo   # in another

The arm waves through each motor in turn, then shows two poses that reach the target.
"""
import math

from armlab.kinematics import HOME, tcp
from armlab.world import Level
from viewer.trace import Trace

level = Level(0, "Viewer demo", free=(0, 1, 2, 3, 4, 5), start=(0, 0, 0, 0, 0, 0), target=(1.0, 1.6, 0.0),
              blurb="No lab code involved: if the arm moves, the viewer works.")
rec = Trace(level, "demo", lab="demo", note="each motor in turn, then two poses that reach the target")


def score(a):
    return math.dist(tcp(a), level.target)


def go(a, b, n=30):
    for i in range(1, n + 1):
        t = i / n
        t = t * t * (3 - 2 * t)
        pose = tuple(round(x + (y - x) * t, 2) for x, y in zip(a, b))
        rec.moved(pose, score(pose))
    return b


pose = (0, 0, 0, 0, 0, 0)
rec.restart(pose, score(pose), "all motors at 0: the arm points straight forward")
pose = go(pose, HOME)
for j, (lo, hi) in enumerate([(-60, 60), (40, 100), (-90, 0), (-90, 90), (-80, 40), (-90, 90)]):
    a = list(pose); a[j] = lo
    b = list(pose); b[j] = hi
    go(pose, tuple(a), 20)
    rec.note_text(f"A{j + 1} moving")
    go(tuple(a), tuple(b), 30)
    pose = go(tuple(b), pose, 20)
pose = go(pose, (0, 0, 90, 0, 0, 0), 40)
rec.note_text("elbow down: (A2, A3) = (0, 90) reaches the target")
pose = go(pose, (0, 90, -90, 0, 0, 0), 50)
rec.note_text("elbow up: (A2, A3) = (90, -90) reaches it too")
rec.save("demo", (0, 90, -90, 0, 0, 0))
