"""
Tests for the island module.
"""

# Each individual test should have a descriptive name
# When a test fails, the first thing you read is the name
# Should describe what was tested and failed
# Should write a docstring to further explain the test

from src.biosim.animals import Herbivore, Carnivore
from src.biosim.island import Island
from unittest import mock
from pytest import approx
import pytest

# We used the lecture notes, ChatGPT and Stackoverflow in order to gain a basic understanding of how
# to structure the tests. ChatGPT and Stackoverflow were used as a "teacher", and did not author
# any of the code we used.

# Stackoverflow was used in order to find out how to test if an error is raised properly. Source:
# https://stackoverflow.com/questions/23337471/how-to-properly-assert-that-an-exception-gets
# -raised-in-pytest


@pytest.fixture
def trial_islands():
    """
    Creates a list of islands to be used in the tests.
    After the test is done, the islands are reset to their default values.
    """

    # Setup:
    islands = [Island(geography="WWWW\nWLHW\nWWWW"), Island(geography="WWW\nWHW\nWWW")]

    yield islands

    # Cleanup:
    for island in islands:
        Herbivore.set_parameters(Herbivore.default_parameters())
        Carnivore.set_parameters(Carnivore.default_parameters())
        island.set_fodder_parameters(island.default_fodder_parameters())
        island.year = 0


@pytest.fixture
def reset_animal_params():
    """Fixture resetting animal parameters."""

    yield

    # Cleanup:
    Herbivore.set_parameters(Herbivore.default_parameters())
    Carnivore.set_parameters(Carnivore.default_parameters())


def test_default_parameters(trial_islands):
    """Tests that the default parameters are set correctly."""

    for island in trial_islands:
        for terrain_type in island.default_fodder_parameters().keys():
            assert island.get_fodder_parameter(terrain_type) \
                   == island.default_fodder_parameters()[terrain_type], \
                   "Parameters are wrongly constructed."


@pytest.mark.parametrize("dict_key, dict_value",
                         [["H", 1],
                          ["L", 1],
                          ["D", 1],
                          ["W", 1]])
def test_set_parameters(trial_islands, dict_key, dict_value):
    """Tests that the parameters are set correctly."""

    for island in trial_islands:
        new_parameters = {dict_key: dict_value}
        island.set_fodder_parameters(new_parameters)
        assert island.get_fodder_parameter(dict_key) == dict_value, \
            "Setting parameters didn't work."


@pytest.mark.parametrize("dict_key, dict_value",
                         [["H", -1],
                          ["L", -1],
                          ["D", -1],
                          ["W", -1]])
def test_set_parameters_negative(trial_islands, dict_key, dict_value):
    """Tests that error is raised when negative parameters are passed."""

    with pytest.raises(ValueError):
        for island in trial_islands:
            new_parameters = {dict_key: dict_value}
            island.set_fodder_parameters(new_parameters), "Setting negative parameters worked."


@pytest.mark.parametrize("dict_key, dict_value",
                         [["S", 1],
                          ["2", 1],
                          ["A", 1],
                          ["s", 1]])
def test_set_parameters_nonexistent(trial_islands, dict_key, dict_value):
    """Tests that error is raised when nonexistent parameters are passed."""

    with pytest.raises(KeyError):
        for island in trial_islands:
            new_parameters = {dict_key: dict_value}
            island.set_fodder_parameters(new_parameters), "Setting nonexistent parameters worked."


@pytest.mark.parametrize("dict_key, dict_value",
                         [["H", "a"],
                          ["L", Herbivore],
                          ["D", (1, 2, 3)],
                          ["W", [1, 2, 3]]])
def test_set_parameters_non_numeric(trial_islands, dict_key, dict_value):
    """Tests that error is raised when other than numeric parameters are passed."""

    with pytest.raises(ValueError):
        for island in trial_islands:
            new_parameters = {dict_key: dict_value}
            island.set_fodder_parameters(new_parameters), "Setting non-numeric parameters worked."


def test_island_map_edges_row():
    """Tests that error is raised when the island map has edges that are not water."""

    geography = """WWW\nWLW\nWLW"""
    with pytest.raises(ValueError):
        Island(geography=geography), "Island map with edges that are not water was accepted."


def test_island_map_edges_col():
    """Tests that error is raised when the island map has edges that are not water."""

    geography = """WWW\nWLL\nWWW"""
    with pytest.raises(ValueError):
        Island(geography=geography), "Island map with edges that are not water was accepted."


def test_island_map_rectangle():
    """Tests that error is raised when the island map is not rectangular."""

    geography = """WWW\nWLW\nWW"""
    with pytest.raises(ValueError):
        Island(geography=geography), "Island map that is not rectangular was accepted."


def test_island_map_invalid():
    """Tests that error is raised when the island map contains invalid characters."""

    geography = """WWW\nWSW\nWWW"""
    with pytest.raises(ValueError):
        Island(geography=geography), "Island map with invalid characters was accepted."


def test_add_population(trial_islands):
    """Tests that the population is added correctly."""

    for island in trial_islands:
        animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore"}]}]
        island.add_population(animal)
        herbivores = island.n_animals_per_species["Herbivore"]
        assert island.n_animals == 1, "The population was not added correctly."
        assert herbivores == 1, "The population was not added correctly."


def test_n_animals_in_cell(trial_islands):
    """Tests that the population is added correctly."""

    for island in trial_islands:
        animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore"}]}]
        island.add_population(animal)
        animals_in_cell = island.cells[(2, 2)].n_animals_in_cell()
        assert animals_in_cell["Herbivore"] == 1, "The population was not added correctly."
        assert animals_in_cell["Carnivore"] == 0, "The population was not added correctly."


def test_add_population_in_water(trial_islands):
    """Tests that error is raised when the population is added to an invalid location."""

    for island in trial_islands:
        animal = [{"loc": (1, 1), "pop": [{"species": "Herbivore"}]}]
        with pytest.raises(ValueError):
            island.add_population(animal), "Population was added to water."


def test_add_population_in_outside_map(trial_islands):
    """Tests that error is raised when the population is added to an invalid location."""

    for island in trial_islands:
        animal = [{"loc": (100, 100), "pop": [{"species": "Herbivore"}]}]
        with pytest.raises(ValueError):
            island.add_population(animal), "Population was added outside the map."


def test_add_population_wrong_species(trial_islands):
    """Tests that error is raised when the population is added with an invalid animal."""

    for island in trial_islands:
        animal = [{"loc": (2, 2), "pop": [{"species": "a"}]}]
        with pytest.raises(ValueError):
            island.add_population(animal), "Population was added with an invalid animal."


@pytest.mark.parametrize("dict_key, dict_value",
                          [["age", -2],
                          ["weight", -2],
                          ["age", "a"],
                          ["weight", "a"]])
def test_add_population_wrong_pop_values(trial_islands, dict_key, dict_value):
    """Tests that error is raised when the population is added with an invalid animal."""

    for island in trial_islands:
        animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore", dict_key: dict_value}]}]
        with pytest.raises(ValueError):
            island.add_population(animal), "Population was added with an invalid parameter."


@pytest.mark.parametrize("pos, f",
                         [[(2, 1), Island.default_fodder_parameters()["W"]],
                          [(2, 2), Island.default_fodder_parameters()["L"]],
                          [(2, 3), Island.default_fodder_parameters()["H"]],
                          [(2, 4), Island.default_fodder_parameters()["D"]]])
def test_island_cells_fodder(pos, f):
    """Tests that the island cells are created correctly."""

    island = Island(geography="WWWWW\nWLHDW\nWWWWW")
    assert island.cells[pos].fodder == f, "The island cells were not constructed correctly."


def test_procreate(trial_islands):
    """Tests that the animals procreate correctly."""

    for island in trial_islands:
        animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore", "age": 1, "weight": 100}]}]
        island.add_population(animal)

        # In order to make sure that the animals procreate, we set gamma to 100.
        Herbivore.set_parameters({"gamma": 100})

        island.procreate()

        assert island.n_animals == 2, "Procreated incorrectly."

        assert len(island.cells[(2, 2)].animals["Herbivore"]) == 2, "Procreated incorrectly."


def test_procreate_no_procreation(trial_islands):
    """Tests that the animals do not procreate when gamma is 0."""

    for island in trial_islands:
        animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore", "age": 1, "weight": 100}]}]
        island.add_population(animal)

        # In order to make sure that the animals DO NOT procreate, we set gamma to 0.
        Herbivore.set_parameters({"gamma": 0})

        island.procreate()

        assert island.n_animals == 1, "Procreated when not supposed to."

        length = len(island.cells[(2, 2)].animals["Herbivore"])
        assert length == 1, "Procreated when not supposed to."


def test_feed(trial_islands):
    """Tests that the animals feed correctly."""

    for island in trial_islands:
        animals = [{"loc": (2, 2), "pop": [{"species": "Herbivore", "age": 0, "weight": 20},
                                           {"species": "Carnivore", "age": 0, "weight": 20}]}]
        island.add_population(animals)

        cell = island.cells[(2, 2)]

        # Set the parameters so that the carnivore will eat the herbivore.
        Herbivore.set_parameters({"phi_age": 0, "phi_weight": 0.01})
        Carnivore.set_parameters({"phi_age": 100, "phi_weight": 100, "DeltaPhiMax": 0.1})
        cell.animals["Carnivore"][0].a = -1

        island.feed()

        assert cell.fodder == island.get_fodder_parameter(cell.cell_type) - Herbivore.F,\
            "The herbivore did not feed correctly."
        assert len(cell.animals["Herbivore"]) == 0, \
            "The carnivore did not feed correctly."


def test_population():
    """Tests that the population list is created correctly."""

    geogr = "WWWWW\nWWLWW\nWLLLW\nWWLWW\nWWWWW"
    pop = [{"loc": (3, 3), "pop": [{"species": "Herbivore", "age": 5,
                                   "weight": 20} for _ in range(10)]},
           {"loc": (3, 4), "pop": [{"species": "Carnivore", "age": 5,
                                    "weight": 20} for _ in range(5)]}]

    island = Island(geogr, pop)

    pop = 0
    for species in island.population.values():
        pop += len(species)

    assert pop == 15, "The population list was not created correctly."


def test_migrate(reset_animal_params):
    """Tests that the animals migrate correctly."""

    geogr = "WWWWW\nWWLWW\nWLLLW\nWWLWW\nWWWWW"
    ini_pop_herbs = [{"loc": (3, 3), "pop": [{"species": "Herbivore", "age": 0, "weight": 50000}]}]
    ini_pop_carns = [{"loc": (3, 3), "pop": [{"species": "Carnivore", "age": 0, "weight": 50000}]}]

    island = Island(geogr, ini_pop_carns+ini_pop_herbs)

    # Set the parameters so that the animals will migrate (and don't die).
    Herbivore.set_parameters({'mu': 1, 'omega': 0, 'gamma': 0, 'eta': 0, 'F': 0, 'a_half': 10000})
    Carnivore.set_parameters({'mu': 1, 'omega': 0, 'gamma': 0, 'eta': 0, 'F': 0, 'a_half': 10000})

    # all animals should have moved from their initial position
    island.migrate()
    for species in ["Herbivore", "Carnivore"]:
        assert island.n_animals_per_species_per_cell[(3, 3)][species] \
            == 0, "Some animals did not migrate."

    n = island.n_animals
    for _ in range(10):
        island.migrate()
        # number of animals should not change
        assert island.n_animals == n, \
            "The animals did not migrate correctly. Number of animals of island changed."


def test_migrate_to_water(reset_animal_params):
    """Tests that the animals migrate correctly."""

    island = Island(geography="WWW\nWLW\nWWW")

    animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore", "age": 0, "weight": 20}]}]
    island.add_population(animal)

    # Set the parameters so that the animals will migrate (and don't die).
    Herbivore.set_parameters({"mu": 100, "omega": 0})

    island.migrate()

    length = len(island.cells[(2, 2)].animals["Herbivore"])
    assert length == 1, "The animals did not migrate correctly."
    assert island.n_animals == 1, "The animals did not migrate correctly."


def test_aging(reset_animal_params):
    """Tests that the animals age correctly."""

    island = Island(geography="WWW\nWLW\nWWW")

    animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore", "age": 0, "weight": 20}]}]
    island.add_population(animal)

    # Set the parameters so that the animals will stay alive.
    Herbivore.set_parameters({"omega": 0})

    num_years = 10
    for _ in range(num_years):
        island.ageing()
    age = island.cells[(2, 2)].animals["Herbivore"][0].a

    assert age == num_years, "The animals did not age correctly."


def test_lose_weight_year(reset_animal_params):
    """Tests that the animals lose weight correctly."""

    island = Island(geography="WWW\nWLW\nWWW")

    animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore", "age": 0, "weight": 20}]}]
    island.add_population(animal)

    # Set the parameters so that the animals will stay alive.
    Herbivore.set_parameters({"omega": 0, "eta": 0.99})

    num_years = 10
    for _ in range(num_years):
        island.weight_loss()
    weight = island.cells[(2, 2)].animals["Herbivore"][0].w

    assert weight == approx(0), "Weight did not decrease correctly."


def test_death(reset_animal_params, mocker):
    """Tests that the animals die correctly."""

    island = Island(geography="WWW\nWLW\nWWW")

    animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore", "age": 0, "weight": 20}]}]
    island.add_population(animal)

    # Set the parameters so that the animals will die.
    Herbivore.set_parameters({"omega": 100})

    island.death()

    length = len(island.cells[(2, 2)].animals["Herbivore"])
    assert length == 0, "The animals did not die correctly."
    assert island.n_animals == 0, "The animals did not die correctly."


def test_yearly_cycle(trial_islands):
    """Tests that the new year function works correctly."""

    for island in trial_islands:

        num_years = 10
        for _ in range(num_years):
            island.yearly_cycle()

        assert island.year == num_years, "The new year function did not work correctly."
