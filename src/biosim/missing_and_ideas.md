I morgen:
=========
- hallvard
* mock fitness in death test? hunt??
* mock random.random -> 1 (100%)
* Lese gjennom og sjekke alle dockstrings.
* Spørre: vits å teste gui.py?
* Sortere metodene i klassene i riktig rekkefølge.
* Se på forelesningsnotater (2 av dem) om hva som vektlegges.
* Finne ut hva som feiler gitlab-ci
* log-file in simulation.py

- thyra
* test_biosim_interface.py
* spørsmål om setup.cfg eksempelfiler se kommentar
  * også om pytest i project requirements
* tox.ini
* legge alle tester in classer
* test_make_movie
* mock fitness in death test? hunt
* other flake8 tests
* Dele opp (sortere) testene i unittests, integraltests osv.?
* Ordne opp i .gitignore (du fjerna den i commit 11:45 fredag)
* Fikse setup.cfg
* Skrive hvordan installere pakken i dokumentasjonen (jeg kan gjøre det hvis du sier hva 
  "kommandoen" er).
---------------------------------------------------------------------------------------------------

Mangler:
========

examples
--------
* 

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

gui.py
------
* Relative imports "."

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
* DeltaPhiMax = 15 ? (Det brukte han i forelesningen)

island.py
---------
* 

GUI:
----
* Velge hist-specs osv.

---------------------------------------------------------------------------------------------------

Ideer:
======
* 

---------------------------------------------------------------------------------------------------

Tips:
=====

* Tester løper i "tilfeldig" rekkefølge.
  - husk å sette tilbake parametre hvis du endrer på dem i en test.
* bruk statistical tests på cases der alle carnivores eller alle herbivores dør
