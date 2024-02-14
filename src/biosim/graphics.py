"""Contains visualisation of the simulation."""


import os
import csv
import warnings
import subprocess
import numpy as np
from matplotlib import patches
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QEventLoop


warnings.filterwarnings("ignore", category=RuntimeWarning)

_DEFAULT_GRAPHICS_DIR = os.path.join('../..', 'data')
_FFMPEG_BINARY = "ffmpeg"
_MAGICK_BINARY = "magick"


class Graphics:
    """
    Provides graphical support for BioSim.

    Parameters
    ----------
    geography : str
        Multi-line string specifying island geography
    vis_years : int
        Years between visualization updates (if 0, disable graphics)
    ymax_animals : int
        Number specifying y-axis limit for graph showing animal numbers
    cmax_animals : dict
        Color-scale limits for animal densities.
    hist_specs : dict
        Specifications for histograms.
    img_years : int
        Years between visualizations saved to files (default: vis_years)
    img_dir : str
        Path to directory for figures
    img_base : str
        Beginning of file name for figures
    img_fmt : str
        File type for figures, e.g. 'png' or 'pdf'
    log_file : str
        If given, write animal counts to this file
    my_colours : dict
        Specify custom colours for the terrain-types.
    terrain_patches : bool
        Whether to show the patch (which colour corresponds to which terrain-type)
    """
    def __init__(self,
                 geography,
                 vis_years,
                 ymax_animals,
                 cmax_animals,
                 hist_specs,
                 img_years,
                 img_dir,
                 img_base,
                 img_fmt,
                 log_file,
                 my_colours,
                 terrain_patches):
        self.geography = geography
        if vis_years:
            self.vis_years = vis_years
            if img_years:
                if img_years % vis_years != 0:
                    raise ValueError("Image interval must be a multiple of visualisation interval.")
        else:
            self.vis_years = 0
        self.ymax_animals = ymax_animals
        cmax = cmax_animals if cmax_animals is not None else {"Herbivore": 90,
                                                              "Carnivore": 90}
        self.cmax_herb = cmax["Herbivore"]
        self.cmax_carn = cmax["Carnivore"]

        if hist_specs is not None:
            try:
                for prop in hist_specs.keys():
                    if prop not in ["weight", "age", "fitness"]:
                        raise ValueError("Invalid property for histogram specification.")
                    keys = hist_specs[prop].keys()
                    if "max" not in keys and "delta" not in keys:
                        raise ValueError("Invalid histogram specification.")
                    self.hist_specs = hist_specs
            except TypeError as err:
                raise TypeError("Invalid histogram specification.") from err
        else:
            self.hist_specs = None
        self._img_years = img_years

        self.my_colours = my_colours
        self.terrain_patches = terrain_patches

        if log_file:
            self._log_file = str(log_file)
        else:
            self._log_file = None
        self._img_ctr = 0
        self._img_fmt = img_fmt
        if img_dir:
            self._img_dir = img_dir
            img_base = str(img_base)
            if img_dir.startswith("."):
                self._img_base = os.path.join(self._img_dir, img_base)
            else:
                if os.path.isabs(self._img_dir):
                    os.makedirs(self._img_dir, exist_ok=True)
                    images = os.path.join(self._img_dir, "images")
                    os.makedirs(images, exist_ok=True)
                    self._img_base = os.path.join(images, img_base)
                else:
                    self._img_dir = os.path.join(_DEFAULT_GRAPHICS_DIR, self._img_dir)
                    os.makedirs(self._img_dir, exist_ok=True)
                    self._img_base = os.path.join(self._img_dir, "images")
                    os.makedirs(self._img_base, exist_ok=True)
                    self._img_base = os.path.join(self._img_base, img_base)
        else:
            self._img_dir = None
            self._img_base = None

        # The following will be initialized by setup
        self.gridspec = None
        self._speed = None
        self.final_year = None
        self._fig = None
        self._map_plot = None
        self._year_ax = None
        self._line_ax = None
        self._line_ax2 = None
        self._animals_plot = None

        self.herbs = None
        self.carns = None
        self.n_herbs = None
        self.n_carns = None
        self._herb_ax = None
        self._herb_plot = None
        self._herb_cbar = None
        self._carn_ax = None
        self._carn_plot = None
        self._carn_cbar = None

        self._fitness_ax = None
        self._fitness_plot = None
        self.fitness_bins = None
        self._fitness_herb = None
        self._fitness_herb_ax = None
        self._fitness_carn = None
        self._fitness_carn_ax = None

        self._age_ax = None
        self._age_plot = None
        self.age_bins = None
        self._age_herb = None
        self._age_herb_ax = None
        self._age_carn = None
        self._age_carn_ax = None

        self._weight_ax = None
        self._weight_plot = None
        self.weight_bins = None
        self._weight_herb = None
        self._weight_herb_ax = None
        self._weight_carn = None
        self._weight_carn_ax = None

    def setup(self, final_year, n_species_cells, speed, figure):
        """
        Prepare graphics, with the format:

        [ Year ][       Animal count      ]   (counter, line plot)
        [ Map ][ Herbivores ][ Carnivores ]   (static, heatmap, heatmap)
        [   Age   ][  Weight ][  Fitness  ]   (histograms)

        Parameters
        ----------
        final_year : int
        n_species_cells : dict
            Initial animal population (per cell).
        speed : float
            Pause between visualization updates (seconds). Only works when not using the GUI.
        figure : plt.Figure
            Used for the GUI.
        """
        self.final_year = final_year

        if self._fig is None and not figure:
            self._fig = plt.figure(figsize=(15, 10))
            self.gridspec = self._fig.add_gridspec(11, 27)
        elif self._fig is None and figure:
            self._fig = figure
            self.gridspec = self._fig.add_gridspec(11, 27)

        if self._year_ax is None:
            self._year_ax = self._fig.add_subplot(self.gridspec[1:2, :1])
            self._year_ax.axis("off")

        if self._line_ax is None:
            self._line_ax = self._fig.add_subplot(self.gridspec[:3, 4:])
            # self._line_ax2 = self._line_ax.twinx()
            self._line_ax.set_title('Populasjon over tid')
            self._line_ax.set_ylabel("Antall dyr")
            # self._line_ax2.set_ylabel("# Carnivores")
            self._line_ax.set_ylim(0, self.ymax_animals)
            # self._line_ax2.set_ylim(0, self.ymax_animals)
            self._line_ax.set_xlim(0, final_year)
            self.herbs = np.arange(0, final_year+1, self.vis_years)
            self.n_herbs = self._line_ax.plot(self.herbs,
                                              np.full_like(self.herbs, np.nan, dtype=float),
                                              linestyle="-",
                                              color=(0.71764, 0.749, 0.63137),
                                              label="Planteetere")[0]
            self.carns = np.arange(0, final_year+1, self.vis_years)
            self.n_carns = self._line_ax.plot(self.carns,
                                              np.full_like(self.carns, np.nan, dtype=float),
                                              linestyle="-",
                                              color=(0.949, 0.7647, 0.56078),
                                              label="Kjøttetere")[0]
            self._line_ax.legend(handles=[self.n_herbs, self.n_carns])
        else:
            old_x_herb, old_y_herb = self.n_herbs.get_data()
            old_x_carn, old_y_carn = self.n_carns.get_data()
            x_herb = np.arange(old_x_herb[-1] + 1, final_year+1)
            x_carn = np.arange(old_x_carn[-1] + 1, final_year+1)
            if len(x_herb) > 0:
                y_herb = np.full_like(x_herb, np.nan, dtype=float)
                self.n_herbs.set_data(np.hstack((old_x_herb, x_herb)),
                                      np.hstack((old_y_herb, y_herb)))
                self.n_carns.set_data(np.hstack((old_x_carn, x_carn)),
                                      np.hstack((old_y_carn, y_herb)))
                self._line_ax.set_xlim(0, final_year)

        if self._map_plot is None:
            self._map_plot = self._fig.add_subplot(self.gridspec[4:7, :9])
            self._island_map(self.my_colours, self.terrain_patches)
            self._map_plot.set_title("Kart over øya")

        herb, carn = self._animal_data(n_species_cells)
        herbivore_colour = (0.71764, 0.749, 0.63137)
        carnivore_colour = (0.949, 0.7647, 0.56078)

        if self._herb_ax is None:
            self._herb_ax = self._fig.add_subplot(self.gridspec[4:7, 9:18])
            self._herb_ax.set_title("Planteeter-tetthet")
            self._herb_ax.axis("off")
            self._herb_ax.set_xlim(-0.75, len(self.geography[0]))
            self._herb_ax.set_ylim(-0.75, len(self.geography))
            outline = patches.Rectangle((-0.5, -0.5),
                                        len(self.geography[0]),
                                        len(self.geography),
                                        linewidth=2,
                                        edgecolor=herbivore_colour,
                                        facecolor="none")
            self._herb_ax.add_patch(outline)

            self._herb_plot = self._herb_ax.imshow(herb,
                                                   cmap="Greens",
                                                   vmin=0,
                                                   vmax=self.cmax_herb)
            self._herb_plot.cmap.set_bad((0, 0, 0))
            self._herb_cbar = self._fig.colorbar(self._herb_plot,
                                                 ax=self._herb_ax,
                                                 fraction=0.046, pad=0.04)
            self._herb_cbar.ax.tick_params(labelsize=7)

        if self._carn_ax is None:
            self._carn_ax = self._fig.add_subplot(self.gridspec[4:7, 18:27])
            self._carn_ax.set_title("Kjøtteter-tetthet")
            self._carn_ax.axis("off")
            self._carn_ax.set_xlim(-0.75, len(self.geography[0]))
            self._carn_ax.set_ylim(-0.75, len(self.geography))
            outline = patches.Rectangle((-0.5, -0.5),
                                        len(self.geography[0]),
                                        len(self.geography),
                                        linewidth=2,
                                        edgecolor=carnivore_colour,
                                        facecolor="none")
            self._carn_ax.add_patch(outline)

            self._carn_plot = self._carn_ax.imshow(carn,
                                                   cmap="Oranges",
                                                   vmin=0,
                                                   vmax=self.cmax_carn)
            self._carn_plot.cmap.set_bad((0, 0, 0))
            self._carn_cbar = self._fig.colorbar(self._carn_plot,
                                                 ax=self._carn_ax,
                                                 fraction=0.046, pad=0.04)
            self._carn_cbar.ax.tick_params(labelsize=7)

        if self.hist_specs is not None:
            for feature, specs in self.hist_specs.items():
                if feature == "age":
                    self.age_bins = np.arange(0,
                                              specs["max"] + specs["delta"]/2,
                                              specs["delta"])
                elif feature == "weight":
                    self.weight_bins = np.arange(0,
                                                 specs["max"] + specs["delta"]/2,
                                                 specs["delta"])
                else:
                    self.fitness_bins = np.arange(0,
                                                  specs["max"] + specs["delta"]/2,
                                                  specs["delta"])
        else:
            self.age_bins = np.arange(0, 45 + 5/2, 5)
            self.fitness_bins = np.arange(0, 1 + 0.1/2, 0.1)
            self.weight_bins = np.arange(0, 60 + 5/2, 5)

        if self._age_ax is None:
            age_counts = np.zeros_like(self.age_bins[:-1], dtype=float)
            self._age_ax = self._fig.add_subplot(self.gridspec[8:11, 0:9])
            self._age_herb = self._age_ax.stairs(age_counts,
                                                 self.age_bins,
                                                 color=herbivore_colour,
                                                 lw=2)
            self._age_carn = self._age_ax.stairs(age_counts,
                                                 self.age_bins,
                                                 color=carnivore_colour,
                                                 lw=2)
            self._age_ax.set_ylim([0, 100])
            self._age_ax.set_xlabel('Alder')
            self._age_ax.set_ylabel('Antall dyr', rotation=90)
            self._age_ax.set_yticks([])

        if self._weight_ax is None:
            weight_counts = np.zeros_like(self.weight_bins[:-1], dtype=float)
            self._weight_ax = self._fig.add_subplot(self.gridspec[8:11, 9:18])
            self._weight_herb = self._weight_ax.stairs(weight_counts,
                                                       self.weight_bins,
                                                       color=herbivore_colour,
                                                       lw=2)
            self._weight_carn = self._weight_ax.stairs(weight_counts,
                                                       self.weight_bins,
                                                       color=carnivore_colour,
                                                       lw=2)
            self._weight_ax.set_ylim([0, 50])
            self._weight_ax.set_xlabel('Vekt')
            self._weight_ax.set_ylabel('')
            self._weight_ax.set_yticks([])

        if self._fitness_ax is None:
            fitness_counts = np.zeros_like(self.fitness_bins[:-1], dtype=float)
            self._fitness_ax = self._fig.add_subplot(self.gridspec[8:11, 18:27])
            self._fitness_herb = self._fitness_ax.stairs(fitness_counts,
                                                         self.fitness_bins,
                                                         color=herbivore_colour,
                                                         lw=2)
            self._fitness_carn = self._fitness_ax.stairs(fitness_counts,
                                                         self.fitness_bins,
                                                         color=carnivore_colour,
                                                         lw=2)
            self._fitness_ax.set_ylim([0, 100])
            self._fitness_ax.set_xlabel('Form')
            self._fitness_ax.set_ylabel('')
            self._fitness_ax.set_yticks([])

        self.setup_log_file() if self._log_file is not None else None

        self._speed = speed

    def setup_log_file(self):
        """Sets up the log file for the simulation if specified."""
        if not os.path.exists(self._log_file):
            directory = os.path.dirname(self._log_file)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            if not os.path.isabs(self._log_file):
                if self._img_dir is not None:
                    if self._img_dir[-1] == ".":
                        self._log_file = os.path.join(self._img_dir, self._log_file)
                    else:
                        self._log_file = os.path.join(self._img_dir, "..", self._log_file)
                else:
                    os.makedirs(_DEFAULT_GRAPHICS_DIR, exist_ok=True)
                    self._log_file = os.path.join(_DEFAULT_GRAPHICS_DIR, self._log_file)

            with open(self._log_file, "w") as file:
                write = csv.writer(file)
                write.writerow(["Iteration", "Herbivores", "Carnivores"])

    def update_graphics(self, year, n_species, n_species_cells, animals,
                        canvas=None, history=True):
        r"""
        Updates the graphics with new data for the given year.

        Parameters
        ----------
        year : int
        n_species : dict

            .. code:: python

                {"Herbivore": 100, "Carnivore": 10}

        n_species_cells : dict

            .. code:: python

                {(10, 10): {"Herbivore": 100, "Carnivore: 10}}

        animals : dict

            .. code:: python

                {"Herbivore": [Herbivore(), Herbivore(), ...], ...}

        canvas : FigureCanvas, optional
            Used for the GUI.
        history : bool, optional
            Whether to return the animals' histories. Used for the GUI.
        """
        self._update_year_counter(year)
        self._update_line_plot(year, n_species)
        self._update_heatmap(year, n_species_cells)
        _history = self._update_animal_features(animals)

        if not canvas:
            self._fig.canvas.flush_events()
            plt.pause(self._speed)

            self._save_image(year)
            self.save_to_file(year, n_species) if self._log_file is not None else None
        else:
            canvas.draw()
            QApplication.processEvents()

            loop = QEventLoop()
            QTimer.singleShot(int(self._speed * 1e8), loop.quit)
            loop.exec_()

        if history:
            return _history
        return None

    def make_movie(self, movie_fmt="mp4"):
        """
        Creates MPEG4 movie from visualization images saved.

        Parameters
        ----------
        movie_fmt : str, optional
            The movie format to use. Either "mp4" or "gif".

        Notes
        -----
            Requires ffmpeg for MP4 and magick for GIF.
            The movie is stored as img_base + movie_fmt.
        """
        if not self._img_base:
            raise RuntimeError("No filename defined.")

        _movie_base = os.path.join(self._img_dir, "U13")

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # section "Compatibility"
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', f'{self._img_base}_%05d.{self._img_fmt}',
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       f'{_movie_base}.{movie_fmt}'])
            except subprocess.CalledProcessError as err:
                raise RuntimeError(f'ERROR: convert failed with: {err}') from err
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       f'{self._img_base}_*.{self._img_fmt}',
                                       f'{_movie_base}.{movie_fmt}'])
            except subprocess.CalledProcessError as err:
                raise RuntimeError(f'ERROR: convert failed with: {err}') from err
        else:
            raise ValueError(f'Unknown movie format: {movie_fmt}')

    def reset_counts(self):
        """Resets the animal count plot."""
        try:
            self._line_ax.remove()
        except AttributeError:
            return
        # self._line_ax2.remove()
        self._line_ax = None
        # self._line_ax2 = None

    def reset_graphics(self):
        """Resets the graphics."""
        try:
            self._line_ax.remove()
        except AttributeError:
            return

        self._line_ax = None
        # self._line_ax2.remove()
        # self._line_ax2 = None
        self._year_ax.remove()
        self._year_ax = None
        self._map_plot.remove()
        self._map_plot = None
        self._herb_ax.remove()
        self._herb_ax = None
        self._herb_cbar.remove()
        self._carn_ax.remove()
        self._carn_ax = None
        self._carn_cbar.remove()
        self._fitness_ax.remove()
        self._fitness_ax = None
        self._age_ax.remove()
        self._age_ax = None
        self._weight_ax.remove()
        self._weight_ax = None

    def _save_image(self, step):
        """
        Saves graphics to file if file name given.

        Parameters
        ----------
        step : int
            Current step of simulation.
        """
        if self._img_base is None or step % self._img_years != 0:
            return

        plt.savefig(f'{self._img_base}_{self._img_ctr:05d}.{self._img_fmt}')
        self._img_ctr += 1

    def _update_year_counter(self, year):
        """
        Update the year counter plot.

        Parameters
        ----------
        year : int
        """
        length = len(str(self.final_year)) - len(str(year)) + 3
        text = "Iterasjon: {:>{}} {:>15}"
        if hasattr(self, "txt"):
            self.txt.remove()

        self.txt = self._year_ax.text(0.5, 0.5,
                                      text.format(year, length, ''),
                                      fontsize=10,
                                      horizontalalignment='center',
                                      verticalalignment='center',
                                      transform=self._year_ax.transAxes)
        self.txt.set_text(text.format(year, length, ''))

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
        y_herbs[index] = n_animals["Herbivore"]
        self.n_herbs.set_ydata(y_herbs)
        y_carns = self.n_carns.get_ydata()
        y_carns[index] = n_animals["Carnivore"]
        self.n_carns.set_ydata(y_carns)

        if not self.ymax_animals:
            _y_max = max(max(y_herbs) * 1.1, max(y_carns) * 1.1)
            _y_max = max(_y_max, self._line_ax.get_ylim()[1])
            self._line_ax.set_ylim(0, _y_max)

            # _y_carn = max(max(y_carns) * 1.1, self._line_ax2.get_ylim()[1])
            # self._line_ax2.set_ylim(0, _y_carn)

    def _island_map(self, my_colours, terrain_patches):
        """
        Creates the island map.

        Parameters
        ----------
        my_colours : dict, optional
        terrain_patches : bool, optional
        """
        colours = {"L": [colour / 255 for colour in [185, 214, 135]],
                   "H": [colour / 255 for colour in [232, 236, 158]],
                   "M": [colour / 255 for colour in [128, 128, 128]],
                   "W": [colour / 255 for colour in [149, 203, 204]]}

        if my_colours is not None:
            for key, val in my_colours.items():
                colours[key] = val

        coloured_map = [[colours[letter] for letter in row] for row in self.geography]

        self._map_plot.imshow(coloured_map)

        # Invisible ticks:
        self._map_plot.set_xticks([])
        self._map_plot.set_yticks([])

        if terrain_patches:
            mapping = {"L": "L", "H": "H", "M": "F", "W": "V"}
            patch_list = [patches.Rectangle((0, 0), 1, 1, color=val,
                                            label=mapping[key])
                          for key, val in colours.items()]
            self._map_plot.legend(handles=patch_list, frameon=False,
                                  bbox_to_anchor=(1, 1), loc=2,
                                  borderaxespad=0.2, handlelength=1.5, handleheight=1.5)

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
        herbs = []
        carns = []
        for i in range(1, len(self.geography)+1):
            row_herb = []
            row_carn = []
            for j in range(1, len(self.geography[0])+1):
                herb, carn = density[(i, j)].values()
                row_herb.append(herb)
                row_carn.append(carn)
            herbs.append(row_herb)
            carns.append(row_carn)

        herb = [[np.nan if val == 0 else val for val in row] for row in herbs]
        carn = [[np.nan if val == 0 else val for val in row] for row in carns]

        return herb, carn

    def _update_heatmap(self, year, n_species_cells,):
        """
        Update the heatmap of animal distributions.

        Parameters
        ----------
        n_species_cells : dict
            A dictionary with cell coordinates as keys and dictionaries with the amount of each
            species in that cell as values.
        """
        herb, carn = self._animal_data(n_species_cells)

        self._herb_plot.set_data(herb[::-1])
        self._carn_plot.set_data(carn[::-1])

        self._herb_plot.cmap.set_bad((1, 1, 1))
        self._carn_plot.cmap.set_bad((1, 1, 1))

        if year % 15 == 0:
            herbs = np.nanmax(herb) + 10
            carns = np.nanmax(carn) + 10
            self._herb_plot.set_clim(0, herbs)
            self._carn_plot.set_clim(0, carns)

    def _update_animal_features(self, animals):
        """
        Update the histograms of animal features.

        Parameters
        ----------
        animals : dict
            A dictionary with species as keys and lists of animal objects as values.

        Returns
        -------
        dict
            A dictionary with species as keys and dictionaries with the average age, weight and
            fitness of the animals as values.
        """
        herbs = animals["Herbivore"]
        carns = animals["Carnivore"]

        herbivores_age = [herb.a for herb in herbs]
        carnivores_age = [carn.a for carn in carns]
        herbs_age, _ = np.histogram(herbivores_age, bins=self.age_bins)
        carns_age, _ = np.histogram(carnivores_age, bins=self.age_bins)

        herbivores_weight = [herb.w for herb in herbs]
        carnivores_weight = [carn.w for carn in carns]
        herbs_weight, _ = np.histogram(herbivores_weight, bins=self.weight_bins)
        carns_weight, _ = np.histogram(carnivores_weight, bins=self.weight_bins)

        herbivores_fitness = [herb.fitness for herb in herbs]
        carnivores_fitness = [carn.fitness for carn in carns]
        herbs_fitness, _ = np.histogram(herbivores_fitness, bins=self.fitness_bins)
        carns_fitness, _ = np.histogram(carnivores_fitness, bins=self.fitness_bins)

        self._age_herb.set_data(herbs_age)
        self._age_carn.set_data(carns_age)
        self._weight_herb.set_data(herbs_weight)
        self._weight_carn.set_data(carns_weight)
        self._fitness_herb.set_data(herbs_fitness)
        self._fitness_carn.set_data(carns_fitness)

        _age_ylim = max(max(max(herbs_age), max(carns_age)) * 1.1, 0.1)
        _weight_ylim = max(max(max(herbs_weight), max(carns_weight)) * 1.1, 0.1)
        _fitness_ylim = max(max(max(herbs_fitness), max(carns_fitness)) * 1.1, 0.1)

        self._age_ax.set_ylim([-_age_ylim*0.03, _age_ylim])
        self._weight_ax.set_ylim([-_weight_ylim*0.03, _weight_ylim])
        self._fitness_ax.set_ylim([-_fitness_ylim*0.03, _fitness_ylim])

        n_herbs = len(herbs)
        n_carns = len(carns)
        return {"Herbivore": {
                     "Age": sum(herbivores_age) / n_herbs if n_herbs > 0 else np.nan,
                     "Weight": sum(herbivores_weight) / n_herbs if n_herbs > 0 else np.nan,
                     "Fitness": sum(herbivores_fitness) / n_herbs if n_herbs > 0 else np.nan
                },
                "Carnivore": {
                    "Age": sum(carnivores_age) / n_carns if n_carns > 0 else np.nan,
                    "Weight": sum(carnivores_weight) / n_carns if n_carns > 0 else np.nan,
                    "Fitness": sum(carnivores_fitness) / n_carns if n_carns > 0 else np.nan}
                }

    def save_to_file(self, year, data):
        """
        Saves the yearly animal counts to file.

        Parameters
        ----------
        year : int
        data : dict
            Animal counts the given year.
        """
        with open(self._log_file, "a", newline="") as file:
            write = csv.writer(file)
            write.writerow([year] + list(data.values()))
