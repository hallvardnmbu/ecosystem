BioSim
------
Simulate a simplified ecosystem of different animal species on an island.

The BioSim package is a framework for modelling biological systems. It is developed as part of
the course INF200 at the Norwegian University of Life Sciences (NMBU). The package contains tools
for a simple biological simulation, and is designed to be easily extendable. The package is highly
customisable, and easy to use.

Features of the BioSim package
------------------------------
* Saving images whilst visualising is done a bit more elegantly than the example in the 
  assignment. When saving an image, an (existing or nonexist) absolute/relative directory can be
  passed. This leads to the corresponding test of Hans Ekkehard Plesser's to fail.

* We have created a GUI which makes using the package more intuitive and simple to use. The GUI
  does however lack some of the features accessible through the command line interface, although 
  the most important ones are included. (Setting visualisation parameters are not included.) See 
  documentation for examples of how to use the GUI (under "Examples").

* We have optimised the code in several places and reduced bottlenecks down to the bare minimum,
  which leads to extremely fast simulation(s); 28.6s when profiling check_sim without visualisation.

* The package is also made extremely generalised (excepting the graphics and GUI parts), which
  makes it easy to extend and modify if needed. Without having to change much of the code. (See
  documentation "On further expansion" for examples on what needs to be done to extend the package.)

* Relevant examples using the package can be found in the 'examples' directory or in the 
  documentation (where additional explanatory text/visuals is included).

* The documentation site is created using a custom-made css-file (editing the RTD-theme), which
  makes it more visually appealing. There is also visual examples included along with the examples.

* In addition to the dockstrings, there are additional sections addressing how to extend the
  package, how to use the package and future ideas for the project.

* Tests are organised by unit- and integration tests within "test_*". We have also created a
  separate test-file for the statistical tests.
