import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import random

# Endre til relative imports "."
from src.biosim.animals import Herbivore, Carnivore

class Island:
    def __init__(self, geography, ini_pop=None):
        self.geography = geography
        self.terrain, self.coordinates = self.terraform()

        # Runs add_population if ini_pop is not None:
        self.add_population(population=ini_pop) if ini_pop is not None else None

    def add_population(self, population):
        """
        Adds a population to the island.

        Parameters
        ----------
        - population: list of dictionaries.
            [{"loc": (x, y), "pop": [{"species": val, "age": val, "weight": val}]}]
        """

        for animals in population:
            location = animals["loc"]
            if location not in self.coordinates:
                raise ValueError("Invalid location: {0}".format(location))
            for animal in animals["pop"]: #if weight or age not specified, added to dictionary
                # with value None
                if "age" not in animal:
                    animal["age"] = None
                if "weight" not in animal:
                    animal["weight"] = None
                try:
                    self.cells[location[0]-1][location[1]-1].add_animal(species=animal["species"],
                                                                        age=animal["age"],
                                                                        weight=animal["weight"])

                    # Her sliter jeg. Jeg vil legge til animals i den rette cellen. Hvordan gjør jeg det?

                except:
                    raise ValueError("Error in adding animal: {0}".format(animal))

    def terraform(self):
        """
        Creates a terrain from a given geography.
        Visualises the map if specified.

        Parameters
        ----------
        - geography: str
            A string representing the geography of the island.
        - visualise: bool
            A boolean representing whether or not the map should be visualised.

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
        - coordinates: list
            A list representing the coordinates of the island.
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
                    raise ValueError("Cell {0} contains an invalid letter ({1}).".format((i+1, j+1),
                                                                                         terrain[i][j]))

        # Creates the coordinate map:
        self.cells = []
        coordinates = []
        for i in range(X):
            row = []
            for j in range(Y):
                row.append(Cell())
                coordinates.append((i+1, j+1))
            self.cells.append(row)

        return terrain, coordinates

    def visualise(self, colours=None):
        """
        Visualises the island.

        Parameters
        ----------
        - colours: dict
            {"Type": [R, G, B]}
            A dictionary containing the colours of the different terrains.
            Must contain types: "W", "L", "H" and "D".
        """

        # Defining colours:
        if type(colours) is not dict:  # Using default colours if not otherwise specified.
            colours = {
                "L": [185, 214, 135],
                "H": [232, 236, 158],
                "D": [255, 238, 186],
                "W": [149, 203, 204]
            }

        X = len(self.terrain)
        Y = len(self.terrain[0])
        coloured_map = np.empty((X, Y, 3), dtype="uint8")

        # Inserting colours into the island:
        for i in range(X):
            for j in range(Y):
                if self.terrain[i][j] == "W":
                    coloured_map[i, j] = colours["W"]
                elif self.terrain[i][j] == "L":
                    coloured_map[i, j] = colours["L"]
                elif self.terrain[i][j] == "H":
                    coloured_map[i, j] = colours["H"]
                elif self.terrain[i][j] == "D":
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

class Cell(Island):

    def __init__(self):
        self.animals = {"Herbivores": [], "Carnivores": []}

    def add_animal(self, species, age=None, weight=None):
        if species == "Herbivore":
            self.animals["Herbivores"].append(Herbivore(age=age, weight=weight))
        else:
            self.animals["Carnivores"].append(Carnivore(age=age, weight=weight))

    # class Cell:
    # {Herbivores: [], Carnivores: []}
    # ini_herbs = [{’loc’: (10, 10),
    # ’pop’: [{’species’: ’Herbivore’, ’age’: 5, ’weight’: 20} for _ in range(150)]}
    # __init__ ^
    # Get older
    # Lose weight
    # etc.

    # Die
    # Loop over elements in lists in dict,
    # remove dead animals from list(s)

if __name__ == "__main__":
    geogr = """\
                   WWWWWWWWWWWWWWWWWWWWW
                   WHWWWWWWHWWWWLLLLLLLW
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

    a = Island(geogr)

    new_animals = [{"loc": (2, 2),
                    "pop": [{"species": "Herbivore", "age": 5, "weight": 20}]}]
    a.add_population(new_animals)

    print(a.cells[1][1].animals["Herbivores"][0].a)
