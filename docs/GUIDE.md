# Project guide

The technical side: how the code is organised, the arm's exact geometry, what the viewer can do, how to add a lab, and fixes for common problems. For what the project *is*, see the [main README](../README.md).

## How it's organised

```
armlab/                  the shared arm: no lab logic, no 3D code
  arm.json               link lengths, joint axes, joint limits (single source of truth)
  kinematics.py          angles → position of every joint and the tool tip
  world.py               Level (target, obstacles, which motors move) + collides()

viewer/                  everything 3D: no lab logic
  __main__.py, serve.py  python3 -m viewer: a tiny local web server
  index.html             the three.js viewer
  trace.py               Trace: how Python sends a run to the viewer
  demo.py                python3 -m viewer.demo
  show.py                python3 -m viewer.show <trace or folder>: replay saved runs
  TRACE_FORMAT.md        the JSON a trace contains

labs/
  00-start-here/         type-along starter: the README holds all the code; finished/ has the answers
  01-reach-search/       one folder per lab: README, your stub file, tests, run script, levels, examples/
  02-genetic-algorithm/  the GA lab (population frames: Trace.generation)
  _template/             copy this to start a new lab

tests/test_platform.py   checks for armlab/ and viewer/trace.py
traces/                  saved runs, one folder per lab (ignored by git)
```

A lab never imports three.js and the viewer never imports a lab. They only meet in a trace file:

```
labs/<lab>/your_code.py ──► viewer.trace.Trace ──► traces/latest.json ──► viewer/index.html
            │                                                                   │
            └──────────── armlab/arm.json ◄──── both read the same arm ─────────┘
```

**The viewer checks the Python side.** For every pose it shows, it compares where `armlab/kinematics.py` said the tool tip was against where three.js actually drew it. It shows `✓ Python and the 3D arm agree (0.04 mm)`, or a red warning if they ever disagree.

## The arm

```
          A4 twist   A5 wrist   A6 flange
   A3 elbow ●═════════●══════●═══╡▸  ← tool tip (between the fingers)
           ║
           ║  upper arm 1.0 m          elbow → tool tip 1.0 m
           ║                           (0.35 + 0.40 + 0.15 + 0.10)
   A2 shoulder ●   ← 0.6 m above the floor
           ▐█▌  A1 base (turns the whole arm left and right)
         ▀▀▀▀▀▀▀
```

| Joint | Name | Turns about | Range |
|---|---|---|---|
| A1 | base | y (vertical) | −170° … 170° |
| A2 | shoulder | z | −90° … 180° |
| A3 | elbow | z | −150° … 150° |
| A4 | forearm twist | x (along the forearm) | −180° … 180° |
| A5 | wrist | z | −120° … 120° |
| A6 | flange | x | −180° … 180° |

- **Coordinates:** x forward, y up, z toward the viewer (the three.js convention). Units are metres and degrees.
- **All joints at 0:** the arm points straight forward along +x, and the tool tip is at (2.0, 0.6, 0).
- **Rest pose** (`home` in `arm.json`): folded up at (0°, 100°, −145°, 0°, −80°, 0°). The viewer opens with the arm there.
- **Rotation direction:** positive angles follow the right-hand rule, so positive A2 and A3 lift the arm.
- **Changing the arm:** edit `armlab/arm.json`. Python and the viewer both pick up the change. Run `python3 tests/test_platform.py` afterwards.

## The viewer

- **Playback:** play, step and scrub through a run. The solid orange arm is the pose the search is currently at. The blue ghost is the pose being *tried*. The coloured line is the path of the tool tip.
- **Run stats:** moves, rejections, **worse moves taken**, restarts and temperature, plus a chart of the score over the run.
- **Landscape:** for 2-motor levels, a heat map of the score over both joints, with the search path drawn on it. Click it to jump the arm there.
- **Manual jog:** a slider per motor, with a live readout of the tool tip and its distance to the target. Useful for checking hand calculations.
- **Move to best:** plays the final answer as one smooth motion.
- **New runs:** the viewer picks up each run you save automatically. To replay an older one, use `python3 -m viewer.show <file>`, **Open trace…**, or drag and drop.
- **Keys:** space plays and pauses; ← and → step one frame.

## Adding a lab

1. Copy the template: `cp -r labs/_template labs/02-your-topic`. It already runs: `python3 labs/02-your-topic/run.py`.
2. Define your tasks in `levels.py`.
3. Replace the random search in `run.py` with your algorithm. Split it into a stub file and tests if other students will fill it in, like lab 01 does.
4. Record with `Trace(level, "algorithm name", lab="02-your-topic")`:
   - `rec.tried(pose, score, accepted)` for each pose scored;
   - `rec.restart(pose, score)` when a new run starts;
   - `rec.save()` at the end.
5. Write the lab's README and add a row to the Labs table in the [main README](../README.md).

If a new lab needs something the viewer can't show yet, add it to `viewer/` and document it in `viewer/TRACE_FORMAT.md`. Lab code should still go through `Trace`.

## Troubleshooting

| Problem | Fix |
|---|---|
| `Port 8765 is busy` | The viewer is already running in another terminal. Use that one, or `python3 -m viewer 8766`. |
| The page is blank or grey | three.js loads from cdn.jsdelivr.net, so you need an internet connection. |
| "Opened as a file" message | You opened `index.html` directly. Start it with `python3 -m viewer` instead, or drag a trace onto the page. |
| A run doesn't appear | Check `traces/latest.json` was updated (`run.py` prints `saved …`), and that the **play new runs** box is ticked. |
