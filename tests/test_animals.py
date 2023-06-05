from src.biosim.animals import Herbivore, Carnivore

Thyra = Herbivore((1,1))
Hallvard = Carnivore((1,1), age=10, weight=10)

def check():
    print(" > Parameters")
    print("  ", Thyra.get_parameters())
    print("  ", Hallvard.get_parameters())

    print(" > Weight")
    print("  ", Thyra.w)
    print("  ", Hallvard.w)

    print(" > Age")
    print("  ", Thyra.a)
    print("  ", Hallvard.a)

    print(" > Fitness")
    print("  ", Thyra.fitness)
    print("  ", Hallvard.fitness)

print("Initial state")
check()

print("Calling functions")
Thyra.aging()
Hallvard.aging()
Thyra.gain_weight(10)
Hallvard.gain_weight(1000)
Thyra.lose_weight()
Hallvard.lose_weight()
Thyra.lose_weight_birth(10)
Hallvard.lose_weight_birth(1000)

check()

print("Changing parameters")
new_parameters_1 = {"w_birth": 100}
# new_parameters_2 = {"DeltaPhiMax": 0}

Thyra.set_parameters(parameters=new_parameters_1)
Herbivore.set_parameters({"F": 100})
# Hallvard.set_parameters(new_parameters_2)
# Carnivore.set_parameters({"feil": 100}) # Raises error
# Carnivore.set_parameters({"DeltaPhiMax": 0}) # Raises error

check()