# Template lab

Not a lab, just a starting point. `run.py` does random search, the simplest possible baseline, and sends it to the viewer:

```bash
python3 -m viewer                          # terminal 1, repo root
python3 labs/_template/run.py --tries 500  # terminal 2
```

To start a new lab:

1. `cp -r labs/_template labs/02-your-topic`
2. **Add a "Read first" table to your README** (book, section, pages, what it's for) before the first step. Every lab here has one; see [lab 01](../01-reach-search/README.md#read-first). Planned labs and their readings are in [docs/ROADMAP.md](../../docs/ROADMAP.md).
3. Edit `levels.py` with your targets, obstacles, and which motors move.
4. Replace `random_search` in `run.py` with your algorithm. Keep the `rec.tried(...)` / `rec.save()` calls so the viewer can replay it.
5. Rewrite this README for your lab, and add it to the table in the main README.

`run.py` uses three shared pieces:
- `armlab.kinematics`: `tcp(pose)`, `tool_direction(pose)`, `LIMITS`;
- `armlab.world`: `Level`, `collides(pose, level)`;
- `viewer.trace`: `Trace`.

[`viewer/TRACE_FORMAT.md`](../../viewer/TRACE_FORMAT.md) describes what a trace records.
