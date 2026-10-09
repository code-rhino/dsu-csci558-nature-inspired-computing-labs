# Lab 02 · recorded example runs

Runs of a finished `ga.py`. They're traces only, with no code. From the repo root:

```bash
python3 -m viewer.show labs/02-genetic-algorithm/examples       # list them
python3 -m viewer.show labs/02-genetic-algorithm/examples/1     # play number 1
```

| # | Run | What to look for |
|---|---|---|
| 1 | Level 1, defaults (30 arms, 60 generations) | The thin arms start scattered across the scene and collapse onto the target. In the **landscape** panel the white dots crowd onto the bright spot. Finishes 1.7 cm away. |
| 2 | Level 1, **no mutation** (`--pm 0`), seed 1 | Diversity drains from about 8 bits to 0.5. The population freezes 18 cm from the target, with nothing left to recombine. |
| 3 | Level 1, **no crossover** (`--pc 0`) | Mutation alone still gets there, but compare the diversity and the average line with example 1. |
| 4 | Level 2, around the post, seed 1 | The population finds the elbow-up route over the post. |
| 5 | Level 2, seed 0 | **The backwards-reach trap** again: the base swings to 170° and the arm reaches over its head, 17.7 cm short. GAs fall into it too. |
| 6 | Level 3, six motors, 60 arms × 150 generations, seed 1 | 48-bit chromosomes. The gripper ends up 2.0 cm from the part, pointing within 0.5° of straight down. |

The population is drawn as thin skeletons coloured green (best) to red (worst). The orange arm is each generation's best.
