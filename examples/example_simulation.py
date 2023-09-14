"""
This is a small demo script running a BioSim simulation.
"""

from biosim.simulation import BioSim

if __name__ == "__main__":

    nmbu = """\
              WWWWWWWWWWWWWWWWWWWWWWWWWWW
              WWWWWWWWWWWWWWWWWWWLLLWLLLW
              WWWWWWWWWWWWWWWWWWWLHLWLHLW
              WWWWWWWWWLLLLLLLLLLLHLWLHLW
              WWWWWWWWWLHHHHHHHHHLHLWLHLW
              WWWWWWWWWLHLLLLLLLLLHLLLHLW
              WWWWWWWWWLHLWWWWWWWLHHHHHLW
              WWWWWWWWWLHLWLLLLLLLLLLLLLW
              WWWWWWWWWLHLWLHHHHLWWLHLWWW
              WWWLLLLLLLHLLLHLLHLLWLHLWWW
              WWWLHHHHHHHHHLHLHHHLWLHLWWW
              WWWLHLLLLLHLLLHLLLHLWLHLWWW
              WWWLHLWWWLHLWLHHHHHLWLHLWWW
              WWWLHLWLLLLLLLLLLLLLWLHLWWW
              WWWLHLWLHHLHHLWLHLWWWLHLWWW
              WWWLHLWLHHHHHLLLHLLLLLHLWWW
              WWWLHLWLHLHLHLHHHHHHHHHLWWW
              WWWLHLWLHLLLHLLLHLLLLLLLWWW
              WWWLHLWLHLWLHLLLHLWWWWWWWWW
              WLLLLLLLLLWLLLWLHLWWWWWWWWW
              WLHHLLHLWWWWWWWLHLWWWWWWWWW
              WLHHHLHLLLLLLLLLHLWWWWWWWWW
              WLHLHLHLHHHHHHHHHLWWWWWWWWW
              WLHLHHHLLLLLLLLLLLWWWWWWWWW
              WLHLLHHLWWWWWWWWWWWWWWWWWWW
              WLLLLLLLWWWWWWWWWWWWWWWWWWW
              WWWWWWWWWWWWWWWWWWWWWWWWWWW"""

    population = [{"loc": (14, 14),
                   "pop": [{"species": "Herbivore", "age": 5, "weight": 20} for _ in range(150)]},
                  {"loc": (14, 14),
                   "pop": [{"species": "Carnivore", "age": 5, "weight": 20} for _ in range(40)]}]

    sim = BioSim(island_map=nmbu, ini_pop=population, seed=123456, vis_years=1)

    sim.simulate(300)
