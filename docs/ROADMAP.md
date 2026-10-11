# Lab roadmap

The labs follow the order of the CSCI 558 course modules, so each one can be used when the class reaches that topic. They all use the same farm and the same spraying drone. Every lab gets the same treatment:
- a **Read first** table (book, section, pages);
- by-hand exercises before code;
- stubs and tests;
- recorded example runs;
- no solution code in the shared repo.

**Books:** FNC = de Castro, *Fundamentals of Natural Computing*. CI = Eberhart & Shi, *Computational Intelligence: Concepts to Implementations*.

| Lab | Status | Course module · topic | The drone problem |
|---|---|---|---|
| 00 · Start here | ✅ ready | Module 2 intro | Score a route; random search; rules of thumb vs. brute force |
| 01 · Route search | next | Module 2 · search, hill-climbing, annealing | Best spraying order; where to put the base station |
| 02 · Genetic algorithm | planned | Module 2 · topic 4, GA | Evolving routes; a bit-string GA for base placement |
| 03 · Evolution strategies | planned | Module 2 · topic 6, ES | Placing the base station (real numbers) |
| 04 · Particle swarm | planned | Module 2 · topic 8, PSO | Placing two refill stations for farm 4 |
| 05 · Ant colony: routes and safe paths | planned | Swarm intelligence (Ant System paper) | Routes, and planning paths round obstacles yourself |
| 06 · A neural network learns the energy | planned | Module 3 · topics 10–12, ANN | Learning a flight's energy from logged flights |
| 07 · Fuzzy controller | planned | Module 4 · topic 15, fuzzy logic | Holding spraying height in gusts |
| 08 · A fleet of drones | idea | Vehicle routing | Splitting the zones between two or three drones |

The robot-arm version of labs 00–02 is archived at git tag `robot-arm-v1` (branch `robot-arm`). It could come back later as its own lab, for example a URDF / ROS lab.

### What "ready" means for a lab

A lab is ready to hand to students when it has all of these:

- [ ] `README.md` with a **Read first** table, then numbered steps: by hand → write → check → see it
- [ ] a stub file (every function `raise NotImplementedError`) and a test file, run as `python3 test_x.py N`
- [ ] `run.py` with `--runs N` for success rates over seeds 0..N-1, recording through `viewer.trace.Trace(..., lab="NN-name")`
- [ ] farms from `farmlab/farms.py`, or its own farms, each with a best-known energy
- [ ] **every command in the README runs at the step where it appears** (no step should need a function from a later step)
- [ ] a Part E experiments table, with measured results behind a fold
- [ ] `examples/`: recorded runs of a finished version (traces only) plus a "what to look for" README
- [ ] a reference solution in the private instructor kit, passing every test and reproducing every number in the README
- [ ] a row in the main README's Labs table, and its status updated here

---

## 01 · Route search

Ported from the arm version's lab 01, keeping its shape: eleven steps, each with a by-hand exercise, a test and a way to watch it.

**Students build:**
- **neighbourhoods** for a route: swap two zones, move one zone (insert), reverse a section (2-opt);
- steepest hill-climbing, iterated hill-climbing (FNC Alg. 3.1–3.2), stochastic hill-climbing (3.3) and simulated annealing (3.4–3.5);
- a fair comparison over 20 seeds by number of evaluations.

**The lessons it's built around** (to be measured with the reference solution before the README quotes any numbers):
- **The neighbourhood is part of the algorithm.** Expect swap-only hill-climbing to get stuck where 2-opt doesn't. This is the drone version of the arm's "one motor vs. two motors" result.
- **Direction matters because of weight.** 2-opt reverses a section of the route, so on this problem it changes the energy even when the distance stays the same. That doesn't happen in the travelling salesman problem.
- **Farm 4 is rugged.** Local search ends in many different places (10 distinct end points in early testing), so restarts and annealing earn their keep.

**A two-number problem, to keep the landscape picture:** where should the base station go? Its (x, y) is two numbers, so the viewer can draw a **heat map** of total energy over every position, with the search's path on top. That's the arm lab's best teaching moment, kept.

**Viewer work needed:** a "landscape" panel for two-number problems, and frames that move the base station.

| Read first | Pages |
|---|---|
| FNC 3.1–3.2 Problem solving as a search task | 61–65 |
| FNC 3.3.1 Hill climbing (Alg. 3.1–3.3) | 65–68 |
| FNC 3.3.2 Simulated annealing (Alg. 3.4–3.5) | 68–72 |
| FNC 3.5.4 Hill-climbing, simulated annealing, and genetic algorithms | 99–100 |

## 02 · Genetic algorithm

**Students build:**
- a population of routes, with **order crossover** and swap or inversion mutation. Single-point crossover on a route would visit some zones twice, so this is the place to explain why the encoding decides the operators;
- roulette-wheel selection and elitism, as in FNC;
- for comparison with the book, a **bit-string GA** (16 bits for the base station's x and y) with single-point crossover and bit-flip mutation, exactly as in FNC 3.5.2.

**They'll see:** the best route of each generation drawn boldly and up to 12 others faintly (`Trace.generation`, already built), with diversity collapsing.

| Read first | Pages |
|---|---|
| FNC 3.4.3 Basic principles of genetics | 76–82 |
| FNC 3.5.1–3.5.3 Standard EA, Genetic algorithms, Examples | 86–99 |
| CI Ch. 3 "Genetic Algorithms" through "Comments on Genetic Algorithms" | 51–67 |
| CI Ch. 4 "Genetic Algorithm Implementation" | 103–117 |

## 03 · Evolution strategies

**Students build:** real-valued base-station positions; Gaussian mutation; (μ + λ) and (μ, λ); the 1/5 success rule; self-adapting step sizes.

**They'll see:** a cloud of candidate base stations on the heat map, closing in, with σ plotted beside the energy.

**Industry tie:** evolution strategies (especially CMA-ES) are a standard tool for tuning continuous design parameters.

| Read first | Pages |
|---|---|
| FNC 3.6.1 Evolution strategies | 100–103 |
| CI Ch. 3 "Evolution Strategies" | 75–81 |

## 04 · Particle swarm

**Students build:** a swarm searching for the best place for **two** refill stations on farm 4 (four numbers). Each trip uses whichever station is better. Personal and global bests, inertia, velocity clamping.

**They'll see:** the swarm's particles moving over the field, with the global best marked.

**Industry tie:** particle swarms are widely used for facility placement and for tuning controller gains.

| Read first | Pages |
|---|---|
| FNC 5.4.1–5.4.5 Particle swarm | 246–256 |
| CI Ch. 3 "Particle Swarm Optimization" | 87–92 |
| CI Ch. 4 "Particle Swarm Optimization Implementation" | 118–142 |

## 05 · Ant colony: routes and safe paths

**Part A · Routes (the main lab).** Ants build spraying routes zone by zone, guided by pheromone and by distance. This is the Ant System paper's own problem, plus weight and refill trips.

**Part B · Safe paths.** So far `farmlab` has planned the way round obstacles for students. Here they do it themselves: a graph of waypoints round the farm's obstacles, and ants (then Dijkstra, for comparison) find the shortest safe path.

**They'll see:** zone-to-zone edges coloured by pheromone strength, fading as it evaporates.

**Viewer work needed:** edges coloured by a value (new frame fields).

| Read first | Pages |
|---|---|
| FNC 5.1–5.2.3 Ant colonies, foraging, ACO | 205–224 |
| Dorigo, Maniezzo & Colorni (1996), "Ant System", *IEEE Trans. SMC-B* 26(1), 29–41 (`ant-tsp-01.pdf` in the course files) | whole paper |

## 06 · A neural network learns the energy

**Students build:** a small multilayer perceptron trained by backpropagation on logged flights (generated by `farmlab`, with noise added). It learns to predict a leg's energy from distance, load and wind. They then use it as a fast stand-in for the real model inside a search, and measure how much worse the routes get.

| Read first | Pages |
|---|---|
| FNC 4.3 Artificial neural networks | 132–151 |
| FNC 4.4.3–4.4.4 LMS, error surfaces, MLP and backpropagation | 160–178 |
| CI Ch. 5 and Ch. 6 "Back-propagation Implementation" | 145–196, 218–235 |

## 07 · Fuzzy controller

**Students build:** a Mamdani fuzzy controller that keeps the drone at spraying height over the crop while wind gusts push it around. For example: "if the height error is LARGE NEGATIVE and falling, thrust is HIGH". It covers fuzzification, rules firing in parallel, and centroid defuzzification.

**They'll see:** the drone bobbing in gusts with a simple proportional controller, then holding steady with theirs, with live membership values for each rule.

| Read first | Pages |
|---|---|
| CI Ch. 7 Fuzzy systems, especially "Developing a Fuzzy Controller" | 269–314 |
| CI Ch. 8 "Evolving Fuzzy Rule Systems" (stretch) | 353–371 |

## 08 · A fleet of drones · idea

Two or three drones share one base. Which drone sprays which zones, and in what order? This is the vehicle routing problem, which is where GAs and ant colonies are used commercially for real.
