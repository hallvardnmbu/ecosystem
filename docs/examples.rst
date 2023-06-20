Examples
=================

Below are some examples of how to use the simulation framework.

Example simulation (without GUI):
---------------------------------

.. image:: _static/images/example_simulation.png
   :width: 700px
   :align: center
   :class: bordered-image

.. literalinclude:: ../examples/example_simulation.py
    :language: python

Example simulation (with GUI):
------------------------------

To use the GUI, import :mod:`biosim.gui` and create an instance of the GUI class, specifying the
desired map size (:code:`instance = BioSimGUI(map_size)`). The GUI will then open in a new window
when :code:`instance.mainloop()` is called.

Some pros and cons of the GUI:

* Easy to visualise.

* Prevents the user from inputting invalid values.

* A bit clumsy when navigating from the simulation plot back to the GUI.

* Easy to use.

* Able to continue on the previous simulation (as well as add animals), or reset it.

* Possibility of specifying animal and landscape parameters.

* Not able to specify visualisation parameters.

* Able to navigate back and forth from drawing and simulating.

* Super fun!

.. raw:: html

   <iframe width="700" height="394" src="https://www.youtube.com/embed/1mKAqzywuL8" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>

To use the GUI, run the following code (and change :code:`map_size` to your liking):

.. literalinclude:: ../examples/example_with_gui.py
    :language: python

Example changing species' parameters:
-------------------------------------

Changing the species' parameters yield a different result. Here is an example changing a few of
the parameters.

.. image:: _static/images/example_different_parameters.png
   :width: 700px
   :align: center
   :class: bordered-image

.. literalinclude:: ../examples/example_different_parameters.py
    :language: python

Making a mp4 movie:
-------------------

Saves a movie in the specified directory (can be absolute or nonexisting). The movie is saved as
the specified filename, and is created using the saved images of the simulation.

.. literalinclude:: ../examples/example_save_movie.py
    :language: python
