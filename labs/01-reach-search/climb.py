"""Your file. Search algorithms that find motor angles for the arm.

Work through this lab's README.md one step at a time. Each step replaces one or two
`raise NotImplementedError` below. Check yourself with:

    python3 test_climb.py        # every step
    python3 test_climb.py 4      # steps 1-4 only

Watch any algorithm in 3D with run.py (see README, "Seeing it").

Conventions used everywhere in this file:
  * A pose is a tuple of 6 whole-number angles in degrees: (A1, A2, A3, A4, A5, A6).
  * `free` is a tuple of joint indices the search may change, e.g. (1, 2) = shoulder and elbow.
  * Scores are LOWER-IS-BETTER (a distance). The opposite of most GA fitness functions.
  * Every random number comes from `rng`, a random.Random you are given.
  * `rec` records what the search does for the viewer. Leave it as NULL when you don't care.
"""
import itertools
import math
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)]  # repo root + this lab

from armlab.kinematics import LIMITS, tcp, tool_direction
from armlab.world import collides
from viewer.trace import NULL

L1, L2 = 1.0, 1.0   # upper arm and forearm(+wrist+gripper) lengths, from armlab/arm.json


# ---------------------------------------------------------------- Step 1
def planar_tip(a2, a3):
    """Where the tool tip is, relative to the shoulder, when only A2 and A3 move.

    Returns (x, y): x forward, y up. Angles in degrees.
    A2 = 0 is the upper arm pointing straight forward; A3 = 0 is the forearm in line with it.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 2
def distance(p, q):
    """Straight-line distance between two points of any (equal) dimension."""
    raise NotImplementedError


def reach_score(angles, level):
    """How far the tool tip is from the level's target, in metres. Use tcp() from armlab.kinematics."""
    raise NotImplementedError


# ---------------------------------------------------------------- Step 3
def neighbors(angles, free, step, diagonal=False):
    """Poses one move away from `angles`, keeping every joint inside LIMITS.

    diagonal=False: change ONE free joint by +step or -step.
        Order: for each joint in `free`, +step first, then -step.
    diagonal=True: change ANY combination of free joints by +step, 0 or -step (not all 0).
        Order: itertools.product((step, 0, -step), repeat=len(free)).
    Joints not in `free` never change. Return a list of tuples.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 4
def hill_climb(start, score, nbrs, rec=NULL):
    """Steepest-descent hill-climbing (FNC Alg. 3.1, flipped to minimise).

    score: function pose -> number (lower is better)
    nbrs:  function pose -> list of neighbouring poses
    Each round, score every neighbour; move to the best one if it is STRICTLY better,
    otherwise stop.

    Recording: rec.restart(start, s) once at the beginning, rec.tried(n, s) for every
    neighbour you score, rec.moved(pose, s) each time you move.

    Return (best_pose, best_score, path) where path is [start, ..., best_pose].
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 5
def ik_2link(x, y):
    """The answer key: exact (A2, A3) pairs that put the tip at (x, y) from the shoulder.

    Law of cosines. Return a list of two (a2, a3) tuples in degrees (float):
    first with A3 > 0 (elbow down), then A3 < 0 (elbow up). Return [] if out of reach.
    """
    raise NotImplementedError


def brute_force(score, free, start, step=1):
    """Try every combination of the free joints (within LIMITS) on a `step`-degree grid.

    Joints not in `free` keep their value from `start`.
    Return (best_pose, best_score, number_of_poses_scored).
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 6
def random_pose(level, rng):
    """level.start, with every free joint set to a random whole degree inside its limits."""
    raise NotImplementedError


def iterated_hc(level, score, nbrs, n_restarts, rng, rec=NULL):
    """Iterated hill-climbing (FNC Alg. 3.2): hill_climb from n random poses, keep the best.

    Pass `rec` through to hill_climb so every climb is recorded.
    Return (best_pose, best_score, ends) where ends lists each climb's final pose.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 7
def accept_prob(f_cur, f_new, T):
    """FNC Alg. 3.3, flipped to minimise: P = 1 / (1 + exp((f_new - f_cur) / T)).

    A better (smaller) f_new gives P > 0.5. Must not overflow for tiny T.
    """
    raise NotImplementedError


def random_neighbor(angles, free, max_step, rng):
    """Pick ONE free joint at random (rng.choice) and move it by a random non-zero whole
    number in [-max_step, max_step] (rng.randint), clamped to that joint's LIMITS."""
    raise NotImplementedError


def stochastic_hc(start, score, free, T, max_iter, rng, max_step=5, rec=NULL):
    """Stochastic hill-climbing (FNC Alg. 3.3), `max_iter` tries.

    Each try: random_neighbor -> score it -> move there if rng.random() < accept_prob(...).
    Recording: rec.restart(start, s) once, then rec.tried(n, s, accepted, T) every try.
    Return (best_pose, best_score): the best pose VISITED, not where it ended.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 8
def anneal(start, score, free, T0, beta, max_iter, rng, max_step=10, rec=NULL):
    """Simulated annealing (FNC Alg. 3.4/3.5, minimising).

    Each try: random_neighbor -> if better, move; else move with probability
    exp(-(f_new - f_cur) / T). After every try, T = T * beta.
    Recording: as stochastic_hc.
    Return (best_pose, best_score).
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 9
def penalized(score, level, penalty=10.0):
    """Wrap a score so poses that hit the floor or a box cost `penalty` extra.

    Returns a NEW function pose -> number. Use collides(pose, level) from armlab.world.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 10
def angle_between(u, v):
    """Angle between two 3D vectors, in radians (0 .. pi)."""
    raise NotImplementedError


def pose_score(angles, level, w=0.5):
    """Level 4: distance to the target + w * angle between the gripper and level.down.

    tool_direction(angles) from lab gives the way the gripper points.
    w turns radians into metres: with w = 0.5, being 1 rad off costs the same as 50 cm.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 11 (stretch)
def decode_pose(bits, level, n_bits=8):
    """GA encoding: n_bits per free joint, in level.free order, mapped onto that joint's
    LIMITS (lo + value * (hi - lo) / (2**n_bits - 1)), then rounded to a whole degree.
    Joints not in level.free come from level.start. Return a tuple of 6.
    """
    raise NotImplementedError
