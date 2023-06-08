from biosim.island import Island
import pytest


# Each individual test should have a descriptive name
# When a test fails, the first thing you read is the name
# Should describe what was tested and failed
# Should write a docstring to further explain the test
# organise test types in classes?

SEED = 112233


@pytest.fixture
def reset_parameters():
    """Resets the class parameters to their default values."""
    yield


@pytest.fixture(autouse=True)
def make_test_island():

    """Creates a island with a simple geography and a single carnivore
        to test functions on."""

    test_geography = """\
                        WWWWW
                        WWLWW
                        WWWWW"""

    test_pop = [{"loc": (2, 3),"pop": [{"species": "Carnivore" }]}]

    return Island(ini_pop=test_pop, geography=test_geography)


def test_add_population():

    """Tests that the population is added correctly."""
    test_island=make_test_island()

    test_island.add_population([{"loc": (2, 3),"pop": [{"species": "Herbivore" }]}])
    assert test_island.n_animals == 2, "The population was not added correctly."

