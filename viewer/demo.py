"""Check the viewer works. Needs no lab code.

    python3 -m viewer        # in one terminal
    python3 -m viewer.demo   # in another

Shows three routes on the obstacle farm, each better than the last, then the drone flies the last one.
"""
from farmlab.farms import BEST_KNOWN, get_farm
from farmlab.flight import route_score
from viewer.trace import Trace

farm = get_farm(3)
rec = Trace(farm, "demo", lab="demo", note="three hand-picked routes, then the drone flies the last one")

routes = [
    (list(range(14)), "Zones in name order, Z1 to Z14: the obvious route, and an expensive one."),
    ([1, 9, 2, 13, 4, 12, 11, 7, 8, 6, 5, 10, 3, 0], "Always the nearest zone next: much better."),
    ([0, 9, 1, 13, 2, 3, 10, 5, 8, 6, 4, 12, 11, 7],
     f"West side first, then east: better again. The best known is {BEST_KNOWN[3]} Wh; finding it is what the labs are about."),
]
for k, (route, text) in enumerate(routes):
    s = route_score(route, farm)
    if k == 0:
        rec.restart(route, s, text)
    else:
        rec.moved(route, s)
        rec.note_text(text)
rec.save("demo", routes[-1][0])
