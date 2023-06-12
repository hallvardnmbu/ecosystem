"""
Tests for the simulation module.
"""

from src.biosim.simulation import BioSim
from src.biosim.animals import Animal
from pytest_mock import mocker
from pytest import approx
import pytest


@pytest.fixture
def trial_simulation():
    """
    Creates a simulations to be used in the tests.
    After the test is done, the simulation is reset to its default values.
    """

    # Setup:
    sim_population = [{"loc": (2, 2), "pop": [{"species": "Herbivore",
                                               "age": 5,
                                               "weight": 20} for _ in range(150)]},
                      {"loc": (2, 2), "pop": [{"species": "Carnivore",
                                               "age": 5,
                                               "weight": 20} for _ in range(40)]}]
    sim = BioSim(island_map="WWWWW\nWLHDW\nWWWWW", ini_pop=sim_population, seed=1)

    yield sim

    # Cleanup:
    sim = BioSim(island_map="WWWWW\nWLHDW\nWWWWW", ini_pop=sim_population, seed=1)


@pytest.fixture
def trial_simulation_empty():
    """
    Creates a simulations without animals to be used in the tests.
    """

    # Setup:
    sim = BioSim(island_map="WWWWW\nWLHDW\nWWWWW", ini_pop=[], seed=1)

    yield sim

    # Cleanup:
    sim = BioSim(island_map="WWWWW\nWLHDW\nWWWWW", ini_pop=[], seed=1)


@pytest.mark.parametrize("param, val",
                         [["eta", 0.1],
                          ["a_half", 40],
                          ["phi_age", 0.6],
                          ["w_half", 10]])
def test_set_animal_parameters(trial_simulation, param, val):
    """
    Tests that the parameters are set correctly.
    """

    new_parameter = {param: val}
    trial_simulation.set_animal_parameters("Herbivore", new_parameter)

    assert Animal.mapping()["Herbivore"].get_parameters()[param] == val, "Setting parameters " \
                                                                         "didn't work."


def test_set_invalid_animal_parameter_keys(trial_simulation):
    """
    Tests that wrong parameter key cannot be set.
    """

    with pytest.raises(KeyError):
        trial_simulation.set_animal_parameters("Herbivore", {"a": 2})
        get_param = Animal.mapping()["Herbivore"].get_parameters()["a"]
        assert get_param == 2, "Setting wrong parameter key worked."


@pytest.mark.parametrize("param, val",
                         [["eta", -1],
                          ["eta", "a"],
                          ["eta", [1]],
                          ["eta", ["a"]],
                          ["eta", {"a": 1}]])
def test_set_invalid_animal_parameter_value_type(trial_simulation, param, val):
    """
    Tests that wrong parameter value types cannot be set.
    """

    with pytest.raises(ValueError):
        trial_simulation.set_animal_parameters("Herbivore", {param: val})
        get_param = Animal.mapping()["Herbivore"].get_parameters()[param]
        assert get_param == val, "Setting wrong parameter values worked."


@pytest.mark.parametrize("param, val",
                         [["eta", -1],
                          ["eta", "a"],
                          ["eta", [1]],
                          ["eta", ["a"]],
                          ["eta", {"a": 1}]])
def test_set_invalid_animal_parameter_values(trial_simulation, param, val):
    """
    Tests that wrong parameter value types cannot be set.
    """

    with pytest.raises(ValueError):
        trial_simulation.set_animal_parameters("Herbivore", {param: val})
        get_param = Animal.mapping()["Herbivore"].get_parameters()[param]
        assert get_param == val, "Setting wrong parameter values worked."


def test_year_construction(trial_simulation):
    """
    Tests that the year increases correctly when simulating.
    """

    assert trial_simulation.island.year == 0, "Year is not constructed correctly."


def test_year_increase(trial_simulation):
    """
    Tests that the year increases correctly when simulating.
    """

    num_years = 10
    trial_simulation.simulate(num_years)

    assert trial_simulation.island.year == num_years, "Year is not increasing correctly."


def test_add_population(trial_simulation_empty):
    """
    Tests that the number of animals increases correctly when simulating.
    """

    animal = [{"loc": (2, 2), "pop": [{"species": "Herbivore",
                                       "age": 5,
                                       "weight": 20}]}]
    trial_simulation_empty.add_population(animal)

    assert trial_simulation_empty.num_animals == 1, "Population is not added correctly."



