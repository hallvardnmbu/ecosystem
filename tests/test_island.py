from biosim.island import Island
import pytest


# Each individual test should have a descriptive name
# When a test fails, the first thing you read is the name
# Should describe what was tested and failed
# Should write a docstring to further explain the test

def test_add_population(island):
    """Tests that the population is added correctly."""
    test_island = Island(ini_pop=[{"loc": (2, 2),"pop": [{"species": "Carnivore" }]}])
    test_island.add_population([{"loc": (2, 2),"pop": [{"species": "Herbivore" }]}])
    assert animals.size() == 2, "The population was not added correctly."

