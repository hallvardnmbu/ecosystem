Future ideas
============

The BioSim-package is a reasonably fresh project, and there are many features that are "missing".
The following list is comprised of a few of these features, that are planned to be implemented in
the future. Bear in mind that this project is a part of the INF200-course at NMBU, and that there
is a probability of discontinuation due to the uncertain future of the authors. Feel free,
however, to contact the authors if you wish to take over the project. So, if time was not of the
essence, the following features would be implemented:

Animals
-------

* Hiding.

May hide in the forest, behind rocks or dig down, to prevent being preyed on. This, in turn,
leads to different probabilities of death for the different species in the different cell types.

* Overpopulation.

Great possibility of death if there are more than X animals in the same cell.

* Sickness.

Animals may get sick occasionally. Also if they haven't eaten in a while.

* Evolution.

The parameters of a species may change. Say there are 10X Herbivores contra Carnivores; then the
Herbivores' parameters may change for the better.

* Gene manipulation.

There is a probability of gene manipulation (parameter change), that leads to balance/imbalance
in the population of the ecosystem.

* Movement.

Different species prefers different terrain types. The probability of migration is therefore
determined by these preferances, and animals generally move towards the terrains they prefer.

Cells
-----

* Vegetation.

The vegetation properties of a cell are determined by the cell type, and changes as the animals
eat, and the years pass. Different vegetation types are eaten by different species. For instance
may Herbivores eat the grass, while birds eat the berries in trees.

* Different cell types.

A variety of different cell types, with corresponding vegetation properties.

* The map is created using a wave-collapse-function.

Different cell-types may only be neighbors to certain other types. A cell of type "Mountain-peak"
may for instance not be directly next to "Desert" etc.

* Natural disasters.

There is a probability of natural disasters. For instance flooding, where all cells are briefly
turned to "Water" - then back again. Likewise, a drought may happen, and the vegetation grows
slower for a short while. Another probability is fire, where some of the neighboring cells are
turned to "Burnt" for a few years, until the vegetation grows back. A pandemic/meteor may
even strike, and kill everything!

Island
------

* Weather.

During a yearly cycle the weather changes. This, in turn, affects the vegetation on the island.

* Pack immunity.

If there for instance are 10X Herbivores (contra Carnivores) in a cell, they achieve pack
immunity, meaning that the Carnivores are unable to prey on them. Which in turn leads to a higher
probability of Carnivores dying.
