On further expansion
====================

This package is designed to be easily expandable. Both new species and new terrain-types can be
added with (relative) ease (depending on the significance of the additions).

In order to add another species, the following steps are necessary:

* Create a new subspecies with its own default parameters and behaviour.

* Update the yearly cycle-methods in :mod:`island.py` to include the new species.

* (Optional) Update the graphics-method in :mod:`graphics.py` to include the new species.

In order to modify the terrain-types, the following steps are necessary:

* Add the new terrain-type to :code:`default_fodder_parameters` and :code:`get_fodder_parameter`.

* Add the new terrain to the various places they are needed. Here a search for the standard
  terrain-types should show you where the new type is needed.

.. raw:: html

   <div style="text-align: left; font-size: 30px; margin-bottom: 20px;">
      <b>Examples</b>
   </div>

Adding a new species (without specifying new yearly- and graphics-methods):
----------------------------------------------------------------------------

* Addition to :mod:`animals.py` (paste at the bottom of the module and modify):

    .. code-block:: python

        class Bird(Animal):
        """
        Subclass for Birds.

        Parameters
        ----------
        age : int, optional
            Age of the animal.
        weight : float, optional
            Weight of the animal.
        """

        @classmethod
        def default_parameters(cls):
            """
            Default parameters for Birds.

            Returns
            -------
            dict
                Default parameters for Birds.
            """

            return {"w_birth": 6.0,
                    "sigma_birth": 1.0,
                    "beta": 0.75,
                    "eta": 0.125,
                    "a_half": 40.0,
                    "phi_age": 0.3,
                    "w_half": 4.0,
                    "phi_weight": 0.4,
                    "mu": 0.4,
                    "gamma": 0.8,
                    "zeta": 3.5,
                    "xi": 1.1,
                    "omega": 0.8,
                    "F": 50.0,
                    "DeltaPhiMax": 10.0}

        @classmethod
        def default_motion(cls):
            """
            Default movement parameters for Birds.

            Returns
            -------
            stride : int
                Step size.
            movable : dict
                Movable terrain.
            """

            return {"stride": 3,
                    "movable": {"H": True, "L": True, "M": True, "W": True}}

Here a new species called "Bird" is added. The bird-species has a modified stride-size of 3
(moves three tiles per year) and can move on all terrain-types.

Adding a new terrain-type ("D" for "Desert"):
-----------------------------------------------

* :code:`default_fodder_parameters`

    .. code-block:: python

        @classmethod
        def default_fodder_parameters(cls):
            """
            Returns a dictionary with the default fodder parameters for the different terrain types.

            Returns
            -------
            dict
                A dictionary with the default fodder parameters for the different terrain types.
            """

            return {"H": 300, "L": 800, "M": 0, "W": 0, "D": 100}

* :code:`get_fodder_parameters`

    .. code-block:: python

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
                    "M": cls.M,
                    "W": cls.W,
                    "D": cls.D}[terrain_type]

From island to mainland:
------------------------

If it is desired to create a mainland-map, it is also necessary to modify :code:`_terraform()` in
:mod:`island.py`. The necessary code to change (or remove) is the following:

    .. code-block:: python

        for i in range(x):
            if self.geography[i][0] != "W" or self.geography[i][y-1] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")
        for j in range(y):
            if self.geography[0][j] != "W" or self.geography[x-1][j] != "W":
                raise ValueError("The edges of the map must be 'W' (Water).")

Notes on changing the GUI:
--------------------------

If it is desired to change the GUI, contact the author (Hallvard H. Lavik) of this package or try
modifying the code yourself. As the GUI was meant as a fun side-project and for the
ECOL100-course, it is not as generalised as the rest of the package. It was buildt for
the specific case of Herbivores and Carnivores on an island of terrain-types Lowland, Highland,
Mountain and Water.
