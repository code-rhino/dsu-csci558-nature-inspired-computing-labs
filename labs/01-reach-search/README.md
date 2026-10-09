# Lab 01 · Reach search

Teach the arm to reach a target using the search methods from Chapter 3 of *Fundamentals of Natural Computing* (FNC): hill-climbing, iterated hill-climbing, stochastic hill-climbing and simulated annealing, with a genetic algorithm as a stretch goal. **You write the algorithms.** The viewer replays every pose your algorithm tried, so you can watch it climb, get stuck, and escape.

## Read first

Read these **before** you start. Each step below also says which part of the reading it implements.

| Book | Section | Pages | For |
|---|---|---|---|
| FNC (de Castro) | 3.1–3.2 Introduction; Problem solving as a search task | 61–65 | Representation, objective, evaluation (all steps) |
| FNC | 3.3.1 Hill climbing: Algorithms 3.1, 3.2, 3.3 | 65–68 | Steps 4, 6, 7 |
| FNC | 3.3.2 Simulated annealing: Algorithms 3.4, 3.5 | 68–72 | Step 8. Written to *minimise*, like our scores. |
| FNC | 3.5.4 Hill-climbing, simulated annealing, and genetic algorithms | 99–100 | Part E: what to expect when you compare them |
| CI (Eberhart & Shi) | Ch. 3, "Evolutionary Computation Overview" and "EC Paradigm Attributes" | 47–51 | Why stochastic rules aren't "just random" |
| FNC + CI | 3.5.2 Genetic algorithms (FNC); "Genetic Algorithms" through "Comments on Genetic Algorithms" (CI) | FNC 88–91; CI 51–67 | Step 11 (stretch) |

## Setup

From the repo root (see the [main README](../../README.md)):

```bash
python3 -m viewer                   # terminal 1: leave it running
cd labs/01-reach-search             # terminal 2: every command below runs from here
python3 test_climb.py               # 0 passed · 0 failed · 19 to do
```

**Want to see where you're heading?** [`examples/`](examples/README.md) has nine recorded runs of a finished version, with no code. Before you write anything, try `python3 -m viewer.show labs/01-reach-search/examples/1` from the repo root. If you haven't yet, do [Lab 00 · Start here](../00-start-here/README.md) first: it builds the same plumbing step by step.

## Files in this lab

| File | Who writes it | What it is |
|---|---|---|
| `climb.py` | **you** | Every algorithm, as stubs. Each step replaces one `raise NotImplementedError`. |
| `test_climb.py` | provided | 19 checks by step. `python3 test_climb.py 4` runs steps 1–4. |
| `run.py` | provided | Runs your algorithm on a level and sends it to the viewer. Add `--runs 20` to run 20 seeds and report a success rate instead. |
| `levels.py` | provided | The four levels below. |

Your code only uses three things from outside this folder: `tcp()` and `tool_direction()` from `armlab.kinematics`, `collides()` from `armlab.world`, and the `rec` recorder from `viewer.trace`.

## The levels

- **Scores are distances, so lower is better.** That's the opposite of the fitness functions in most GA examples, so every "is it better?" comparison flips.
- **A pose** is a tuple of six whole-degree angles, `(A1, A2, A3, A4, A5, A6)`. Each level says which motors (`free`) the search may change.

| Level | Motors that move | Task | Is there an answer key? |
|---|---|---|---|
| 1 | A2, A3 | Reach (1, 1) from the shoulder. Both links are 1 m, so it can be done by hand. | ✅ formula and brute force |
| 2 | A1, A2, A3 | Reach a point off to the side, without going through the floor | ✅ formula (not built here) |
| 3 | A1, A2, A3 | Level 1's target, but a post blocks the easy answer | ❌ |
| 4 | all 6 | Reach the part on the crate **with the gripper pointing straight down** | ❌ |

---

# The walkthrough

Every step has the same shape:

1. **By hand.** Work the small case on paper with a calculator first.
2. **Write.** Fill in the function in `climb.py`.
3. **Check.** Run `python3 test_climb.py N` until every line passes.
4. **See it.** Run the `run.py` command and watch it in the viewer.

Hints are folded. Try without them first.

## Step 0 — Look around (15 min)

1. Check the viewer works: from the repo root, run `python3 -m viewer.demo`. The arm should wave each motor in turn.
2. Read the arm section of the [main README](../../README.md#the-arm), then `armlab/kinematics.py` (60 lines). `tcp(angles)` is the function you'll use most.
3. In the viewer, press **Manual jog**. Set A2 = 0, A3 = 90. The readout should say the tool tip is at **(1.000, 1.600, 0.000)**. That's the level 1 target.
4. Read `levels.py` and the `Level` class in `armlab/world.py`. Note what `free`, `start`, `target`, `boxes` and `down` mean.

---

# Part A — The arm as a search problem

## Step 1 — Where is the tip? (`planar_tip`)

Only A2 and A3 move, so the arm is the two-link arm from the hand example, standing up.

**By hand:** Fill in the tip position (x forward, y up, measured from the shoulder) for:

| A2 | A3 | x | y |
|---|---|---|---|
| 0 | 0 | | |
| 0 | 90 | | |
| 90 | −90 | | |
| 30 | 40 | | |

Check the last row with **Manual jog**. The viewer measures from the floor, so add 0.6 to y.

<details><summary>Hint</summary>

The elbow is at `(L1·cos A2, L1·sin A2)`. The forearm's angle **in the world** is A2 + A3, because angles add along the chain. The last row should be about (1.208, 1.440).
</details>

**Write:** `planar_tip(a2, a3)`. **Check:** `python3 test_climb.py 1`. The second test compares you against the full 3D arm at 50 random poses.

## Step 2 — The score (`distance`, `reach_score`)

**By hand:** Level 1 starts with every motor at 0. How far is the tip from the target? (Use your Step 1 table.)

**Write:** `distance(p, q)` for any number of dimensions, then `reach_score(angles, level)` using `tcp` from `lab.kinematics`.
**Check:** `python3 test_climb.py 2`.

## Step 3 — Neighbours (`neighbors`)

**By hand:**
1. List the neighbours of (0, 0, 0, 0, 0, 0) with `free = (1, 2)` and `step = 10`, one motor at a time.
2. How many neighbours are there if any **combination** of the 2 free motors can move? With 3 motors? With all 6?

<details><summary>Hint</summary>

Each free motor can go +step, 0 or −step, so 3^k combinations, minus the one where nothing moves. With 6 motors that's 728 poses to score **for every single step**. Remember that number in Step 10.
</details>

**Write:** `neighbors(angles, free, step, diagonal=False)`. Keep the order given in the docstring; the tests depend on it. Drop any pose that breaks a joint limit.
**Check:** `python3 test_climb.py 3`.

---

# Part B — Hill-climbing

## Step 4 — Hill-climbing (`hill_climb`)

FNC Algorithm 3.1, steepest version, **minimising**: score every neighbour, move to the best one if it is *strictly* better, otherwise stop.

**By hand:** Level 1, start (0, 0), steps of 10°, one motor at a time. Do the first four rows with a calculator:

| Step | (A2, A3) | Score | Best neighbour |
|---|---|---|---|
| 0 | (0, 0) | 1.414 | ? |
| 1 | | | |
| 2 | | | |
| 3 | | | |

Then predict: will it reach the target, (0, 90)?

**Write:** `hill_climb(start, score, nbrs, rec=NULL)`. Call `rec.restart` once, `rec.tried` for each neighbour you score, and `rec.moved` for each move. That recording is what the viewer replays.
**Check:** `python3 test_climb.py 4`.

**See it:**

```bash
python3 run.py 1 hc --step 10              # watch where it stops
python3 run.py 1 hc --step 10 --diagonal
python3 run.py 1 hc --step 1
python3 run.py 1 hc --step 1 --diagonal
```

Turn on the **Side** camera and scroll down to the **Landscape** panel. That panel is every (A2, A3) pair coloured by score, with bright meaning close to the target. It shows the problem you couldn't picture from the textbook.

<details><summary>Why does the 10° walk stop at (20, 60), 35 cm short, with no obstacles anywhere?</summary>

Look at the landscape. The bright valley runs **diagonally**. From (20, 60), turning either motor on its own makes the score worse, while turning both together, to (10, 70), makes it better. A climber that can only move one motor at a time can't see that move, so it stops.

**The neighbourhood is part of the algorithm.** A poor choice creates local optima that don't exist in the problem itself. With `--diagonal` it reaches (0, 90) in 9 moves.

Smaller steps don't fix it. With 1° steps it stops somewhere else entirely: (45, 0), with the arm stretched straight out at the target, 59 cm away. From there, turning A2 by −1° and A3 by +2° *together* would help, but no single-motor move does. `--step 1 --diagonal` gets there.
</details>

## Step 5 — The answer key (`ik_2link`, `brute_force`)

You can't judge a search method unless you know the true answer. Level 1 has two ways to get it.

**By hand:** use the law of cosines for the target (1, 1) with L1 = L2 = 1:

  cos A3 = (x² + y² − L1² − L2²) / (2·L1·L2)
  A2 = atan2(y, x) − atan2(L2·sin A3, L1 + L2·cos A3)

You should get two answers: elbow down and elbow up.

**Write:** `ik_2link(x, y)` and `brute_force(score, free, start, step=1)`.
**Check:** `python3 test_climb.py 5`.
**See it:** `python3 run.py 1 brute`

**Think:** Brute force on level 1 scores 81,571 poses. How many would it need for level 4's six motors at 1° steps? This is the "too many to try" condition from the reading: why search exists at all.

## Step 6 — Iterated hill-climbing (`random_pose`, `iterated_hc`)

FNC Algorithm 3.2: climb from several random starts and keep the best.

**By hand:** run `python3 run.py 2 hc --runs 20`. If a single climb succeeds with probability p (read it off that result), what's the chance that **at least one of 8** climbs succeeds? (1 − (1 − p)⁸.) Write the number down; you'll check it in a minute.

**Rule from here on:** every random number comes from the `rng` you're given. Never `import random` inside an algorithm. That makes every run repeatable from its seed.

**Write:** `random_pose(level, rng)` and `iterated_hc(...)`. Pass `rec` through to `hill_climb`.
**Check:** `python3 test_climb.py 6`.
**See it:** `python3 run.py 2 ihc --restarts 8`, then `python3 run.py 2 ihc --runs 20`. Was your prediction right? Restarts show up as jumps in the score chart.

---

# Part C — Stochastic search

## Step 7 — Stochastic hill-climbing (`accept_prob`, `random_neighbor`, `stochastic_hc`)

FNC Algorithm 3.3. The climber tries **one random** neighbour and moves there with a probability that depends on how much better or worse it is, so sometimes it takes a **worse** step. FNC's formula is for maximising. Because we minimise, the sign flips:

  P(move) = 1 / (1 + e^((f_new − f_cur) / T))

**By hand:** fill in P for a move that makes the score **worse** by Δ:

| Δ (metres worse) | T = 0.001 | T = 0.02 | T = 0.2 |
|---|---|---|---|
| 0.01 | | | |
| 0.10 | | | |

What does a large T turn the search into? What does a tiny T turn it into?

<details><summary>Check your table</summary>

Δ = 0.01: about 0.00005, 0.378, 0.488. Δ = 0.10: about 0, 0.0067, 0.378. A large T makes it a random walk; a tiny T makes it hill-climbing. FNC p.68 says the same thing.
</details>

**Write:** the three functions. `accept_prob` must not crash when T is tiny (`math.exp(10000)` overflows). Return the **best pose visited**, not the last one.
**Check:** `python3 test_climb.py 7`.
**See it:**

```bash
python3 run.py 1 shc --T 0.001
python3 run.py 1 shc --T 0.02
python3 run.py 1 shc --T 0.2
```

Watch **worse moves taken** in Run stats, and the narration when the arm takes one.

## Step 8 — Simulated annealing (`anneal`)

FNC Algorithms 3.4–3.5 (pp. 69–71). It's stochastic hill-climbing, except T starts high and **cools** after every try: `T = T * beta`. FNC's version also minimises: always take a better move; take a worse one with probability e^(−Δ/T).

**By hand:**
1. With T0 = 0.5 and β = 0.998, what is T after 4,000 tries?
2. What β would bring T down to 0.001 after exactly 4,000 tries?

<details><summary>Check</summary>

1. 0.5 × 0.998⁴⁰⁰⁰ ≈ 0.00017.
2. β = (0.001 / 0.5)^(1/4000) ≈ 0.99845.
</details>

**Write:** `anneal(...)`.
**Check:** `python3 test_climb.py 8`.
**See it:** `python3 run.py 3 sa`. The dashed line in the score chart is T. Notice that worse moves are common early on and almost disappear by the end: the "drunk kangaroo sobering up" from FNC p.99.

---

# Part D — Obstacles and six motors

## Step 9 — Collisions (`penalized`)

Level 3 has a post exactly where the level 1 answer with the elbow down would go. Its start pose is clear of the post, but random starts may not be. `lab.levels.collides(pose, level)` says whether a pose hits the floor or a box. You decide what a collision **costs**.

**Write:** `penalized(score, level, penalty)`. It returns a *new* function that adds `penalty` to colliding poses.
**Check:** `python3 test_climb.py 9`.

**Experiment:**

```bash
python3 run.py 3 hc --runs 20
python3 run.py 3 ihc --runs 20
python3 run.py 3 sa --runs 20
python3 run.py 3 sa --runs 20 --penalty 0.5
```

Then pick a seed that failed and watch it: `python3 run.py 3 sa --seed N`.

<details><summary>Open after you've watched a failure</summary>

Most failures end with the base turned to about ±170° and the arm reaching **backwards over its own head**, about 17 cm short. It's a near miss, because the base stops at ±170° rather than turning the full 180°. To get from there to the real answer, the base has to swing through ~170° of poses that are all worse, and annealing rarely accepts that many worse moves in a row. Iterated hill-climbing doesn't need to cross that valley: it just starts again somewhere else. **The shape of the landscape decides which method wins, not how clever the method is.**
</details>

## Step 10 — Pointing down (`angle_between`, `pose_score`)

Level 4 frees all six motors. The tip has to reach the part **and** the gripper has to point straight down. One score has to combine metres and radians:

  score = distance + w · (angle between the gripper and straight down)

**By hand:** with w = 0.5, how many centimetres of reach error cost the same as being 10° off vertical? What happens to the arm's behaviour if w is tiny? If w is huge?

**Write:** `angle_between(u, v)` (the dot product, then `acos`, with the value clamped to [−1, 1]) and `pose_score(angles, level, w)`.
**Check:** `python3 test_climb.py 10`.

**Experiment:**

```bash
python3 run.py 4 hc  --runs 10 --w 0.5
python3 run.py 4 ihc --runs 10 --w 0.5 --step 2 --restarts 5
python3 run.py 4 sa  --runs 10 --w 0.5 --iters 8000 --beta 0.999
```

Then repeat all three with `--w 0.2`. Here success means within 5 cm **and** within 10° of vertical.

## Step 11 (stretch) — A genetic algorithm

If you've written a simple GA before (binary encoding, roulette selection, single-point crossover, bit mutation), reuse it here:
1. **Encoding:** 8 bits per free joint. That's 48 bits on level 4.
2. **Write `decode_pose(bits, level)`:** each 8-bit chunk maps onto that joint's limits: lo + value × (hi − lo) / 255. Check with `python3 test_climb.py 11`.
3. **Fitness:** a GA maximises, but these scores are minimised. Use something like `1 / (1 + score)`.
4. **Run it:** run your GA with that fitness. To watch it, call `rec.tried(pose, score)` for every individual you score.
5. **Compare** it with the other methods using the same evaluation count.

---

# Part E — Comparing fairly

Compare methods by **how many fitness evaluations** they used, not by how long they ran or how many steps they took. `run.py --runs` reports the average evaluations, and the best, median and worst scores across seeds. **One run of a stochastic method tells you nothing**, which is why every row is 20 seeds.

| Level | Method | Settings | Success / runs | Avg. evaluations | Worst score |
|---|---|---|---|---|---|
| 1 | hill-climbing | step 1 | | | |
| 1 | iterated | 8 restarts | | | |
| 2 | hill-climbing | | | | |
| 2 | iterated | 8 restarts | | | |
| 2 | stochastic | T = 0.02 | | | |
| 3 | hill-climbing | | | | |
| 3 | iterated | 8 restarts | | | |
| 3 | annealing | T0 0.5, β 0.998 | | | |
| 4 | iterated | w 0.5 / w 0.2 | | | |
| 4 | annealing | w 0.5 / w 0.2 | | | |

**Predict before you run:** which method wins each level?

<details><summary>Open after you have your own numbers</summary>

My runs, using the reference solution with `run.py`'s default settings. Each cell is successes / runs · average evaluations. Levels 1–3 are seeds 0–19; level 4 is seeds 0–9.

| Level | Hill-climbing | Iterated (8 restarts) | Stochastic HC (T 0.02) | Annealing |
|---|---|---|---|---|
| 1 | 18/20 · 429 | 20/20 · 3,664 | 19/20 · 4,001 | 20/20 · 4,001 |
| 2 | 15/20 · 1,026 | 20/20 · 7,693 | 15/20 · 4,001 | 16/20 · 4,001 |
| 3 | 4/20 · 934 | **19/20** · 8,175 | 5/20 · 4,001 | 7/20 · 4,001 (10/20 with 8,000 tries, T0 1.0, max-step 20) |
| 4, w = 0.5 | 3/10 · 2,590 | **9/10** · 7,156 (step 2, 5 restarts) | — | 7/10 · 8,001 |
| 4, w = 0.2 | 0/10 · 2,542 | 3/10 · 6,958 | — | **7/10** · 8,001 |

What I'd put in a report:

1. **Iterated hill-climbing wins levels 1–3.** When restarts are cheap and the good basins are reasonably large, restarting beats being clever.
2. **Annealing earns its place on level 4 with w = 0.2.** Change w and you change the landscape, and the ranking of the methods changes with it. Iterated HC falls from 9/10 to 3/10 while annealing holds at 7/10. **There's no best algorithm, only a best algorithm for a given landscape.**
3. **On level 3 the post isn't the hard part.** A penalty of 10, 1 or 0.3 gave me the same annealing result. The real trap is the backwards reach over the top (Step 9).
4. **A worst score above 10 means the run ended inside an obstacle.** Find one of those seeds, watch it, and explain why the climber couldn't get out.
5. **Report the spread, not just the average.** "Median 0.009, worst 10.9" says far more than "average 1.1".
</details>

---

## Progress

- [ ] Step 0 — viewer and demo work
- [ ] Steps 1–3 — the arm as a search problem
- [ ] Steps 4–6 — hill-climbing, the answer key, restarts
- [ ] Steps 7–8 — stochastic hill-climbing and annealing
- [ ] Steps 9–10 — obstacles, six motors, weighting the score
- [ ] Step 11 — GA (stretch; the full version is [lab 02](../02-genetic-algorithm/README.md))
- [ ] Part E — the comparison table

## Notes

- **Your single-motor hill-climber is close to Cyclic Coordinate Descent (CCD),** an inverse-kinematics method used in games and robotics.
- **Your runs are saved** to `traces/01-reach-search/` at the repo root, and ignored by git. To replay an older one, use **Open trace…** or drag the file onto the viewer. Name a run with `--name`.
- **Sharing results:** if you compare numbers with classmates, say which seeds you used. `--runs 20` always uses seeds 0–19, so everyone's runs are comparable.
