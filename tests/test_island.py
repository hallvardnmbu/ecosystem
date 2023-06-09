from biosim.island import Island
import pytest


# Each individual test should have a descriptive name
# When a test fails, the first thing you read is the name
# Should describe what was tested and failed
# Should write a docstring to further explain the test
# organise test types in classes?

# Overall parameters for probabilistic tests
SEED = 112233   # random seed for tests
ALPHA = 0.01  # significance level for statistical tests

@pytest.fixture
def reset_params():
    """
    Fixture resetting class parameters on Bacteria.

    The fixture resets Bacteria class-level parameters before leaving a test.
    """

    # no set-up
    yield
    Island.set_fodder_parameters(default_fodder_parameters())














@pytest.fixture
def reset_parameters():
    """Resets the class parameters to their default values."""
    yield


@pytest.fixture(autouse=True)
def make_test_island():

    """Creates a island with a simple geography and a single carnivore
        to test functions on."""

    test_geography = """\
                        WWWWWW
                        WWLHWW
                        WWWWWW"""

    test_pop = [{"loc": (2, 3),"pop": [{"species": "Carnivore" }]}]

    return Island(ini_pop=test_pop, geography=test_geography)


def test_add_population():

    """Tests that the population is added correctly."""
    test_island=make_test_island()

    test_island.add_population([{"loc": (2, 3),"pop": [{"species": "Herbivore" }]}])
    assert test_island.n_animals == 2, "The population was not added correctly."

def test_migration():

    """Tests that the migration is performed correctly. Give the carnivor
    really good fitness so that it will migrate with high probability.
    """
    test_island=make_test_island()

    test_island.migration()
    assert test_island.n_animals != 1, "The migration was not performed correctly."
    assert