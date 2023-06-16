"""
Contains simulation.
"""

# The material in this file is licensed under the BSD 3-clause license
# https://opensource.org/licenses/BSD-3-Clause
# (C) Copyright 2023 Hans Ekkehard Plesser / NMBU


import matplotlib.pyplot as plt
import random

from .island import Island
from .graphics import Graphics


class BioSim:
    r"""
    Simulation class.

    Parameters
    ----------
    island_map : str
        Multi-line string specifying island geography
    ini_pop : list
        List of dictionaries specifying initial population
    seed : int
        Integer used as random number seed
    vis_years : int
        Years between visualization updates (if 0, disable graphics)
    ymax_animals : int
        Number specifying y-axis limit for graph showing animal numbers
    cmax_animals : dict
        Color-scale limits for animal densities, see below
    hist_specs : dict
        Specifications for histograms, see below
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

    Notes
    -----
    - If ymax_animals is None, the y-axis limit should be adjusted automatically.
    - If cmax_animals is None, sensible, fixed default values should be used.
    - cmax_animals is a dict mapping species names to numbers, e.g.,

      .. code:: python

         {'Herbivore': 50, 'Carnivore': 20}

    - hist_specs is a dictionary with one entry per property for which a histogram
      shall be shown. For each property, a dictionary providing the maximum value
      and the bin width must be given, e.g.,

      .. code:: python

         {'weight': {'max': 80, 'delta': 2},
          'fitness': {'max': 1.0, 'delta': 0.05}}

      Permitted properties are 'weight', 'age', 'fitness'.
    - If img_dir is None, no figures are written to file.
    - Filenames are formed as

      .. code:: python

         Path(img_dir) / f'{img_base}_{img_number:05d}.{img_fmt}'

      where `img_number` are consecutive image numbers starting from 0.

    - `img_dir` and `img_base` must either be both None or both strings.
    """

    def __init__(self,
                 island_map,
                 ini_pop,
                 seed=1,
                 vis_years=None,
                 ymax_animals=None,
                 cmax_animals=None,
                 hist_specs=None,
                 img_years=1,
                 img_dir=None,
                 img_base="U13",
                 img_fmt='png',
                 log_file=None):

        random.seed(seed)

        if vis_years == 0 or vis_years is None:
            self.vis_years = False
        else:
            self.vis_years = vis_years

        self.island = Island(geography=island_map, ini_pop=ini_pop)

        self.graphics = Graphics(geography=self.island.geography,
                                 initial_density=self.island.n_animals_per_species_per_cell,
                                 vis_years=vis_years,
                                 ymax_animals=ymax_animals,
                                 cmax_animals=cmax_animals,
                                 hist_specs=hist_specs,
                                 img_years=img_years,
                                 img_dir=img_dir,
                                 img_base=img_base,
                                 img_fmt=img_fmt,
                                 log_file=log_file)

    def set_animal_parameters(self, species, params):
        """
        Set parameters for animal species.

        Parameters
        ----------
        species : str
            Name of species for which parameters shall be set.
        params : dict
            New parameter values.

        Raises
        ------
        KeyError
            If invalid parameter keys are passed.
        ValueError
            If invalid parameter values are passed.
        """

        try:
            self.island.species_map[species].set_parameters(params)
        except KeyError as e:
            # Here I googled how to retrieve the element in a set. I found that I could use
            # next(iter(...)):
            difference = next(iter(set(params.keys()) - set(self.island.species_map.keys())))
            if species not in self.island.species_map.keys():
                raise KeyError(f"Invalid species: {species}. Valid species:"
                               f" {', '.join(list(self.island.species_map.keys()))}")
            elif f"Invalid parameter: {difference}" in str(e):
                raise KeyError(f"Invalid key: {difference}.")
            else:
                raise KeyError(f"Invalid parameter keys in {params}.")
        except ValueError:
            raise ValueError("Invalid parameter value(s).")

    def set_landscape_parameters(self, landscape, params):
        """
        Set parameters for landscape type.

        Parameters
        ----------
        landscape : str
            Code letter for landscape.
        params : dict
            New parameter values.

        Raises
        ------
        ValueError
            If invalid landscape type is passed.
            If invalid parameter keys are passed.
            If invalid parameter values are passed.
        """

        if "f_max" not in params:
            raise ValueError(f"Invalid parameter key {params}. Valid keys are 'f_max'.")
        else:
            try:
                if params["f_max"] < 0:
                    raise ValueError(f"Parameter value {params['f_max']} must be positive.")
            except TypeError:
                raise ValueError(f"Parameter value {params['f_max']} must be a number.")
        if landscape not in self.island.default_fodder_parameters():
            raise ValueError(f"Invalid landscape type {landscape}.")

        new_parameters = {landscape: params["f_max"]}
        self.island.set_fodder_parameters(new_parameters)

    def simulate(self, num_years, speed=1e-6):
        """
        Run simulation while visualizing the result.

        Parameters
        ----------
        num_years : int
            Number of years to simulate.
        speed : float, optional
            The interval between plot data-updates.
        """

        simulate_years = num_years + self.year + 1
        self.graphics.setup(simulate_years)

        while self.year < simulate_years:

            if self.vis_years:
                if self.year % self.vis_years == 0:
                    self.graphics.update_graphics(self.year,
                                                  self.num_animals_per_species,
                                                  self.island.n_animals_per_species_per_cell,
                                                  self.island.population,
                                                  speed)
            self.island.yearly_cycle()

        plt.draw()

    def add_population(self, population):
        """
        Add a population to the island

        Parameters
        ----------
        population : list of dictionaries
            Adds a population to the island.
        """

        self.island.add_population(population)

    @property
    def year(self):
        """Last year simulated."""

        return self.island.year

    @property
    def num_animals(self):
        """Total number of animals on island."""

        return sum(self.num_animals_per_species.values())

    @property
    def num_animals_per_species(self):
        """Number of animals per species in island, as dictionary."""

        return self.island.n_animals_per_species

    def make_movie(self, movie_fmt="mp4"):
        """
        Create MPEG4 movie from visualization images saved.
        """

        if movie_fmt not in ["mp4", "gif"]:
            raise ValueError(f"Invalid movie format {movie_fmt} (valid: mp4 or gif).")

        self.graphics.make_movie(movie_fmt)
