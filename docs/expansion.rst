Further expansion
=================

This package is designed to be easily expandable. Both new species and new terrain-types can be
added with relative ease.

In order to modify the species, the following steps are necessary:

* Create a new subspecies with its own parameters and behaviour.

* Update the feed-method in :mod:`island.py` to include the new species.

* (Optional) Update the graphics-method in :mod:`graphics.py` to include the new species.

In order to modify the terrain-types, the following steps are necessary:

* Add the new terrain-type to :code:`default_fodder_parameters` and :code:`get_fodder_parameter`.

.. raw:: html

   <div style="text-align: left; font-size: 30px; margin-bottom: 20px;">
      <b>Examples</b>
   </div>

Adding a new species (without specifying a new feed- and graphics-method):
--------------------------------------------------------------------------

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

            return 3, {"H": True, "L": True, "D": True, "W": True}

Here a new species called "Bird" is added. The bird-species has a modified stride-size of 3
(moves three tiles per year) and can move on all terrain-types.

Adding a new terrain-type ("M" for "Mountain"):
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

            return {"H": 300, "L": 800, "D": 0, "W": 0, "M": 100}

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
                    "D": cls.D,
                    "W": cls.W,
                    "M": cls.M}[terrain_type]

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

If it is desired to change the GUI, contact the authors of this package or try modifying the code
yourself. As the GUI was meant as a fun side-project, it was not prioritised when it came to
generalising the code, and was therefore buildt for the specific case of Herbivores and
Carnivores on an island of terrain-types Lowland, Highland, Desert and Water.