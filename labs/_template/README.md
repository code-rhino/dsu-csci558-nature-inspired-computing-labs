# Template lab

Not a lab, just a starting point. `run.py` does random search over spraying routes, the simplest possible baseline, and sends it to the viewer:

```bash
python3 -m viewer                                   # terminal 1, repo root
python3 labs/_template/run.py --farm 3 --tries 500  # terminal 2
```

To start a new lab:

1. `cp -r labs/_template labs/01-your-topic`
2. **Add a "Read first" table to your README** (book, section, pages, what it's for) before the first step. Every lab here has one; see [lab 00](../00-start-here/README.md#read-first). Planned labs and their readings are in [docs/ROADMAP.md](../../docs/ROADMAP.md).
3. Pick farms from `farmlab/farms.py`, or define your own `Farm` (zones, obstacles, wind, tank and battery sizes).
4. Replace `random_search` in `run.py` with your algorithm. Keep the `rec.tried(...)` / `rec.save()` calls so the viewer can replay it.
5. Rewrite this README for your lab, and add it to the table in the main README.

`run.py` uses three shared pieces:
- `farmlab.farms`: `get_farm(n)`, `BEST_KNOWN`;
- `farmlab.flight`: `route_score(route, farm)` (fast), `fly(route, farm)` (every leg and trip);
- `viewer.trace`: `Trace`.

[`viewer/TRACE_FORMAT.md`](../../viewer/TRACE_FORMAT.md) describes what a trace records.
