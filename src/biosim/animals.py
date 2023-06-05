import random
random.seed(1)
from math import exp

class Animal:
    @classmethod
    def set_parameters(cls, parameters=None):
        """
        Set the parameters for an animal.

        Parameters
        ----------
        - parameters : dict
            {"parameter": value}

        Raises
        ------
        - ValueError
            If invalid parameter values are passed.
        """

        if parameters is None:
            return
        class_parameters = cls.default_parameters()
        for key in parameters:
            if key not in class_parameters:
                raise ValueError("Invalid parameter: {}".format(key))
            class_parameters[key] = parameters[key]
        cls.parameters = class_parameters

    @classmethod
    def get_parameters(cls):
        """
        Get the parameters for an animal.
        """

        try:
            return cls.parameters
        except:
            return cls.default_parameters()

    def __init__(self, position, weight, age):
        self.position = position
        self.a = age
        if not weight:
            self.w = random.lognormvariate(self.get_parameters()["w_birth"], self.get_parameters()["sigma_birth"])
        else:
            self.w = weight

    def aging(self):
        """
        Increments the age of the animal by one year.
        """

        self.a += 1

    def gain_weight(self, food):
        """
        Increments the weight of the animal by the factor beta and the amount of food eaten.
        """

        self.w += self.get_parameters()["beta"] * food

    def lose_weight(self):
        """
        Decrements the weight of the animal by the factor eta.
        """

        self.w -= self.get_parameters()["eta"] * self.w

    def lose_weight_birth(self, baby_weight):
        """
        Decrements the weight of the animal by the factor xi and the weight of the baby.
        """

        self.w -= self.get_parameters()["xi"] * baby_weight

    def baby_weight(self):
        """
        Calculates the weight of the baby.
        """

        if random.random() < min(1, self.get_parameters()["gamma"] * self.fitness * 10): # BYTT "10" MED: "self.count_animals_cell()" COUNT ANIMAL CELL!):
            return random.lognormvariate(self.get_parameters()["w_birth"], self.get_parameters()["sigma_birth"])

    def give_birth(self, baby_weight):
        """
        Creates a new animal with the given weight at the same position as the parent.
        """

        if baby_weight > self.w:
            return
        self.lose_weight_birth(baby_weight)
        self.__class__(position=self.position, weight=baby_weight)

    @property
    def fitness(self):
        """
        Calculates the fitness of the animal.
        """

        # Get parameters
        phi_age = self.get_parameters()["phi_age"]
        phi_weight = self.get_parameters()["phi_weight"]
        a_half = self.get_parameters()["a_half"]
        w_half = self.get_parameters()["w_half"]

        # Calculates parts of the fitness function
        qpos = (1 + exp(phi_age * (self.a - a_half)))**(-1)
        qneg = (1 + exp(-phi_weight * (self.w - w_half)))**(-1)

        if self.w <= 0:
            return 0
        else:
            return qpos * qneg

class Herbivore(Animal):
    @classmethod
    def default_parameters(cls):
        """
        Default parameters for Herbivores.
        """

        return {"w_birth": 8.0,
                "sigma_birth": 1.5,
                "beta": 0.9,
                "eta": 0.05,
                "a_half": 40.0,
                "phi_age": 0.2,
                "w_half": 10.0,
                "phi_weight": 0.1,
                "mu": 0.25,
                "gamma": 0.2,
                "zeta": 3.5,
                "xi": 1.2,
                "omega": 0.4,
                "F": 10.0}

    def __init__(self, position, weight=None, age=0):
        super().__init__(position, weight, age)

class Carnivore(Animal):
    @classmethod
    def default_parameters(cls):
        """
        Default parameters for Carnivores.
        """

        return {"w_birth": 6.0,
                "sigma_birth": 1.0,
                "beta": 0.75,
                "eta": 0.125,
                "a_half": 40.0,
                "phi_age": 0.3,
                "w_half": 4.0,
                "phi_weight": 0.4,
                "mu": 0.4,
                "gamma": 0.8,
                "zeta": 3.5,
                "xi": 1.1,
                "omega": 0.8,
                "F": 50.0,
                "DeltaPhiMax": 10.0}

    def __init__(self, position, weight=None, age=0):
        super().__init__(position, weight, age)