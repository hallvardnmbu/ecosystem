"""Contains the different animal species."""


from math import exp, sqrt, log
import random


class Animal:
    """
    Parent class for animal species.

    Parameters
    ----------
    age : int
    weight : float

    Raises
    ------
    ValueError
        If age or weight is invalid values.
    """
    @classmethod
    def birthweight(cls):
        r"""
        A continuous probability distribution of a random variable whose logarithm is normally
        distributed, which is used to draw birth weights

        Returns
        -------
        weight : float
            From the normal distribution.

        Notes
        -----
        :math:`\mu` and :math:`\sigma` are calculated from the birth weight and its standard
        deviation through the following equations:

        .. math::

            \mu = \log \left( \frac{{w_{\textrm{birth}}^2}}{{\sqrt{{\sigma_{\textrm{birth}}^2
            + w_{\textrm{birth}}^2}}}} \right)


            \sigma = \sqrt{\log \left( 1 + \frac{{\sigma_{\textrm{birth}}^2}}{{w_{\textrm{
            birth}}^2}}
            \right)}

        (Retrieved from: https://en.wikipedia.org/wiki/Log-normal_distribution).
        """
        mu = log((cls.w_birth**2)/sqrt(cls.w_birth**2 + cls.sigma_birth**2))
        sigma = sqrt(log(1 + ((cls.sigma_birth**2)/(cls.w_birth**2))))

        return random.lognormvariate(mu, sigma)

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

        Raises
        ------
        ValueError
            If stride is nonzero or negative.
        TypeError
            If stride is not a number.
        KeyError
            If invalid terrain types are passed to new_movable.
        """
        if new_stride is not None:
            try:
                cls.stride = round(new_stride)
            except TypeError as err:
                raise TypeError("Stride should be a number.") from err
        else:
            try:
                stride = cls.stride  # noqa
            except AttributeError:
                cls.stride = cls.default_motion()["stride"]

        if new_movable is not None:
            movable = cls.default_motion()["movable"]
            if not all(key in movable.keys() for key in new_movable.keys()):
                raise KeyError("New movable terrain contains invalid terrain types.")
            for key, boolean in new_movable.items():
                cls.movable[key] = boolean
        else:
            try:
                movable = cls.movable  # noqa
            except AttributeError:
                cls.movable = cls.default_motion()["movable"]

    @classmethod
    def get_parameters(cls):
        """
        Get the parameters for a species.

        Returns
        -------
        dict
        """
        return {"w_birth": cls.w_birth,
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
                "DeltaPhiMax": cls.DeltaPhiMax}

    @classmethod
    def set_parameters(cls, new_parameters):
        r"""
        Set the parameters for a species (and updates the probability of procreation).

        Parameters
        ----------
        new_parameters : dict

            .. code:: python

                {'parameter': value, ...}

        Raises
        ------
        ValueError
            If invalid parameter keys are passed.
            If invalid parameter values are passed.
            If invalid parameter types are passed.

        Notes
        -----
        When calling the function, one can call it on both the subclass and the object, with the
        same result.

            .. code:: python

                Subclass.set_parameters()
                Object.set_parameters()
        """
        for key, val in new_parameters.items():
            if key not in cls.default_parameters():
                raise KeyError(f"Invalid parameter: {key}")
            try:
                if key == "DeltaPhiMax" and val <= 0:
                    raise ValueError(f"Value for: {key} ({val}) should be positive.")

                if key == "eta" and val > 1:
                    raise ValueError(f"Value for: {key} ({val}) should be less than or equal to 1.")

                try:
                    if val < 0:
                        raise ValueError(f"Value for: {key} should be nonzero or positive.")
                except TypeError as err:
                    raise ValueError(f"Value for: {key} should be a number.") from err
            # This extra "except" is needed in case "DeltaPhiMax" or "eta" is not a number.
            except TypeError as err:
                raise ValueError(f"Value for: {key} should be a number.") from err

            setattr(cls, key, val)

        cls._update_w_procreate()

    @classmethod
    def _update_w_procreate(cls):
        """Updates the weight condition of procreation for the species."""
        cls.w_procreate = cls.zeta * (cls.w_birth + cls.sigma_birth)

    def __init__(self, weight, age):
        try:
            if not age:
                self.a = 0
            elif int(age) < 0:
                raise ValueError("Age should be positive.")
            else:
                self.a = age
            if not weight:
                self.w = self.birthweight()
            elif float(weight) <= 0:
                raise ValueError("Weight should be positive.")
            else:
                self.w = weight
        except ValueError as err:
            raise ValueError(f"Age: {age} and weight: {weight} must both be numbers.") from err
        self._fitness = None

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
        will neither lose weight nor give birth.
        """
        if self.w > self.xi * baby_weight:
            self.w -= self.xi * baby_weight
            self.calculate_fitness()
            return True
        return False

    def gain_weight(self, food):
        r"""
        Increments the weight of the animal by the factor :math:`\beta` and the amount of food
        eaten, and calculates the new fitness of the animal.

        Parameters
        ----------
        food : float
            The amount of food eaten.
        """
        self.w += self.beta * food
        self.calculate_fitness()

    def aging(self):
        """Increments the age of the animal by one year."""
        self.a += 1

    def lose_weight_year(self):
        r"""Decrements the weight of the animal by the factor :math:`\eta`."""
        self.w -= self.eta * self.w

    def calculate_fitness(self):
        r"""
        Calculates the fitness of the animal.

        Notes
        -----
        The fitness is calculated as follows:

        .. math::

            \Phi = \begin{cases}
                        0 & w \leq 0 \\
                        q^+ (a, a_{\frac{1}{2}}) \times q^-(w, w_{\frac{1}{2}}) & \textrm{elsewhere}
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
        return {"stride": 1,
                "movable": {"H": True, "L": True, "M": True, "W": False}}

    @classmethod
    def default_parameters(cls):
        """
        Default parameters for Herbivores.

        Returns
        -------
        dict
        """
        return {"w_birth": 10.0,        # Babyweight ~ 2.6 kg.
                "sigma_birth": 4.0,
                "beta": 0.05,           # Weightincrease when eating ~ 1 kg.
                "eta": 0.2,             # Weightloss 10% per year.
                "a_half": 2.5,
                "phi_age": 5.0,         # Life span ~ 5 years. Fitness decreases.
                "w_half": 3.0,
                "phi_weight": 0.09,
                "mu": 17.0,             # Rapid movement.
                "gamma": 0.9,           # Birthprobability p = fitness * gamma.
                "zeta": 0.22,           # Baby if weight > 3.08 kg.
                "xi": 0.42,             # Weightloss ~ 1.1 kg at birth.
                "omega": 0.4,
                "F": 20.0,              # Appetite.
                "DeltaPhiMax": 10.0}

    def __init__(self, age=None, weight=None):
        super().__init__(weight, age)

    def graze(self, available_fodder):
        """
        An animal tries to graze on the available fodder.

        Parameters
        ----------
        available_fodder : float
            The amount of fodder available at the current location.

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
        return {"stride": 1,
                "movable": {"H": True, "L": True, "M": True, "W": False}}

    @classmethod
    def default_parameters(cls):
        """
        Default parameters for Carnivores.

        Returns
        -------
        dict
        """
        return {"w_birth": 6.0,
                "sigma_birth": 1.0,
                "beta": 0.6,
                "eta": 0.125,
                "a_half": 40.0,
                "phi_age": 0.45,
                "w_half": 4.0,
                "phi_weight": 0.28,
                "mu": 0.4,
                "gamma": 0.8,
                "zeta": 3.5,
                "xi": 1.1,
                "omega": 0.3,           # "High" mortality.
                "F": 70.0,              # Appetite.
                "DeltaPhiMax": 10.0}

    def __init__(self, age=None, weight=None):
        super().__init__(weight, age)

    def predation(self, herbivores, herbivores_copy):
        r"""
        The herbivore tries to kill and eat the herbivores at the current location.

        Parameters
        ----------
        herbivores : list
            List of herbivores at the current location.
        herbivores_copy : list

        Notes
        -----
        Carnivores try to kill herbivores with a probability given by:

        .. math::

            p = \begin{cases}
                    0 & \textrm{if } \Phi_{\textrm{carn}} \leq \Phi_{\textrm{herb}} \\
                    \frac{\Phi_{\textrm{carn}} - \Phi_{\textrm{herb}}}{\Delta \Phi_{\textrm{max}}} &
                    \textrm{if } 0 < \Phi_{\textrm{carn}} - \Phi_{\textrm{herb}} <
                    \Delta \Phi_{\textrm{max}} \\
                    1 & \textrm{otherwise}
                \end{cases}.
        """
        eaten = 0
        delta_phi_max = self.DeltaPhiMax

        for herbivore in herbivores_copy:

            herbivore_fitness = herbivore.fitness
            carnivore_fitness = self.fitness
            difference = carnivore_fitness - herbivore_fitness

            if carnivore_fitness <= herbivore_fitness:
                prob = 0
            elif 0 < difference < delta_phi_max:
                prob = difference / delta_phi_max
            else:
                prob = 1

            if random.random() < prob:

                herbivores.remove(herbivore)
                rest = self.F - eaten
                if herbivore.w < rest:
                    eaten += herbivore.w
                    self.gain_weight(food=herbivore.w)
                else:
                    self.gain_weight(food=rest)
                    break
