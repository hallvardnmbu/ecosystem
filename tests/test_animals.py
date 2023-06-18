"""
Tests for the animals module.
"""


from src.biosim.animals import Herbivore, Carnivore
import scipy.stats as stat
from math import log
import pytest


# We used the lecture notes, ChatGPT and Stackoverflow in order to gain a basic understanding of how
# to structure the tests. ChatGPT and Stackoverflow were used as a "teacher", and did not author
# any of the code we used.

# Stackoverflow was used in order to find out how to test if an error is raised properly. Source:
# https://stackoverflow.com/questions/23337471/how-to-properly-assert-that-an-exception-gets
# -raised-in-pytest


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

    yield animals

    # Cleanup:
    for animal in animals:
        animal.a = age
        animal.w = weight
        animal.set_parameters(animal.default_parameters())


def test_animal_init(trial_animals):
    """Tests that the animal is initialized correctly."""

    assert Herbivore(1, 1).w_birth == float(8)
    assert Carnivore(1, 1).w_birth == float(6)


def test_default_parameters(trial_animals):
    """Tests that the default parameters are set correctly."""

    for animal in trial_animals:
        assert animal.get_parameters() == animal.default_parameters(), "Parameters are wrong."


@pytest.mark.parametrize("dict_key, dict_value",
                         [["eta", 0.1],
                          ["a_half", 40],
                          ["phi_age", 0.6],
                          ["w_half", 10]])
def test_set_parameters(trial_animals, dict_key, dict_value):
    """Tests that the parameters are set correctly."""

    for animal in trial_animals:
        new_parameters = {dict_key: dict_value}
        animal.set_parameters(new_parameters)
        assert animal.get_parameters()[dict_key] == dict_value, "Setting parameters didn't work."


@pytest.mark.parametrize("dict_key, dict_value",
                         [["eta", -0.1],
                          ["a_half", -40],
                          ["phi_age", -0.6],
                          ["w_half", -10]])
def test_set_parameters_negative(dict_key, dict_value):
    """Tests that the parameters are set correctly."""

    with pytest.raises(ValueError):
        Herbivore.set_parameters({dict_key: dict_value}), "Setting negative parameters worked."


@pytest.mark.parametrize("dict_key",
                         [0,
                          -1])
def test_set_parameters_dpm(dict_key):
    """Tests that the parameters are set correctly."""

    with pytest.raises(ValueError):
        Carnivore.set_parameters({"DeltaPhiMax": dict_key}), "Setting DeltaPhiMax to <= 0 worked."


def test_set_parameters_eta():
    """Tests that the parameters are set correctly."""

    with pytest.raises(ValueError):
        Herbivore.set_parameters({"eta": 10}), "Setting eta to >1 worked."


@pytest.mark.parametrize("dict_key, dict_value",
                         [["a", 0.1],
                          ["b", 40],
                          ["c", 52],
                          ["d", 100]])
def test_set_parameters_nonexistent_key(dict_key, dict_value):
    """Tests that the parameters are set correctly."""

    with pytest.raises(KeyError):
        Herbivore.set_parameters({dict_key: dict_value}), "Setting nonexistent parameters worked."


@pytest.mark.parametrize("dict_key, dict_value",
                         [["eta", "a"],
                          ["a_half", Herbivore],
                          ["phi_age", (1, 2, 3)],
                          ["w_half", [1, "2", 3]]])
def test_set_parameters_nonexistent_value(dict_key, dict_value):
    """Tests that the parameters are set correctly."""

    with pytest.raises(ValueError):
        Herbivore.set_parameters({dict_key: dict_value}), "Setting nonexistent parameters worked."


def test_lognormv(trial_animals):
    """Tests that the lognormv function works correctly."""

    for animal in trial_animals:

        sample_size = 1000
        weights = [animal.lognormv() for _ in range(sample_size)]
        log_weights = [log(weight) for weight in weights]

        # Shapiro-Wilk test. A low p-value indicates that we are uncertain of uniformity.
        # Retrieved from scipy.stats.shapiro.
        _, p_val = stat.shapiro(log_weights)

        # If the p-value is below the confidence level, we reject the null hypothesis (uniformity).
        assert p_val > 0.01, "(WILL SOMETIME FAIL) Weights are not normally distributed (p < 0.01)."


def test_lognormv_with_animals(trial_animals, mocker):
    """Tests that the lognormv function works correctly."""

    mocker.patch("random.lognormvariate", return_value=1)
    for animal in trial_animals:
        assert animal.lognormv() == 1, "Calling lognormv with an animal didn't work."


def test_lognormv_without_animals(mocker):
    """Tests that the lognormv function works correctly."""

    Carnivore.set_parameters(Carnivore.default_parameters())

    mocker.patch("random.lognormvariate", return_value=1)
    assert Carnivore.lognormv() == 1, "Calling lognormv using the class didn't work."


def test_create_animal():
    """Tests that the animal is created correctly."""

    animal = Herbivore(age=0, weight=1)
    assert animal.a == 0, f"Age for {animal.__class__.__name__} is wrongly constructed."
    assert animal.w == 1, f"Weight for {animal.__class__.__name__} is wrongly constructed."


@pytest.mark.parametrize("age, weight",
                         [[-1, 1],
                          [1, -1],
                          [-1, -1]])
def test_create_animal_negative(age, weight):
    """Tests that the animal is created correctly."""

    with pytest.raises(ValueError):
        Herbivore(age=age, weight=weight), "Creating animal with negative values worked."


@pytest.mark.parametrize("age, weight",
                         [["a", 1],
                          [1, "a"],
                          ["a", "a"]])
def test_create_animal_nonnumber(age, weight):
    """Tests that the animal is created correctly."""

    with pytest.raises(ValueError):
        Herbivore(age=age, weight=weight), "Creating animal with non-numbers worked."


def test_set_motion(trial_animals):
    """Tests that the motion is set correctly."""

    for animal in trial_animals:
        animal.set_motion(new_stride=1)
        assert animal.stride == 1, f"Motion for {animal.__class__.__name__} is wrongly set."


def test_set_motion_negative(trial_animals):
    """Tests that the motion is set correctly."""

    for animal in trial_animals:
        with pytest.raises(ValueError):
            animal.set_motion(new_stride=-1), f"Setting negative motion for" \
                                              f" {animal.__class__.__name__} " \
                                              f"worked."


def test_set_motion_nonnumber(trial_animals):
    """
    Tests that the motion is set correctly.
    """
    for animal in trial_animals:
        with pytest.raises(TypeError):
            animal.set_motion(new_stride="a"), f"Setting non-number motion for" \
                                               f" {animal.__class__.__name__} " \
                                               f"worked."


def test_set_motion_terrain(trial_animals):
    """Tests that the motion is set correctly."""

    for animal in trial_animals:
        animal.set_motion(new_movable={"W": True})
        assert animal.movable["W"], f"Motion terrain for {animal.__class__.__name__} is wrongly " \
                                    f"set."


def test_set_motion_invalid_terrain(trial_animals):
    """Tests that the motion is set correctly."""

    for animal in trial_animals:
        with pytest.raises(KeyError):
            animal.set_motion(new_movable={"w": True}), \
                f"Setting motion terrain thats not in map for {animal.__class__.__name__} worked."


def test_aging(trial_animals):
    """Tests that the age increases by one after aging() is called."""

    num_years = 10
    for animal in trial_animals:
        for _ in range(num_years):
            animal.aging()
        assert animal.a == num_years, f"Age for {animal.__class__.__name__} did not increase by " \
                                      f"one."


def test_gain_weight(trial_animals):
    """Tests that the weight increases by the factor beta after gain_weight() is called."""

    num_years = 10
    for animal in trial_animals:

        animal.set_parameters({"beta": 1})
        weight = animal.w
        food = 1

        for _ in range(num_years):
            animal.gain_weight(food)

        weight *= food + num_years

        assert animal.w == weight, f"Weight for {animal.__class__.__name__} did not increase " \
                                   f"correctly."


def test_lose_weight_year(trial_animals):
    """Tests that the weight decreases by the factor eta after lose_weight() is called."""

    num_years = 10
    for animal in trial_animals:

        animal.set_parameters({"eta": 0.99})

        for _ in range(num_years):
            animal.lose_weight_year()

        assert animal.w == pytest.approx(0), f"Weight for {animal.__class__.__name__} did not " \
                                             f"decrease correctly."


def test_lose_weight_birth(trial_animals):
    """Tests that the weight decreases by the factor eta after lose_weight_birth() is called."""

    num_years = 10
    for animal in trial_animals:

        animal.set_parameters({"xi": 0.1})
        animal.w = 10
        baby_weight = 1

        for _ in range(num_years):
            animal.lose_weight_birth(baby_weight)

        assert animal.w == pytest.approx(9), f"Weight for {animal.__class__.__name__} did not " \
                                             f"decrease correctly."


def test_lose_weight_birth_small_weight(trial_animals):
    """Tests whether a baby is born if the mother's weight is too low."""

    for animal in trial_animals:

        animal.set_parameters({"xi": 1})
        animal.w = 0.9
        baby_weight = 1

        assert not animal.lose_weight_birth(baby_weight), "Loss of weight did not return False."


def test_fitness():
    """Tests that the fitness is calculated correctly."""

    animals = [Herbivore(age=0, weight=1),
               Carnivore(age=0, weight=1),
               Herbivore(age=0, weight=10000),
               Carnivore(age=0, weight=10000)]

    Herbivore.set_parameters(Herbivore.default_parameters())
    Carnivore.set_parameters(Carnivore.default_parameters())

    for animal in animals:
        if animal.w == 1:
            animal.w = 0
            assert animal.fitness == 0,  f"Fitness for {animal.__class__.__name__} is incorrect."
        if animal.w == 10000:
            assert 0.999 < animal.fitness < 1, \
                    f"Fitness for {animal.__class__.__name__} is incorrect."
