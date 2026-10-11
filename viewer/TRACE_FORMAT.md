# Trace format

A trace is one JSON file describing one run of a search. `viewer/trace.py` writes it, and `viewer/index.html` reads it. You only need this page if you want to write traces some other way, for example from another language, or to extend the viewer.

```jsonc
{
  "id": "1760000000.123",          // changes on every save; the viewer reloads when it changes
  "lab": "00-start-here",          // shown above the title; also the traces/ subfolder
  "algo": "random search",
  "note": "--farm 3",              // free text, shown after the title
  "drone": { ... },                // a full copy of farmlab/drone.json, so a trace replays on its own
  "farm": {
    "number": 3, "title": "Obstacles · 14 zones", "blurb": "…",
    "base": [-15, 50],             // metres: x east, y north
    "field": [0, 0, 160, 100],     // where the crop grows
    "wind": [-2, -1],              // m/s the air moves (east, north)
    "tank_l": 20, "battery_wh": 500,
    "zones": [{ "name": "Z1", "x": 10, "y": 10, "need_l": 4, "w": 20, "h": 20 }, …],
    "obstacles": [{ "kind": "silo", "rect": null, "circle": [100, 40, 4], "height": 16, "label": "silo" }, …],
    "best_known_wh": 329.2,        // null for a farm that isn't one of farmlab/farms.py's
    "paths": { "-1,4": [[-15, 50], [23.05, 58.95], …], … }   // detours round obstacles; any pair not listed is a straight line
  },
  "best": {                        // the route the drone flies at the end, worked out leg by leg by farmlab.flight.fly
    "route": [4, 12, 11, 7, …], "trips": [[4, 12, 11, 7], …],
    "energy_wh": 329.196, "distance_m": 996.1, "stranded": 0,
    "legs": [{ "from": -1, "to": 4, "load_l": 20, "mass_kg": 45, "metres": 101.2, "wh": 45.5,
               "battery_wh": 454.5, "path": [[-15, 50], …] }, …]
  },
  "evaluations": 2001,             // routes scored (moved() doesn't count: the route was already scored)
  "dropped": 0,                    // frames over the 30,000 cap (counted, not stored)
  "seconds": 1.23,
  "frames": [
    { "k": "restart", "o": [0, 1, 2, …], "s": 530.0, "t": [[0, 1, 2, 3], …] },
    { "k": "try",     "o": [3, 1, 0, …], "s": 512.4, "t": [...], "T": 0.5 },
    { "k": "move",    "o": [3, 1, 0, …], "s": 512.4, "t": [...], "m": "optional message" }
  ]
}
```

Stops are numbered **−1 for the base**, then 0, 1, 2… for the zones in `farm.zones` order.

## Frames

| Field | Meaning |
|---|---|
| `k` | `restart`: a new climb starts here. `try`: a route was scored but not moved to (drawn as the blue dashed route). `move`: the search moved here (the coloured route follows). |
| `o` | the route: zone numbers in the order they're sprayed |
| `s` | the score in Wh; **lower is better** |
| `t` | the route split into trips back to base (from `farmlab.flight.plan_trips`), so the viewer can draw it |
| `T` | optional temperature, plotted as the dashed line. If `algo` contains "stochastic", the narration uses stochastic hill-climbing's acceptance rule, 1/(1 + e^(Δ/T)); otherwise annealing's, e^(−Δ/T). |
| `m` | optional message, shown in "What's happening". Playback pauses briefly on it. |

**Population frames** (`k: "gen"`, written by `Trace.generation`) describe a whole generation. `o`, `s` and `t` are its best member. They also have `P` (every member's route), `PT` (their trips), `S` (their scores), `mean` (the average score) and optionally `d` (diversity). The viewer draws the best route boldly and up to 12 others faintly.

## How the viewer uses it

- **The coloured route** is the most recent `move`, `restart` or `gen` frame, one colour per trip.
- **"Best so far"** is the lowest `s` among `move`, `restart` and `gen` frames.
- **"Worse moves taken"** counts `move` frames whose score is higher than the previous position's.
- **The flight** replays `best.legs`: battery and tank gauges come straight from Python's numbers. The viewer recomputes every leg's energy from `drone`, `farm` and the leg's `path`, and checks each path stays `clearance_m` from every obstacle. It shows "✓ Python and the viewer agree" or a red warning.
- **Spraying** is drawn as back-and-forth passes over the zone. That's for show: the energy model counts flying from zone centre to zone centre, and doesn't charge for spraying, take-off or landing.
