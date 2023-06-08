Mangler:
--------
    animals.py
    ----------
        * Relative imports "."

    island.py
    ---------
        * Fjerne "if ...": i hver annual cycle (for å sjekke om det er dyr i cellen).
        * Forbedre celle-oppsettet (forenkle for-løkkene).
        * Migrasjon
        * Død (fjerne dyr)
        * Fjerne @classmethod for default parameter-funksjonene?

    simulation.py
    -------------
        * Relative imports "."
        * Annual cycle

    /tests
    ------
        test_animals.py
        ---------------
            * Teste alle metodene

        test_island.py
        --------------
            * Teste alle metodene
            * Legge til dyr, teste at det blir lagt til riktig osv.
            * Sjekke at dyr blir lagt til i både Cell.herbivore/carnivore OG Cell.animals

    package structure
    ----------------
       * directory layout
       * configuration files
        - license maybe the MIT or the BSD license
        - readme.md
        - pyproject.toml
        - setup.cfg
        - setup.py


---------------------------------------------------------------------------------------------------

Kan forbedres:
--------------
    animals.py
    ----------
        * Forenkle default parameter-funksjonene(?)
        * "huske" ting i formler for å spare tid (mener å huske at det var noe som kunne gjøres)
        * Animal.species -> gjøre dette på en annen måte for å slippe dette?

    island.py
    ---------
        * Forbedre indeksering i celler (se f.eks. .add_population())
        * Forbedre .n_animals() (ha en egen variabel for å slippe å ha to for-løkker som blir +- 1
          ved __init__ og død)
        * Forbedre procreation
        * Generelt: forbedre celle-systemet.
        * Forbedre Cell.add_animal()
        * Gjøre det umulig å legge til "ugyldige" fager i .visualise()
        * Spare tid ved å ikke iterere gjennom vann
          - Bruke itertools

        * Island skal ikke "bruke" animals. Det skal skje i animals.
        * Flytte herbivore_eat_fodder og carnivore_eat_herbivore til animals.py (også andre metoder?)

    GUI:
    ----
        * Tegne kartet
        * Plassere dyr på kartet

    Endre if-testene. Lage metoder i klassene, som gjør dette lettere.
    ------------------------------------------------------------------
        island.py:
        ----------
            80: if self.terrain[location[0]-1][location[1]-1] == "W":
            156: if terrain[i][0] != "W" or terrain[i][Y-1] != "W"
            159: if terrain[0][j] != "W" or terrain[X-1][j] != "W":

---------------------------------------------------------------------------------------------------

Ideer:
------
    * Flyvende dyr (kan bevege seg over flere celler, også over vann)
    * Gjemme seg i skogen eller grave seg ned i ørkenen (kan ikke bli spist)
    * Herbivores kan drepe Carnivores HVIS: det er flere enn X Herbivores og mindre enn Y Carnivores
      i cellen
    * Dør av overpopulasjon (er vel på en måte sånn allerede, med at det ikke er nok mat?)
    * Dyr kan bli syke (og kan dø)
    * PANDEMI/METEOR! (alle dyr dør)


---------------------------------------------------------------------------------------------------

Tips:
-----
    * når dyr dør, ikke slett de fra listen mens du går gjennom den.
     gjør slik:

     keep the good ones

        d = list(range(10))

        d = [n for n in d if not (n % 2 == 0 or n % 3 == 0)]
        print(d)

   * Tester løper i "tilfeldig" rekkefølge.
        - husk å sette tilbake parapetre hvis duu endrer på dem i en test.

   * bruk statistical tests på cases der alle carnivores eller alle herbivores dør
