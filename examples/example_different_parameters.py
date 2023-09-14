"""
Example using different species' parameters.
"""

from biosim.simulation import BioSim

if __name__ == "__main__":

    map = """\
             WWWWWWWWWWWWW
             WWWLWWWWWHHWW
             WWLLLWWLWHLLW
             WWLLLLWWWMLMW
             WWHHLLLHWWMMW
             WHHLLLHWWWLMW
             WWWHHWWWWWMWW
             WWWWWWWWWWWWW"""

    population = [{"loc": (4, 11),
                   "pop": [{"species": "Herbivore", "age": 5, "weight": 20} for _ in range(100)]
                          + [{"species": "Carnivore", "age": 5, "weight": 20} for _ in range(50)]},
                  {"loc": (5, 5),
                   "pop": [{"species": "Herbivore", "age": 5, "weight": 20} for _ in range(100)]
                          + [{"species": "Carnivore", "age": 5, "weight": 20} for _ in range(20)]}]

    sim = BioSim(island_map=map, ini_pop=population, seed=123456, vis_years=1)

    sim.set_animal_parameters("Herbivore",
                              {"eta": 0.01,
                               "omega": 0.25,
                               "beta": 0.95,
                               "zeta": 4.5})
    sim.set_animal_parameters("Carnivore",
                              {"omega": 0.7,
                               "F": 35,
                               "DeltaPhiMax": 7.5})

    sim.simulate(250)