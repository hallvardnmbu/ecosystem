class Animal:
    def __init__(self, position, weight, age):
        self.position = position
        self.weight = weight
        self.age = age

class Herbivore(Animal):
    def __init__(self, position, weight=None, age=0):
        super().__init__(position, weight, age)

class Carnivore(Animal):
    def __init__(self, position, weight=None, age=0):
        super().__init__(position, weight, age)