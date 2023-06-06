from math import exp
import random

class Animal:
    @classmethod
    def set_parameters(cls, new_parameters):
        """
        Set the parameters for a species.
        When calling the function, one can call it on both the subclass and the object, with the same result.
            Subclass.set_parameters() or
            Object.set_parameters()

        Parameters
        ----------
        - parameters : dict
            {"parameter": value}

        Raises
        ------
        - ValueError
            If invalid parameters are passed.
        """

        # Check if parameters are valid:
        for key, val in new_parameters.items():
            if val < 0:
                raise ValueError("Value for: {0} should be nonzero or positive.".format(key))
            if key == "DeltaPhiMax" and val <= 0:
                raise ValueError("Value for: {0} should be positive.".format(key))
            if key == "eta" and val > 1:
                raise ValueError("Value for: {0} should be less than or equal to 1.".format(key))

        # Update new parameters:
        for key, value in new_parameters.items():
            if key not in cls.default_parameters():
                raise ValueError("Invalid parameter: {0}".format(key))
            setattr(cls, key, value)

    @classmethod
    def get_parameters(cls):
        """
        Get the parameters for a species.

        Returns
        -------
        - parameters : dict

        """
        parameters = {"w_birth": cls.w_birth,
                      "sigma_birth": cls.sigma_birth,
                      "beta": cls.beta,
                      "eta": cls.eta,
                      "a_half": cls.a_half,
                      "phi_age": cls.phi_age,
                      "w_half": cls.w_half,
                      "phi_weight": cls.phi_weight,
                      "mu": cls.mu,
                      "gamma": cls.gamma,
                      "zeta": cls.zeta,
                      "xi": cls.xi,
                      "omega": cls.omega,
                      "F": cls.F,
                      "unlivable_terrain": cls.unlivable_terrain}
        if cls is Carnivore:
            parameters["DeltaPhiMax"] = cls.DeltaPhiMax
        return parameters

    def __init__(self, weight, age):
        self.a = age if age is not None else 0
        self.weight = weight if weight is not None else random.lognormvariate(self.w_birth,
                                                                              self.sigma_birth)

    def aging(self):
        """
        Increments the age of the animal by one year.
        """

        self.a += 1

    def gain_weight(self, food):
        """
        Increments the weight of the animal by the factor beta and the amount of food eaten.
        """

        self.w += self.beta * food

    def lose_weight(self):
        """
        Decrements the weight of the animal by the factor eta.
        """

        self.w -= self.eta * self.w

    def lose_weight_birth(self, baby_weight):
        """
        Decrements the weight of the animal by the factor xi and the weight of the baby.
        """

        self.w -= self.xi * baby_weight

    def baby_weight(self):
        """
        Calculates the weight of the baby.
        """

        if random.random() < min(1, self.gamma * self.fitness * 10): # BYTT "10" MED: "self.count_animals_cell()" COUNT ANIMAL CELL!):
            return random.lognormvariate(self.w_birth, self.sigma_birth)

    def give_birth(self, baby_weight):
        """
        Creates a new animal with the given weight at the same position as the parent.
        """

        if baby_weight > self.w:
            return
        self.lose_weight_birth(baby_weight)
        self.__class__(weight=baby_weight)

    @property
    def fitness(self):
        """
        Calculates the fitness of the animal.
        """

        if self.w <= 0:
            return 0
        # Calculates parts of the fitness function:
        q_pos = (1 + exp(self.phi_age * (self.a - self.a_half))) ** (-1)
        q_neg = (1 + exp(-self.phi_weight * (self.w - self.w_half))) ** (-1)
        return q_pos * q_neg

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
                "F": 10.0,
                "unlivable_terrain"="W"}

    def __init__(self, age=None, weight=None):
        try:
            self.set_parameters(Herbivore.get_parameters())
        except:
            self.set_parameters(Herbivore.default_parameters())
        super().__init__(weight, age)

        # Add to the cell.

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
                "DeltaPhiMax": 10.0,
                "unlivable_terrain"= "W"}

    def __init__(self, age=None, weight=None):
        try:
            self.set_parameters(Carnivore.get_parameters())
        except:
            self.set_parameters(Carnivore.default_parameters())
        super().__init__(weight, age)

        # Add to the cell.

# I morgen:
#
# Lage cellene.
#   - Gjør at hvert dyr som blir laget blir plassert i cellen osv.
#
# Lage en funksjon som teller antall dyr i en celle.
#   - I "baby_weight": endre "10" med "self.count_animals_cell()" (eller tilsvarende).