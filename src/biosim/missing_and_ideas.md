Mangler:
========

To make html
------------
* file and class docstrings
* do not commit build directory
   - only the "red" files
* advanced sphinxs features is appreciated
* add the math formulas (nicely formatted)
   - by a good sphinxs theme 
* Use NEST guide to write good documentation, see
  https://www.nest-simulator.readthedocs.io/en/latest/developer_space/guidelines/styleguide.html
* Formler:
     Bruke "r": raw string, for å kunne bruke backslash i latex-kode.
     - r"text here"
     - Dockstring
         """
         .. math::
            latex code
         """
       :math:`\frac{1}{2}`

Plotting pycharm
----------------
* call plot at the end of the simulation, don't call it 350 times!
  - call plot once and update data 350 times
    - see plot_update.py  
* fig.canas.flush_events()  # flush the GUI events
* plt.pause(1e-6)  # pause 1e-6 seconds
* counter with help from time_counter.py

animals.py
----------
* Relative imports "."

island.py
---------
* Relative imports "."

simulation.py
-------------
* Relative imports "."

  Og gjør det mulig å "fortsette" der du slapp (uten å begynne på nytt?)

visualisation.py
----------------
* Lage enkle visualiseringer for:
  - Antall år: teller
  - Herbivores sine posisjoner (heatmap)
  - Carnivores sine posisjoner (heatmap)
  - Fitness (histogram)
  - Age (histogram)
  - Weight (histogram)
* Sette sammen til én figur

---------------------------------------------------------------------------------------------------

/tests
======

test_animals.py
---------------
* Teste (de nye) eat-funksjonene.
* Fikse de testene som ikke funker.

test_island.py
--------------
* Fikse de testene som ikke funker.
* Legge til dyr, teste at det blir lagt til riktig osv.
* Sjekke at dyr blir lagt til i både Cell.herbivore/carnivore OG Cell.animals

package structure
----------------
* directory layout
* configuration files
  - readme.md
  - setup.cfg
    - Homepage for package and specific URLs
  - tox.ini

---------------------------------------------------------------------------------------------------

Kan forbedres:
==============
animals.py
----------
* Forenkle default parameter-funksjonene(?)

* DeltaPhiMax = 15 ? (Det brukte han i forelesningen)

island.py
---------
* Island skal ikke "bruke" animals. Det skal skje i animals.

GUI:
----
* Tegne kartet
* Plassere dyr på kartet

Endre if-testene. Lage metoder i klassene, som gjør dette lettere:
==================================================================

island.py:
----------
* 80: if self.terrain[location[0]-1][location[1]-1] == "W":
* 156: if terrain[i][0] != "W" or terrain[i][Y-1] != "W"
* 159: if terrain[0][j] != "W" or terrain[X-1][j] != "W":

---------------------------------------------------------------------------------------------------

Ideer:
======
* Gjemme seg i skogen eller grave seg ned i ørkenen (kan ikke bli spist)
* Herbivores kan drepe Carnivores HVIS: det er flere enn X Herbivores og mindre enn Y Carnivores
 i cellen
* Dør av overpopulasjon (er vel på en måte sånn allerede, med at det ikke er nok mat?)
* Dyr kan bli syke (og kan dø)
* PANDEMI/METEOR! (alle dyr dør)


---------------------------------------------------------------------------------------------------

Tips:
=====
* når dyr dør, ikke slett de fra listen mens du går gjennom den.
  - gjør slik:

       keep the good ones

          d = list(range(10))

          d = [n for n in d if not (n % 2 == 0 or n % 3 == 0)]
          print(d)

* Tester løper i "tilfeldig" rekkefølge.
  - husk å sette tilbake parapetre hvis duu endrer på dem i en test.
* bruk statistical tests på cases der alle carnivores eller alle herbivores dør
