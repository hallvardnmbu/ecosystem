"""
Package for visualisation of the simulation.
"""


import matplotlib.pyplot as plt
import numpy as np
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
                 initial_density,
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
        self.initial_density = initial_density
        self.vis_years = vis_years
        self.ymax_animals = ymax_animals
        cmax = cmax_animals if cmax_animals is not None else {"Herbivore": 90,
                                                              "Carnivore": 90}
        self.cmax_herb = cmax["Herbivore"]
        self.cmax_carn = cmax["Carnivore"]

        if hist_specs is not None:
            for prop in hist_specs:
                if prop not in ["weight", "age", "fitness"]:
                    raise ValueError("Invalid property for histogram specification.")
                if "max" not in hist_specs[prop] and "delta" not in hist_specs[prop]:
                    raise ValueError("Invalid histogram specification.")
                self.hist_specs = hist_specs
        else:
            self.hist_specs = None

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
        self._year_ax = None
        self._line_ax = None
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

    def setup(self, final_year):
        """
        Prepare graphics, with the format:

        [ Year ][       Animal count      ]   (line plot)
        [ Map ][ Herbivores ][ Carnivores ]   (static, heatmap, heatmap)
        [   Age   ][  Weight ][  Fitness  ]   (histograms)
        """

        colours = {"L": tuple([colour / 255 for colour in [185, 214, 135]]),
                   "H": tuple([colour / 255 for colour in [232, 236, 158]]),
                   "D": tuple([colour / 255 for colour in [255, 238, 186]]),
                   "W": tuple([colour / 255 for colour in [149, 203, 204]])}

        if self._fig is None:
            self._fig = plt.figure(figsize=(15, 10))
            self.gs = self._fig.add_gridspec(11, 27)
            self._fig.tight_layout()

        if self._year_ax is None:
            self._year_ax = self._fig.add_subplot(self.gs[1:2, :1])
            self._year_ax.set_xlabel("Year count")
            self._year_ax.axis("off")

        if self._line_ax is None:
            self._line_ax = self._fig.add_subplot(self.gs[:3, 4:])
            self._line_ax.set_title('Number of animals')
            self._line_ax.set_ylim(0, self.ymax_animals)
            self._line_ax.set_xlim(0, final_year)
            self.herbs = np.arange(0, final_year, self.vis_years)
            self.n_herbs = self._line_ax.plot(self.herbs,
                                              np.full_like(self.herbs, np.nan, dtype=float),
                                              linestyle="-",
                                              color=(0.71764, 0.749, 0.63137),
                                              label="Herbivores")[0]
            self.carns = np.arange(0, final_year, self.vis_years)
            self.n_carns = self._line_ax.plot(self.carns,
                                              np.full_like(self.carns, np.nan, dtype=float),
                                              linestyle="-",
                                              color=(0.949, 0.7647, 0.56078),
                                              label="Carnivores")[0]
            self._line_ax.legend()
        else:
            old_x_herb, old_y_herb = self.n_herbs.get_data()
            old_x_carn, old_y_carn = self.n_carns.get_data()
            x_herb = np.arange(old_x_herb[-1] + 1, final_year)
            x_carn = np.arange(old_x_carn[-1] + 1, final_year)
            if len(x_herb) > 0:
                y_herb = np.full_like(x_herb, np.nan, dtype=float)
                self.n_herbs.set_data(np.hstack((old_x_herb, x_herb)),
                                      np.hstack((old_y_herb, y_herb)))
                self.n_carns.set_data(np.hstack((old_x_carn, x_carn)),
                                      np.hstack((old_y_carn, y_herb)))
                self._line_ax.set_xlim(0, final_year)

        if self._map_plot is None:
            self._map_plot = self._fig.add_subplot(self.gs[4:7, :9])
            self._island_map(self.my_colours)
            self._map_plot.set_title("Map of Rossumøya (Pylandia)")

        herb, carn = self._animal_data(self.initial_density)

        if self._herb_ax is None:
            self._herb_ax = self._fig.add_subplot(self.gs[4:7, 9:18])
            self._herb_ax.set_title("Herbivore density")
            self._herb_ax.axis("off")

            self._herb_plot = self._herb_ax.imshow(herb,
                                                   cmap="coolwarm",
                                                   vmin=0,
                                                   vmax=self.cmax_herb)
            self._herb_plot.cmap.set_bad(colours["W"])
            self._fig.colorbar(self._herb_plot,
                               ax=self._herb_ax,
                               fraction=0.046, pad=0.04)

        if self._carn_ax is None:
            self._carn_ax = self._fig.add_subplot(self.gs[4:7, 18:27])
            self._carn_ax.set_title("Carnivore density")
            self._carn_ax.axis("off")

            self._carn_plot = self._carn_ax.imshow(carn,
                                                   cmap="coolwarm",
                                                   vmin=0,
                                                   vmax=self.cmax_carn)
            self._carn_plot.cmap.set_bad(colours["W"])
            self._fig.colorbar(self._carn_plot,
                               ax=self._carn_ax,
                               fraction=0.046, pad=0.04)

        if self._age_ax is None:
            self._age_ax = self._fig.add_subplot(self.gs[8:11, 0:9])
            self._age_ax.set_xlabel('Value')
            self._age_ax.set_ylabel('Age')

        if self._weight_ax is None:
            self._weight_ax = self._fig.add_subplot(self.gs[8:11, 9:18])
            self._weight_ax.set_xlabel('Value')
            self._weight_ax.set_ylabel('Weight')

        if self._fitness_ax is None:
            self._fitness_ax = self._fig.add_subplot(self.gs[8:11, 18:27])
            self._fitness_ax.set_xlabel('Value')
            self._fitness_ax.set_ylabel('Fitness')

    def update_graphics(self, year, n_animals, n_animals_cells, animals):
        r"""
        Updates the graphics with new data for the given year.

        Parameters
        ----------
        year : int
        n_animals : dict

            .. code:: python

                {"Herbivores": 100, "Carnivores": 10}

        n_animals_cells : dict

            .. code:: python

                {(10, 10): {"Herbivores": 100, "Carnivores": 10}}
        animals : dict

            .. code:: python

                {"Herbivores": [Herbivore(), Herbivore(), ...], ...}
        """

        self._update_year_counter(year)
        self._update_line_plot(year, n_animals)
        self._update_heatmap(n_animals_cells)
        self._update_animal_features(animals, self.hist_specs)
        plt.pause(0.001)

    def _update_year_counter(self, year):
        """
        Update the year counter plot.

        Parameters
        ----------
        year : int
        """

        text = "Year: {}"
        if hasattr(self, "txt"):
            self.txt.remove()

        self.txt = self._year_ax.text(0.5, 0.5, text.format(year), fontsize=10,
                                  horizontalalignment='center',
                                  verticalalignment='center',
                                  transform=self._year_ax.transAxes)
        self.txt.set_text(text.format(year))

    def _update_line_plot(self, year, n_animals):
        """
        Update the animal count plot.

        Parameters
        ----------
        year : int
        n_animals : dict
        """

        index = year // self.vis_years
        y_herbs = self.n_herbs.get_ydata()
        y_herbs[index] = n_animals["Herbivores"]
        self.n_herbs.set_ydata(y_herbs)
        y_carns = self.n_carns.get_ydata()
        y_carns[index] = n_animals["Carnivores"]
        self.n_carns.set_ydata(y_carns)

        if not self.ymax_animals:
            _ylim = max(max(n_animals.values()) * 1.1, self._line_ax.get_ylim()[1])
            self._line_ax.set_ylim(0, _ylim)

    def _island_map(self, my_colours=None):
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

        self._map_plot.imshow(coloured_map)

        x_ticks = range(len(self.geography[0]))
        x_ticks_labels = range(1, len(self.geography[0]) + 1)
        y_ticks = range(len(self.geography))
        y_ticks_labels = range(1, len(self.geography) + 1)

        self._map_plot.set_xticks(x_ticks)
        self._map_plot.set_xticklabels(x_ticks_labels)
        self._map_plot.set_yticks(y_ticks)
        self._map_plot.set_yticklabels(y_ticks_labels)

    def _animal_data(self, density):
        """
        Extract animal data from density dictionary.

        Parameters
        ----------
        density : dict
            A dictionary with cell coordinates as keys and dictionaries with the amount of each
            species as values.

        Returns
        -------
        herb, carn : list
            Lists of lists with the amount of each species in each cell.
        """

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

    def _update_heatmap(self, density):
        """
        Update the heatmap of animal distributions
        .
        Parameters
        ----------
        density : dict
            A dictionary with cell coordinates as keys and dictionaries with the amount of each
            species in that cell as values.
        """

        herb, carn = self._animal_data(density)

        self._herb_plot.set_data(herb)
        self._carn_plot.set_data(carn)

        water = (149 / 255, 203 / 255, 204 / 255)
        self._herb_plot.cmap.set_bad(water)
        self._carn_plot.cmap.set_bad(water)

    def _update_animal_features(self, animals, hist_specs):
        """
        Update the histograms of animal features.

        Parameters
        ----------
        animals : dict
            A dictionary with species as keys and lists of animal objects as values.
        hist_specs : dict
            A dictionary specifying the histogram specifications for each feature.
        """

        if hist_specs is not None:
            for feature, specs in hist_specs.items():
                if feature == "age":
                    age_max = specs["max"]
                    age_bins = np.arange(0, age_max, specs["delta"])
                elif feature == "weight":
                    weight_max = specs["max"]
                    weight_bins = np.arange(0, weight_max, specs["delta"])
                else:
                    fitness_max = specs["max"]
                    fitness_bins = np.arange(0, fitness_max, specs["delta"])
        else:
            age_max = 60
            age_bins = np.arange(0, age_max, 5)
            fitness_max = 1
            fitness_bins = np.arange(0, fitness_max, 0.1)
            weight_max = 60
            weight_bins = np.arange(0, weight_max, 5)

        herbs = animals["Herbivore"]
        carns = animals["Carnivore"]

        colours = [(0.71764, 0.749, 0.63137),
                  (0.949, 0.7647, 0.56078)]

        herbs_age = [herb.a for herb in herbs]
        carns_age = [carn.a for carn in carns]

        self._age_ax.clear()
        self._age_ax.hist(herbs_age,
                          bins=age_bins,
                          alpha=0.8,
                          color=colours[0])
        self._age_ax.hist(carns_age,
                          bins=age_bins,
                          alpha=0.8,
                          color=colours[1])
        self._age_ax.set_xlim(0, age_max)
        self._age_ax.set_title("Age")

        herbs_weight = [herb.w for herb in herbs]
        carns_weight = [carn.w for carn in carns]
        self._weight_ax.clear()
        self._weight_ax.hist(herbs_weight,
                             bins=weight_bins,
                             alpha=0.8,
                             color=colours[0])
        self._weight_ax.hist(carns_weight,
                             bins=weight_bins,
                             alpha=0.8,
                             color=colours[1])
        self._weight_ax.set_xlim(0, weight_max)
        self._weight_ax.set_title("Weight")

        herbs_fitness = [herb.fitness for herb in herbs]
        carns_fitness = [carn.fitness for carn in carns]
        self._fitness_ax.clear()
        self._fitness_ax.hist(herbs_fitness,
                              bins=fitness_bins,
                              alpha=0.8,
                              color=colours[0])
        self._fitness_ax.hist(carns_fitness,
                              bins=fitness_bins,
                              alpha=0.8,
                              color=colours[1])
        self._fitness_ax.set_xlim(0, fitness_max)
        self._fitness_ax.set_title("Fitness")
