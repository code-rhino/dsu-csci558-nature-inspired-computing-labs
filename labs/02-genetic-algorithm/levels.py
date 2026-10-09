"""Lab 02's levels and the score. Provided: you wrote a score like this in lab 01.

Each level is a Level from armlab.world. score() is lower-is-better (metres, plus penalties);
your fitness() in ga.py turns it into the higher-is-better number a GA needs.
"""
import math

from armlab.kinematics import HOME, tcp, tool_direction
from armlab.world import Level, collides

LEVELS = {
    1: Level(
        1, "Reach · 2 motors", free=(1, 2), start=(0, 0, 0, 0, 0, 0), target=(1.0, 1.6, 0.0),
        blurb="Lab 01's first level: 16 bits of DNA. The landscape panel shows the whole population."),
    2: Level(
        2, "Around the post · 3 motors", free=(0, 1, 2), start=(0, 60, 30, 0, 0, 0), target=(1.0, 1.6, 0.0),
        floor=True, boxes=(((0.5, 0.0, -0.25), (0.8, 1.1, 0.25)),),
        blurb="24 bits of DNA. Lab 01's hardest 3-motor level, with its backwards-reach trap."),
    3: Level(
        3, "Pick from above · 6 motors", free=(0, 1, 2, 3, 4, 5), start=HOME, target=(1.1, 0.25, 0.4),
        floor=True, down=(0.0, -1.0, 0.0), boxes=(((0.95, 0.0, 0.25), (1.25, 0.12, 0.55)),),
        blurb="48 bits of DNA: all six motors, gripper pointing straight down."),
}

PENALTY = 10.0   # added for hitting the floor or a box
W = 0.5          # level 3: metres per radian of gripper error


def get_level(n):
    return LEVELS[n]


def score(pose, level):
    """Lower is better: metres from the target (+ W x gripper angle error on level 3) (+ PENALTY if colliding)."""
    s = math.dist(tcp(pose), level.target)
    if level.down:
        cos = sum(a * b for a, b in zip(tool_direction(pose), level.down))
        s += W * math.acos(max(-1.0, min(1.0, cos)))
    if collides(pose, level):
        s += PENALTY
    return s


def success(pose, level):
    """Within 5 cm, not colliding, and (level 3) within 10 degrees of straight down."""
    if collides(pose, level) or math.dist(tcp(pose), level.target) >= 0.05:
        return False
    if level.down:
        cos = sum(a * b for a, b in zip(tool_direction(pose), level.down))
        return math.degrees(math.acos(max(-1.0, min(1.0, cos)))) < 10
    return True
