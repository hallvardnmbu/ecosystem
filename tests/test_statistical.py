"""
Tests the interfaces between the units/modules of Biosim.
"""


from biosim.animals import Herbivore, Carnivore
from biosim.island import Island
import scipy.stats as stat
from math import isclose
from math import log
import random
import pytest


# %% Fixtures:

@pytest.fixture
def trial_animals():
    """
    Creates a list of animals to be used in the tests.
    After the test is done, the animals are reset to their default values.
    """

    # Setup:
    age = 0
    weight = 1
    animals = [Herbivore(age, weight), Carnivore(age, weight)]
    for animal in animals:
        animal.set_parameters(animal.default_parameters())
        animal.set_motion()
    yield animals

    # Cleanup:
    for animal in animals:
        animal.a = age
        animal.w = weight
        animal.set_parameters(animal.default_parameters())


# @pytest.fixture
# def trial_island_10():
#     """
#     Creates an island with animals.
#     """
#
#     # Setup:
#     geography = "WWWWW\nWWDWW\nWDDDW\nWWDWW\nWWWWW"
#     ini_pop = [{"loc": (3, 3), "pop": [{"species": "Herbivore", "age": 5, "weight": 20} for _ in
#                                        range(10)]}]
#     island = Island(geography, ini_pop)
#
#     yield island


@pytest.fixture
def trial_island_1000():
    """
    Creates an island with animals.
    """

    # Setup:
    geography = "WWWWW\nWWDWW\nWDDDW\nWWDWW\nWWWWW"
    ini_pop = [{"loc": (3, 3), "pop": [{"species": "Herbivore", "age": 5, "weight": 20} for _ in
                                       range(1000)]}]
    island = Island(geography, ini_pop)

    yield island


# %% animals.py:

def test_lognormv(trial_animals):
    """Tests that the lognormv function works correctly."""

    for animal in trial_animals:

        sample_size = 1000
        weights = [animal.lognormv() for _ in range(sample_size)]
        log_weights = [log(weight) for weight in weights]

        # Shapiro-Wilk test. A low p-value indicates that we are uncertain of uniformity.
        # Retrieved from scipy.stats.shapiro.
        _, p_val = stat.shapiro(log_weights)

        # If the p-value is below the confidence level, we reject the null hypothesis (uniformity).
        assert p_val > 0.01, "(WILL SOMETIME FAIL) Weights are not normally distributed (p < 0.01)."


# %% island.py:

def test_migration_over_time():
    """
    Tests that the migration works as intended over time.
    """

    pop_sizes = [random.randint(1000, 2000) for _ in range(20)]  # Different population sizes.
    geo = """\
             WWWWWWW
             WLLLLLW
             WLLLLLW
             WLLLLLW
             WLLLLLW
             WWWWWWW"""
    migrated = []  # List of relative migrated pop to desired location.

    for n in pop_sizes:
        random.seed(n)
        pop = [{"species": "Herbivore", "age": 0, "weight": 2000} for _ in range(n)]
        ini_pop = [{"loc": (4, 4), "pop": pop}]
        island = Island(geography=geo, ini_pop=ini_pop)

        # Set the parameters so that the animals will migrate (and don't die).
        island.species_map["Herbivore"].set_parameters({'mu': 1,
                                                        'omega': 0,
                                                        'gamma': 0,
                                                        'eta': 0,
                                                        'F': 0,
                                                        'a_half': 10000})
        island.set_fodder_parameters(island.default_fodder_parameters())

        # Run the migration for 2 years.
        island.yearly_cycle()
        island.yearly_cycle()

        _, _, n_animals_per_species_per_cell = island.animals()

        animals = n_animals_per_species_per_cell[(4, 6)]["Herbivore"]

        migrated.append(animals / n)

    mean = sum(migrated)/len(migrated)

    assert isclose(0.25**2, mean, rel_tol=0.09), "Migration is wrongly distributed."


def test_death_rate(trial_island_1000):
    """
    Tests that the animals dying rate is correct.
    """

    for animal in trial_island_1000.animals()[0]["Herbivore"]:
        animal.set_parameters({"omega": 0.5})
        animal.w = 1
        fitness = animal.fitness

    num_years = 10
    for _ in range(num_years):
        trial_island_1000.death()

    expected = (1-0.5*(1-fitness))**num_years * 1000 + 10  # +10 to add a little bit of wiggle room.

    assert trial_island_1000.animals()[1]["Herbivore"] <= expected, "The death rate is incorrect."



def test_procreation_over_time():
    """
    Tests that the procreation works as intended over time.
    """

    # Big population for high probability of procreation.
    pop_sizes = [random.randint(1000, 2000) for _ in range(20)] # different population sizes]
    geo = """\
             WWWWWWW
             WLLLLLW
             WLLLLLW
             WLLLLLW
             WLLLLLW
             WWWWWWW"""

    relative_procreation=[]        # list of new population

    for n in pop_sizes:
        pop = [{"species": "Herbivore", "age": 1, "weight": 2000} for _ in range(n)]
        ini_pop=[{"loc": (4, 4), "pop": pop}]
        island = Island(geography=geo, ini_pop=ini_pop)

        # In order to make 100 percent of animals to procreate.
        #mocker.patch("_update_p_procreate", return_value=1)
        island.species_map["Herbivore"].set_parameters({'gamma': 10000})
        # Let the fodder be enough for the animals.
        island.set_fodder_parameters({"L": 80000})

        # Run the procreation for 3 years.
        island.feed()
        island.procreate()
        island.feed()
        island.procreate()
        island.feed()
        island.procreate()

        _, n_species, _ = island.animals()
        p = sum(n_species.values())
        relative_procreation.append(p/n)

    mean = sum(relative_procreation)/len(relative_procreation)
    wanted= 2**3
    limit= 0.05

    assert math.isclose(wanted, mean, rel_tol=limit), "Procreated incorrectly."
