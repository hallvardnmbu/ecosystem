"""
Tests the interfaces between the units/modules of Biosim.
"""

from src.biosim.animals import Herbivore, Carnivore
from src.biosim.island import Island
from src.biosim.simulation import BioSim
import scipy.stats as stat
from math import log
import random
import pytest
seed = 123456


def test_migration_over_time():
    """
    Tests that the migration works as intended over time.
    """

    # Setup:

    pop_sizes = [random.randint(1000, 20000) for _ in range(100)] # different population sizes]
    geo = "WWWWWW\n"
          "WLLLLW\n"
          "WLLLLW\n"
          "WLLLLW\n"
          "WWWWWW"
    migrated=[]        # list of relative migrated pop to desired location

    for n in pop_sizes:
        pop = [{"species": "Herbivore", "age": 0, "weight": 2000} for _ in range(n)]
        ini_pops.append({"loc": (4, 4), "pop": pop})
        island = Island(geography=geo, ini_pop=ini_pop)

        # Set the parameters so that the animals will migrate (and don't die).
        island.species_map["Herbivore"].set_parameters({'mu': 1, 'omega': 0, 'gamma': 0, 'eta': 0, 'F': 0, 'a_half': 10000})
        island.set_fodder_parameters(island.default_fodder_parameters())

        # Run the migration for 2 years.
        island.yearly_cycle()
        island.yearly_cycle()

        a, b, n_animals_per_species_per_cell= island.animals()

        migrated.append(island.n_animals_per_species_per_cell["Herbivore"][(2, 2)]/n)

    limit= 0.05
    wanted = 100*0.25**2
    _, p_val = stat.shapiro(migrated)

    assert p_val > limit, "the migration is not close to normal distribution"


