# Lab 00 · Start here

**Type along and build your first search in about 45 minutes.** You'll make the arm move, measure how far it is from a target, write a search that hunts for a good pose, and then find out honestly how good that search is. Every piece of code is on this page. Type it yourself rather than pasting; that's where the learning happens.

**What you'll end up with:** your own `my_first_search.py` (about 60 lines), a 3D replay of it searching, and a measured result that explains why the rest of the labs exist.

## Read first

| Book | Section | Pages | Why |
|---|---|---|---|
| FNC (de Castro) | 3.1 Introduction, 3.2 Problem solving as a search task | 61–65 | The three ingredients of every search: representation, objective, evaluation. You'll write all three today. |
| CI (Eberhart & Shi) | Ch. 3, "Evolutionary Computation Overview" and "EC Paradigm Attributes" | 47–51 | Why these methods use a score directly instead of calculus. |
| FNC, for the bonus step | 4.4.3 ADALINE, the LMS algorithm, and error surfaces | 160–163 | Gradient descent on an error surface: the idea behind "follow the slope". |

## Before you start

From the repo root, start the viewer and leave it running in its own terminal window:

```bash
python3 -m viewer
```

Your browser opens with the arm folded at rest. Everything below runs in a **second** terminal, from the repo root.

---

## Step 1 · Create your file (2 min)

Create `labs/00-start-here/my_first_search.py` and type:

```python
import math
import random
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))   # lets Python find armlab/ and viewer/

from armlab.kinematics import FOLDED, LIMITS, tcp
from armlab.world import Level, collides
from viewer.trace import Trace
```

The `sys.path` line tells Python to look two folders up, at the repo root, for the shared code. Run it: `python3 labs/00-start-here/my_first_search.py`. **No output is good.** An `ImportError` means the file isn't in `labs/00-start-here/`.

## Step 2 · Where is the gripper? (5 min)

A **pose** is six motor angles in degrees: `(base, shoulder, elbow, twist, wrist, flange)`. `tcp(pose)` tells you where the gripper ends up, as `(x, y, z)` in metres: x forward, y up, z sideways.

**Predict first** (the upper arm is 1 m, the forearm plus gripper is 1 m, and the shoulder is 0.6 m off the floor):

| Pose | Your guess for (x, y, z) |
|---|---|
| `(0, 0, 0, 0, 0, 0)`, everything at zero | |
| `(0, 90, 0, 0, 0, 0)`, shoulder raised 90° | |
| `(90, 0, 0, 0, 0, 0)`, base turned 90° | |

Then add this to the bottom of your file and run it:

```python
print(tcp((0, 0, 0, 0, 0, 0)))
print(tcp((0, 90, 0, 0, 0, 0)))
print(tcp((90, 0, 0, 0, 0, 0)))
```

<details><summary>What you should see</summary>

```
(2.0, 0.6, 0.0)                 arm straight out, 2 m forward at shoulder height
(1.22e-16, 2.6, 0.0)            straight up; 1.22e-16 is just 0 with rounding noise
(1.22e-16, 0.6, -2.0)           swung round to the side
```
</details>

That's **forward kinematics**: angles in, position out. It's easy. The hard direction, position in and angles out, is what we're going to *search* for. Delete the three `print` lines before going on.

## Step 3 · Make it move (10 min)

The viewer replays a **trace**: a list of poses you record in Python. Add a task (a **Level**) and a helper that glides from one pose to another:

```python
level = Level(1, "My first target", free=(0, 1, 2), start=FOLDED, target=(1.2, 1.0, 0.5), floor=True,
              blurb="Base, shoulder and elbow move. Reach the yellow ball without going through the floor.")


def glide(rec, a, b, steps=30):
    """Record `steps` poses on a straight line from pose a to pose b."""
    for i in range(1, steps + 1):
        t = i / steps
        pose = tuple(x + (y - x) * t for x, y in zip(a, b))
        rec.moved(pose, 0)          # 0 = no score yet; step 4 fixes that


if __name__ == "__main__":
    rec = Trace(level, "hello arm", lab="00-start-here")
    rec.restart(FOLDED, 0)
    glide(rec, FOLDED, (0, 0, 0, 0, 0, 0))
    glide(rec, (0, 0, 0, 0, 0, 0), (0, 90, 0, 0, 0, 0))
    glide(rec, (0, 90, 0, 0, 0, 0), (90, 90, -90, 0, 0, 0))
    rec.save()
```

What the pieces mean:
- **`free=(0, 1, 2)`:** only the base, shoulder and elbow are allowed to move.
- **`start=FOLDED`:** begin from the folded rest pose.
- **`target`:** where the yellow ball is.
- **`floor=True`:** going through the floor counts as a collision.

Run it. The viewer picks it up by itself: the arm unfolds, straightens out, points up, then turns and bends. Try the **Side** and **Top** cameras, and drag to orbit.

**Try:** add a fourth `glide` that brings the arm back to `FOLDED`.

## Step 4 · Score a pose (5 min)

To search, you need a number that says how good a pose is: the **evaluation function** from FNC 3.2. Ours is the distance from the gripper to the target, with a big penalty for hitting the floor. Add it above `glide`:

```python
def score(pose):
    """How far the gripper is from the target, in metres. Hitting the floor costs 10 extra."""
    d = math.dist(tcp(pose), level.target)
    if collides(pose, level):
        d += 10
    return d
```

Now change the `0` inside `glide` to `score(pose)` so the replay shows real scores. Check one by hand by adding `print(score(FOLDED))` at the top of the `__main__` block. You should get **0.842**: the folded arm's gripper is 84.2 cm from the ball.

**Check it in the viewer:** press **Manual jog** and drag the sliders. The panel shows the distance to the target live. Can you get under 10 cm by hand?

## Step 5 · Your first search: random guessing (10 min)

The simplest possible search: try lots of random poses and keep the best. Add these two functions:

```python
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
        rec.tried(pose, s, accepted=better)     # the viewer moves the arm only when better
        if better:
            best, best_score = pose, s
    return best, best_score
```

And replace your whole `__main__` block with:

```python
if __name__ == "__main__":
    rec = Trace(level, "random search", lab="00-start-here")
    best, s = random_search(2000, random.Random(0), rec)
    print("best pose:", best)
    print(f"distance: {s * 100:.1f} cm")
    rec.save()
```

**Why `random.Random(0)`?** The `0` is a **seed**. The same seed gives the same "random" numbers, so you and your classmates get exactly the same run and can compare results.

Run it, then watch the replay:

```
best pose: (-21, -29, 78, 0, 0, 0)
distance: 26.8 cm
```

**What to watch:**
- The blue ghost arm flails around, one random guess at a time.
- The orange arm only moves when a guess beats the best so far.
- In the score chart, the green "best" line drops quickly at first, then hardly at all.

## Step 6 · How good is it, really? (5 min)

One run proves nothing: maybe seed 0 was unlucky. Scientists run many trials. Add this and call `test20()` instead of the search, by temporarily replacing the `__main__` block's contents with `test20()`:

```python
class NoRecord:
    """Stands in for Trace when you don't want to record (much faster)."""
    def restart(self, *a): pass
    def tried(self, *a, **k): pass


def test20(tries=2000):
    wins = 0
    for seed in range(20):
        best, s = random_search(tries, random.Random(seed), NoRecord())
        print(f"seed {seed:2}: {s * 100:5.1f} cm")
        wins += s < 0.05
    print(f"within 5 cm: {wins} of 20")
```

**The result:** within 5 cm in **0 of 20** runs. Even with 20,000 guesses per run, it's only 1 of 20.

**Why?** Three motors with whole-degree settings give 341 × 271 × 301 ≈ 28 million poses. Only a tiny patch of them puts the gripper within 5 cm of the ball. Random guessing doesn't **learn** anything from its previous guesses. Every method in Chapter 3 is a way of using what you've already found to make a better next guess.

## Bonus · Follow the slope (10 min)

Here's one way to learn from previous guesses: measure which direction is downhill and step that way. That's **gradient descent**. It isn't one of the Chapter 3 methods, because it needs the *slope* of the landscape and not just the score, but it's a good contrast.

The finished version is in `finished/follow_the_slope.py`. Read its `slope()` and `gradient_descent()` functions (about 30 lines), then run it:

```bash
python3 labs/00-start-here/finished/follow_the_slope.py 1     # your target: 0.1 cm in 148 evaluations
python3 labs/00-start-here/finished/follow_the_slope.py 2     # a post in the way: stuck 80 cm short
python3 labs/00-start-here/finished/follow_the_slope.py 2 --restarts 5 --seed 3     # restarts get around it
python3 labs/00-start-here/finished/follow_the_slope.py 3     # six motors, gripper pointing down
```

Compare: **2,000 random guesses got to 26.8 cm, while 148 slope-guided steps got to 0.1 cm.** But on level 2 the slope points straight into the post and the arm gets stuck there. Being stuck on a "best nearby" answer is called a **local optimum**, and escaping it is what lab 01 is about.

---

## Check your work

If something doesn't match, compare with the finished files:

| File | What it is |
|---|---|
| `finished/my_first_search.py` | Steps 1–6, complete. Run with `--test20` for step 6. |
| `finished/follow_the_slope.py` | The bonus, complete, with three levels, restarts and `--runs`. |
| `finished/test_finished.py` | Checks that the finished files still give the numbers quoted on this page. |

## Where next

**[Lab 01 · Reach search](../01-reach-search/README.md):** hill-climbing, restarts, stochastic hill-climbing and simulated annealing from FNC Chapter 3, on the same arm. You've already built the hard part: a score, a search loop, and a way to watch it.
