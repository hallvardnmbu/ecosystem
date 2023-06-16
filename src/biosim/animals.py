"""
Contains the different animal species.
"""


import random
from math import exp, sqrt, log


class Animal:
    """
    Parent class for animal species.
    """

    @classmethod
    def motion(cls):
        """
        Get the movement parameters for the species.

        Returns
        -------
        movable : dict
            Movable terrain.
        stride : int
            Step size.
        """

        return cls.movable, cls.stride

    @classmethod
    def set_motion(cls, new_movable=None, new_stride=None):
        """
        Sets the movement parameters for the species.

        Parameters
        ----------
        new_movable : dict
            Movable terrain.
        new_stride : int
            Step size.
        """

        if new_stride is not None:
            try:
                if new_stride < 0:
                    raise ValueError("Stride should be nonzero or positive.")
                cls.stride = round(new_stride)
            except TypeError:
                raise TypeError("Stride should be a number.")
        else:
            stride, _ = cls.default_motion()
            cls.stride = stride

        if new_movable is not None:
            _, movable = cls.default_motion()
            if not all(key in movable.keys() for key in new_movable.keys()):
                raise KeyError("Invalid keys in new_movable.")
            for key, boolean in new_movable.items():
                cls.movable[key] = boolean
        else:
            _, movable = cls.default_motion()
            cls.movable = movable

        return

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
    def set_parameters(cls, new_parameters):
        r"""
        Set the parameters for a species.
        When calling the function, one can call it on both the subclass and the object, with the
        same result.

            .. code:: python

                Subclass.set_parameters()
                Object.set_parameters()

        Parameters
        ----------
        new_parameters : dict

            .. code:: python

                {'parameter': value}

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

        cls.update_p_procreate()

    @classmethod
    def update_p_procreate(cls):
        """
        Updates the probability of procreation for the species.
        """

        cls.p_procreate = cls.zeta * (cls.w_birth + cls.sigma_birth)

    @classmethod
    def lognormv(cls):
        r"""
        A continuous probability distribution of a random variable whose
        logarithm is normally distributed, which is used to draw birth weights

        Returns
        -------
        weight : float
            From the normal distribution.

        Notes
        -----
        :math:`\mu` and :math:`\sigma` are calculated from the birth weight and its standard
        deviation through the following equations:

        .. math::

            \mu = \log \left( \frac{{w_{\text{birth}}^2}}{{\sqrt{{\sigma_{\text{birth}}^2
            + w_{\text{birth}}^2}}}} \right)

            \sigma = \sqrt{\log \left( 1 + \frac{{\sigma_{\text{birth}}^2}}{{w_{\text{birth}}^2}}
            \right)}

        (Retrieved from: https://en.wikipedia.org/wiki/Log-normal_distribution).
        """

        mu = log((cls.w_birth**2)/sqrt(cls.w_birth**2 + cls.sigma_birth**2))
        sigma = sqrt(log(1 + ((cls.sigma_birth**2)/(cls.w_birth**2))))

        return random.lognormvariate(mu, sigma)

    def __init__(self, weight, age):
        try:
            if not age:
                self.a = 0
            elif int(age) < 0:
                raise ValueError("Age should be positive.")
            else:
                self.a = age
            if not weight:
                self.w = self.lognormv()
            elif float(weight) <= 0:
                raise ValueError("Weight should be positive.")
            else:
                self.w = weight
        except ValueError:
            raise ValueError(f"Age: {age} and weight: {weight} must both be numbers.")
        self._fitness = None
        self.set_motion()

    def aging(self):
        """
        Increments the age of the animal by one year.
        """

        self.a += 1

    def gain_weight(self, food):
        r"""
        Increments the weight of the animal by the factor :math:`\beta` and the amount of food
        eaten.
        """

        self.w += self.beta * food
        self.calculate_fitness()

    def lose_weight_year(self):
        r"""
        Decrements the weight of the animal by the factor :math:`\eta`.
        """

        self.w -= self.eta * self.w

    def lose_weight_birth(self, baby_weight):
        r"""
        Decrements the weight of the parent by the factor :math:`\xi` if the parent weights enough.

        Parameters
        ----------
        baby_weight : float
            The weight of the baby.

        Returns
        -------
        bool
            True if the parent can lose :math:`\xi` * baby_weight, False otherwise.

        Notes
        -----
        If :math:`\xi` * baby_weight is greater than the weight of the parent, the parent
        will not give birth.
        """

        if self.w > self.xi * baby_weight:
            self.w -= self.xi * baby_weight
            self.calculate_fitness()
            return True
        else:
            return False

    def calculate_fitness(self):
        r"""
        Calculates the fitness of the animal.

        Notes
        -----
        The fitness is calculated as follows:

        .. math::

            \Phi = \begin{cases}
                        0 & w \leq 0 \\
                        q^+ (a, a_{\frac{1}{2}}) \times q^-(w, w_{\frac{1}{2}}) & \text{elsewhere}
                    \end{cases}

            q^\pm (x, x_{\frac{1}{2}}, \phi) = \frac{1}{1 + e^{\pm \phi(x-x_{\frac{1}{2}})}}.
        """

        if self.w <= 0:
            self._fitness = 0
        else:
            q_pos = (1 + exp(self.phi_age * (self.a - self.a_half))) ** (-1)
            q_neg = (1 + exp(-self.phi_weight * (self.w - self.w_half))) ** (-1)

            self._fitness = q_pos * q_neg

    @property
    def fitness(self):
        """
        Returns the fitness of the animal.

        Returns
        -------
        fitness : float
        """

        if self._fitness is None:
            self.calculate_fitness()

        return self._fitness


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
    def default_motion(cls):
        """
        Default movement parameters for Herbivores.

        Returns
        -------
        stride : int
            Step size.
        movable : dict
            Movable terrain.
        """

        return 1, {"H": True, "L": True, "D": True, "W": False}

    def __init__(self, age=None, weight=None):
        super().__init__(weight, age)

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
    def default_motion(cls):
        """
        Default movement parameters for Carnivores.

        Returns
        -------
        stride : int
            Step size.
        movable : dict
            Movable terrain.
        """

        return 1, {"H": True, "L": True, "D": True, "W": False}

    def __init__(self, age=None, weight=None):
        super().__init__(weight, age)

    def predation(self, herbivores):
        r"""
        The herbivore tries to kill and eat the herbivores at the current location.

        Parameters
        ----------
        herbivores : list
            List of herbivores at current location.

        Returns
        -------
        killed : list
            List of herbivores that were killed.

        Notes
        -----
        Carnivores try to kill herbivores with a probability given by:

        .. math::

            p = \begin{cases}
                    0 & \text{if } \Phi_{\text{carn}} \leq \Phi_{\text{herb}} \\
                    \frac{\Phi_{\text{carn}} - \Phi_{\text{herb}}}{\Delta \Phi_{\text{max}}} &
                    \text{if } 0 < \Phi_{\text{carn}} - \Phi_{\text{herb}} <
                    \Delta \Phi_{\text{max}} \\
                    1 & \text{otherwise}
                \end{cases}.
        """

        eaten = 0
        killed = []

        for herbivore in herbivores:

            carnivore_fitness = self.fitness
            herbivore_fitness = herbivore.fitness
            difference = carnivore_fitness - herbivore_fitness

            if carnivore_fitness <= herbivore_fitness:
                p = 0
            elif 0 < difference < self.DeltaPhiMax:
                p = difference / self.DeltaPhiMax
            else:
                p = 1

            if random.random() < p:

                if herbivore.w < self.F - eaten:
                    eaten += herbivore.w
                    self.gain_weight(food=herbivore.w)
                else:
                    rest = self.F - eaten
                    self.gain_weight(food=rest)
                    break

                killed.append(herbivore)

        return killed
