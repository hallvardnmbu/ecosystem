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
    return [Herbivore(), Carnivore(), Herbivore(weight=0), Carnivore(weight=0)]

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
            animal.gain_weight(10)
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
        q_pos = (1 + exp(animal.phi_age * (animal.a - animal.a_half))) ** (-1)
        q_neg = (1 + exp(-animal.phi_weight * (animal.w - animal.w_half))) ** (-1)
        fitness = q_pos * q_neg
        if animal.w == 0:
            fitness = 0
        assert animal.fitness == fitness, f"Fitness for {type(animal).__name__} did not match the formulas."

def test_set_parameters(animals):
    for animal in animals:
        new_parameters = {"eta": 0.1}
        animal.set_parameters(new_parameters)
        assert animal.eta == 0.1, f"Parameter eta for {type(animal).__name__} was not set correctly."

def test_get_parameters(animals):
    for animal in animals:
        parameters = animal.get_parameters()
        assert parameters["eta"] == animal.eta, f"Parameter eta for {type(animal).__name__} was not retrieved correctly."