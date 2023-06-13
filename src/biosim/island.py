"""
Module for the island and its cells.
"""


import random
import textwrap
import itertools

from animals import Animal


class Island:
    """
    Class for the island.

    Parameters
    ----------
    geography : str
        A multi-line string specifying the geography of the island.
    ini_pop : list, optional
        A list of dictionaries specifying the initial population of animals.
    """

    @classmethod
    def default_fodder_parameters(cls):
        """
        Returns a dictionary with the default fodder parameters for the different terrain types.

        Returns
        -------
        dict
            A dictionary with the default fodder parameters for the different terrain types.
        """

        return {"H": 300, "L": 800, "D": 0, "W": 0}

    @classmethod
    def set_fodder_parameters(cls, new_parameters):
        """
        Set the parameters for the fodder on the island in the different terrain types.

        Parameters
        ----------
        new_parameters : dict
            Example: {`terrain`: value}

        Raises
        ------
        KeyError
            If invalid parameters are passed.
        ValueError
            If negative parameters are passed.
        """

        for key, val in new_parameters.items():
            if key not in cls.default_fodder_parameters():
                raise KeyError(f"Invalid parameter: {key}")
            try:
                if val < 0:
                    raise ValueError(f"{key}'s value ({val}) can not be negative.")
                setattr(cls, key, val)
            except TypeError:
                raise ValueError(f"Invalid value for: {key} ({val}).")

    @classmethod
    def get_fodder_parameter(cls, terrain_type):
        """
        Returns the fodder parameters for the given terrain type.

        Parameters
        ----------
        terrain_type : str
            The terrain type.

        Returns
        -------
        float
            The fodder parameter for the given terrain type.
        """

        return {"H": cls.H,
                "L": cls.L,
                "D": cls.D,
                "W": cls.W}[terrain_type]

    def __init__(self, geography, ini_pop=None):
        self.year = 0
        self.geography = textwrap.dedent(geography).split("\n")
        self.set_fodder_parameters(self.default_fodder_parameters())
        self.cell_grid = self._terraform()
        self.add_population(population=ini_pop) if ini_pop is not None else None

    def population(self):
        """
        Returns the population of the island.

        Returns
        -------
        list
            A list of dictionaries specifying the population of the island.
        """
        return [cell.animals() for cell in self.cell_grid]

    def _terraform(self):
        """
        Checks whether the geography is valid, and creates the grid of cell-objects.

        Raises
        ------
        ValueError
            If the edges of the map are not `W` (Water).
            If the map is not rectangular.
            If the map contains invalid terrain types.
        """

        x = len(self.geography)
        y = len(self.geography[0])

        for i in range(x):
            if len(self.geography[i]) != y:
                raise ValueError("The map must be rectangular.")

        for i in range(x):
            if self.geography[i][0] != "W" or self.geography[i][y-1] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")
        for j in range(y):
            if self.geography[0][j] != "W" or self.geography[x-1][j] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")

        if any(letter not in ["W", "L", "H", "D"] for row in self.geography for letter in row):
            raise ValueError("The map contains invalid terrain types.")

        cell_grid = []
        for i in range(x):
            row = []
            for j in range(y):
                # Creates the cell-objects in the grid with the index corresponding to the terrain:
                row.append(Cell(cell_type=self.geography[i][j]))
            cell_grid.append(row)

        return cell_grid

    def add_population(self, population):
        """
        Adds a population to the island.

        Parameters
        ----------
        population : list of dict
            Example: [{`loc`: (x, y), `pop`: [{`species`: str, `age`: int, `weight`: float}]}]

        Raises
        ------
        ValueError
            If the location is not on the map.
            If the location is in Water (`W`).
            If the animal is incorrectly defined.
        """

        for location_animals in population:
            location = location_animals["loc"]
            if location[0] > len(self.geography) or location[1] > len(self.geography[0]):
                raise ValueError(f"Invalid location: {location}.")

            i = location[0] - 1
            j = location[1] - 1

            animals = location_animals["pop"]
            for animal in animals:

                if animal["species"] not in Animal.mapping().keys():
                    raise ValueError(f"Invalid species: {animal}.")
                species = animal["species"]
                if "age" not in animal:
                    animal["age"] = 0
                if "weight" not in animal:
                    animal["weight"] = Animal.mapping()[species].lognormv()

                movable, _ = Animal.mapping()[species].motion()
                if not movable[self.geography[i][j]]:
                    raise ValueError(f"Invalid terrain: {location}.")
                else:
                    cell = self.cell_grid[i][j]
                    age = animal["age"]
                    weight = animal["weight"]
                    cell.animals[species].append(Animal.mapping()[species](age=age, weight=weight))

    @property
    def n_animals_per_species(self):
        """
        Counts the number of animals per species on the island.

        Returns
        -------
        n_animals_per_species: dict
        Example: {`Herbivores`: n_herbivores, `Carnivores`: n_carnivores}
         """

        n_animals_per_species = {"Herbivores": 0, "Carnivores": 0}
        for animals in self.n_animals_per_species_per_cell.values():
            for species, n_animals in animals.items():
                if n_animals != 0:
                    n_animals_per_species[species] += n_animals
        return n_animals_per_species

    @property
    def n_animals_per_species_per_cell(self):
        """
        Counts the number of animals per species on the island.

        Returns
        -------
        n_animals_per_species : dict
            Example: {"(x, y)": {`Herbivores`: n_herbivores, `Carnivores`: n_carnivores}}
        """

        n_animals_per_species_per_cell = {}
        for x, cells in enumerate(self.cell_grid):
            for y, cell in enumerate(cells):
                n_animals_per_species_per_cell[f"({x+1}, {y+1})"] = cell.n_animals_in_cell()
        return n_animals_per_species_per_cell

    @property
    def n_animals(self):
        """
        Counts the number of animals on the island.

        Returns
        -------
        n_animals : int
        """

        animals = self.n_animals_per_species
        return animals["Herbivores"] + animals["Carnivores"]

    def procreate(self):
        """
        Iterates through all the animals on the island.
        The baby is added to the same cell as the parent if the following is met:
        The baby-to-be's weight is less than the parent's weight.
        A probability of min(1, gamma * fitness * N).
          Where:
            gamma: species-specific parameter.
            fitness: the parents' fitness.
            N: number of animals of the same species in the cell.
        """

        for cells in self.cell_grid:
            for cell in cells:

                animals_in_cell = {"Herbivore": len(cell.animals["Herbivore"]),
                                   "Carnivore": len(cell.animals["Carnivore"])}

                babies = []
                for animal in itertools.chain(*cell.animals.values()):

                    # Procreation may only take place if the following is satisfied:
                    if animal.w >= animal.zeta * (animal.w_birth + animal.sigma_birth):

                        n = animals_in_cell[animal.species]
                        if random.random() < min(1, animal.gamma * animal.fitness * n):
                            baby_weight = animal.lognormv()

                            # If the parents' weight is greater than the baby's weight * xi, the
                            # baby is born, and the parents' weight decreases accordingly ^:
                            if animal.lose_weight_birth(baby_weight):
                                baby = Animal.mapping()[animal.species](age=0,
                                                                        weight=baby_weight)
                                # For the newborns to be excluded from being able to procreate,
                                # they are placed in the parents' cell after the loop.
                                babies.append(baby)

                for baby in babies:
                    cell.animals[baby.species].append(baby)

    def feed(self):
        """
        Iterates through all the animals on the island.
        Herbivores eat before carnivores, and eat fodder. The fittest herbivores eat first.
        Carnivores eat herbivores. They hunt in random order and prey on the weakest herbivores
        first.
        """

        for cells in self.cell_grid:
            for cell in cells:
                if cell.animals["Herbivore"]:

                    cell.grow_fodder()

                    cell.animals["Herbivore"] = sorted(cell.animals["Herbivore"],
                                                       key=lambda herb: herb.fitness,
                                                       reverse=True)
                    for herbivore in cell.animals["Herbivore"]:
                        cell.fodder -= herbivore.graze(cell.fodder)

                    random.shuffle(cell.animals["Carnivore"])
                    cell.animals["Herbivore"] = sorted(cell.animals["Herbivore"],
                                                       key=lambda herb: herb.fitness)
                    for carnivore in cell.animals["Carnivore"]:
                        killed = carnivore.predation(cell.animals["Herbivore"])
                        cell.animals["Herbivore"] = [herb for herb in cell.animals["Herbivore"]
                                                     if herb not in killed]

    def migrate(self):
        """
        Iterates through all the animals on the island.
        An animal migrates with a probability of mu * fitness, and moves to a random neighbouring
        cell.
        """

        migrating_animals = []
        for i, cells in enumerate(self.cell_grid):
            for j, cell in enumerate(cells):
                for animal in itertools.chain(*cell.animals.values()):

                    # The probability of migrating is calculated:
                    if random.random() < animal.mu * animal.fitness:

                        movable, stride = animal.motion()
                        x, y = random.choice([(stride, 0),
                                              (-stride, 0),
                                              (0, stride),
                                              (0, -stride)])

                        if movable[self.geography[i + x][j + y]]:
                            new_cell = self.cell_grid[i + x][j + y]
                            movement = (animal, cell, new_cell)
                            migrating_animals.append(movement)

        # In order to prevent animals from moving multiple times (say an animal moves from (1,
        # 1) -> (1, 2), we don't want the animal to be able to move again), the movements are
        # executed after each cell has been iterated through:
        for movement in migrating_animals:
            animal, from_cell, to_cell = movement
            from_cell.animals[animal.species].remove(animal)
            to_cell.animals[animal.species].append(animal)

    def ageing(self):
        """
        Iterates through all the animals on the island and ages them accordingly.
        """

        for cells in self.cell_grid:
            for cell in cells:
                for animal in itertools.chain(*cell.animals.values()):
                    animal.aging()

    def weight_loss(self):
        """
        Iterates through all the animals on the island and decrements their weight accordingly.
        """

        for cells in self.cell_grid:
            for cell in cells:
                for animal in itertools.chain(*cell.animals.values()):
                    animal.lose_weight_year()

    def death(self):
        """
        Iterates through all the animals on the island and removes them if they die.
        """

        for cells in self.cell_grid:
            for cell in cells:

                dying_animals = []
                for animal in itertools.chain(*cell.animals.values()):
                    if animal.w <= 0 or random.random() < animal.omega * (1 - animal.fitness):
                        dying_animals.append(animal)

                for animal in dying_animals:
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
        self.ageing()
        self.weight_loss()
        self.death()

        self.year += 1

        if self.year % 10 == 0:
            print(f"Year: {self.year}")


class Cell:
    """
    A cell on the island.

    Parameters
    ----------
    cell_type : str
        The terrain-type of the cell. Determines if animals can move through the cell or not.
    """

    def __init__(self, cell_type):
        self.cell_type = cell_type
        self.fodder = Island.get_fodder_parameter(cell_type)
        self.animals = {"Herbivore": [],
                        "Carnivore": []}

    def grow_fodder(self):
        """
        Grows fodder in the cell.
        """

        self.fodder = Island.get_fodder_parameter(self.cell_type)

    def n_animals_in_cell(self):
        """
        Counts the number of animals per species per cell.

        Returns
        -------
        n_animals_per_species : dict
            Example: {`Herbivores`: n_herbivores, `Carnivores`: n_carnivores}
        """
        n_animals_in_cell = {}
        n_animals_in_cell["Herbivores"] = len(self.animals["Herbivore"])
        n_animals_in_cell["Carnivores"] = len(self.animals["Carnivore"])

        return n_animals_in_cell
