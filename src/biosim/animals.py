class Animal:
    @classmethod
    def set_parameters(cls, parameters=None):
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
        self.weight = weight
        self.age = age

    @property
    def fitness(self):
        pass

class Herbivore(Animal):
    @classmethod
    def default_parameters(cls):
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