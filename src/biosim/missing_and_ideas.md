I morgen:
=========
- hallvard
* 

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

Til ekasmen:
============
* Se mappe "eksamen_bilder" sammenlikn med hans plots.
* Sammenlikne vår sample_sim 1000. år med han sin.
* Film (ligger i Exam-mappen)
* Profile check_sim og ha med i presentasjon
* Høyreklikk på biosim -> "Diagrams" -> "Show diagram"

---------------------------------------------------------------------------------------------------

Exam evaluation:
================

Code 70%

* setup.cfg, setup.py, tox.ini, pyproject.toml in place, based on BioLab example
* Running tox runs your tests (even if some fail)
* All flake8 tests pass
* "Dead code" removed
* More powerful tests (e.g. statistical tests)

Delivery 20%
------------
* Does your code deliver on all requirements described in Sec. 1–3 of the task description?
* Your code runs "out of the box"
* Packaging, so that python -m build and tox works

Quality 20%
-----------
* Do you follow PEP8 rules (but with lines up to 100 characters allowed)?
* correct directory layout
* configuration files
  - readme.md
  - tox.ini

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
* 

Bonus 5%
--------
* 

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

---------------------------------------------------------------------------------------------------

/tests
======

Kjør med coverage 'pytest --cov --cov-report term-missing', og dekk de viktigste linjene.
