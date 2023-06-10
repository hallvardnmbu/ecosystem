import random
import textwrap
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from animals import Herbivore, Carnivore


class Island:
    @classmethod
    def default_fodder_parameters(cls):
        """
        Returns a dictionary with the default fodder parameters for the different terrain types.

        Returns
        -------
        - default_fodder_parameters: dictionary
        """

        return {"H": 300, "L": 800, "D": 0, "W": 0}

    def __init__(self, geography, ini_pop=None):
        self.year = 0
        self.animal_classes = {"Herbivore": Herbivore,
                               "Carnivore": Carnivore}
        self.geography = textwrap.dedent(geography).split("\n")
        self.available_fodder = Island.default_fodder_parameters()

        # Tests if the geography is valid, and creates the cell-grid (consisting of Cell-objects):
        self.cell_grid = self._terraform()

        # Runs add_population if ini_pop is not None:
        self.add_population(population=ini_pop) if ini_pop is not None else None

    def _terraform(self):
        """
        Checks whether the geography is valid, and creates the grid of cell-objects.

        Raises
        ------
        - ValueError
            If the edges of the map are not "W" (Water).
            If the map is not rectangular.
            If the map contains invalid terrain types.
        """

        X = len(self.geography)
        Y = len(self.geography[0])

        # Checks whether the map is rectangular:
        for i in range(X):
            # len(terrain) is "static", while len(terrain[i]) is "dynamic".
            if len(self.geography[i]) != Y:
                raise ValueError(f"The map must be rectangular.")

        # Checks whether the edges of the map is water:
        for i in range(X):
            if self.geography[i][0] != "W" or self.geography[i][Y-1] != "W":
                raise ValueError(f"The edges of the map must be 'W' (Water).")
        for j in range(Y):
            if self.geography[0][j] != "W" or self.geography[X-1][j] != "W":
                raise ValueError(f"The edges of the map must be 'W' (Water).")

        # Checks whether the map contains only valid characters:
        if any(letter not in ["W", "L", "H", "D"] for row in self.geography for letter in row):
            raise ValueError(f"The map contains invalid terrain types.")

        # Creates the empty cell-grid, where each cell (object) will be stored:
        cell_grid = []
        for i in range(X):
            row = []
            for j in range(Y):
                # Sets the f_max-parameter for each cell to the default value for the terrain-type:
                fodder = self.available_fodder[self.geography[i][j]]
                # Creates the cell-objects in the grid with the index corresponding to the terrain:
                row.append(Cell(cell_type=self.geography[i][j], max_fodder=fodder))
            cell_grid.append(row)

        return cell_grid

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

            # Convert location to 0-indexing:
            i = location[0] - 1
            j = location[1] - 1

            # Check if location is on the map and not "W":
            try:
                if not self.cell_grid[i][j].can_move:
                    raise ValueError(f"Animals cannot be placed in water {location}.")
            except:
                raise ValueError(f"Location {location} is not on the island.")

            # Iterate through the animals at the given location:
            animals = location_animals["pop"]
            for animal in animals:
                species = animal["species"]
                if "age" not in animal:
                    animal["age"] = 0
# Weight = None: ENDRE ALLE STEDER. DET SKAL VÆRE LIK .lognormv(). HELST KUN ETT STED, IKKE FLERE.
                if "weight" not in animal:
                    animal["weight"] = self.animal_classes[species].lognormv()
# Could also do:
    # animal["age"] = None if "age" not in animal else animal["age"]
    # animal["weight"] = None if "weight" not in animal else animal["weight"]
# But that ^ requires double 'animal["age"]'. Ask TA which is fastest.

                try:
                    cell = self.cell_grid[i][j]
                    age = animal["age"]
                    weight = animal["weight"]
                    cell.animals[species].append(self.animal_classes[species](age=age,
                                                                              weight=weight))
                except:
                    raise ValueError(f"Error when adding: {animal}. Double check the parameters.")

        # The function "set_fodder_parameters" is not @classmethod, such that multiple islands
        # can be modelled with different fodder parameters (at the same time).
        def set_fodder_parameters(self, new_parameters=None):
            """
            Updates the parameters for the fodder on the island in the different terrain types.

            Parameters
            ----------
            - new_parameters: dict
                {"terrain": value}

            Raises
            ------
            - ValueError
                If negative parameters are passed.
                If invalid parameters are passed.
            """

            for key, val in new_parameters.items():
                if key not in self.available_fodder:
                    raise ValueError(f"Invalid parameter: {key}")
                try:
                    if val < 0:
                        raise ValueError(f"{key}'s value can not be negative.")
                    self.available_fodder[key] = float(val)
                except:
                    raise ValueError(f"Invalid value for: {0}".format(key))

    # The function "set_fodder_parameters" is not @classmethod, such that multiple islands
    # can be modelled with different fodder parameters (at the same time).
    def set_fodder_parameters(self, new_parameters=None):
        """
        Set the parameters for the fodder on the island in the different terrain types.

        Parameters
        ----------
        - new_parameters: dict
            {"terrain": value}

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
                    raise ValueError(f"Invalid parameter: {key}")
                try:
                    if val < 0:
                        raise ValueError(f"{key}'s value can not be negative.")
                    self.available_fodder[key] = float(val)
                except:
                    raise ValueError(f"Invalid value for: {0}".format(key))

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

        animals = self.n_animals_per_species
        return animals["Herbivores"] + animals["Carnivores"]

    def procreate(self):
        """
        Iterates through all the animals on the island.
        The baby is added to the same cell as the parent if the following is met:
        - The baby-to-be's weight is less than the parent's weight.
        - A probability of min(1, gamma * fitness * N).
          Where:
            - gamma: species-specific parameter.
            - fitness: the parents' fitness.
            - N: number of animals of the same species in the cell.
        """

        for cells in self.cell_grid:
            for cell in cells:
                babies = []
                # HER ER DET NOE FEIL!!!!

                # Calculate the number of animals in the cell outside the loop:
                animals_in_cell = {"Herbivore": len(cell.herbivores),
                                   "Carnivore": len(cell.carnivores)}

                for animal in cell.herbivores + cell.carnivores:
                    if animal.w >= animal.zeta * (animal.w_birth + animal.sigma_birth):

                        # Retrieve the number of animals of the same species in the cell:
                        n = animals_in_cell[animal.species]

                        if random.random() < min(1, animal.gamma * animal.fitness * n):
                            baby_weight = animal.lognormv()
                            if baby_weight < animal.w:

                                # If the parents' weight is greater than the baby's weight * xi,
                                # the baby is born:
                                if animal.lose_weight_birth(baby_weight):  # (True / False ^)

                                    # Creates the baby of the parents' species:
                                    baby = self.animal_classes[animal.species](age=0,
                                                                               weight=baby_weight)

                                    # For the newborns to be excluded from being able to
                                    # procreate, they are placed in the parents' cell outside loop.
                                    babies.append(baby)

                # Iteration of adults in the cell is done, and the newborns are added:
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

# Bytte dette (if ...) ut med "if cell.can_move" ? Går det raskere, kanskje?
# Tror kanskje ikke det er raskere. ???
                if cell.herbivores or cell.carnivores:

                    # Growth of fodder occurs before the animals eat:
                    cell.fodder = cell.fodder_max

                    # Sort herbivores by descending fitness:
                    herbivores = sorted(cell.herbivores,
                                        key=lambda herbivore: herbivore.fitness,
                                        reverse=True)

                    # Herbivores eat first:
                    for herbivore in herbivores:
                        cell.herbivore_eat_fodder(amount=herbivore.F, animal=herbivore)

# Burde fitness reknes ut på nytt før sorteringen? Eller skal kun den første sorteringen brukes?
# Sort herbivores by ascending fitness (flip^)?
    # herbivores = herbivores[::-1]
                    herbivores = sorted(cell.herbivores,
                                        key=lambda herbivore: herbivore.fitness)

                    # Sort carnivores randomly:
                    carnivores = cell.carnivores
                    random.shuffle(carnivores)

                    # Carnivores eat herbivores after the herbivores have eaten:
                    for carnivore in carnivores:
                        killed = cell.carnivore_kill(carnivore, herbivores)
                        herbivores = [herb for herb in herbivores if herb not in killed]

    def migrate(self):
        """
        Iterates through all the animals on the island.
        An animal migrates with a probability of mu * fitness, and moves to a random neighbouring
        cell.
        """

        migrating_animals = []
        for i, cells in enumerate(self.cell_grid):
            for j, cell in enumerate(cells):

                # Each animal has a probability of migrating, once a year:
                for animal in cell.herbivores + cell.carnivores:

                    # The probability of migrating is calculated:
                    if random.random() < animal.mu * animal.fitness:

                        # Randomly chooses a neighbouring cell if the animal migrates:
                        move_x, move_y = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])

                        # Finds the new cell:
                        new_cell = self.cell_grid[i + move_x][j + move_y]

                        # Checks if the new cell is a valid cell (Cell.can_move = True/False),
                        # and moves the animal if it is:
                        if new_cell.can_move:
                            movement = (animal, cell, new_cell)
                            migrating_animals.append(movement)

        # In order to prevent animals from moving multiple times (say an animal moves from (1,
        # 1) -> (1, 2), we don't want the animal to be able to move again), the movements are
        # executed after each cell has been iterated through:
        for movement in migrating_animals:
            animal, from_cell, to_cell = movement
            from_cell.animals[animal.species].remove(animal)
            to_cell.animals[animal.species].append(animal)

# Ha denne inne i migrate, etter at dyret har flyttet seg!!!!! Sparer å iterere gjennom alle!
    def age_increment(self):
        """
        Iterates through all the animals on the island, and ages them by one year.
        """

        for cells in self.cell_grid:
            for cell in cells:
                for animal in cell.herbivores + cell.carnivores:
                    animal.aging()

# Ha denne inne i migrate, etter at dyret har flyttet og blitt eldre!!!!! Sparer å iterere
# gjennom alle!
    def weight_loss(self):
        """
        Iterates through all the animals on the island, and makes them lose weight.
        """

        for cells in self.cell_grid:
            for cell in cells:
                for animal in cell.herbivores + cell.carnivores:
                    animal.lose_weight()

# Dette er kanskje ikke vits? Vil aldri bli mindre enn 0 iom. at 0 < eta < 1?
                    if animal.w <= 0:
                        cell.animals[animal.species].remove(animal)

# Ha denne inne i migrate, etter at dyret har flyttet og blitt eldre og mista vekt!!!!! Sparer å
# iterere gjennom alle!
    def death(self):
        """
        Iterates through all the animals on the island.
        An animal dies if:
        - It's weight is (less than or) equal to zero.
        - A probability of omega * (1 - fitness).
        """

        for cells in self.cell_grid:
            for cell in cells:
                for animal in cell.herbivores + cell.carnivores:
                    if random.random() < animal.omega * (1 - animal.fitness) or animal.w <= 0:
                        cell.animals[animal.species].remove(animal)
                    else:
                        # Decrements the weight of the animals that don't die, since this is the
                        # last step of the yearly cycle:
                        animal.lose_weight_year()

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
        self.age_increment()
        self.weight_loss()
        self.death()

# Fjerne ._new_year() og ha self.year += 1 i stedet???
        self._new_year()

    def _new_year(self):
        """
        Adds a new year to the island.
        """

        self.year += 1

    def visualise(self, my_colours=None):
        """
        Visualises the island.

        Parameters
        ----------
        - my_colours: dict
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

        # Creates a matrix with items as the colours of the island:
        coloured_map = np.array([[colours[type] for type in row] for row in self.geography],
                                dtype=np.uint8)

        # Visualising the island:
        plt.imshow(coloured_map)
        plt.xticks([]), plt.yticks([]), plt.title(f"Map of Rossumøya (Pylandia)")

        # Descriptory text for the terrain types:
        description = {"L": "Lowland", "H": "Highland", "D": "Desert", "W": "Water"}
        patches = [mpatches.Patch(color=(val[0] / 255, val[1] / 255, val[2] / 255),
                                  label="{0}".format(
                                      str(pd.DataFrame([key]).replace(description)[0][0]))) for
                   key, val in colours.items()]
        plt.legend(handles=patches, bbox_to_anchor=(0, -0.01), loc=2, borderaxespad=0)

        plt.show()


class Cell:
    def __init__(self, max_fodder, cell_type):
        self.can_move = True if cell_type != "W" else False

        self.fodder_max = max_fodder
        self.fodder = max_fodder

        self.herbivores = []
        self.carnivores = []
        self.animals = {"Herbivore": self.herbivores,
                        "Carnivore": self.carnivores}

    def herbivore_eat_fodder(self, amount, animal):
        """
        Removes fodder from the cell.
        If the amount to be removed is greater than the amount of fodder in the cell, the fodder
        is set to 0.
        """

        if self.fodder < amount:
            # If the fodder available in the cell is less than the amount the animal wants to
            # eat, it eats the available fodder:
            food = self.fodder
        else:
            # Otherwise the animal eats the amount it wants to eat:
            food = amount

        # Decrements the available fodder in the cell and increments the weight of the animal:
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

            # If the carnivore has eaten enough, it stops killing:
            if food >= carnivore.F:
                break
# BRUKE EN while-LØKKE I STEDET?

            # Calculates the probability of the carnivore killing the herbivore:
            if carnivore.fitness <= herbivore.fitness:
                p = 0
            elif 0 < carnivore.fitness - herbivore.fitness < carnivore.DeltaPhiMax:
                p = (carnivore.fitness - herbivore.fitness) / carnivore.DeltaPhiMax
            else:
                p = 1

            # If the carnivore kills the herbivore, it eats the meat and the herbivore dies:
            if random.random() < p:
                food += herbivore.w

                # The fitness is re-evaluated for each herbivore killed. Therefore, the carnivore
                # eats the herbivores as they are killed, and not everything at the end:
                carnivore.gain_weight(food=herbivore.w)

                self.herbivores.remove(herbivore)
                killed.append(herbivore)

        return killed
