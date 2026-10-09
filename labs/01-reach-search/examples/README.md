# Lab 01 · recorded example runs

These are runs of a finished version of lab 01, saved as traces. You can **watch** them without seeing any solution code: they show what correct behaviour looks like, including the failures you should expect.

```bash
python3 -m viewer                                          # terminal 1, repo root
python3 -m viewer.show labs/01-reach-search/examples       # list them
python3 -m viewer.show labs/01-reach-search/examples/1     # play number 1
```

| # | Run | What to look for |
|---|---|---|
| 1 | Level 1, hill-climbing, 10° steps | Stops at (20°, 60°), 35 cm short. Scroll to **Landscape**: the bright valley runs diagonally and one-motor moves can't follow it. |
| 2 | Same, with `--diagonal` | Moving both motors together reaches (0°, 90°) in 9 moves. |
| 3 | Level 1, hill-climbing, 1° steps | Smaller steps don't fix it. It stops stretched straight at the target, 59 cm away. |
| 4 | Level 1, brute force | The answer key: every pose on a 2° grid. The best-so-far line drops in steps. |
| 5 | Level 2, iterated hill-climbing, 8 restarts | Each restart is a jump in the score chart. Some random restarts begin **inside the floor**: the arm turns red, and the climb has to get out before it can improve. |
| 6 | Level 1, stochastic hill-climbing, T = 0.2 | T is too high: about half the moves are worse ones and the arm wanders. Compare **worse moves taken** with **moves**. |
| 7 | Level 3, simulated annealing, seed 0 | Wild at first, settling as T (dashed line) cools. Finishes elbow-up over the post. |
| 8 | Level 3, simulated annealing, seed 1 | **The trap:** the base swings round to 170° and the arm reaches backwards over its head, 17 cm short. Press **Move to best** to see it. |
| 9 | Level 4, simulated annealing, 6 motors, w = 0.2 | All six motors, with the gripper pointing straight down at the crate. |

**Red arm:** lab 01 *penalises* collisions instead of forbidding them, so a search may try poses that go through the post or the floor. They just score badly. The viewer turns those poses red. Between two frames the arm is animated in a straight line, so it can appear to pass through the post even when both poses are clear: the replay is a sequence of poses the search tried, not a planned motion.

When your own `climb.py` works, your runs with the same commands and seeds should look like these (the command is shown in the viewer's title).
