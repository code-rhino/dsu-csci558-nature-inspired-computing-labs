"""The energy model: what a route costs. Shared by every lab.

A ROUTE is an order to visit the zones in, e.g. (2, 0, 3, 1): a permutation of 0..n-1.
fly(route, farm) turns it into trips and adds up the energy:

  * The drone loads exactly the fertiliser the next trip needs, takes off from the base,
    sprays the zones of that trip in route order, and flies home to refill and swap batteries.
  * A trip ends early (back to base) when the next zone's fertiliser wouldn't fit in the tank,
    or when the battery couldn't fly that trip and get home. This is plan_trips().
  * Energy for one leg (Wh) = wh_per_kg_m x mass on board (kg) x metres flown.
    The drone gets LIGHTER as it sprays, so the order changes what every later leg costs.
  * Wind: the drone spends the same power per second whatever the wind does, so a headwind
    costs more seconds and a tailwind fewer: each metre counts cruise / (cruise + wind along the path).

Numbers come from farmlab/drone.json. They're illustrative, picked so a leg can be checked
with a calculator: carrying 40 kg for 100 m costs 0.01 x 40 x 100 = 40 Wh.
"""
import math
from dataclasses import dataclass
from functools import lru_cache

from .world import DRONE, path

K = DRONE["wh_per_kg_m"]
EMPTY = DRONE["empty_mass_kg"]
KG_PER_L = DRONE["kg_per_l"]
CRUISE = DRONE["cruise_m_s"]


@lru_cache(maxsize=None)
def _effort(farm):
    """effort[i + 1][j + 1]: wind-adjusted metres from stop i to stop j (-1 = base). Equal to the
    flown distance when there's no wind; not symmetric when there is."""
    n = len(farm.zones)
    wx, wy = farm.wind
    table = [[0.0] * (n + 1) for _ in range(n + 1)]
    for i in range(-1, n):
        for j in range(-1, n):
            if i == j:
                continue
            p = path(i, j, farm)
            e = 0.0
            for a, b in zip(p, p[1:]):
                d = math.dist(a, b)
                along = (wx * (b[0] - a[0]) + wy * (b[1] - a[1])) / d if d else 0.0
                e += d * CRUISE / (CRUISE + along)
            table[i + 1][j + 1] = e
    return table


def leg_energy(i, j, mass_kg, farm):
    """Wh to fly from stop i to stop j (-1 = base) carrying a total of mass_kg (drone + fertiliser)."""
    return K * mass_kg * _effort(farm)[i + 1][j + 1]


def trip_energy(trip, farm):
    """Wh for one trip: base -> each zone of `trip` in order -> base, spraying as it goes."""
    E = _effort(farm)
    load = sum(farm.zones[z].need_l for z in trip) * KG_PER_L
    mass, here, wh = EMPTY + load, 0, 0.0
    for z in trip:
        wh += K * mass * E[here][z + 1]
        mass -= farm.zones[z].need_l * KG_PER_L
        here = z + 1
    return wh + K * mass * E[here][0]


def plan_trips(route, farm):
    """Split a route into trips, in order. A zone starts a new trip when adding it to the current one
    would overfill the tank or need more battery than a full charge. Returns a list of lists."""
    trips, cur, litres = [], [], 0.0
    for z in route:
        need = farm.zones[z].need_l
        if cur and (litres + need > farm.tank + 1e-9 or trip_energy(cur + [z], farm) > farm.battery + 1e-9):
            trips.append(cur)
            cur, litres = [], 0.0
        cur.append(z)
        litres += need
    if cur:
        trips.append(cur)
    return trips


@dataclass
class Flight:
    route: tuple
    trips: list                      # the route split into trips, e.g. [[2, 0], [3, 1]]
    energy_wh: float                 # total energy for every trip
    distance_m: float                # total metres flown
    legs: list                       # one dict per leg: from, to, load_l, mass_kg, metres, wh, battery_wh (left after it)
    stranded: int                    # trips that need more than a full battery (can't happen unless a zone is too far)

    @property
    def score(self):
        """Lower is better: the energy, plus 1,000 Wh for every trip the battery can't finish."""
        return self.energy_wh + 1000.0 * self.stranded


def check_route(route, farm):
    n = len(farm.zones)
    if sorted(route) != list(range(n)):
        raise ValueError(f"a route must visit each of the {n} zones exactly once (0..{n - 1}); got {list(route)}")


def fly(route, farm):
    """Fly a whole route. Returns a Flight with the trips, every leg, and the totals."""
    check_route(route, farm)
    E = _effort(farm)
    trips = plan_trips(route, farm)
    legs, total, metres, stranded = [], 0.0, 0.0, 0
    for trip in trips:
        litres = sum(farm.zones[z].need_l for z in trip)
        battery = farm.battery
        here = -1
        for z in trip + [-1]:
            mass = EMPTY + litres * KG_PER_L
            p = path(here, z, farm)
            d = sum(math.dist(a, b) for a, b in zip(p, p[1:]))
            wh = K * mass * E[here + 1][z + 1]
            battery -= wh
            legs.append({"from": here, "to": z, "load_l": litres, "mass_kg": mass, "metres": d, "wh": wh,
                         "battery_wh": battery})
            total += wh
            metres += d
            if z >= 0:
                litres -= farm.zones[z].need_l
            here = z
        if battery < -1e-9:
            stranded += 1
    return Flight(tuple(route), trips, total, metres, legs, stranded)


def route_score(route, farm):
    """The number every search minimises, in Wh: the same as fly(route, farm).score, only faster.
    Lower is better."""
    check_route(route, farm)
    total, stranded = 0.0, 0
    for trip in plan_trips(route, farm):
        wh = trip_energy(trip, farm)
        total += wh
        stranded += wh > farm.battery + 1e-9
    return total + 1000.0 * stranded
