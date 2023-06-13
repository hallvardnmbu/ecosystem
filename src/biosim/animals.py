"""
Module for the different animal species.
"""


import random
from math import exp, sqrt, log


class Animal:
    """
    Parent class for animal species.
    """

    @classmethod
    def set_parameters(cls, new_parameters):
        """
        Set the parameters for a species.
        When calling the function, one can call it on both the subclass and the object, with the
        same result.
            Subclass.set_parameters() or
            Object.set_parameters()

        Parameters
        ----------
        new_parameters : dict
            {`parameter`: value}

        Raises
        ------
        ValueError
            If invalid parameters are passed.
        """

        for key, val in new_parameters.items():
            if key not in cls.default_parameters():
                raise KeyError(f"Invalid parameter: {key}")
            try:
                if key == "DeltaPhiMax" and val <= 0:
                    raise ValueError(f"Value for: {key} should be positive.")
                elif key == "eta" and val > 1:
                    raise ValueError(f"Value for: {key} should be less than or equal to 1.")
                else:
                    try:
                        if val < 0:
                            raise ValueError(f"Value for: {key} should be nonzero or positive.")
                    except TypeError:
                        raise ValueError(f"Value for: {key} should be a number.")
            # This extra "except" is needed in case "DeltaPhiMax" or "eta" is not a number.
            except TypeError:
                raise ValueError(f"Value for: {key} should be a number.")

            setattr(cls, key, val)

    @classmethod
    def get_parameters(cls):
        """
        Get the parameters for a species.

        Returns
        -------
        parameters : dict
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
                      "F": cls.F}
        if cls is Carnivore:
            parameters["DeltaPhiMax"] = cls.DeltaPhiMax
        return parameters

    @classmethod
    def lognormv(cls):
        """
        A continuous probability distribution of a random variable whose
        logarithm is normally distributed, which is used to draw birth weights

        Returns
        -------
        weight : float
            From the normal distribution.
        """

        try:
            cls.get_parameters()
        except AttributeError:
            cls.set_parameters(cls.default_parameters())

        mu = log((cls.w_birth**2)/sqrt(cls.w_birth**2 + cls.sigma_birth**2))
        sigma = sqrt(log(1 + ((cls.sigma_birth**2)/(cls.w_birth**2))))

        return random.lognormvariate(mu, sigma)

    @classmethod
    def mapping(cls):
        """
        Maps the string to the class.
        This is done to avoid having to import all the subclasses (upon further expanding for
        different species/subspecies).

        Returns
        -------
        dict
            Class mapping.
        """

        return {"Herbivore": Herbivore,
                "Carnivore": Carnivore}

    def __init__(self, weight, age):
        try:
            if int(age) < 0:
                raise ValueError("Age should be positive.")
            else:
                self.a = age
            if not weight:
                self.w = self.lognormv()
            elif weight < 0:
                raise ValueError("Weight should be positive.")
            else:
                self.w = weight
        except TypeError:
            raise ValueError(f"Age: {age} and weight: {weight} must both be numbers.")

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

    def lose_weight_year(self):
        """
        Decrements the weight of the animal by the factor eta.
        """

        self.w -= self.eta * self.w

    def lose_weight_birth(self, baby_weight):
        """
        Decrements the weight of the parent by the factor eta if the parent weights enough.

        Parameters
        ----------
        baby_weight : float
            The weight of the baby.

        Returns
        -------
        bool
            True if the parent can lose xi * baby_weight, False otherwise.
        """

        if self.w > self.xi * baby_weight:
            self.w -= self.xi * baby_weight
            return True
        else:
            return False

    @property
    def fitness(self):
        """
        Calculates the fitness of the animal.

        Returns
        -------
        fitness : float
            The fitness of the animal.
        """

        if self.w <= 0:
            return 0
        q_pos = (1 + exp(self.phi_age * (self.a - self.a_half))) ** (-1)
        q_neg = (1 + exp(-self.phi_weight * (self.w - self.w_half))) ** (-1)
        return q_pos * q_neg


class Herbivore(Animal):
    """
    Subclass for Herbivores.

    Parameters
    ----------
    age : int, optional
        Age of the animal.
    weight : float, optional
        Weight of the animal.
    """

    @classmethod
    def default_parameters(cls):
        """
        Default parameters for Herbivores.

        Returns
        -------
        dict
            Default parameters for Herbivore.
        """

        return {"w_birth": 8.0,
                "sigma_birth": 1.5,
                "beta": 0.9,
                "eta": 0.05,
                "a_half": 40.0,
                "phi_age": 0.6,
                "w_half": 10.0,
                "phi_weight": 0.1,
                "mu": 0.25,
                "gamma": 0.2,
                "zeta": 3.5,
                "xi": 1.2,
                "omega": 0.4,
                "F": 10.0}

    @classmethod
    def motion(cls):
        """
        Sets the movement parameters for the Carnivore.

        Returns
        -------
        movable : dict
            Movable terrain.
        stride : int
            Step size.
        """

        cls.movable = {"H": True,
                       "L": True,
                       "D": True,
                       "W": False}
        cls.stride = 1

        return cls.movable, cls.stride

    def __init__(self, age=None, weight=None):
        try:
            self.set_parameters(Herbivore.get_parameters())
        except AttributeError:
            self.set_parameters(Herbivore.default_parameters())
        super().__init__(weight, age)
        self.species = "Herbivore"

    def graze(self, available_fodder):
        """
        An animal tries to graze on the available fodder.

        Parameters
        ----------
        available_fodder : float
            The amount of fodder available at current location.

        Returns
        -------
        grazed : float
            The amount of fodder grazed.
        """

        if available_fodder >= self.F:
            self.gain_weight(self.F)
            grazed = self.F
        else:
            self.gain_weight(available_fodder)
            grazed = available_fodder

        return grazed


class Carnivore(Animal):
    """
    Subclass for Carnivores.

    Parameters
    ----------
    age : int, optional
        Age of the animal.
    weight : float, optional
        Weight of the animal.
    """

    @classmethod
    def default_parameters(cls):
        """
        Default parameters for Carnivores.

        Returns
        -------
        dict
            Default parameters for Carnivore.
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

    @classmethod
    def motion(cls):
        """
        Sets the movement parameters for the Carnivore.

        Returns
        -------
        movable : dict
            Movable terrain.
        stride : int
            Step size.
        """

        cls.movable = {"H": True,
                       "L": True,
                       "D": True,
                       "W": False}
        cls.stride = 1

        return cls.movable, cls.stride

    def __init__(self, age=None, weight=None):
        try:
            self.set_parameters(Carnivore.get_parameters())
        except AttributeError:
            self.set_parameters(Carnivore.default_parameters())
        super().__init__(weight, age)
        self.species = "Carnivore"

    def predation(self, herbivores):
        """
        The herbivore tries to kill an eat the herbivores at the current location.

        Parameters
        ----------
        herbivores : list
            List of herbivores at current location.

        Returns
        -------
        killed : list
            List of herbivores that were killed.
        """

        eaten = 0
        killed = []

        for herbivore in herbivores:
            if eaten >= self.F:
                break

            carnivore_fitness = self.fitness
            herbivore_fitness = herbivore.fitness
            if carnivore_fitness <= herbivore_fitness:
                p = 0
            elif 0 < carnivore_fitness - herbivore_fitness < self.DeltaPhiMax:
                p = (carnivore_fitness - herbivore_fitness) / self.DeltaPhiMax
            else:
                p = 1

            if random.random() < p:
                eaten += herbivore.w

                self.gain_weight(food=herbivore.w)

                killed.append(herbivore)

        return killed
