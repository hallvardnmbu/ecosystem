from src.biosim.animals import Herbivore, Carnivore
import pytest
from math import exp

# Each individual test should have a descriptive name
# When a test fails, the first thing you read is the name
# Should describe what was tested and failed
# Should write a docstring to further explain the test

# I used ChatGPT and Stackoverflow in order to gain a basic understanding of how to structure the
# tests.

@pytest.fixture
def animals():
    return [Herbivore(weight=10000), Carnivore(weight=10000), Herbivore(weight=0),
            Carnivore(
        weight=0)]

def test_age_increase(animals):
    """Tests that the age increases by one after aging() is called."""
    num_days = 10
    for animal in animals:
        for _ in range(num_days):
            animal.aging()
        assert animal.a == num_days, f"Age for {type(animal).__name__} did not increase by one."

def test_gain_weight(animals):
    """Tests that the weight increases by the factor beta after gain_weight() is called."""
    num_days = 10
    for animal in animals:
        weight = animal.w
        for _ in range(num_days):
            animal.gain_weight(1000000)
            weight += animal.beta * 10
        assert animal.w == weight, f"Weight for {type(animal).__name__} did not increase by the " \
                               f"factor beta."

def test_lose_weight(animals):
    """Tests that the weight decreases by the factor eta after lose_weight() is called."""
    num_days = 10
    for animal in animals:
        weight = animal.w
        for _ in range(num_days):
            animal.lose_weight()
            weight -= animal.eta * weight
        assert animal.w == weight, f"Weight for {type(animal).__name__} did not decrease by the " \
                               f"factor eta."

def test_lose_weight_birth(animals):
    pass

def test_baby_weight(animals):
    pass

def test_give_birth(animals):
    pass

def test_fitness(animals):
    """Tests that the fitness is calculated correctly."""
    for animal in animals:
        if animal.w > 9999:
            assert 0.998 <= animal.fitness <= 1, f"Fitness for {type(animal).__name__} " \
                                                       f"with weight: {animal.w} did not match " \
                                                       f"the formulas."
        elif animal.w == pytest.approx(0):
            assert animal.fitness == pytest.approx(0), f"Fitness for {type(animal).__name__} " \
                                                       f"with weight: {animal.w} did not match " \
                                                       f"the " \
                                                       f"formulas."
def test_set_parameters(animals):
    """Tests that the parameters are set correctly."""
    for animal in animals:
        new_parameters = {"eta": 0.1}
        animal.set_parameters(new_parameters)
        assert animal.eta == 0.1, f"Parameter eta for {type(animal).__name__} was not set correctly."

def test_get_parameters(animals):
    """Tests that the parameters are retrieved correctly."""
    for animal in animals:
        parameters = animal.get_parameters()
        assert parameters["eta"] == animal.eta, f"Parameter eta for {type(animal).__name__} was not retrieved correctly."