"""
Tests the interfaces between the units/modules of Biosim.
"""


from src.biosim.animals import Herbivore, Carnivore
from src.biosim.island import Island
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

def test_birthweight(trial_animals):
    """Tests that the birthweight function works correctly."""

    for animal in trial_animals:

        sample_size = 1000
        weights = [animal.birthweight() for _ in range(sample_size)]
        log_weights = [log(weight) for weight in weights]

        # Shapiro-Wilk test. A low p-value indicates that we are uncertain of uniformity.
        # Retrieved from scipy.stats.shapiro.
        _, p_val = stat.shapiro(log_weights)

        # If the p-value is below the confidence level, we reject the null hypothesis (uniformity).
        assert p_val > 0.01, "(WILL SOMETIME FAIL) Weights are not normally distributed (p < 0.01)."


# %% island.py:

# def test_migration_over_time():
#     """
#     Tests that the migration works as intended over time.
#     """
#
#     pop_sizes = [random.randint(1000, 2000) for _ in range(20)]  # Different population sizes.
#     geo = """\
#              WWWWWWW
#              WLLLLLW
#              WLLLLLW
#              WLLLLLW
#              WLLLLLW
#              WWWWWWW"""
#     migrated = []  # List of relative migrated pop to desired location.
#
#     for n in pop_sizes:
#         random.seed(n)
#         pop = [{"species": "Herbivore", "age": 0, "weight": 2000} for _ in range(n)]
#         ini_pop = [{"loc": (4, 4), "pop": pop}]
#         island = Island(geography=geo, ini_pop=ini_pop)
#
#         # Set the parameters so that the animals will migrate (and don't die).
#         island.species_map["Herbivore"].set_parameters({'mu': 1,
#                                                         'omega': 0,
#                                                         'gamma': 0,
#                                                         'eta': 0,
#                                                         'F': 0,
#                                                         'a_half': 10000})
#         island.set_fodder_parameters(island.default_fodder_parameters())
#
#         # Run the migration for 2 years.
#         island.yearly_cycle()
#         island.yearly_cycle()
#
#         _, _, n_animals_per_species_per_cell = island.animals()
#
#         animals = n_animals_per_species_per_cell[(4, 6)]["Herbivore"]
#
#         migrated.append(animals / n)
#
#     mean = sum(migrated)/len(migrated)
#
#     assert isclose(0.25**2, mean, rel_tol=0.09), "Migration is wrongly distributed."


def test_procreation_over_time(trial_island_1000, mocker):
    """
    Tests that the procreation works as intended over time.
    """

    trial_island_1000.species_map["Herbivore"].set_parameters({'gamma': 100000,
                                                               'zeta': 0})
    # All baby-weights are 0:
    mocker.patch("random.lognormvariate", return_value=0)

    num_years = 5
    for _ in range(num_years):
        trial_island_1000.procreate()
        # Sets the new (and old) generation's weight to 20.
        for animal in trial_island_1000.animals()[0]["Herbivore"]:
            animal.w = 20

    n_species = trial_island_1000.animals()[1]["Herbivore"]
    expected = (2)**num_years * 1000

    assert n_species == expected, "Procreated incorrectly."


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
