"""The bridge from Python to the 3D viewer: record what a search did, save it as JSON.

The file format is described in viewer/TRACE_FORMAT.md.

    from viewer.trace import Trace
    rec = Trace(farm, "hill-climbing", lab="01-route-search")
    ...  your algorithm calls rec.tried(...) / rec.moved(...) / rec.restart(...)
    rec.save()            # -> traces/01-route-search/<name>.json and traces/latest.json

Algorithms take `rec=NULL`. NULL ignores every call, so the
algorithms run at full speed when you aren't recording.
"""
import json
import os
import re
import time
from pathlib import Path

from farmlab.farms import BEST_KNOWN
from farmlab.flight import fly, plan_trips
from farmlab.world import DRONE, path

ROOT = Path(__file__).resolve().parent.parent
MAX_FRAMES = 30000


class _Null:
    def __getattr__(self, _):
        return lambda *a, **k: None


NULL = _Null()


def _farm_json(farm):
    return {
        "number": farm.number, "title": farm.title, "blurb": farm.blurb,
        "base": list(farm.base), "field": list(farm.field), "wind": list(farm.wind),
        "tank_l": farm.tank, "battery_wh": farm.battery,
        "zones": [{"name": z.name, "x": z.x, "y": z.y, "need_l": z.need_l, "w": z.w, "h": z.h} for z in farm.zones],
        "obstacles": [{"kind": o.kind, "rect": list(o.rect) if o.rect else None,
                       "circle": list(o.circle) if o.circle else None, "height": o.height, "label": o.label}
                      for o in farm.obstacles],
        "best_known_wh": BEST_KNOWN.get(farm.number) if _is_standard(farm) else None,
        "paths": _detours(farm),
    }


def _detours(farm):
    """Waypoints for every pair of stops that can't fly straight: {"i,j": [[x, y], ...]} (-1 = base)."""
    out = {}
    for i in range(-1, len(farm.zones)):
        for j in range(-1, len(farm.zones)):
            if i != j:
                p = path(i, j, farm)
                if len(p) > 2:
                    out[f"{i},{j}"] = [[round(x, 2), round(y, 2)] for x, y in p]
    return out


def _is_standard(farm):
    from farmlab.farms import FARMS
    return FARMS.get(farm.number) == farm


def _flight_json(flight, farm):
    legs = []
    for leg in flight.legs:
        legs.append({**{k: round(v, 3) if isinstance(v, float) else v for k, v in leg.items()},
                     "path": [[round(x, 2), round(y, 2)] for x, y in path(leg["from"], leg["to"], farm)]})
    return {"route": list(flight.route), "trips": flight.trips, "energy_wh": round(flight.energy_wh, 3),
            "distance_m": round(flight.distance_m, 2), "stranded": flight.stranded, "legs": legs}


class Trace:
    def __init__(self, farm, algo, note="", lab=""):
        self.farm, self.algo, self.note, self.lab = farm, algo, note, lab
        self.frames, self.dropped, self.evaluations = [], 0, 0
        self.started = time.time()

    def _add(self, frame):
        if len(self.frames) >= MAX_FRAMES:
            self.dropped += 1
            return
        self.frames.append(frame)

    def _route(self, kind, route, score, T=None, msg=None):
        route = [int(z) for z in route]
        f = {"k": kind, "o": route, "s": round(float(score), 3), "t": plan_trips(route, self.farm)}
        if T is not None:
            f["T"] = round(float(T), 6)
        if msg:
            f["m"] = msg
        self._add(f)

    def tried(self, route, score, accepted=False, T=None):
        """A route was scored. accepted=True if the search moved there."""
        self.evaluations += 1
        self._route("move" if accepted else "try", route, score, T)

    def moved(self, route, score, T=None):
        """The search moved to `route`, which it has already scored (so it isn't counted again)."""
        self._route("move", route, score, T)

    def restart(self, route, score, msg=None):
        """A new climb begins at `route` (iterated hill-climbing, or the very first route)."""
        self.evaluations += 1
        self._route("restart", route, score, None, msg)

    def generation(self, routes, scores, diversity=None):
        """A whole population (GA, ant colony...). The viewer draws the best route boldly and the rest faintly.

        routes: list of routes; scores: their scores (lower is better); diversity: optional number to plot.
        """
        self.evaluations += len(routes)
        k = min(range(len(scores)), key=lambda i: scores[i])
        best = [int(z) for z in routes[k]]
        self._add({"k": "gen", "o": best, "s": round(float(scores[k]), 3), "t": plan_trips(best, self.farm),
                   "P": [[int(z) for z in r] for r in routes],
                   "PT": [plan_trips([int(z) for z in r], self.farm) for r in routes], "S": [round(float(s), 2) for s in scores],
                   "mean": round(sum(scores) / len(scores), 3),
                   **({"d": round(float(diversity), 4)} if diversity is not None else {})})

    def note_text(self, text):
        """A message the viewer shows at this point in the replay."""
        if self.frames:
            self.frames[-1]["m"] = text

    # ------------------------------------------------------------------ saving
    def save(self, name=None, best=None, evaluations=None):
        """Write traces/<lab>/<name>.json and traces/latest.json (what the viewer watches).

        best: the route the drone flies at the end (default: the lowest-scoring frame).
        evaluations: how many routes were scored, if you counted them some other way.
        """
        farm = self.farm
        if best is None and self.frames:
            best = min(self.frames, key=lambda f: f["s"])["o"]
        data = {
            "id": f"{time.time():.3f}",
            "lab": self.lab,
            "algo": self.algo,
            "note": self.note,
            "drone": DRONE,
            "farm": _farm_json(farm),
            "best": _flight_json(fly(best, farm), farm) if best is not None else None,
            "evaluations": evaluations if evaluations is not None else self.evaluations,
            "dropped": self.dropped,
            "seconds": round(time.time() - self.started, 3),
            "frames": self.frames,
        }
        top = ROOT / "traces"
        out = top / self.lab if self.lab else top
        out.mkdir(parents=True, exist_ok=True)
        stem = name or f"F{farm.number}-" + re.sub(r"[^A-Za-z0-9]+", "-", self.algo).strip("-")
        text = json.dumps(data, separators=(",", ":"))
        (out / f"{stem}.json").write_text(text)
        _write_atomic(top / "latest.json", text)
        print(f"saved {(out / stem).relative_to(ROOT)}.json  ({len(self.frames)} frames"
              + (f", {self.dropped} not recorded" if self.dropped else "") + ")")
        return out / f"{stem}.json"


def _write_atomic(target, text):
    """Write to a temporary file, then rename: the viewer never reads a half-written file."""
    tmp = target.with_suffix(".tmp")
    tmp.write_text(text)
    os.replace(tmp, target)
