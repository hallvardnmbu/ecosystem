Mangler:
--------
    animals.py
    ----------
        * Relative imports "."
        * random.lognormvariate -> egen funksjon

    island.py
    ---------
        * Relative imports "."
        * Angi default "fodder" i hver celle (hvert år)
        * Sortere dyr etter fitness(?)
        * Fødsel: N is the number of animals of the same species in the cell at the start of the
          breeding season.
        * Migrasjon
        * Død (fjerne dyr)
        * Mat. Endre fodder parametre og få det til å funke for cellene og Island. (fra 
          classmethod til én og én)
        * Endre fra "if 'Herbivore'" osv. til type() [se forelesning 3].

    simulation.py
    -------------
        * Relative imports "."
        * Annual cycle

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

    GUI:
    ----
        * Tegne kartet
        * Plassere dyr på kartet

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