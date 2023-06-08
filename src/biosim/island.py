import random
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from .animals import Herbivore, Carnivore

class Island:
    @classmethod
    def default_fodder_parameters(cls):
        """
        Returns the default parameters for the fodder on the island in the different terrain types.
        """

        return {"H": 300, "L": 800, "D": 0, "W": 0}

    def __init__(self, geography, ini_pop=None):
        self.available_fodder = Island.default_fodder_parameters()

        self.geography = geography
        self.terrain, self.coordinates = self.terraform()

        # Runs add_population if ini_pop is not None:
        self.add_population(population=ini_pop) if ini_pop is not None else None

        self.year = 0

    def set_fodder_parameters(self, new_parameters=None):
        """
        Set the parameters for the fodder on the island in the different terrain types.

        Parameters
        ----------
        - new_parameters: dict
            {"terrain": value}
            If None, the default parameters are set.

        Raises
        ------
        - ValueError
            If negative parameters are passed.
            If invalid parameters are passed.
        """

        if new_parameters is None:
            self.available_fodder = Island.default_fodder_parameters()
        else:
            for key, val in new_parameters.items():
                if key not in self.available_fodder:
                    raise ValueError("Invalid parameter: {0}".format(key))
                if type(val) != int and val < 0:
                    raise ValueError("Value for: {0} should be a positive integer.".format(key))
                self.available_fodder[key] = val

    def add_population(self, population):
        """
        Adds a population to the island.

        Parameters
        ----------
        - population: list of dictionaries.
            [{"loc": (x, y), "pop": [{"species": val, "age": val, "weight": val}]}]

        Raises
        ------
        - ValueError
            If the location is not on the map.
            If the location is in Water ("W").
            If the animal is invalid.
        """

        for location_animals in population:
            location = location_animals["loc"]
            if location not in self.coordinates:
                raise ValueError("Invalid location: {0}".format(location))

            # Convert location to 0-indexing:
            i = location[0]-1
            j = location[1]-1
            if self.terrain[i][j] == "W":
                raise ValueError("Animals cannot be placed in water (location: {0}).".format(
                    location))

            # Iterate through the animals at the given location:
            animals = location_animals["pop"]
            for animal in animals:
                if "age" not in animal:
                    animal["age"] = None
                if "weight" not in animal:
                    animal["weight"] = None
                try:
                    self.cell_grid[i][j].add_animal(species=animal["species"],
                                                age=animal["age"],
                                                weight=animal["weight"])
                except:
                    raise ValueError("Error when adding: {0}. Double check the parameters.".format(
                        animal))

    @property
    def n_animals_per_species(self):
        """
        Counts the number of animals per species on the island.

        Returns
        -------
        - n_animals_per_species: dictionary
            {"Herbivores": n_herbivores, "Carnivores": n_carnivores}
        """

        n_animals_per_species = {"Herbivores": 0, "Carnivores": 0}
        for cells in self.cell_grid:
            for cell in cells:
                n_animals_per_species["Herbivores"] += len(cell.herbivores)
                n_animals_per_species["Carnivores"] += len(cell.carnivores)
        return n_animals_per_species

    @property
    def n_animals(self):
        """
        Counts the number of animals on the island.

        Returns
        -------
        - n_animals: int
        """

        both = self.n_animals_per_species
        n_animals = both["Herbivores"] + both["Carnivores"]

        return n_animals

    def terraform(self):
        """
        Creates a terrain from a given geography.
        Visualises the map if specified.

        Parameters
        ----------
        - geography: str
            A string representing the geography of the island.

        Raises
        ------
        - ValueError
            If the edges of the map are not "W" (Water).
            If the map is not rectangular.
            If the map contains invalid terrain types.

        Returns
        -------
        - terrain: list of strings
            A list of strings representing the terrain of the island.
        - coordinates: list
            A list representing the coordinates of the island. Each letter in the terrain
            corresponds to its own cell.
            The top left corner has the coordinates (1, 1).
        """

        island = textwrap.dedent(self.geography)
        terrain = island.split("\n")
        X = len(terrain)
        Y = len(terrain[0])

        # Checks whether the map is rectangular:
        for i in range(X):
            if len(terrain[i]) != Y:
                raise ValueError("The map must be rectangular.")

        # Checks whether the edges are "W" (Water):
        for i in range(X):
            if terrain[i][0] != "W" or terrain[i][Y-1] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")
        for j in range(Y):
            if terrain[0][j] != "W" or terrain[X-1][j] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")

        # Checks whether the map contains only valid characters:
        invalid = any(letter not in ["W", "L", "H", "D"] for row in terrain for letter in row)
        if invalid:
            raise ValueError("The map contains invalid terrain types.")

        # Creates the cells and coordinate-map:
        self.cell_grid = []
        coordinates = []
        for i in range(X):
            row = []
            for j in range(Y):
                fodder = self.available_fodder[terrain[i][j]]
                row.append(Cell(cell_type=terrain[i][j], fodder=fodder))
                coordinates.append((i+1, j+1))
            self.cell_grid.append(row)

        return terrain, coordinates

    def visualise(self, my_colours=None):
        """
        Visualises the island.

        Parameters
        ----------
        - colours: dict
            {"Type": [R, G, B]}
            A dictionary containing the colours of the different terrains.
            Valid "Type"'s are: "L", "H", "D", "W".
        """

        colours = {"L": [185, 214, 135],
                   "H": [232, 236, 158],
                   "D": [255, 238, 186],
                   "W": [149, 203, 204]}

        # Adds the user-defined colours:
        if my_colours is not None:
            for key, val in my_colours.items():
                colours[key] = val

        coloured_map = np.array([[colours[type] for type in row] for row in self.terrain],
                                dtype=np.uint8)

        # Visualising the island:
        plt.imshow(coloured_map)
        plt.xticks([]), plt.yticks([]), plt.title("Map of Rossumøya (Pylandia)")

        description = {"L": "Lowland", "H": "Highland", "D": "Desert", "W": "Water"}
        patches = [mpatches.Patch(color=(val[0] / 255, val[1] / 255, val[2] / 255),
                                  label="{0}".format(
                                      str(pd.DataFrame([key]).replace(description)[0][0]))) for
                   key, val in colours.items()]
        plt.legend(handles=patches, bbox_to_anchor=(0, -0.01), loc=2, borderaxespad=0)

        plt.show()

    def procreate(self):
        """
        Iterates through all the animals on the island.
        An animal gives birth to a baby if the following conditions are met:
        - A probability of min(1, gamma * fitness * N).
        - The baby's weight is less than the parent's weight.
        If a baby is born, it is added to the cell of the parent.
        """

        for cells in self.cell_grid:
            for cell in cells:
                # Procreation of herbivores if cell is habitated by them and if the conditions are met:
                if cell.herbivores:
                    H = len(cell.herbivores)
                    for animal in cell.herbivores:
                        if random.random() < min(1, animal.gamma * animal.fitness * H):
                            baby_weight = animal.lognormv()
                            if baby_weight < animal.w:
                                cell.add_animal(species=animal.species, age=0, weight=baby_weight)

                # Procreation of carnivores if cell is habitated by them and if the conditions are met:
                if cell.carnivores:
                    C = len(cell.carnivores)
                    for animal in cell.carnivores:
                        if random.random() < min(1, animal.gamma * animal.fitness * C):
                            baby_weight = animal.lognormv()
                            if baby_weight < animal.w:
                                cell.add_animal(species=animal.species, age=0, weight=baby_weight)

    def feed(self):
        """
        Iterates through all the animals on the island.
        Herbivores eat fodder. The fittest herbivores eat first.
        Carnivores eat herbivores. They hunt in random order and prey on the weakest herbivores
        first.
        """

        for cells in self.cell_grid:
            for cell in cells:
                if cell.herbivores or cell.carnivores:
                    cell.reset_fodder()

                    # Sort herbivores by descending fitness:
                    herbivores = sorted(cell.herbivores, key=lambda herbivore: herbivore.fitness,
                                        reverse=True)

                    for herbivore in herbivores:
                        cell.herbivore_eat_fodder(amount=herbivore.F, animal=herbivore)

                    # Sort herbivores by ascending fitness (flip^):
                    herbivores = herbivores[::-1]
                    # Sort carnivores randomly:
                    carnivores = cell.carnivores
                    random.shuffle(carnivores)

                    for carnivore in carnivores:
                        killed = cell.carnivore_kill(carnivore, herbivores)
                        herbivores = [herbivore for herbivore in herbivores if herbivore not in killed]

    def migrate(self):
        """
        Iterates through all the animals on the island.
        An animal migrates with a probability of mu * fitness, and moves to a random neighbouring cell.
        """

        moves = []
        for i, cells in enumerate(self.cell_grid):
            for j, cell in enumerate(cells):
                if cell.herbivores or cell.carnivores:
                    for animal in cell.herbivores + cell.carnivores:
                        if random.random() < animal.mu * animal.fitness:
                            direction = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
                            # Finds the new cell:
                            new_cell = self.cell_grid[i+direction[0]][j+direction[1]]
                            # Checks if the new cell is a valid cell (Cell.can_move = True/False):
                            if new_cell.can_move:
                                movement = (animal, cell, new_cell)
                                moves.append(movement)

        for move in moves:
            animal = move[0]
            from_cell = move[1]
            to_cell = move[2]
            from_cell.animals[animal.species].remove(animal)
            to_cell.animals[animal.species].append(animal)

    def aging(self):
        """
        Iterates through all the animals on the island, and ages them by one year.
        """

        for i, cells in enumerate(self.cell_grid):
            for j, cell in enumerate(cells):
                if cell.herbivores or cell.carnivores:
                    for animal in cell.herbivores + cell.carnivores:
                        animal.aging()

    def weight_loss(self):
        """
        Iterates through all the animals on the island, and makes them lose weight.
        """

        for i, cells in enumerate(self.cell_grid):
            for j, cell in enumerate(cells):
                if cell.herbivores or cell.carnivores:
                    for animal in cell.herbivores + cell.carnivores:
                        animal.lose_weight()

    def death(self):
        """
        Iterates through all the animals on the island, and 'kills' them if:
        - The animal's weight is 0.
        - A probability of weight * (1 - fitness).
        """

        for i, cells in enumerate(self.cell_grid):
            for j, cell in enumerate(cells):
                if cell.herbivores or cell.carnivores:
                    for animal in cell.herbivores + cell.carnivores:
                        if animal.a == 0:
                            cell.animals[animal.species].remove(animal)
                        if random.random() < animal.omega * (1 - animal.fitness):
                            cell.animals[animal.species].remove(animal)

    def yearly_cycle(self):
        """
        Runs through the yearly cycle of the island in the following order:
            1. Procreation
            2. Feeding
            3. Migration
            4. Aging
            5. Weight loss
            6. Death
        All animals undergo the same steps simultaneously.
        """

        self.procreate()
        self.feed()
        self.migrate()
        self.aging()
        self.weight_loss()
        self.death()
        self.new_year()

    def new_year(self):
        """
        Adds a new year to the island.
        """

        self.year += 1

class Cell:

    def __init__(self, fodder, cell_type=None):
        self.can_move = True if cell_type != "W" else False

        self.fodder_max = fodder
        self.fodder = fodder

        self.herbivores = []
        self.carnivores = []
        self.animals = {"Herbivore": self.herbivores,
                        "Carnivore": self.carnivores}
        self.animal_map = {"Herbivore": Herbivore,
                           "Carnivore": Carnivore}

    def herbivore_eat_fodder(self, amount, animal):
        """
        Removes fodder from the cell.
        If the amount to be removed is greater than the amount of fodder in the cell, the fodder is set to 0.
        """

        if self.fodder < amount:
            food = self.fodder
        else:
            food = amount

        self.fodder -= food
        animal.gain_weight(food=food)

    def carnivore_kill(self, carnivore, herbivores):
        """
        Carnivores tries to kill Herbivores in the same cell.
        Parameters
        ----------
        - carnivore: class object
            One of the carnivores in the cell.
        - herbivores: list
            Herbivores in the cell sorted by ascending fitness.
        """

        food = 0
        killed = []
        for herbivore in herbivores:
            if food >= carnivore.F:
                food = carnivore.F
                break
            if carnivore.fitness <= herbivore.fitness:
                p = 0
            elif 0 < carnivore.fitness - herbivore.fitness < carnivore.DeltaPhiMax:
                p = (carnivore.fitness - herbivore.fitness) / carnivore.DeltaPhiMax
            else:
                p = 1
            if random.random() < p:
                food += herbivore.w

                self.herbivores.remove(herbivore)
                killed.append(herbivore)

        carnivore.gain_weight(food=food)
        return killed

    def reset_fodder(self):
        """
        Resets the amount of fodder in the cell to the maximum amount of that terrain type.
        """

        self.fodder = self.fodder_max

    def add_animal(self, species, age=None, weight=None):
        """
        Adds an animal to the cell.

        Parameters
        ----------
        - species: str
            A string representing the species of the animal.
        - age: int
            An integer representing the age of the animal.
        - weight: float
            A float representing the weight of the animal.

        Raises
        ------
        - ValueError
            If the species is not "Herbivore" or "Carnivore".
        """

        try:
            self.animals[species].append(self.animal_map[species](age=age, weight=weight))
        except:
            raise ValueError("The species must be either 'Herbivore' or 'Carnivore'.")

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
    b = Island(geogr)

    new_animals = [{"loc": (2, 2),
                    "pop": [{"species": "Herbivore"} for _ in range(20)] + [{"species":
                                                                                 "Carnivore"} for
                                                                            _ in range(20)]}]
    a.add_population(new_animals)

    print("a", a.available_fodder)
    print("b", b.available_fodder)

    a.set_fodder_parameters({"H": 1})

    print("a", a.available_fodder)
    print("b", b.available_fodder)

    print("a", a.n_animals)
    print("a", a.cells[1][1].herbivores)
