from src.biosim.animals import Herbivore, Carnivore
from pytest import approx
import pytest

# Each individual test should have a descriptive name
# When a test fails, the first thing you read is the name
# Should describe what was tested and failed
# Should write a docstring to further explain the test

# We used the lecture notes, ChatGPT and Stackoverflow in order to gain a basic understanding of how
# to structure the tests. ChatGPT and Stackoverflow were used as a "teacher", and did not author
# any of the code we used.

@pytest.fixture
def trial_animals():
    """Creates a list of animals to be used in the tests."""

    return [Herbivore(age=0, weight=1), Carnivore(age=0, weight=1)]

@pytest.fixture
def reset_animal_defaults(trial_animals):
    """Resets the default parameters for the animals."""

    yield

    for animal in trial_animals:
        animal.a = 0
        animal.w = 1
        animal.set_parameters(animal.default_parameters())

def test_default_parameters(trial_animals):
    """Tests that the default parameters are set correctly."""

    for animal in trial_animals:
        assert animal.get_parameters() == animal.default_parameters()

def test_set_parameters(trial_animals, reset_animal_defaults):
    """Tests that the parameters are set correctly."""

    for animal in trial_animals:
        new_parameters = {"eta": 0.1}
        animal.set_parameters(new_parameters)
        assert animal.get_parameters()["eta"] == new_parameters["eta"]

# def test_lognormv(trial_animals, reset_animal_defaults):
#     """Tests that the lognormv function works correctly."""

def test_aging(trial_animals, reset_animal_defaults):
    """Tests that the age increases by one after aging() is called."""

    num_days = 10
    for animal in trial_animals:
        for _ in range(num_days):
            animal.aging()
        assert animal.a == num_days, f"Age for {type(animal).__name__} did not increase by one."

def test_gain_weight(trial_animals, reset_animal_defaults):
    """Tests that the weight increases by the factor beta after gain_weight() is called."""

    num_days = 10
    for animal in trial_animals:

        animal.set_parameters({"beta": 1})
        weight = animal.w
        food = 1

        for _ in range(num_days):
            animal.gain_weight(food)

        weight *= food + num_days

        assert animal.w == weight, f"Weight for {type(animal).__name__} did not increase correctly."

def test_lose_weight_year(trial_animals, reset_animal_defaults):
    """Tests that the weight decreases by the factor eta after lose_weight() is called."""

    num_days = 10
    for animal in trial_animals:

        animal.set_parameters({"eta": 0.99})

        for _ in range(num_days):
            animal.lose_weight_year()

        assert animal.w == approx(0), f"Weight for {type(animal).__name__} did not decrease " \
                                      f"correctly."

def test_lose_weight_birth(trial_animals, reset_animal_defaults):
    """Tests that the weight decreases by the factor eta after lose_weight() is called."""

    num_days = 10
    for animal in trial_animals:

        animal.set_parameters({"eta": 0.99})

        for _ in range(num_days):
            animal.lose_weight_year()

        assert animal.w == approx(0), f"Weight for {type(animal).__name__} did not decrease " \
                                      f"correctly."

def test_lose_weight_birth(trial_animals, reset_animal_defaults):
    """Tests that the weight decreases by the factor eta after lose_weight_birth() is called."""

    num_days = 10
    for animal in trial_animals:

        animal.set_parameters({"xi": 0.1})
        animal.w = 10
        baby_weight = 1

        for _ in range(num_days):
            animal.lose_weight_birth(baby_weight)

        assert animal.w == approx(9), f"Weight for {type(animal).__name__} did not decrease " \
                                    f"correctly."

def test_fitness():
    """Tests that the fitness is calculated correctly."""

    animals = [Herbivore(age=0, weight=0), Carnivore(age=0, weight=0),
               Herbivore(age=0, weight=10000), Carnivore(age=0, weight=10000)]

    for animal in animals:
        if animal.w == 0:
            assert animal.fitness == approx(0), "Fitness for animal with weight 0 is incorrect."
        else:
            assert 0.999 < animal.fitness < 1, "Fitness for animal with weight 10000 is " \
                                                 "incorrect."
