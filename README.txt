BioSim
------
Simulate a simplified ecosystem of different animal species on an island.

The BioSim package is a framework for modeling biological systems. It is developed as part of
the course INF200 at the Norwegian University of Life Sciences (NMBU). And expanded to be used as a
part of the ECOL100-course at the same university. The package contains tools for a simple
biological simulation, and is designed to be easily extendable. The package is highly optimized,
and easy to use.

* Relevant examples using the package can be found in the 'examples' directory or through the
  documentation (where additional explanatory text/visuals is included).

Features
--------
* The code has been highly optimized, and bottlenecks are kept down to the bare minimum, which leads
  to extremely fast simulation(s).

* In addition to being optimized, the package is also extremely generalized (excepting the graphics
  and GUI parts), which makes it easy to extend and modify if needed. (See documentation 'On further
  expansion' for examples on what needs to be done when extending the package.)

* Additional feature; 'motion.' This can be seen species-specific parameters, and determines which
  terrain-types an animal can move to, and how big the step size is.

* Autogeneration of maps. When using the GUI, the user has the option of autocompleting the map
  drawing. This will automatically generate a 'realistic' map, either continuing on the user drawing
  or starting from scratch.

* Tests are organized by unit- and integration tests within 'test_*'. There is, in addition, a
  separate test file for statistical tests.

Documentation
-------------
* Graphical and explained examples of the package in use.

* Created using a custom-made css-file (editing the RTD-theme), which makes it the more visually
  appealing.

* In addition to the docstrings, there are additional sections in the documentation addressing how
  to extend the package, how to use the package and future ideas for the project.
