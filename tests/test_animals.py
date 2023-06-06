from src.biosim.animals import Herbivore, Carnivore
import pytest

# Each individual test should have a descriptive name
# When a test fails, the first thing you read is the name
# Should describe what was tested and failed
# Should write a docstring to further explain the test

@pytest.fixture
def animals():
    return [Herbivore(), Carnivore()]

def test_age_increase(animals):
    """Tests that the age increases by one after aging() is called."""
    num_days = 10
    for animal in animals:
        for _ in range(num_days):
            animal.aging()
        assert animal.a == num_days, f"Age for {type(animal).__name__} did not increase by one."