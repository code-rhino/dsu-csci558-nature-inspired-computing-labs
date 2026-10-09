# Lab 02 · Genetic algorithm

Evolve arm poses instead of climbing to them. Each candidate pose becomes a **chromosome** (a string of bits). A **population** of them is improved generation after generation by **selection**, **crossover** and **mutation**. The viewer draws the whole population at once: watch a scattered crowd of thin arms collapse onto the target.

**Before this lab:** [Lab 00 · Start here](../00-start-here/README.md). [Lab 01](../01-reach-search/README.md) helps but isn't required; Part E compares your GA against it.

## Read first

| Book | Section | Pages | For |
|---|---|---|---|
| FNC (de Castro) | 3.4.3 Basic principles of genetics (the rest of 3.4 is optional background) | 76–82 | Chromosomes, genes, alleles: the vocabulary of this lab |
| FNC | 3.5.1 Standard evolutionary algorithm | 86–88 | The loop you'll write in Step 8 |
| FNC | 3.5.2 Genetic algorithms: roulette wheel, crossover, mutation | 88–91 | Steps 4–6 |
| FNC | 3.5.3 Examples of application, especially "Numerical function optimization" | 91–99 | Binary encoding of a number (p. 99), used in Step 1 |
| FNC | 3.5.4 Hill-climbing, simulated annealing, and genetic algorithms | 99–100 | Part E: what a population buys you |
| CI (Eberhart & Shi) | Ch. 3, "Genetic Algorithms" through "Comments on Genetic Algorithms" | 51–67 | A worked GA by hand, and the schema theorem (why crossover works) |
| CI | Ch. 4, "Genetic Algorithm Implementation" | 103–117 | How a full GA program is organised |

## Setup

```bash
python3 -m viewer                          # terminal 1, repo root: leave it running
cd labs/02-genetic-algorithm               # terminal 2: every command below runs from here
python3 test_ga.py                         # 0 passed · 0 failed · 12 to do
python3 -m viewer.show examples            # (from the repo root) recorded runs of a finished GA
```

| File | Who writes it | What it is |
|---|---|---|
| `ga.py` | **you** | Every GA piece, as stubs. Each step replaces one `raise NotImplementedError`. |
| `test_ga.py` | provided | 12 checks by step. `python3 test_ga.py 4` runs steps 1–4. |
| `run.py` | provided | Runs your GA on a level and sends it to the viewer. `--runs 20` reports a success rate. |
| `levels.py` | provided | The three levels, `score()` (lower is better) and `success()` (within 5 cm). |
| `examples/` | provided | Six recorded runs of a finished GA. [What to look for](examples/README.md). |

## The levels

| Level | Motors | Chromosome | Task |
|---|---|---|---|
| 1 | A2, A3 | 16 bits | Lab 01's two-motor reach. The **landscape panel** shows the whole population as white dots. |
| 2 | A1, A2, A3 | 24 bits | Lab 01's "around the post", with its backwards-reach trap. |
| 3 | all 6 | 48 bits | Reach the part on the crate with the gripper pointing straight down. |

---

# The walkthrough

Same shape as lab 01: **by hand**, then **write**, then **check** (`python3 test_ga.py N`), then **see it**. Hints are folded.

## Step 1 · Decode a chromosome (`decode`)

A motor's angle is stored as an 8-bit whole number v, from 0 to 255, then stretched over that motor's range (FNC p. 99):

  angle = lo + v × (hi − lo) / 255, rounded to a whole degree

**By hand** (level 1: A2 runs −90…180, A3 runs −150…150):
1. The chromosome `01010101 10000000`. What are v for A2 and v for A3? What pose is it?
2. How many different angles can one 8-bit gene express? How far apart are neighbouring A2 angles?

<details><summary>Check</summary>

1. v = 85 and 128. A2 = −90 + 85 × 270/255 = 0. A3 = −150 + 128 × 300/255 = 0.59 → 1. The pose is (0, 0, 1, 0, 0, 0).
2. 256 values, about 1.06° apart for A2. That's about 2 cm of tool movement at full reach, so the GA can't place the arm more finely than that. Keep it in mind for Part E.
</details>

**Write:** `decode(bits, level, n_bits=8)`. **Check:** `python3 test_ga.py 1`.

## Step 2 · Fitness (`fitness`)

`score()` is lower-is-better, but a roulette wheel needs **higher is better and never negative**. The usual fix: fitness = 1 / (1 + score).

**By hand:** what's the fitness of a perfect pose (score 0)? Of a pose 1 m away? Of a pose through the post (score about 10.4)? Why not just use −score?

<details><summary>Check</summary>

1, 0.5 and about 0.088. Negative numbers can't be slice sizes on a wheel.
</details>

**Write:** `fitness(pose, level)`. **Check:** `python3 test_ga.py 2`.

## Step 3 · A random population (`random_population`)

**By hand:** in a random population of 16-bit chromosomes, how many bits would you expect two individuals to differ by, on average? (You'll check this in Step 7.)

**Write:** `random_population(N, length, rng)`. **Check:** `python3 test_ga.py 3`.

## Step 4 · Roulette-wheel selection (`roulette`)

Each individual gets a slice of the wheel proportional to its fitness (FNC p. 89). Spin once for every place in the next generation.

**By hand:** fitnesses `[1, 2, 3, 4]`.
1. Write down the four slices of [0, 1).
2. Which individual does each of the spins 0.05, 0.1, 0.59 and 0.99 pick?
3. Over many spins, what fraction of picks go to the fittest individual?

<details><summary>Check</summary>

1. [0, 0.1), [0.1, 0.3), [0.3, 0.6), [0.6, 1).
2. Individuals 0, 1, 2, 3. A spin exactly on a boundary, like 0.1, belongs to the next slice.
3. 40%.
</details>

**Write:** `roulette(pop, fits, rng, spins=None)`. Return **copies**: if two places in the next generation share one list, mutating one changes the other. **Check:** `python3 test_ga.py 4`.

## Step 5 · Crossover (`crossover`, `crossover_pairs`)

Single-point crossover (FNC p. 90): cut both parents at the same place and swap the tails.

**By hand:** cross `000000` and `111111` at cut 2. Then: a pair is crossed only when its random r < pc. With pc = 0.6 and r = 0.5 and 0.7 for two pairs, which pairs cross?

**Write:** both functions. **Check:** `python3 test_ga.py 5`.

## Step 6 · Mutation (`mutate`)

Flip each bit with a small probability pm (FNC p. 91).

**By hand:** level 1, 30 children of 16 bits, pm = 0.02. About how many bits flip per generation?

<details><summary>Check</summary>

30 × 16 × 0.02 ≈ 9.6.
</details>

**Write:** `mutate(ind, pm, rng)`. Return a **new** list. **Check:** `python3 test_ga.py 6`.

## Step 7 · Diversity (`hamming`, `diversity`)

Diversity is the average number of bits by which two individuals differ. When it falls to 0, every chromosome is identical and crossover can't create anything new.

**Write:** both. **Check:** `python3 test_ga.py 7`. Was your Step 3 guess right? (A random 16-bit population averages 8.)

## Step 8 · The whole GA (`run_ga`)

The loop from FNC 3.5.1–3.5.2, in this order: decode, score and fitness; **record** the generation; stop if it's the last one; then roulette, crossover, mutate; then **elitism** (copy the best `elite` of this generation into the next, unchanged).

**Write:** `run_ga(...)`. Call `rec.generation(poses, scores, diversity)` once per generation; that's what the viewer draws. **Check:** `python3 test_ga.py 8`. One of the tests checks the claim on FNC p. 91: **without mutation, no bit position can ever take a value it didn't have in generation 0.**

**See it:**

```bash
python3 run.py 1               # default settings: 30 arms, 60 generations, pm 0.02, elite 1
python3 run.py 1 --pm 0        # no mutation: watch diversity in Run stats
python3 run.py 3 --N 60 --gens 150
```

What to watch:
- **3D view:** the thin arms are the population, from green (best) to red (worst). The orange arm is the best of each generation.
- **Score chart:** best (green) and average (dashed yellow).
- **Run stats:** diversity.
- **Landscape panel** (level 1): the population as white dots, gathering on the bright spots.

---

# Part E · Experiments

Every row is `python3 run.py LEVEL --runs 20 [options]`. Fill in the success count, and say how many evaluations each run used: N × (generations + 1).

| Level | Options | What changes | Success / 20 | Evaluations |
|---|---|---|---|---|
| 1 | *(defaults)* | | | 1,830 |
| 1 | `--pm 0` | no mutation | | |
| 1 | `--pc 0` | no crossover | | |
| 1 | `--elite 0` | no elitism | | |
| 2 | *(defaults)* | | | |
| 2 | `--N 40 --gens 100` | bigger budget | | |
| 2 | `--pm 0` | | | |
| 2 | `--bits 10` | finer angles, longer chromosome | | |
| 3 | `--N 40 --gens 100 --runs 10` | | | |
| 3 | `--N 60 --gens 150 --runs 10` | | | |

**Predict before you run.** Which matters more here, crossover or mutation? Will more bits help on level 2?

<details><summary>Open after you have your numbers</summary>

My results, from the reference solution:

| Level | Options | Success | Evaluations per run |
|---|---|---|---|
| 1 | defaults | 18/20 | 1,830 |
| 1 | no mutation | 8/20 | 1,830 |
| 1 | no crossover | 13/20 | 1,830 |
| 1 | no elitism | 16/20 | 1,830 |
| 2 | defaults | 10/20 | 1,830 |
| 2 | N 40, 100 generations | 10/20 | 4,040 |
| 2 | no mutation | **0/20** | 1,830 |
| 2 | 10 bits | 3/20 | 1,830 |
| 3 | N 40, 100 generations | 5/10 | 4,040 |
| 3 | N 60, 150 generations | 9/10 | 9,060 |

What to take from it:

1. **Mutation is not optional.** Without it, diversity drains to almost nothing and the population freezes wherever it happens to be. Level 2 goes to 0 of 20. Recorded example 2 shows it happening.
2. **Crossover helps, but less than you might expect** on these small chromosomes: 18 vs. 13 of 20 on level 1.
3. **Finer isn't free.** With 10 bits, the base can finally sit at exactly 0°, but the chromosome has 2⁶ = 64 times as many possible values to search. With the same budget, success drops from 10 to 3 of 20.
4. **A bigger budget didn't help level 2.** Some runs fall into lab 01's backwards-reach trap (recorded example 5); others end just over the 5 cm line. Running longer doesn't fix either, because by then the population has converged.
5. **Compared with lab 01 on the same levels:**
   - Level 2 here is lab 01's level 3: iterated hill-climbing got 19/20 in about 8,200 evaluations; annealing got 7/20 in 4,000; the GA gets 10/20 in 1,830.
   - On six motors (lab 01's level 4, w = 0.5): iterated hill-climbing got 9/10 in about 7,200; the GA gets 9/10 in 9,060.

   **The GA isn't magic; it's competitive.** Its strength (FNC 3.5.4) is searching many regions at once and combining their good parts, which pays off most when the space is huge and the good parts really can be combined.
</details>

---

## Stretch

- **Tournament selection:** pick k random individuals and keep the best. Replace `roulette` and compare. Is it more or less forgiving of a few very fit individuals?
- **Gray code:** in plain binary, 127 → 128 flips all 8 bits (`01111111` → `10000000`). Decode with Gray code instead, so neighbouring angles differ by one bit, and re-run Part E.
- **Real-valued genes:** skip the bits and store angles directly. That's most of the way to lab 03 (evolution strategies).

## Progress

- [ ] Steps 1–3: encoding, fitness, population
- [ ] Steps 4–7: selection, crossover, mutation, diversity
- [ ] Step 8: the whole GA, watched in the viewer
- [ ] Part E: experiments
