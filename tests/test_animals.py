from src.biosim.animals import Animal, Herbivore, Carnivore

Thyra = Herbivore((1,1))
Hallvard = Carnivore((1,1))

# Checking the parameters
print(Thyra.parameters)
print(Hallvard.parameters)