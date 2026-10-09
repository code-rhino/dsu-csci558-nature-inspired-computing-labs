# Lab roadmap

The labs follow the order of the CSCI 558 course modules, so each one can be used when the class reaches that topic. Every lab gets the same treatment:
- a **Read first** table (book, section, pages);
- by-hand exercises before code;
- stubs and tests;
- recorded example runs;
- no solution code in the shared repo.

**Books:** FNC = de Castro, *Fundamentals of Natural Computing*. CI = Eberhart & Shi, *Computational Intelligence: Concepts to Implementations*.

| Lab | Status | Course module · topic |
|---|---|---|
| 00 · Start here | ✅ ready | Module 2 intro |
| 01 · Reach search | ✅ ready | Module 2 · search, hill-climbing, annealing |
| 02 · Genetic algorithm | ✅ ready | Module 2 · topic 4, GA |
| 03 · Evolution strategies | next | Module 2 · topic 6, ES |
| 04 · Particle swarm | planned | Module 2 · topic 8, PSO |
| 05 · Ant colony: task order and safe paths | planned | Swarm intelligence (Ant System paper) |
| 06 · A neural network learns to reach | planned | Module 3 · topics 10–12, ANN |
| 07 · Fuzzy controller | planned | Module 4 · topic 15, fuzzy logic |
| 08 · A real robot model (URDF) | idea | Ties the labs to ROS 2 / industry tools |

Labs 02–04 all need one viewer feature, **showing a whole population in each frame**. It was built with lab 02 (`Trace.generation`), so 03 and 04 get it for free.

### What "ready" means for a lab

A lab is ready to hand to students when it has all of these:

- [ ] `README.md` with a **Read first** table, then numbered steps: by hand → write → check → see it
- [ ] a stub file (every function `raise NotImplementedError`) and a test file, run as `python3 test_x.py N`
- [ ] `run.py` with `--runs N` for success rates over seeds 0..N-1, recording through `viewer.trace.Trace(..., lab="NN-name")`
- [ ] `levels.py` (or shared levels), with start poses that don't collide
- [ ] a Part E experiments table, with measured results behind a fold
- [ ] `examples/`: recorded runs of a finished version (traces only) plus a "what to look for" README
- [ ] a reference solution in the private instructor kit, passing every test
- [ ] a row in the main README's Labs table, and its status updated here

---

## 02 · Genetic algorithm ✅

[Ready](../labs/02-genetic-algorithm/README.md). The plan it was built from:


**Students build:**
- a population of arm poses, each encoded as a bit string (8 bits per motor, so 48 bits for six motors);
- roulette-wheel selection, single-point crossover and bit-flip mutation;
- a run loop that records every generation.

**They'll see:**
- a cloud of ghost arms that tightens around the target generation by generation;
- the best and average score per generation;
- population diversity (Hamming distance) collapsing.

**Experiments:**
- crossover-only vs. mutation-only;
- population size;
- elitism;
- how the GA compares against lab 01's methods for the same number of evaluations.

| Read first | Pages |
|---|---|
| FNC 3.4 Evolutionary biology (skim; read 3.4.3 Basic principles of genetics) | 73–86 |
| FNC 3.5.1–3.5.3 Standard evolutionary algorithm, Genetic algorithms, Examples | 86–99 |
| CI Ch. 3 "Genetic Algorithms" through "Comments on Genetic Algorithms" (includes the schema theorem) | 51–67 |
| CI Ch. 4 "Genetic Algorithm Implementation" | 103–117 |

## 03 · Evolution strategies

**Students build:**
- real-valued angles with no bit strings;
- Gaussian mutation;
- (μ + λ) and (μ, λ) selection;
- the 1/5 success rule;
- self-adapting step sizes.

**They'll see:**
- the step size σ shrinking as the population homes in, plotted beside the score;
- a population of ghost arms, using lab 02's viewer feature.

**Experiments:**
- plus vs. comma selection;
- fixed vs. self-adapted σ;
- ES vs. GA on the six-motor level, where real numbers suit the problem better than bits.

**Industry tie:** evolution strategies (especially CMA-ES) are a standard tool for tuning robot controllers and searching for robot policies, and OpenAI (2017) showed ES can stand in for reinforcement learning on some control tasks. This is the most "industry" lab on the list.

| Read first | Pages |
|---|---|
| FNC 3.6.1 Evolution strategies | 100–103 |
| CI Ch. 3 "Evolution Strategies" (Selection; Key issues) | 75–81 |

## 04 · Particle swarm

**Students build:**
- particles that are arm poses, each with a velocity;
- personal best and global best;
- inertia weight and velocity clamping.

**They'll see:**
- a swarm of arms converging, with faint trails showing each particle's velocity;
- the global best marked on screen.

**Experiments:**
- inertia weight;
- global vs. ring (local) neighbourhoods;
- swarm size vs. number of iterations for a fixed evaluation budget.

**Industry tie:** particle swarms are widely used to tune controller gains, where each particle is one set of gains. A stretch step can tune a simple joint controller instead of a pose.

| Read first | Pages |
|---|---|
| FNC 5.4 Social adaptation of knowledge: 5.4.1 Particle swarm through 5.4.5 Summary | 246–256 |
| CI Ch. 3 "Particle Swarm Optimization" | 87–92 |
| CI Ch. 4 "Particle Swarm Optimization Implementation" | 118–142 |

## 05 · Ant colony: task order and safe paths

Two parts, both real industrial problems:

**Part A · Task order (the main lab).** The arm must visit 10 weld points (or pick 10 parts). In what order? It's the travelling salesman problem, exactly what the Ant System paper solves, with "distance" being how far the motors have to turn between poses.

**Part B · A safe path.** A search finds the final pose, but the replay can still pass *through* the post on the way there. Plan a **collision-free path** from the rest pose to the target through a graph of safe waypoint poses.

**Students build:**
- the tour-length (or path-cost) function;
- ants that build tours, lay pheromone and let it evaporate;
- a comparison with a greedy nearest-neighbour tour (Part A) and Dijkstra's shortest path (Part B).

**They'll see:**
- the arm touching each point in the chosen order;
- edges coloured by pheromone strength;
- the arm moving along a path around the post.

**Viewer work needed:** draw tour and graph edges, coloured by a value (new frame fields), and several targets at once.

**Experiments:**
- evaporation rate;
- α vs. β (pheromone vs. distance);
- number of ants.

| Read first | Pages |
|---|---|
| FNC 5.1–5.2.3 Introduction; Ant colonies; Ant foraging; Ant colony optimization (S-ACO and general ACO) | 205–224 |
| Dorigo, Maniezzo & Colorni (1996), "Ant System: Optimization by a Colony of Cooperating Agents", *IEEE Trans. SMC-B* 26(1), 29–41 (`ant-tsp-01.pdf` in the course files) | whole paper |

## 06 · A neural network learns to reach

**Students build:**
- a training set generated by forward kinematics: random poses, each paired with where its gripper ends up;
- a small multilayer perceptron, trained by backpropagation, that maps target → angles (two motors first);
- a comparison of its instant answer with lab 01's search.

**They'll see:**
- the network's guess as a ghost arm next to the true pose;
- the error shrinking over training epochs.

**Experiments:**
- hidden-layer size;
- learning rate;
- why the network averages the elbow-up and elbow-down answers into a wrong one.

| Read first | Pages |
|---|---|
| FNC 4.3 Artificial neural networks (neurons, architectures, learning approaches) | 132–151 |
| FNC 4.4.3 ADALINE, LMS, error surfaces; 4.4.4 Multi-layer perceptron and backpropagation | 160–178 |
| CI Ch. 5 Neural network concepts and paradigms | 145–196 |
| CI Ch. 6 "Back-propagation Implementation" | 218–235 |

## 07 · Fuzzy controller

**Students build:** a Mamdani fuzzy controller that moves the arm over time. For example: "if the elbow error is LARGE POSITIVE, turn the elbow FAST". It covers fuzzification, rules firing in parallel, and centroid defuzzification.

**They'll see:**
- smooth, human-like motion toward the target;
- live membership values for each rule.

**Experiments:**
- the number and shape of membership functions;
- a fuzzy controller vs. a simple proportional controller;
- (stretch) tuning the rules with lab 02's GA, as in CI Ch. 8.

**Industry tie:** fuzzy control is used in appliances, cameras and process control. It turns an expert's rules of thumb into a controller without a mathematical model.

| Read first | Pages |
|---|---|
| CI Ch. 7 Fuzzy systems concepts and paradigms, especially "Developing a Fuzzy Controller" | 269–314 (controller: 301–313) |
| CI Ch. 8 "Evolving Fuzzy Rule Systems" (stretch) | 353–371 |

## 08 · A real robot model (URDF) · idea

**Why:** the labs use a made-up arm defined in `armlab/arm.json`. Real robots are described in **URDF**, the robot-description format ROS 2 and MoveIt use. Loading a real arm's URDF would let students run their lab 01–04 solvers on a real robot's geometry and joint limits, and compare against a standard inverse-kinematics solver such as KDL.

**Needs:** a URDF reader in `armlab/` that produces the same joint list as `arm.json` (offsets, axes, limits), and the viewer drawing the robot's meshes (the `urdf-loader` library for three.js). Check the model's licence before bundling it.

| Read first | Pages |
|---|---|
| ROS 2 / MoveIt documentation on URDF and kinematics plugins | online |

---

**Not planned:** genetic programming (FNC 3.6.3). Evolving programs doesn't map naturally onto reaching with an arm, and forcing it would make a confusing lab. If a GP lab is wanted, a better fit is evolving a *controller expression* for lab 07's task.
