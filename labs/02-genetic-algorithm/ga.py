"""Your file. A genetic algorithm that evolves arm poses.

Work through this lab's README.md one step at a time. Each step replaces one or two
`raise NotImplementedError` below. Check yourself with:

    python3 test_ga.py        # every step
    python3 test_ga.py 4      # steps 1-4 only

Conventions:
  * An individual (a "chromosome") is a list of 0s and 1s: n_bits bits per free motor,
    in level.free order, most significant bit first.
  * score(pose, level) from levels.py is LOWER-is-better. A GA needs HIGHER-is-better,
    which is what fitness() is for.
  * Every random number comes from `rng`, a random.Random you are given.
  * `rec` records each generation for the viewer. Leave it as NULL when you don't care.
"""
import sys
from pathlib import Path
sys.path[:0] = [str(Path(__file__).resolve().parents[2]), str(Path(__file__).resolve().parent)]  # repo root + this lab

from armlab.kinematics import LIMITS
from levels import score
from viewer.trace import NULL


# ---------------------------------------------------------------- Step 1
def decode(bits, level, n_bits=8):
    """Chromosome -> pose. Each n_bits chunk is a whole number v (0 .. 2**n_bits - 1), mapped
    onto its motor's LIMITS (lo, hi) as lo + v * (hi - lo) / (2**n_bits - 1), rounded to a
    whole degree (FNC p. 99). Motors not in level.free keep their value from level.start.
    Return a tuple of 6.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 2
def fitness(pose, level):
    """Higher is better: 1 / (1 + score(pose, level)). A perfect pose scores 0, so fitness 1."""
    raise NotImplementedError


# ---------------------------------------------------------------- Step 3
def random_population(N, length, rng):
    """N random chromosomes, each `length` bits (rng.randint(0, 1) per bit)."""
    raise NotImplementedError


# ---------------------------------------------------------------- Step 4
def roulette(pop, fits, rng, spins=None):
    """Roulette-wheel selection (FNC p. 89): spin len(pop) times.

    Each individual owns a slice of [0, 1) proportional to its fitness, in order.
    A spin s (rng.random(), or spins[k] if given) picks the first individual whose slice
    ends AFTER s. If every fitness is 0, pick int(s * len(pop)).
    Return (pool, picked): COPIES of the chosen chromosomes, and their indices.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 5
def crossover(a, b, cut):
    """Single-point crossover (FNC p. 90): swap everything from position `cut` on.
    Return the two children."""
    raise NotImplementedError


def crossover_pairs(pool, pc, rng, rs=None, cuts=None):
    """Pair up (0,1), (2,3), ... For pair k draw r (rng.random(), or rs[k]); if r < pc, cut at
    rng.randint(1, length - 1) (or cuts[k]) and cross, otherwise copy both unchanged.
    An odd one out at the end is copied. Return (children, used) where used[k] is the cut or None.
    """
    raise NotImplementedError


# ---------------------------------------------------------------- Step 6
def mutate(ind, pm, rng):
    """Bit-flip mutation (FNC p. 91): flip each bit when rng.random() < pm.
    Return a NEW list; never change `ind`."""
    raise NotImplementedError


# ---------------------------------------------------------------- Step 7
def hamming(a, b):
    """How many positions differ."""
    raise NotImplementedError


def diversity(pop):
    """Average Hamming distance over every pair in the population (0 = all identical)."""
    raise NotImplementedError


# ---------------------------------------------------------------- Step 8
def run_ga(level, N, pc, pm, generations, rng, n_bits=8, elite=0, rec=NULL):
    """The whole GA (FNC Algorithm 3.6). Start from random_population, then for gen = 0..generations:

      1. decode every chromosome, score it, and compute fitness
      2. append {"gen", "best_pose", "best_score", "mean_score", "diversity"} to the history
         and call rec.generation(poses, scores, diversity)
      3. stop after recording the last generation
      4. otherwise: roulette -> crossover_pairs -> mutate every child
      5. elitism: if elite > 0, the `elite` best of THIS generation replace the first `elite`
         children, unchanged
    Return the history list (generations + 1 entries).
    """
    raise NotImplementedError
