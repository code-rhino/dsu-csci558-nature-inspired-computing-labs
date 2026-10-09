# Trace format

A trace is one JSON file describing one run of a search. `viewer/trace.py` writes it, and `viewer/index.html` reads it. You only need this page if you want to write traces some other way, for example from another language, or to extend the viewer.

```jsonc
{
  "id": "1760000000.123",          // changes on every save; the viewer reloads when it changes
  "lab": "01-reach-search",        // shown above the title; also the traces/ subfolder
  "algo": "simulated annealing",
  "note": "3 sa --seed 1",         // free text, shown after the title
  "arm": { ... },                  // a full copy of armlab/arm.json, so a trace replays on its own
  "level": {
    "number": 3, "title": "Around the post · 3 motors", "blurb": "…",
    "free": [0, 1, 2],             // joint indices the search may change
    "start": [0, 0, 0, 0, 0, 0],
    "target": [1.0, 1.6, 0.0],
    "floor": true,
    "boxes": [[[0.5, 0.0, -0.25], [0.8, 1.1, 0.25]]],   // [min corner, max corner]
    "down": null                   // or a direction the gripper must point, e.g. [0, -1, 0]
  },
  "best": [0, 90, -90, 0, 0, 0],   // the pose "Move to best" goes to
  "evaluations": 4001,
  "dropped": 0,                    // frames over the 30,000 cap (counted, not stored)
  "seconds": 1.23,
  "landscape": {                   // only when exactly two joints are free, otherwise null
    "joints": [1, 2], "lo": [-90, -150], "step": 2,
    "values": [[1.41, 1.39, …], …] // values[i][j]: distance at (lo0 + i·step, lo1 + j·step); -1 = collision
  },
  "frames": [
    { "k": "restart", "a": [0,0,0,0,0,0], "s": 1.414, "p": [2.0, 0.6, 0.0] },
    { "k": "try",     "a": [0,10,0,0,0,0], "s": 1.169, "p": [...], "T": 0.5 },
    { "k": "move",    "a": [0,10,0,0,0,0], "s": 1.169, "p": [...], "m": "optional message" }
  ]
}
```

## Frames

| Field | Meaning |
|---|---|
| `k` | `restart`: a new climb starts here. `try`: a pose was scored but not moved to (drawn as the ghost arm). `move`: the search moved here (the solid arm follows). |
| `a` | the six joint angles in degrees |
| `s` | the score; **lower is better** |
| `p` | the tool tip that Python computed, used for the "Python and 3D agree" check |
| `c` | `1` if this pose hits the floor or an obstacle. The viewer turns the arm red. Searches that use a penalty may visit such poses. |
| `T` | optional temperature, plotted as the dashed line |
| `m` | optional message, shown in "What's happening" |

**Population frames** (`k: "gen"`, written by `Trace.generation`) describe a whole generation. `a`, `s` and `p` are its best member. They also have `P` (every member's pose), `S` (their scores), `mean` (the average score) and optionally `d` (diversity). The viewer draws every member as a thin skeleton coloured by rank, and moves the solid arm to the best.

## How the viewer uses it

- **The solid arm** is at the most recent `move`, `restart` or `gen` frame.
- **"Best so far"** is the lowest `s` among `move` and `restart` frames.
- **"Worse moves taken"** counts `move` frames whose score is higher than the previous position's.
