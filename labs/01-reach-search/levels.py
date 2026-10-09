"""The four levels of lab 01. Each one is a Level from armlab.world."""
from armlab.world import FOLDED, HOME, Level

# Level 1 starts straight out at (0, 0) because the hand walk-through starts there.
# Level 3 starts raised: folded up, the gripper would sit inside the post.
# The others start folded up, the arm's rest pose.

LEVELS = {
    1: Level(
        1, "Reach · 2 motors", free=(1, 2), start=(0, 0, 0, 0, 0, 0),
        target=(1.0, 1.6, 0.0),
        blurb="Shoulder and elbow only. Same problem as the 2-link arm worked by hand: "
              "target is (1, 1) from the shoulder, both links are 1 m."),
    2: Level(
        2, "Turn and reach · 3 motors", free=(0, 1, 2), start=FOLDED,
        target=(0.8, 1.2, -0.9), floor=True,
        blurb="The base can turn now, so the target can be anywhere around the arm."),
    3: Level(
        3, "Around the post · 3 motors", free=(0, 1, 2), start=(0, 60, 30, 0, 0, 0),
        target=(1.0, 1.6, 0.0), floor=True,
        boxes=(((0.5, 0.0, -0.25), (0.8, 1.1, 0.25)),),
        blurb="Level 1's target, but a post blocks the elbow-down answer. "
              "The arm has to go up and over."),
    4: Level(
        4, "Pick from above · 6 motors", free=(0, 1, 2, 3, 4, 5), start=HOME,
        target=(1.1, 0.25, 0.4), floor=True, down=(0.0, -1.0, 0.0),
        boxes=(((0.95, 0.0, 0.25), (1.25, 0.12, 0.55)),),
        blurb="All six motors. Reach the part on the crate with the gripper pointing "
              "straight down, without touching the crate."),
}


def get_level(n):
    return LEVELS[n]


def get_level(n):
    return LEVELS[n]
