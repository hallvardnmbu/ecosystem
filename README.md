Biosim 
-------
A simulation of a simplified ecosystem on an island.

The BioSim package is a framework for modelling biological systems. It is developed as part of
the course INF200 at the Norwegian University of Life Sciences. The package contains tools for a
simple biological simulation, and is designed to be easily extendable. The package is highly
customisable, and easy to use.

* Saving images whilst visualising is done a bit more elegantly than the example in the 
  assignment. When saving an image, a (nonexist) absolute/relative directory can be passed. This 
  leads to the corresponding Hans Ekkehard Plesser's test to fail. 

* We have created a GUI which simplifies running the simulation, and is more intuitive. The GUI 
  does however lack some of the features accessible through the command line interface, although 
  the most important ones are included. (Setting visualisation parameters are not included.) See 
  documentation for example of how to use the GUI (under "Examples").

* We have optimised the code in several places, which leads to extremely fast simulation(s). (28.
  6s when profiling check_sim without visualisation.)

* The package is also made extremely generalised (excepting the graphics and GUI parts), whick 
  makes it easy to extend and modify if needed, without having to change much of the code. (See 
  documentation for examples on what needs to be done to extend the package.)

* Relevant examples using the package can be found in the 'examples' directory or in the 
  documentation (where additional explanatory text is included).

* The documentation is created using a custom made css-file, which makes it more visually 
  appealing. There are also several images included, to make it more fun to read as well as see 
  examples of what the package does.

* The documentation has additional pages addressing how to extend the package, how to use the 
  package and future ideas for the project.