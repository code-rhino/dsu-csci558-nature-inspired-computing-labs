"""What a task looks like (a Farm), and how the drone gets from one spot to another.

Coordinates are metres on the ground: x points east, y points north. The base station is
where the drone takes off, refills its tank and swaps its battery.

A Farm lists the zones that need fertiliser, the obstacles in the way, and the wind.
Shared by every lab; the standard farms are in farmlab/farms.py.

The drone never flies through an obstacle: path(a, b, farm) finds the shortest way round,
keeping `clearance_m` (drone.json) away from every obstacle. Labs only search over the
ORDER of the zones; the flying-around is done for them.
"""
import heapq
import json
import math
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

DRONE = json.loads((Path(__file__).resolve().parent / "drone.json").read_text())


@dataclass(frozen=True)
class Zone:
    name: str                       # "Z1", "Z2", ... shown in the viewer
    x: float                        # centre of the zone, metres east
    y: float                        # centre of the zone, metres north
    need_l: float                   # litres of fertiliser this zone needs
    w: float = 20.0                 # zone size, metres (for drawing)
    h: float = 20.0


@dataclass(frozen=True)
class Obstacle:
    kind: str                       # "silo", "barn", "trees", "powerline" or "nofly" (how the viewer draws it)
    rect: tuple = None              # (x0, y0, x1, y1), or
    circle: tuple = None            # (x, y, radius)
    height: float = 10.0            # metres, for drawing only: the drone always goes round, never over
    label: str = ""


@dataclass(frozen=True)
class Farm:
    number: int                     # shown in the viewer as "Farm n"
    title: str
    base: tuple                     # (x, y) of the base station
    zones: tuple                    # Zone, ...
    field: tuple = (0.0, 0.0, 160.0, 100.0)   # (x0, y0, x1, y1): where the crop grows (for drawing)
    obstacles: tuple = ()           # Obstacle, ...
    wind: tuple = (0.0, 0.0)        # (east, north) in m/s: the direction the air moves
    tank_l: float = None            # None = drone.json's tank
    battery_wh: float = None        # None = drone.json's battery
    blurb: str = ""

    @property
    def tank(self):
        return self.tank_l if self.tank_l is not None else DRONE["tank_l"]

    @property
    def battery(self):
        return self.battery_wh if self.battery_wh is not None else DRONE["battery_wh"]

    def spot(self, i):
        """Where stop i is: -1 is the base, 0..n-1 are the zones."""
        return self.base if i < 0 else (self.zones[i].x, self.zones[i].y)


# ------------------------------------------------------------------ obstacles as polygons
def _polygon(ob, grow):
    """The obstacle as a convex polygon (counter-clockwise), grown outwards by `grow` metres."""
    if ob.rect:
        x0, y0, x1, y1 = ob.rect
        return [(x0 - grow, y0 - grow), (x1 + grow, y0 - grow), (x1 + grow, y1 + grow), (x0 - grow, y1 + grow)]
    cx, cy, r = ob.circle
    n = 12
    R = (r + grow) / math.cos(math.pi / n)          # the 12-gon goes round the circle, not inside it
    return [(cx + R * math.cos(2 * math.pi * k / n), cy + R * math.sin(2 * math.pi * k / n)) for k in range(n)]


def _cuts(a, b, poly):
    """True if the segment a-b passes through the inside of convex polygon `poly` (Cyrus-Beck clipping)."""
    t0, t1 = 0.0, 1.0
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = len(poly)
    for k in range(n):
        p, q = poly[k], poly[(k + 1) % n]
        nx, ny = q[1] - p[1], -(q[0] - p[0])       # outward normal of a counter-clockwise edge
        num = nx * (a[0] - p[0]) + ny * (a[1] - p[1])
        den = nx * dx + ny * dy
        if abs(den) < 1e-12:
            if num >= 0:
                return False                        # parallel to this edge and outside it
            continue
        t = -num / den
        if den < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 >= t1 - 1e-9:
            return False
    return t1 - t0 > 1e-6


def inside_obstacle(p, farm, grow=None):
    """True if point p is inside an obstacle (grown by the drone's clearance)."""
    grow = DRONE["clearance_m"] if grow is None else grow
    for ob in farm.obstacles:
        poly = _polygon(ob, grow)
        if all((q[0] - pp[0]) * (p[1] - pp[1]) - (q[1] - pp[1]) * (p[0] - pp[0]) > 0
               for pp, q in zip(poly, poly[1:] + poly[:1])):
            return True
    return False


def blocked(a, b, farm):
    """True if flying straight from a to b would come closer than the clearance to an obstacle."""
    return any(_cuts(a, b, _polygon(ob, DRONE["clearance_m"])) for ob in farm.obstacles)


# ------------------------------------------------------------------ shortest way round
@lru_cache(maxsize=None)
def _graph(farm):
    """Corners of every grown obstacle, plus base and zones: the points a shortest path can bend at."""
    polys = [_polygon(ob, DRONE["clearance_m"]) for ob in farm.obstacles]
    corners = [c for poly in (_polygon(ob, DRONE["clearance_m"] + 0.05) for ob in farm.obstacles) for c in poly]
    spots = [farm.base] + [(z.x, z.y) for z in farm.zones]
    nodes = spots + [c for c in corners if not any(_inside(c, p) for p in polys)]
    n = len(nodes)
    edges = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if not any(_cuts(nodes[i], nodes[j], p) for p in polys):
                d = math.dist(nodes[i], nodes[j])
                edges[i].append((j, d))
                edges[j].append((i, d))
    return nodes, edges


def _inside(c, poly):
    return all((q[0] - p[0]) * (c[1] - p[1]) - (q[1] - p[1]) * (c[0] - p[0]) > 0 for p, q in zip(poly, poly[1:] + poly[:1]))


@lru_cache(maxsize=None)
def _paths_from(farm, s):
    """Dijkstra from graph node s. Returns (dist, prev) over every node."""
    nodes, edges = _graph(farm)
    dist = [math.inf] * len(nodes)
    prev = [-1] * len(nodes)
    dist[s] = 0.0
    heap = [(0.0, s)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in edges[u]:
            if d + w < dist[v] - 1e-12:
                dist[v], prev[v] = d + w, u
                heapq.heappush(heap, (d + w, v))
    return dist, prev


def path(i, j, farm):
    """The waypoints the drone flies from stop i to stop j (-1 = base, 0.. = zones), as [(x, y), ...].

    A straight line [a, b] when nothing is in the way, otherwise the shortest way round.
    """
    s, t = i + 1, j + 1                         # graph node 0 is the base, then the zones
    if s == t:
        return [farm.spot(i)]
    dist, prev = _paths_from(farm, s)
    if math.isinf(dist[t]):
        raise ValueError(f"no way from {i} to {j} on farm {farm.number}: something is walled in")
    nodes = _graph(farm)[0]
    out = [t]
    while out[-1] != s:
        out.append(prev[out[-1]])
    return [nodes[k] for k in reversed(out)]


def flight_distance(i, j, farm):
    """Metres flown from stop i to stop j, going round obstacles."""
    p = path(i, j, farm)
    return sum(math.dist(a, b) for a, b in zip(p, p[1:]))
