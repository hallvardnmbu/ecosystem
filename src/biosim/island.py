import textwrap
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

class Island:
    def __init__(self, geography):
        self.geography = geography
        self.terrain = self.terraform()

    @staticmethod
    def terraform(self, visualise=False, colours=None):
        """
        Creates a terrain from a given geography.
        Visualises the map if specified.

        Parameters
        ----------
        - geography: str
            A string representing the geography of the island.
        - visualise: bool
            A boolean representing whether or not the map should be visualised.
        - colours: dict
            {"Type": [R, G, B]}
            A dictionary containing the colours of the different terrains.
            Must contain types: "W", "L", "H" and "D".

        Raises
        ------
        - ValueError
            If the edges of the map are not "W" (Water).
            If the map is not rectangular.
            If the map contains invalid terrain types.

        Returns
        -------
        - terrain: nested list
            A nested list representing the terrain of the island.
        """

        island = textwrap.dedent(self.geography)
        terrain = island.split("\n")
        X = len(terrain)
        Y = len(terrain[0])

        # Checks whether the edges are "W" (Water):
        for i in range(X):
            if terrain[i][0] != "W" or terrain[i][Y-1] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")
        for j in range(Y):
            if terrain[0][j] != "W" or terrain[X-1][j] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")

        # Checks whether the map is rectangular:
        for i in range(X):
            if len(terrain[i]) != Y:
                raise ValueError("The map must be rectangular.")

        # Checks whether the map contains only valid characters:
        for i in range(X):
            for j in range(Y):
                if terrain[i][j] not in ["W", "L", "H", "D"]:
                    raise ValueError("Cell {0} contains an invalid letter ({1}).".format((i, j), terrain[i][j]))

        # Visualise the map:
        if visualise:

            # Defining colours:
            if type(colours) is not dict:  # Using default colours if not otherwise specified.
                colours = {
                    "L": [185, 214, 135],
                    "H": [232, 236, 158],
                    "D": [255, 238, 186],
                    "W": [149, 203, 204]
                }

            coloured_map = np.empty((X, Y, 3), dtype="uint8")

            # Inserting colours into the island:
            for i in range(X):
                for j in range(Y):
                    if terrain[i][j] == "W":
                        coloured_map[i, j] = colours["W"]
                    elif terrain[i][j] == "L":
                        coloured_map[i, j] = colours["L"]
                    elif terrain[i][j] == "H":
                        coloured_map[i, j] = colours["H"]
                    elif terrain[i][j] == "D":
                        coloured_map[i, j] = colours["D"]

            # Visualising the island:
            plt.imshow(coloured_map)
            plt.xticks([]), plt.yticks([]), plt.title("Map of Pylandia")

            description = {"L": "Lowland", "H": "Highland", "D": "Desert", "W": "Water"}
            patches = [mpatches.Patch(color=(val[0] / 255, val[1] / 255, val[2] / 255),
                                      label="{0}".format(
                                          str(pd.DataFrame([key]).replace(description)[0][0]))) for
                       key, val in colours.items()]
            plt.legend(handles=patches, bbox_to_anchor=(0, -0.01), loc=2, borderaxespad=0)

            plt.show()

        return terrain

# The code in this function is given by lecturer Hans Ekkehard Plesser.
"""
Compatibility check for BioSim simulations.
This script shall function with biosim packages written for
the INF200 project June 2023.
"""
# __author__ = "Hans Ekkehard Plesser, NMBU"
# __email__ = "hans.ekkehard.plesser@nmbu.no"
# import textwrap
# import matplotlib.pyplot as plt
# from biosim.simulation import BioSim
# if __name__ == ’__main__’:
# geogr = """\
#     WWWWWWWWWWWWWWWWWWWWW
#     WWWWWWWWHWWWWLLLLLLLW
#     WHHHHHLLLLWWLLLLLLLWW
#     WHHHHHHHHHWWLLLLLLWWW
#     WHHHHHLLLLLLLLLLLLWWW
#     WHHHHHLLLDDLLLHLLLWWW
#     WHHLLLLLDDDLLLHHHHWWW
#     WWHHHHLLLDDLLLHWWWWWW
#     WHHHLLLLLDDLLLLLLLWWW
#     WHHHHLLLLDDLLLLWWWWWW
#     WWHHHHLLLLLLLLWWWWWWW
#     WWWHHHHLLLLLLLWWWWWWW
#     WWWWWWWWWWWWWWWWWWWWW"""
# geogr = textwrap.dedent(geogr)
# ini_herbs = [{’loc’: (10, 10),
# ’pop’: [{’species’: ’Herbivore’,
# ’age’: 5,
# ’weight’: 20}
# for _ in range(150)]}]
# ini_carns = [{’loc’: (10, 10),
# ’pop’: [{’species’: ’Carnivore’,
# ’age’: 5,
# ’weight’: 20}
# for _ in range(40)]}]
#
#
# sim = BioSim(island_map=geogr, ini_pop=ini_herbs,
#
# seed=123456,
#
# hist_specs={’fitness’: {’max’: 1.0, ’delta’: 0.05},
#
# ’age’: {’max’: 60.0, ’delta’: 2},
#
# ’weight’: {’max’: 60, ’delta’: 2}},
#
# vis_years=1)
#
# sim.set_animal_parameters(’Herbivore’, {’zeta’: 3.2, ’xi’: 1.8})
#
# sim.set_animal_parameters(’Carnivore’, {’a_half’: 70, ’phi_age’: 0
#
# ’omega’: 0.3, ’F’: 65,
#
# ’DeltaPhiMax’: 9.})
#
# sim.set_landscape_parameters(’L’, {’f_max’: 700})
#
# sim.simulate(num_years=100)
#
# sim.add_population(population=ini_carns)
#
# sim.simulate(num_years=100)
#
# plt.savefig(’check_sim.pdf’)