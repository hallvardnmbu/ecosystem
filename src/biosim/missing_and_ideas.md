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
* simulate() kjører ett år for mye?!
  -         plain_sim.simulate(num_years=2)
            assert plain_sim.year == 2
            assert 3 == 2 
* Hva skjer her?
  -         assert os.path.isfile(figfile_base + '_00000.png')
            AssertionError: assert False
             +  where False = <function isfile at 0x10d7abd80>(('figfileroot' + '_00000.png'))
             +    where <function isfile at 0x10d7abd80> = <module 'posixpath' (frozen)>.isfile
             +      where <module 'posixpath' (frozen)> = os.path 
* Rydde opp i "n_animals_..." i island.py

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

Exam evaluation:
================

Code 70%

* (Almost) all test_biosim_interface.py tests pass
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
