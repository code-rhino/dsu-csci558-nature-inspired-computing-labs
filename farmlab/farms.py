"""The standard farms, from easy to hard. Labs use these (or define their own Farm).

The crop field runs 160 m east by 100 m north and is cut into 20 m x 20 m cells. A soil test
says which cells need fertiliser and how much: those are the zones. The base station sits
just off the west edge.

    1  One tank         8 zones, all in one trip. 40,320 orders: brute force gives the answer key.
    2  Refill runs      14 zones, 3+ tank loads: the route is split into trips back to base.
    3  Obstacles        farm 2 plus a windbreak, a silo, a power line, a barn and a no-fly zone.
    4  Wind and an      farm 3 with a steady wind and a smaller battery, so flying out and
       old battery     flying back cost different amounts, and trips get shorter.
"""
from .world import Farm, Obstacle, Zone

BASE = (-15.0, 50.0)


def _zones(spec):
    """(column, row, litres) on the 20 m grid -> Zones named Z1, Z2, ..."""
    return tuple(Zone(f"Z{k + 1}", 10.0 + 20 * c, 10.0 + 20 * r, float(need)) for k, (c, r, need) in enumerate(spec))


ONE_TANK = _zones([(6, 4, 5), (1, 1, 1), (3, 3, 3), (7, 0, 2), (2, 4, 4), (4, 1, 1), (5, 2, 2), (1, 3, 2)])

REFILL = _zones([(0, 0, 4), (1, 2, 6), (2, 4, 3), (3, 1, 5), (4, 3, 7), (5, 0, 2), (6, 2, 4),
                 (7, 4, 6), (7, 1, 3), (2, 2, 2), (4, 0, 5), (6, 4, 3), (5, 3, 4), (1, 4, 5)])

OBSTACLES = (
    Obstacle("trees", rect=(58.0, 20.0, 62.0, 80.0), height=12.0, label="windbreak"),
    Obstacle("silo", circle=(100.0, 40.0, 4.0), height=16.0, label="silo"),
    Obstacle("powerline", rect=(88.0, 59.5, 175.0, 60.5), height=11.0, label="power line"),
    Obstacle("barn", rect=(100.0, 82.0, 122.0, 98.0), height=9.0, label="barn"),
    Obstacle("nofly", rect=(0.0, 62.0, 20.0, 100.0), height=30.0, label="no-fly: farmhouse"),
)

FARMS = {
    1: Farm(1, "One tank · 8 zones", BASE, ONE_TANK,
            blurb="Eight zones need 20 L between them: exactly one tank, so it's a single trip. "
                  "Which order costs the least energy?"),
    2: Farm(2, "Refill runs · 14 zones", BASE, REFILL,
            blurb="59 L to spray with a 20 L tank. The route is split into trips back to base to refill; "
                  "the order decides how the trips fall."),
    3: Farm(3, "Obstacles · 14 zones", BASE, REFILL, obstacles=OBSTACLES,
            blurb="Same zones as farm 2, but now a windbreak, a silo, a power line, a barn and the "
                  "farmhouse's no-fly zone are in the way. The drone flies round them."),
    4: Farm(4, "Wind and an old battery · 14 zones", BASE, REFILL, obstacles=OBSTACLES,
            wind=(-2.0, -1.0), battery_wh=135.0,
            blurb="A steady wind from the north-east, and a worn battery that holds 135 Wh. "
                  "Flying into the wind costs more, and trips have to be shorter."),
}


# The lowest energy anyone has found for each farm (Wh). Farm 1's is exact: every one of its 40,320
# orders was tried. The others come from many long runs of local search and annealing, so a
# better route may exist: if you beat one, that's worth telling your instructor about.
BEST_KNOWN = {1: 143.4, 2: 309.8, 3: 329.2, 4: 433.3}


def get_farm(n):
    return FARMS[n]
