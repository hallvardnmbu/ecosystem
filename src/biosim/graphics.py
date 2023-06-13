"""
Package for visualisation of the simulation.
"""


import matplotlib.pyplot as plt
import itertools
import numpy as np
import subprocess
import os


_DEFAULT_GRAPHICS_DIR = os.path.join('../..', 'data')

_FFMPEG_BINARY = "ffmpeg"
_MAGICK_BINARY = "magick"


class Graphics:
    """
    Provides graphical support for BioSim.
    """

    def __init__(self,
                 geography,
                 ini_density,
                 vis_years,
                 ymax_animals,
                 cmax_animals,
                 hist_specs,
                 img_years,
                 img_dir,
                 img_base,
                 img_fmt,
                 log_file,
                 img_name="dv",
                 my_colours=None):

        self.geography = geography
        self.ini_density = ini_density
        self.vis_years = vis_years
        self.ymax_animals = ymax_animals
        self.cmax_animals = cmax_animals if cmax_animals is not None else {"Herbivore": 50, "Carnivore": 20}
        self.hist_specs = hist_specs
        self.img_years = img_years
        self.img_base = img_base
        self.img_fmt = img_fmt
        self.log_file = log_file
        self.img_name = img_name
        self.my_colours = my_colours
        self._img_ctr = 0

        if img_dir is not None:
            self._img_base = os.path.join(img_dir, img_name)
        else:
            self._img_base = None

        # The following will be initialized by setup
        self._fig = None
        self._map_plot = None
        self._count_ax = None
        self._count_plot = None
        self._animals_ax = None
        self._animals_plot = None
        self._herb_ax = None
        self._herb_plot = None
        self._carn_ax = None
        self._carn_plot = None
        self._fitness_ax = None
        self._fitness_plot = None
        self._age_ax = None
        self._age_plot = None
        self._weight_ax = None
        self._weight_plot = None

    def setup(self):
        """
        Prepare graphics.

        Call this before calling `update()` for the first time after
        the final time step has changed.
        """

        # Create a new figure window if it doesn't exist
        if self._fig is None:
            self._fig = plt.figure(figsize=(12, 8)) # 15, 10
            self._fig.tight_layout()

        x_ticks = range(len(self.geography[0]))
        x_ticks_labels = range(1, len(self.geography[0]) + 1)
        y_ticks = range(len(self.geography))
        y_ticks_labels = range(1, len(self.geography) + 1)

        if self._map_plot is None:
            self._map_plot = self._fig.add_subplot(3, 3, 1)
            self.island_map(x_ticks, x_ticks_labels, y_ticks, y_ticks_labels)

        if self._count_ax is None:
            self._count_ax = self._fig.add_subplot(3, 3, 2)
            self._count_ax.set_xlabel("Year count")
            self._count_ax.axis("off")

        if self._animals_ax is None:
            self._animals_ax = self._fig.add_subplot(3, 3, 3)

        herb, carn = self.animal_data(self.ini_density)
        water = (149 / 255, 203 / 255, 204 / 255)

        if self._herb_ax is None:
            self._herb_ax = self._fig.add_subplot(3, 3, 4)
            self._herb_ax.set_xticks(x_ticks)
            self._herb_ax.set_xticklabels(x_ticks_labels)
            self._herb_ax.set_yticks(y_ticks)
            self._herb_ax.set_yticklabels(y_ticks_labels)

            self._herb_plot = self._herb_ax.imshow(herb,
                                                   cmap="coolwarm",
                                                   vmin=0,
                                                   vmax=self.cmax_animals["Herbivore"])
            self._herb_plot.cmap.set_bad(water)
            herb_cb = self._fig.colorbar(self._herb_plot, ax=self._herb_ax,
                                         fraction=0.046, pad=0.04)
            herb_cb.set_label('Herbivore density')

        if self._carn_ax is None:
            self._carn_ax = self._fig.add_subplot(3, 3, 6)
            self._carn_ax.set_xticks(x_ticks)
            self._carn_ax.set_xticklabels(x_ticks_labels)
            self._carn_ax.set_yticks(y_ticks)
            self._carn_ax.set_yticklabels(y_ticks_labels)

            self._carn_plot = self._carn_ax.imshow(carn,
                                                   cmap="coolwarm",
                                                   vmin=0,
                                                   vmax=self.cmax_animals["Carnivore"])
            self._carn_plot.cmap.set_bad(water)
            carn_cb = self._fig.colorbar(self._carn_plot, ax=self._carn_ax,
                                         fraction=0.046, pad=0.04)
            carn_cb.set_label('Carnivore density')

        if self._age_ax is None:
            self._age_ax = self._fig.add_subplot(3, 3, 7)
            self._age_ax.set_xlabel('Value')
            self._age_ax.set_ylabel('Age')

        if self._weight_ax is None:
            self._weight_ax = self._fig.add_subplot(3, 3, 8)
            self._weight_ax.set_xlabel('Value')
            self._weight_ax.set_ylabel('Weight')

        if self._fitness_ax is None:
            self._fitness_ax = self._fig.add_subplot(3, 3, 9)
            self._fitness_ax.set_xlabel('Value')
            self._fitness_ax.set_ylabel('Fitness')

    def island_map(self, x_ticks, x_ticks_labels, y_ticks, y_ticks_labels, my_colours=None):
        """
        Creates the island map.

        Parameters
        ----------
        my_colours : dict, optional
        """

        colours = {"L": [colour / 255 for colour in [185, 214, 135]],
                   "H": [colour / 255 for colour in [232, 236, 158]],
                   "D": [colour / 255 for colour in [255, 238, 186]],
                   "W": [colour / 255 for colour in [149, 203, 204]]}

        if my_colours is not None:
            for key, val in my_colours.items():
                colours[key] = val

        coloured_map = [[colours[letter] for letter in row] for row in self.geography]

        self._map_plot.set_title("Map of Rossumøya (Pylandia)")
        # self._map_plot.axis("off")


        self._map_plot.imshow(coloured_map)

        self._map_plot.set_xticks(x_ticks)
        self._map_plot.set_xticklabels(x_ticks_labels)
        self._map_plot.set_yticks(y_ticks)
        self._map_plot.set_yticklabels(y_ticks_labels)

    def year_counter(self, year):
        """
        Update the year counter plot.

        Parameters
        ----------
        year : int
            Current year.
        """

        text = "Year: {}"
        if hasattr(self, "txt"):
            self.txt.remove()

        self.txt = self._count_ax.text(0.5, 0.5, text.format(year), fontsize=20,
                                  horizontalalignment='center',
                                  verticalalignment='center',
                                  transform=self._count_ax.transAxes)
        self.txt.set_text(text.format(year))
        # plt.pause(0.01)

    def animals(self, n_animals):
        """
        Update the animal count plot.

        Parameters
        ----------
        n_animals : dict
            Number of animals in each species.
        """
        self._animals_ax.clear()
        self._animals_ax.set_title('Number of animals')
        self._animals_ax.set_xticks(range(len(n_animals)))
        self._animals_ax.set_xticklabels(list(n_animals.keys()))
        self._animals_ax.bar(range(len(n_animals)),
                             n_animals.values(),
                             align='center',
                             color=[(0.71764, 0.749, 0.63137),
                                    (0.949, 0.7647, 0.56078)])

    def animal_data(self, density):

        herb = []
        carn = []
        for x in range(len(self.geography)):
            row_herb = []
            row_carn = []
            for y in range(len(self.geography[0])):
                cell = f"({x+1}, {y+1})"
                row_herb.append(density[cell].get("Herbivores", 0))
                row_carn.append(density[cell].get("Carnivores", 0))
            herb.append(row_herb)
            carn.append(row_carn)

        herb = [[np.nan if val==0 else val for val in row] for row in herb]
        carn = [[np.nan if val==0 else val for val in row] for row in carn]

        return herb, carn

    def update_animals(self, density):

        herb, carn = self.animal_data(density)

        self._herb_plot.set_data(herb)
        self._carn_plot.set_data(carn)

        water = (149 / 255, 203 / 255, 204 / 255)
        self._herb_plot.cmap.set_bad(water)
        self._carn_plot.cmap.set_bad(water)

        # self._herb_plot.canvas.draw()
        # self._carn_plot.canvas.draw()

    def update_animal_data(self, animals):

        herbs = animals["Herbivores"]
        carns = animals["Carnivores"]

        herbs_age = [herb.a for herb in herbs]
        carns_age = [carn.a for carn in carns]

        self._age_ax.clear()
        self._age_ax.hist(herbs_age, bins=10, alpha=0.5, label="Herbivores")
        self._age_ax.hist(carns_age, bins=10, alpha=0.5, label="Carnivores")

        herbs_weight = [herb.w for herb in herbs]
        carns_weight = [carn.w for carn in carns]
        self._weight_ax.clear()
        self._weight_ax.hist(herbs_weight, bins=10, alpha=0.5, label="Herbivores")
        self._weight_ax.hist(carns_weight, bins=10, alpha=0.5, label="Carnivores")

        herbs_fitness = [herb.fitness for herb in herbs]
        carns_fitness = [carn.fitness for carn in carns]
        self._fitness_ax.clear()
        self._fitness_ax.hist(herbs_fitness, bins=10, alpha=0.5, label="Herbivores")
        self._fitness_ax.hist(carns_fitness, bins=10, alpha=0.5, label="Carnivores")

        self._fig.canvas.draw()

    def update_graphics(self, year, num_animals, n_animals_cells, animals):

        self.year_counter(year)
        self.animals(num_animals)
        self.update_animals(n_animals_cells)
        self.update_animal_data(animals)
