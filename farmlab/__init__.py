"""farmlab: the shared farm and drone. No lab logic and no viewer code lives here.

    farmlab/drone.json   the drone: mass, tank, battery, energy per kg per metre
    farmlab/world.py     Zone, Obstacle, Farm, and path(): the way round obstacles
    farmlab/flight.py    the energy model: plan_trips(), fly(), route_score()
    farmlab/farms.py     the standard farms, from an open field to obstacles and wind
"""
