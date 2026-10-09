"""This lab's tasks. Copy, rename, and change freely. See armlab/world.py for every field."""
from armlab.world import FOLDED, Level

LEVELS = {
    1: Level(
        1, "Reach · 3 motors", free=(0, 1, 2), start=FOLDED,
        target=(1.2, 1.0, 0.5), floor=True,
        blurb="Template level: base, shoulder and elbow move; don't go through the floor."),
}


def get_level(n):
    return LEVELS[n]
