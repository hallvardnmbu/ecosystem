"""Contains the island and its cells."""


from operator import attrgetter
import itertools
import textwrap
import random
import math

from .animals import Animal


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
        """
        return {"H": 300, "L": 800, "M": 0, "W": 0,
                "alpha": 0.1, "v_max": 800}

    @classmethod
    def set_fodder_parameters(cls, new_parameters):
        r"""
        Set the parameters for the fodder on the island in the different terrain types.

        Parameters
        ----------
        new_parameters : dict

            .. code:: python

                {'terrain': int, ...}

        Raises
        ------
        ValueError
            If invalid parameter keys are passed.
            If invalid parameter values are passed.
        """
        for key, val in new_parameters.items():
            if key not in cls.default_fodder_parameters():
                raise ValueError(f"Invalid parameter: {key}")
            try:
                if val < 0:
                    raise ValueError(f"{key}'s value ({val}) can not be negative.")
                setattr(cls, key, val)
            except TypeError as err:
                raise ValueError(f"Invalid value for: {key} ({val}).") from err

    @classmethod
    def get_fodder_parameter(cls, parameter):
        """
        Returns the fodder parameters for the given terrain type.

        Parameters
        ----------
        parameter : str

        Returns
        -------
        float
            The fodder parameter for the given terrain type.
        """
        return {"H": cls.H,
                "L": cls.L,
                "M": cls.M,
                "W": cls.W,
                "alpha": cls.alpha,
                "v_max": cls.v_max}[parameter]

    def __init__(self, geography, ini_pop=None):
        self.year = 0
        self.geography = textwrap.dedent(geography).split("\n")

        self.species_map = {}
        for cls in Animal.__subclasses__():
            self.species_map[cls.__name__] = cls
            cls.set_motion()
            cls.set_parameters(cls.default_parameters())
        self.set_fodder_parameters(self.default_fodder_parameters())

        self.cells = self._terraform()
        self.inhabited_cells = {}

        self.add_population(population=ini_pop) if ini_pop is not None else None

    def _terraform(self):
        r"""
        Checks whether the geography is valid, and creates the grid of cell-objects.

        Returns
        -------
        cells : dict
            A dictionary containing the cells of the island with the location as the keys.

        Raises
        ------
        ValueError
            If the edges of the map are not 'W' (Water).
            If the map is not rectangular.
            If the map contains invalid terrain types.
        """
        cols = len(self.geography)
        rows = len(self.geography[0])

        for i in range(cols):
            if len(self.geography[i]) != rows:
                raise ValueError("The map must be rectangular.")

        for i in range(cols):
            if self.geography[i][0] != "W" or self.geography[i][rows-1] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")
        for j in range(rows):
            if self.geography[0][j] != "W" or self.geography[cols-1][j] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")

        allowed = Island.default_fodder_parameters().keys()
        if any(letter not in allowed for row in self.geography for letter in row):
            raise ValueError("The map contains invalid terrain types.")

        cells = {}
        for i in range(cols):
            for j in range(rows):
                # Creates the Cell-objects in the grid with the index corresponding to the terrain:
                cells[(i+1, j+1)] = Cell(cell_type=self.geography[i][j])

        return cells

    def add_population(self, population):
        r"""
        Adds a population to the island.

        Parameters
        ----------
        population : list of dict

            .. code:: python

                [{'loc': (x, y), 'pop': [{'species': str, 'age': int, 'weight': float}]}, ...]

        Raises
        ------
        ValueError
            If the location is not on the map.
            If the location is in Water ('W').
            If the animal is incorrectly defined.

        Notes
        -----
        When adding a population to the island, the inhabited cells are stored. This makes it
        significantly faster to go through the annual cycle (by only iterating through the
        inhabited cells).
        """
        for location_animals in population:
            location = location_animals["loc"]
            if location[0] > len(self.geography) or location[1] > len(self.geography[0]):
                raise ValueError(f"Invalid location: {location}.")

            i, j = location
            self.inhabited_cells[self.cells[(i, j)]] = (i, j)
            animals = location_animals["pop"]
            for animal in animals:

                if animal["species"] not in self.species_map:
                    raise ValueError(f"Invalid species: {animal}.")
                species = animal["species"]

                if not self.species_map[species].movable[self.geography[i-1][j-1]]:
                    raise ValueError(f"Invalid terrain: {location}.")

                cell = self.cells[(i, j)]
                if "age" not in animal:
                    age = None
                else:
                    age = animal["age"]
                if "weight" not in animal:
                    weight = None
                else:
                    weight = animal["weight"]
                cell.animals[species].append(self.species_map[species](age=age, weight=weight))

    def procreate(self):
        r"""
        Iterates through all the animals on the island.
        The baby is added to the same cell as the parent if the following is met:

            1. The baby-to-be's weight is less than the parent's weight.
            2. A probability of min(1, :math:`\gamma` * :math:`\Phi` * N).

        Where:

            :math:`\gamma`: species-specific parameter.
            :math:`\Phi`: the parents' fitness.
            N: number of animals of the same species in the cell.
        """
        for cell in self.inhabited_cells:
            p_baby = {cls.__name__: cls.gamma * len(cell.animals[cls.__name__])
                      for cls in Animal.__subclasses__()}

            for animal in list(itertools.chain(*cell.animals.values())).copy():

                # Procreation may only take place if the following is satisfied:
                if animal.w >= animal.w_procreate:

                    if random.random() < animal.fitness * p_baby[animal.__class__.__name__]:
                        baby_weight = animal.birthweight()

                        # If the parents' weight is greater than the baby's weight * xi, the
                        # baby is born, and the parents' weight decreases accordingly ^:
                        if animal.lose_weight_birth(baby_weight):
                            baby = animal.__class__(age=0, weight=baby_weight)

                            cell.animals[baby.__class__.__name__].append(baby)

    def feed(self):
        """
        Iterates through all the animals on the island.
        Herbivores eat before carnivores and eat fodder. The fittest herbivores eat first.
        Carnivores eat herbivores. They hunt in random order and prey on the weakest herbivores
        first.
        """
        for cell in self.inhabited_cells:
            if cell.animals["Herbivore"]:

                cell.grow_fodder()

                cell.animals["Herbivore"] = sorted(cell.animals["Herbivore"],
                                                   key=attrgetter("fitness"),
                                                   reverse=True)
                for herbivore in cell.animals["Herbivore"]:
                    cell.fodder -= herbivore.graze(cell.fodder)

                # Since the Herbivores eat in order of descending fitness, the order is
                # preserved, and thus the reversion of the list is done without fetching the
                # newly calculated fitness:
                cell.animals["Herbivore"] = cell.animals["Herbivore"][::-1]
                random.shuffle(cell.animals["Carnivore"])
                for carnivore in cell.animals["Carnivore"]:
                    carnivore.predation(cell.animals["Herbivore"], cell.animals["Herbivore"].copy())

    def migrate(self):
        r"""
        Iterates through all the animals on the island.
        An animal migrates with a probability of :math:`\mu` * :math:`\Phi`, and moves to a
        random directly neighbouring cell. The animal may only move to cells it can move through,
        and the cell is selected based on the abundance of fodder in the cell.

        .. math::

            N = \textrm{number of animals of the same species in the cell}

            \textrm{abundance} = \frac{\textrm{fodder}}{\textrm{max}((N + 1) * F, N + 1, F, 1)}

            \textrm{propensity} = e^{\textrm{abundance}}

            \textrm{probability} = \frac{\textrm{propensity of new cell}}{\sum \textrm{propensity}}

        Notes
        -----
        In order to prevent animals from moving multiple times (say an animal moves from (1,
        1) -> (1, 2), we don't want the animal to be able to move again), the movements are
        executed after each cell has been iterated through.

        50% chance of moving if no neighboring cells are preffered.
        """
        migrating_animals = []
        for cell, pos in self.inhabited_cells.items():
            for animal in itertools.chain(*cell.animals.values()):
                if random.random() > animal.mu * animal.fitness:
                    continue

                new_cell = self._migrate(pos, animal)
                if new_cell is None:
                    continue

                movement = (animal, cell, new_cell)
                migrating_animals.append(movement)

        for movement in migrating_animals:
            animal, from_cell, to_cell = movement
            from_cell.animals[animal.__class__.__name__].remove(animal)
            to_cell.animals[animal.__class__.__name__].append(animal)

        self._update_inhabited_cells()

    def _migrate(self, position, animal):
        """
        Determines whether an animal migrates or not, and if it does, to which cell.

        Parameters
        ----------
        position : tuple[int, int]
        animal : Animal

        Returns
        -------
        Cell or None

        Notes
        -----
        - See notes in :math:`migrate`.
        """
        propensity = {}
        possibilities = self._possibilities(position, animal)

        if not possibilities:
            return None

        for i, j in possibilities:
            if animal.__class__.__name__ == "Herbivore":
                fodder = self.cells[(i, j)].fodder
            elif animal.__class__.__name__ == "Carnivore":
                fodder = 0
                for herbivore in self.cells[(i, j)].animals["Herbivore"]:
                    fodder += herbivore.w
            else:
                raise ValueError("Update migration to account for new species.")

            population = len(self.cells[(i, j)].animals[animal.__class__.__name__])
            abundance = fodder / max(((population + 1) * animal.F),
                                     population + 1,
                                     animal.F,
                                     1)
            propensity[(i, j)] = math.exp(abundance)

        new_pos = random.choice(possibilities)

        try:
            probability = propensity[new_pos] / sum(propensity.values())
        except ZeroDivisionError:
            probability = 0.5

        if random.random() < probability:
            return self.cells[new_pos]
        return None

    def _possibilities(self, position, animal):
        """
        Determines the possible cells an animal can migrate to based on its stride.

        Parameters
        ----------
        position : tuple[int, int]
        animal : Animal

        Returns
        -------
        list
            A list of the possible cells the animal can migrate to.
        """
        stride = animal.stride
        possible = []
        x, y = position[0] - 1, position[1] - 1
        for i in range(x - stride, x + stride + 1):
            for j in range(y - stride, y + stride + 1):

                if not (0 <= i < len(self.geography[0]) and 0 <= j < len(self.geography)):
                    continue
                if not animal.movable[self.geography[i][j]]:
                    continue
                if (i - x) ** 2 + (j - y) ** 2 > stride ** 2:
                    continue

                possible.append((i + 1, j + 1))

        if animal.__class__.__name__ == "Herbivore":
            possible.remove(position)
            return possible

        best = {}
        for cell in possible:
            herbivores = len(self.cells[cell].animals["Herbivore"])

            if herbivores == 0:
                continue

            if len(best) < 4:
                best[herbivores] = cell
                continue

            if herbivores > min(best):
                best.pop(min(best))
                best[herbivores] = cell

        return list(best.values())

    def _update_inhabited_cells(self):
        """
        Updates the list of inhabited cells to improve computational cost for most of the yearly
        cycle(s).
        """
        self.inhabited_cells = {}
        for pos, cell in self.cells.items():
            if cell.animals["Herbivore"] or cell.animals["Carnivore"]:
                self.inhabited_cells[cell] = pos

    def ageing(self):
        """Iterates through all the animals on the island and ages them accordingly."""
        for cell in self.inhabited_cells:
            for animal in itertools.chain(*cell.animals.values()):
                animal.aging()

    def weight_loss(self):
        """
        Iterates through all the animals on the island and decrements their weight accordingly.
        """
        for cell in self.inhabited_cells:
            for animal in itertools.chain(*cell.animals.values()):
                animal.lose_weight_year()

    def death(self):
        r"""
        Iterates through all the animals on the island and removes them if they die.

        Notes
        -----
        An animal dies with a probability of :math:`\omega` * (1 - :math:`\Phi`).
        """
        for cell in self.inhabited_cells:
            dying_animals = []
            for animal in list(itertools.chain(*cell.animals.values())).copy():
                animal.calculate_fitness()
                if animal.w <= 0 or random.random() < animal.omega * (1 - animal.fitness):
                    dying_animals.append(animal)
                    cell.animals[animal.__class__.__name__].remove(animal)

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

    def animals(self):
        r"""
        Retrieve the information about the animals on the island.

        Returns
        -------
        population : dict
            A dictionary with lists of the animals per species.

            .. code:: python

                {'Herbivore': [Herbivore(), ...], ...}

        n_animals_per_species : dict
            A dictionary with the number of animals per species.
        n_animals_per_species_per_cell : dict
            A dictionary with the number of animals per species per cell.

            .. code:: python

                {(1, 1): {"Herbivore": n, ...}, ...}
        """
        population = {cls.__name__: [] for cls in Animal.__subclasses__()}
        n_animals_per_species = {cls.__name__: 0 for cls in Animal.__subclasses__()}
        n_animals_per_species_per_cell = {pos: {cls.__name__: 0
                                                for cls in Animal.__subclasses__()}
                                          for pos in self.cells}

        for cell, pos in self.inhabited_cells.items():
            for animal in itertools.chain(*cell.animals.values()):
                population[animal.__class__.__name__].append(animal)
                n_animals_per_species[animal.__class__.__name__] += 1
                n_animals_per_species_per_cell[pos][animal.__class__.__name__] += 1

        return population, n_animals_per_species, n_animals_per_species_per_cell

    def slaughter(self):
        """Slaughter all animals on the island."""
        for cell in self.inhabited_cells:
            cell.animals = {cls.__name__: [] for cls in Animal.__subclasses__()}


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
        self.animals = {cls.__name__: [] for cls in Animal.__subclasses__()}

    def grow_fodder(self):
        r"""
        Grows fodder in the cell.

        Notes
        -----
        The growth of fodder is dependent on how much was left from last cycle and is calculated as:

        .. math::

            f_{\text{new}} = min(f_{\text{old}} + v_{\text{max}} * (1 - \alpha * (f_{\text{max}} - f_{\text{old}}) / f_{
            \text{max}}), f_{\text{max}})

        """
        f_max = Island.get_fodder_parameter(self.cell_type)
        alpha = Island.get_fodder_parameter("alpha")
        v_max = Island.get_fodder_parameter("v_max")

        try:
            growth = v_max * (1 - alpha * (f_max - self.fodder) / f_max)
        except ZeroDivisionError:
            growth = 0

        self.fodder = min(self.fodder + growth, f_max)
