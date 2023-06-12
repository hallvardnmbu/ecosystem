"""
Package for visualisation of the simulation.
"""


import matplotlib.pyplot as plt
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

    def __init__(self, img_years, img_dir=None, img_name="dv", img_fmt="png"):
        if img_dir is not None:
            self._img_base = os.path.join(img_dir, img_name)
        else:
            self._img_base = None

        self.img_fmt = img_fmt

        self._img_ctr = 0
        self._img_step = img_years

        # The following will be initialized by _setup_graphics
        self._fig = None
        self._map_ax = None
        self._img_axis = None
        self._mean_ax = None
        self._mean_line = None

        # island_map : str
        #     Multi-line string specifying island geography
        # ini_pop : list
        #     List of dictionaries specifying initial population
        # seed : int
        #     Integer used as random number seed
        # vis_years : int
        #     Years between visualization updates (if 0, disable graphics)
        # ymax_animals : int
        #     Number specifying y-axis limit for graph showing animal numbers
        # cmax_animals : dict
        #     Color-scale limits for animal densities, see below
        # hist_specs : dict
        #     Specifications for histograms, see below
        # img_years : int
        #     Years between visualizations saved to files (default: `vis_years`)
        # img_dir : str
        #     Path to directory for figures
        # img_base : str
        #     Beginning of file name for figures
        # img_fmt : str
        #     File type for figures, e.g. 'png' or 'pdf'
        # log_file : str
        #     If given, write animal counts to this file

    def update(self, step, sys_map, sys_mean):
        """
        Updates graphics with current data and save to file if necessary.

        Parameters
        ----------
        step : int
            Current time step
        sys_map : array
            Current system status (2d array)
        sys_mean : float
            Current mean value of system
        """

    self._update_system_map(sys_map)
    self._update_mean_graph(step, sys_mean)
    self._fig.canvas.flush_events()  # ensure every thing is drawn
    plt.pause(1e-6)  # pause required to pass control to GUI

    self._save_graphics(step)

    def make_movie(self, movie_fmt="mp4"):
        """
        Creates MPEG4 movie from visualization images saved.

        Notes
        -----
        Requires ffmpeg for MP4 and magick for GIF.

        The movie is stored as `img_base + movie_fmt`
        """

        if self._img_base is None:
            raise RuntimeError("No filename defined.")

        if movie_fmt == 'mp4':
            try:
                # Parameters chosen according to http://trac.ffmpeg.org/wiki/Encode/H.264,
                # (Section: "Compatibility")
                subprocess.check_call([_FFMPEG_BINARY,
                                       '-i', '{}_%05d.png'.format(self._img_base),
                                       '-y',
                                       '-profile:v', 'baseline',
                                       '-level', '3.0',
                                       '-pix_fmt', 'yuv420p',
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: ffmpeg failed with: {}'.format(err))
        elif movie_fmt == 'gif':
            try:
                subprocess.check_call([_MAGICK_BINARY,
                                       '-delay', '1',
                                       '-loop', '0',
                                       '{}_*.png'.format(self._img_base),
                                       '{}.{}'.format(self._img_base, movie_fmt)])
            except subprocess.CalledProcessError as err:
                raise RuntimeError('ERROR: convert failed with: {}'.format(err))
        else:
            raise ValueError('Unknown movie format: ' + movie_fmt)

    def setup(self, final_step, img_step):
        """
        Prepare graphics.

        Call this before calling `update()` for the first time after
        the final time step has changed.

        Parameters
        ----------
        final_step : int
            Last time step to be visualised (upper limit of x-axis)
        """

        # create new figure window
        if self._fig is None:
            self._fig = plt.figure()

        # Add left subplot for images created with imshow().
        # We cannot create the actual ImageAxis object before we know
        # the size of the image, so we delay its creation.
        if self._map_ax is None:
            self._map_ax = self._fig.add_subplot(1, 2, 1)
            self._img_axis = None

        # Add right subplot for line graph of mean.
        if self._mean_ax is None:
            self._mean_ax = self._fig.add_subplot(1, 2, 2)
            self._mean_ax.set_ylim(-0.05, 0.05)

        # needs updating on subsequent calls to simulate()
        # add 1 so we can show values for time zero and time final_step
        self._mean_ax.set_xlim(0, final_step+1)

        if self._mean_line is None:
            mean_plot = self._mean_ax.plot(np.arange(0, final_step+1),
                                           np.full(final_step+1, np.nan))
            self._mean_line = mean_plot[0]
        else:
            x_data, y_data = self._mean_line.get_data()
            x_new = np.arange(x_data[-1] + 1, final_step+1)
            if len(x_new) > 0:
                y_new = np.full(x_new.shape, np.nan)
                self._mean_line.set_data(np.hstack((x_data, x_new)),
                                         np.hstack((y_data, y_new)))

    def _update_system_map(self, sys_map):
        """Update the 2D-view of the system."""

        if self._img_axis is not None:
            self._img_axis.set_data(sys_map)
        else:
            self._img_axis = self._map_ax.imshow(sys_map,
                                                 interpolation='nearest',
                                                 vmin=-0.25, vmax=0.25)
            plt.colorbar(self._img_axis, ax=self._map_ax,
                         orientation='horizontal')

    def _update_mean_graph(self, step, mean):
        """
        Updates the graph with new mean value at step.

        Parameters
        ----------
        step : int
            Current step.
        mean : float
            Current mean value.
        """

        y_data = self._mean_line.get_ydata()
        y_data[step] = mean
        self._mean_line.set_ydata(y_data)

    def _save_graphics(self, step):
        """
        Saves graphics to file if file name given.

        Parameters
        ----------
        step : int
            Step interval to save image.
        """

        if self._img_base is None or step % self._img_step != 0:
            return

        plt.savefig('{base}_{num:05d}.{type}'.format(base=self._img_base,
                                                     num=self._img_ctr,
                                                     type=self._img_fmt))
        self._img_ctr += 1

