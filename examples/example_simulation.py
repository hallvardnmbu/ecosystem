from src.biosim.simulation import BioSim

geogr = """\
           WWWWWWWWWWWWWWWWWWWWW
           WWWWWWWWHWWWWLLLLLLLW
           WHHHHHLLLLWWLLLLLLLWW
           WHHHHHHHHHWWLLLLLLWWW
           WHHHHHLLLLLLLLLLLLWWW
           WHHHHHLLLDDLLLHLLLWWW
           WHHLLLLLDDDLLLHHHHWWW
           WWHHHHLLLDDLLLHWWWWWW
           WHHHLLLLLDDLLLLLLLWWW
           WHHHHLLLLDDLLLLWWWWWW
           WWHHHHLLLLLLLLWWWWWWW
           WWWHHHHLLLLLLLWWWWWWW
           WWWWWWWWWWWWWWWWWWWWW"""

population = [{"loc": (5, 10),
               "pop": [{"species": "Herbivore", "age": 5, "weight": 20} for _ in range(150)]},
              {"loc": (5, 10),
               "pop": [{"species": "Carnivore", "age": 5, "weight": 20} for _ in range(40)]}]

sim = BioSim(island_map=geogr, ini_pop=population, seed=123456)

sim.simulate(200)