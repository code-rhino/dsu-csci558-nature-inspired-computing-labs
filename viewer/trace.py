"""The bridge from Python to the 3D viewer: record what a search did, save it as JSON.

The file format is described in viewer/TRACE_FORMAT.md.

    from viewer.trace import Trace
    rec = Trace(level, "hill-climbing", lab="01-reach-search")
    ...  your algorithm calls rec.tried(...) / rec.moved(...) / rec.restart(...)
    rec.save()            # -> traces/01-reach-search/<name>.json and traces/latest.json

Algorithms take `rec=NULL`. NULL ignores every call, so the
algorithms run at full speed when you aren't recording.
"""
import json
import math
import re
import time
from pathlib import Path

from armlab.kinematics import ARM, tcp
from armlab.world import collides

ROOT = Path(__file__).resolve().parent.parent
MAX_FRAMES = 30000


class _Null:
    def __getattr__(self, _):
        return lambda *a, **k: None


NULL = _Null()


def _r(v, n=4):
    return [round(x, n) for x in v]


class Trace:
    def __init__(self, level, algo, note="", lab=""):
        self.level, self.algo, self.note, self.lab = level, algo, note, lab
        self.frames, self.dropped = [], 0
        self.started = time.time()

    def _add(self, kind, angles, score, T=None, msg=None):
        if len(self.frames) >= MAX_FRAMES:
            self.dropped += 1
            return
        f = {"k": kind, "a": _r(angles, 2), "s": round(float(score), 5), "p": _r(tcp(angles))}
        if collides(angles, self.level):
            f["c"] = 1                   # the pose hits the floor or an obstacle
        if T is not None:
            f["T"] = round(float(T), 6)
        if msg:
            f["m"] = msg
        self.frames.append(f)

    def tried(self, angles, score, accepted=False, T=None):
        """A candidate was scored. accepted=True if the search moved there."""
        self._add("move" if accepted else "try", angles, score, T)

    def moved(self, angles, score, T=None):
        """The search moved to `angles` (same as tried(..., accepted=True))."""
        self._add("move", angles, score, T)

    def restart(self, angles, score, msg=None):
        """A new climb begins at `angles` (iterated hill-climbing)."""
        self._add("restart", angles, score, None, msg)

    def generation(self, poses, scores, diversity=None):
        """A whole population (GA, ES, PSO...). The viewer draws every pose and moves the arm to the best.

        poses: list of poses; scores: their scores (lower is better); diversity: optional number to plot.
        """
        if len(self.frames) >= MAX_FRAMES:
            self.dropped += 1
            return
        k = min(range(len(scores)), key=lambda i: scores[i])
        best = poses[k]
        f = {"k": "gen", "a": _r(best, 2), "s": round(float(scores[k]), 5), "p": _r(tcp(best)),
             "P": [_r(p, 1) for p in poses], "S": [round(float(s), 4) for s in scores],
             "mean": round(sum(scores) / len(scores), 5)}
        if diversity is not None:
            f["d"] = round(float(diversity), 4)
        if collides(best, self.level):
            f["c"] = 1
        self.frames.append(f)

    def note_text(self, text):
        """A message the viewer shows at this point in the replay."""
        if self.frames:
            self.frames[-1]["m"] = text

    # ------------------------------------------------------------------ saving
    def _landscape(self, step=2):
        lv = self.level
        if len(lv.free) != 2:
            return None
        i, j = lv.free
        lo_i, hi_i = ARM["joints"][i]["min"], ARM["joints"][i]["max"]
        lo_j, hi_j = ARM["joints"][j]["min"], ARM["joints"][j]["max"]
        base = list(lv.start)
        rows = []
        for a in range(lo_i, hi_i + 1, step):
            row = []
            for b in range(lo_j, hi_j + 1, step):
                base[i], base[j] = a, b
                if collides(base, lv):
                    row.append(-1)
                else:
                    row.append(round(math.dist(tcp(base), lv.target), 4))
            rows.append(row)
        return {"joints": [i, j], "lo": [lo_i, lo_j], "step": step, "values": rows}

    def save(self, name=None, best=None):
        """Write traces/<lab>/<name>.json and traces/latest.json (what the viewer watches)."""
        lv = self.level
        if best is None and self.frames:
            best = min(self.frames, key=lambda f: f["s"])["a"]
        data = {
            "id": f"{time.time():.3f}",
            "lab": self.lab,
            "algo": self.algo,
            "note": self.note,
            "arm": ARM,
            "level": {
                "number": lv.number, "title": lv.title, "free": list(lv.free), "start": list(lv.start),
                "target": list(lv.target), "floor": lv.floor, "boxes": [list(map(list, b)) for b in lv.boxes],
                "down": list(lv.down) if lv.down else None, "blurb": lv.blurb,
            },
            "best": list(best) if best is not None else None,
            "evaluations": len(self.frames) + self.dropped,
            "dropped": self.dropped,
            "seconds": round(time.time() - self.started, 3),
            "landscape": self._landscape(),
            "frames": self.frames,
        }
        top = ROOT / "traces"
        out = top / self.lab if self.lab else top
        out.mkdir(parents=True, exist_ok=True)
        stem = name or f"L{lv.number}-" + re.sub(r"[^A-Za-z0-9]+", "-", self.algo).strip("-")
        text = json.dumps(data, separators=(",", ":"))
        (out / f"{stem}.json").write_text(text)
        (top / "latest.json").write_text(text)
        print(f"saved {(out / stem).relative_to(ROOT)}.json  ({len(self.frames)} frames"
              + (f", {self.dropped} not recorded" if self.dropped else "") + ")")
        return out / f"{stem}.json"
