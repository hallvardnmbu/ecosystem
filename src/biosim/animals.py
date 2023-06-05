import random
random.seed(1)

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

    def __init__(self, position, weight, age):
        self.position = position
        self.age = age
        if not weight:
            self.weight = random.lognormal(self.parameters["w_birth"], self.parameters["sigma_birth"])
        else:
            self.weight = weight

    def aging(self):
        """
        Increments the age of the animal by one year.
        """

        self.age += 1

    def gain_weight(self, food):
        """
        Increments the weight of the animal by the factor beta and the amount of food eaten.
        """

        self.weight += self.parameters["beta"] * food

    def lose_weight(self):
        """
        Decrements the weight of the animal by the factor eta.
        """

        self.weight -= self.parameters["eta"] * self.weight

    def lose_weight_birth(self, baby_weight):
        """
        Decrements the weight of the animal by the factor xi and the weight of the baby.
        """

        self.weight -= self.parameters["xi"] * baby_weight

    def baby_weight(self):
        """
        Calculates the weight of the baby.
        """

        if random.random() < min(1, self.parameters["gamma"] * self.fitness * 10): # BYTT "10" MED: "self.count_animals_cell()" COUNT ANIMAL CELL!):
            return random.lognormal(self.parameters["w_birth"], self.parameters["sigma_birth"])

    def give_birth(self, baby_weight):
        """
        Creates a new animal with the given weight at the same position as the parent.
        """

        if baby_weight > self.weight:
            return
        self.lose_weight_birth(baby_weight)
        self.__class__(position=self.position, weight=baby_weight)

    @property
    def fitness(self):

        #get parametres
        phi_age = self.parameters["phi_age"]
        phi_weight = self.parameters["phi_weight"]
        a = self.parameters["a"]
        a_half = self.parameters["a_half"]
        w_half = self.parameters["w_half"]

        def qpos(x,xhalf,phi):
            return (1+exp(phi(x-xhalf)))**(-1)
        def qneg(x,xhalf,phi):
            return (1+exp(-phi(x-xhalf)))**(-1)

        if self.weight<=0:
            self.fitness=0
        else:
            self.fitness=qpos(a,a_half,phi_age)*qneg(w,w_half,phi_weight)





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
        self.parameters = self.default_parameters()

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
                "i_weight": 0.4,
                "mu": 0.4,
                "gamma": 0.8,
                "zeta": 3.5,
                "xi": 1.1,
                "omega": 0.8,
                "F": 50.0,
                "DeltaPhiMax": 10.0}

    def __init__(self, position, weight=None, age=0):
        super().__init__(position, weight, age)
        self.parameters = self.default_parameters()