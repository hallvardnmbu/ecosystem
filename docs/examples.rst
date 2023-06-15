Examples
=================

Below are some examples of how to use the simulation framework.

Example simulation (without GUI):
---------------------------------

.. literalinclude:: ../examples/example_simulation.py
    :language: python

Example simulation (with GUI):
------------------------------

To use the GUI, import :mod:`biosim.gui` and create an instance of the GUI class, specifying the
desired map size (:code:`instance = BioSimGUI(map_size)`). The GUI will then open in a new window
when :code:`instance.mainloop()` is called.

The pros and cons of the GUI:

* Easy to visualise.

* A bit clumsy when navigating from the simulation plot back to the GUI.

* Easy to use.

* Able to continue simulating, or reset it.

* Unable to specify parameters for the simulation.

* Able to navigate back and forth from drawing and simulating.

* Super fun.

To use the GUI, run the following code (and change :code:`map_size` to your liking):

.. literalinclude:: ../examples/example_with_gui.py
    :language: python

Making a mp4 movie:
-------------------

.. literalinclude:: ../examples/ex_01_movie.py
    :language: python