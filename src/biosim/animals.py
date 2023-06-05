class Animal:
    def __init__(self, age=0, weight):
        self.age = age
        self.weight = weight

class Herbivore(Animal):
    def __init__(self):
        pass

class Carnivore(Animal):
    def __init__(self):
        pass