"""Start Here, finished: everything from steps 1-6 of the README in one file.

Compare it with your own labs/00-start-here/my_first_search.py.

    python3 labs/00-start-here/finished/my_first_search.py           # one search, sent to the viewer
    python3 labs/00-start-here/finished/my_first_search.py --test20  # step 6: 20 seeds
"""
import math
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))   # the repo root, so the imports below work

from armlab.kinematics import FOLDED, LIMITS, tcp
from armlab.world import Level, collides
from viewer.trace import Trace

# Step 3: the task
level = Level(1, "My first target", free=(0, 1, 2), start=FOLDED, target=(1.2, 1.0, 0.5), floor=True,
              blurb="Base, shoulder and elbow move. Reach the yellow ball without going through the floor.")


def glide(rec, a, b, steps=30):
    """Step 3: record `steps` poses on a straight line from pose a to pose b."""
    for i in range(1, steps + 1):
        t = i / steps
        pose = tuple(x + (y - x) * t for x, y in zip(a, b))
        rec.moved(pose, score(pose))


# Step 4: the score
def score(pose):
    """How far the gripper is from the target, in metres. Hitting the floor costs 10 extra."""
    d = math.dist(tcp(pose), level.target)
    if collides(pose, level):
        d += 10
    return d


# Step 5: random search
def random_pose(rng):
    pose = list(level.start)
    for j in level.free:
        lo, hi = LIMITS[j]
        pose[j] = rng.randint(lo, hi)
    return tuple(pose)


def random_search(tries, rng, rec):
    best = level.start
    best_score = score(best)
    rec.restart(best, best_score)
    for _ in range(tries):
        pose = random_pose(rng)
        s = score(pose)
        better = s < best_score
        rec.tried(pose, s, accepted=better)
        if better:
            best, best_score = pose, s
    return best, best_score


# Step 6: how good is it, really?
class NoRecord:
    def restart(self, *a): pass
    def tried(self, *a, **k): pass


def test20(tries=2000):
    wins = 0
    for seed in range(20):
        best, s = random_search(tries, random.Random(seed), NoRecord())
        print(f"seed {seed:2}: {s * 100:5.1f} cm")
        wins += s < 0.05
    print(f"within 5 cm: {wins} of 20")


if __name__ == "__main__":
    if "--test20" in sys.argv:
        test20()
    else:
        rec = Trace(level, "random search", lab="00-start-here")
        best, s = random_search(2000, random.Random(0), rec)
        print("best pose:", best)
        print(f"distance: {s * 100:.1f} cm")
        rec.save()
