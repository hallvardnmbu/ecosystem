I morgen:
=========
* test til ny funksjon i island
* mock fitness in death test? hunt??
* tox.ini
* save figure og save movie
* GUI (se under)
* readme.md

---------------------------------------------------------------------------------------------------

Mangler:
========

examples
--------
* Eksempler på hvordan å bruke BioSim (fyll inn de tre filene i mappe 'examples')

animals.py
----------
* Relative imports "."

island.py
---------
* Relative imports "."

simulation.py
-------------
* Relative imports "."

graphics.py
-----------
* Relative imports "."
* Save figure
* Make movie

---------------------------------------------------------------------------------------------------

/tests
======

Kjør med coverage 'pytest --cov --cov-report term-missing', og dekk de viktigste linjene.

test_animals.py
---------------
* Fikse de testene som ikke funker.

test_island.py
--------------
* Fikse de testene som ikke funker.

test_simulation.py
------------------
* Fikse de testene som ikke funker.

package structure
-----------------
* directory layout
* configuration files
  - readme.md
  - tox.ini

---------------------------------------------------------------------------------------------------

Kan forbedres:
==============

Sjekk 'run -> profile' for å se hva som tar lang tid (husk å fjerne plottingen)

animals.py
----------
* Forenkle default parameter-funksjonene(?)
* DeltaPhiMax = 15 ? (Det brukte han i forelesningen)

island.py
---------
* Island skal ikke "bruke" animals. Det skal skje i animals.
* "huske" hvilke celler som er vann for å ikke gå gjennom de, funker det bedre?
  - lagre i hver celle hvilke naboceller den kan flytte dyra inni til. kun sjekke en gang om 
    nabocelle er vann eller ikke

GUI:
----
* Tegne kartet
* Plassere dyr på kartet
* Simulere x år, velge hist-specs osv.

---------------------------------------------------------------------------------------------------

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
  -Altså at noen arter har større sannsynlighet for å bli spist i ulike habitat
* Herbivores kan drepe Carnivores HVIS: det er flere enn X Herbivores og mindre enn Y Carnivores
 i cellen
* Dør av overpopulasjon (er vel på en måte sånn allerede, med at det ikke er nok mat?)
* Dyr kan bli syke (og kan dø)
* PANDEMI/METEOR! (alle dyr dør)
  -for eksempel hvis for mange av en art er i en celle,
  -implementere at ved en liten sjanse kan det skje genmanipulasjon
    da kan vi se hvilke parametre som gir balansert økosystem
* flom eller tørke
* større sannsynlighet for å gå til lowland
* lav sannsynlighet for å gå til desert
* høy sannsynliget for å rømme fra carnivores hvis det er mange av de

---------------------------------------------------------------------------------------------------

Tips:
=====

* Tester løper i "tilfeldig" rekkefølge.
  - husk å sette tilbake parametre hvis du endrer på dem i en test.
* bruk statistical tests på cases der alle carnivores eller alle herbivores dør
