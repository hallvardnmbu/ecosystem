I morgen:
=========
- hallvard
* lage "film" som bruker GUI og simulerer
* Oppdatere GUI-gif på nettside.
* Lese gjennom oppgaveteksten og sjekke at alt er oppfylt.
* Til eksamen: plots (se mappe)
  * Sammenlikn vår sample_sim 1000. år med hans (så å si identisk!!! NICE.)

- thyra
* Er setup og det helt ferdig??? Viktigst.
  * Skrive hvordan installere pakken i dokumentasjonen (jeg kan gjøre det hvis du sier hva 
    "kommandoen" er).
  * Fikse setup.cfg
  * spørsmål om setup.cfg eksempelfiler se kommentar
  * også om pytest i project requirements
  * tox.ini
    * Når "tox" skrives i terminal failer så å si ALLE testene. Noe er feil.
* Ordne opp i .gitignore (du fjerna den i commit 11:45 fredag)
* Finne ut hva som feiler gitlab-ci
* legge alle tester in classer
* mock fitness in death test? hunt
* other flake8 tests
* test_biosim_interface.py (vi skal IKKE teste visualisering)
* test_make_movie (er nok ikke vits.)
* Dele opp (sortere) testene i unittests, integraltests osv.
* Integration tester:
  * integration test: checkerboard - statistical test
  * integration test: yearly cycle
  * integration test: death over flere år, får man en kurve som forventa?
  * integration test: birth, ca. antall prosent som forventa osv.?
  * osv. osv. osv.
  * Lag en del av disse, Thyra.
* Få 100% coverage i simulation.py

---------------------------------------------------------------------------------------------------

Exam evaluation:
================

Code 70%

* (Almost) all reference_tests/test_biosim_interface.py tests pass
* setup.cfg, setup.py, tox.ini, pyproject.toml in place, based on BioLab example
* Running tox runs your tests (even if some fail)
* All flake8 tests pass
* Good variable and method names
* "Dead code" removed
* More powerful tests (e.g. statistical tests)
* Optimized code
* Elegant solutions
* Additional features
* All code thoroughly tidied up
* Very well worked through docstrings

Delivery 20%
------------
* Does your code deliver on all requirements described in Sec. 1–3 of the task description?
* Your code runs "out of the box"
* Parameters for animals, landscapes and plotting can be set
* Packaging, so that python -m build and tox works

Quality 20%
-----------
* Have you followed the directory structure?
* Sensible organisation of code into classes?
* Well-chosen class and variable names?
* Is the encapsulation principle in object-oriented programming observed?
* Do you follow PEP8 rules (but with lines up to 100 characters allowed)? 

Tests 15%
---------
* Do you have unit tests for all methodes in classes for animals and landscape types?
* Do you have tests for the island and simulation classes?
* You do NOT need to write tests for visualisation.
* Are your tests meaningful and sufficiently comprehensive?
* Are the tests well written?
* Full score requires comprehensive tests including good use of 
  - Parameterization
  - Fixtures 
  - Statistical tests

Documentation 10%
-----------------
* Do you have documentation text describing the parts of BioSim and how to use them?
* Advanced Sphinx features
  - Math
  - Code
  - Figures

Bonus 5%
--------
* Extraordinarily well-written code

Exam 30%

Presentation 10%
-----------------
* Ability to present and explain your code 
  - Overall structure
  - What solutions you chose and why
  - Why your code is trustworthy
  - Whether you can substantiate your claims about your code

Discussion 20%
--------------
* Do you understand your own code?
* Are you aware of its limitations?
* Can you discuss improvements or extensions to your code?

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
