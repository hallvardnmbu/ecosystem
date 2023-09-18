"""
Improved graphical user interface for BioSim.

Copyright (c) 2023 Hallvard Høyland Lavik / NMBU
This file is part of the BioSim-package, adding a more intuitive GUI.
Released under the MIT License, see included LICENSE file.
"""


import sys
import datetime
from PyQt5.QtCore import Qt, QRect, QRectF, QMimeData, QSize
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QDrag, QPixmap
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QApplication, QWidget,
                             QHBoxLayout, QVBoxLayout, QGroupBox,
                             QLabel, QPushButton, QComboBox, QSlider,
                             QGraphicsView, QGraphicsScene,
                             QMessageBox, QTableWidget, QTableWidgetItem,
                             QGraphicsPixmapItem, QInputDialog)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from .simulation import BioSim
from .animals import Herbivore, Carnivore
from .island import Island


VARIABLE = {"island": ["W" * 21 for _ in range(21)],
            "selected": [(None, None), None, "R-selected"],
            "biosim": None,
            "colours": {"W": "#95CBCC",
                        "H": "#E8EC9E",
                        "L": "#B9D687",
                        "M": "#808080"},
            "parameters": {"Herbivore": Herbivore.default_parameters(),
                           "Carnivore": Carnivore.default_parameters(),
                           "rename": {"Highland": "H",
                                      "Lowland": "L",
                                      "Mountain": "M",
                                      "Water": "W",
                                      "Growth reduction (alpha)": "alpha",
                                      "Growth factor (v_max)": "v_max"}},
            "modified": {},
            "history": {},
            "selection": {
                "Herbivore": {
                    "R-selected": {
                        "w_birth": 10,  # Babyvekt ~ 2.6 kg
                        "sigma_birth": 4,
                        "zeta": 0.22,  # Barn hvis vekt > 3.08 kg
                        "xi": 0.42,  # Mister ~ 1.1 kg ved fødsel.
                        "gamma": 0.9,  # Føder med p = fitness * gamma.
                        "F": 20,  # Appetitt.
                        "beta": 0.05,  # Vektøkning ved mat ~ 1 kg.
                        "eta": 0.2,  # Mister 10% av vekten per år.

                        "phi_age": 5,  # Levetid ~ 5 år. Fitness synker.
                        "a_half": 2.5,
                        "phi_weight": 0.09,
                        "w_half": 3,

                        "mu": 17,  # Høy spredningsevne.
                        "omega": 0.4
                    },
                    "K-selected": {
                        "w_birth": 10,  # Babyvekt ~ 280.0 kg
                        "sigma_birth": 0.03,
                        "zeta": 35,  # Barn hvis vekt > 350 kg
                        "xi": 0.3,  # Mister ~ 84 kg ved fødsel.
                        "gamma": 1.2,  # Føder med p = fitness * gamma.
                        "F": 75,  # Appetitt.
                        "beta": 2,  # Vektøkning ved mat ~ 150 kg.
                        "eta": 0.05,  # Mister 5% av vekten per år.

                        "phi_age": 0.1,  # Fitness.
                        "a_half": 14,
                        "phi_weight": 0.4,
                        "w_half": 2,

                        "mu": 5,  # Spredningsevne.
                        "omega": 0.09  # Lav dødelighet (lever lenger).
                    }
                },
                "Carnivore": {
                    "R-selected": {
                        "beta": 0.75,  # Vektøkning ved mat ~ 1.95 kg.
                        "omega": 0.8,  # Høy dødelighet.
                        "DeltaPhiMax": 10,  # Høy aggressivitet.
                        "F": 50  # Appetitt.
                    },
                    "K-selected": {
                        "beta": 0.09,  # Vektøkning ved mat ~ 108 kg.
                        "omega": 0.25,  # Lav dødelighet.
                        "DeltaPhiMax": 10,
                        "F": 1200,  # Appetitt.
                        "phi_weight": 7
                    }
                }
            },
            "dir": str(sys._MEIPASS) if getattr(sys, 'frozen', False) else "src/biosim/static"}

VARIABLE["parameters"]["Herbivore"].update({"Movement": Herbivore.default_motion()})
VARIABLE["parameters"]["Carnivore"].update({"Movement": Carnivore.default_motion()})
VARIABLE["parameters"]["Fodder"] = {{v: k for k, v
                                     in VARIABLE["parameters"]["rename"].items()}.get(k, k): v
                                    for k, v in Island.default_fodder_parameters().items()}


class BioSimGUI:
    """Class for the graphical user interface."""
    def __init__(self):
        """
        Initialises and starts the application.

        Notes
        -----
        This is made to a class in order to have be visually pleasing (capital letters) without
        "raising" an error.
        """
        Herbivore.set_parameters(Herbivore.default_parameters())
        Carnivore.set_parameters(Carnivore.default_parameters())

        app = QApplication([])
        window = Main()
        window.show()
        app.exec_()

    @staticmethod
    def shrink(island):
        """
        Shrink the edges of the island to the minimum possible border (if not all cells are water).
        This is done by first transposing the island, then removing the top and bottom rows if they
        are only water, and finally transposing the island back to its original orientation and
        doing the same steps again. The island is then expanded to a square by adding water to
        the top and bottom or left and right an equal amount of times at each side until it is a
        square.

        Parameters
        ----------
        island : list

        Returns
        -------
        island : list
        """
        if all(cell == "W" for row in island for cell in row):
            return island
        for _ in range(2):
            # Since transposing is done twice, it will be back to its original when returned.
            island = [''.join(row) for row in zip(*island)]

            # Remove top row(s) if it is only water.
            i = 0
            while (all(cell == "W" for cell in island[i]) and
                   all(cell == "W" for cell in island[i+1])):
                island = island[1:]

            # Remove bottom row(s) if it is only water.
            j = len(island) - 1
            while (all(cell == "W" for cell in island[j]) and
                   all(cell == "W" for cell in island[j-1])):
                island = island[:-1]
                j -= 1

        rows = len(island)
        cols = len(island[0])
        if rows < cols:
            i = 1
            while rows < cols:
                if i % 2 == 0:
                    island.append("W" * cols)
                else:
                    island = ["W" * cols] + island
                i += 1
                rows += 1
        elif cols < rows:
            j = 1
            while cols < rows:
                if j % 2 == 0:
                    island = ["W" + row for row in island]
                else:
                    island = [row + "W" for row in island]
                j += 1
                cols += 1

        return island

    @staticmethod
    def restart():
        """Restart the simulation."""
        VARIABLE["island"] = BioSimGUI.shrink(VARIABLE["island"])
        geogr = "\n".join(VARIABLE["island"])
        try:
            VARIABLE["biosim"].graphics.reset_graphics()
        except (AttributeError, KeyError):
            pass
        VARIABLE["biosim"] = BioSim(island_map=geogr)
        Herbivore.set_parameters(VARIABLE["selection"]["Herbivore"]["R-selected"])
        Carnivore.set_parameters(VARIABLE["selection"]["Carnivore"]["R-selected"])
        VARIABLE["selected"] = [(None, None), None, "R-selected"]
        VARIABLE["history"].clear()


class Main(QMainWindow):
    """Class for the main window."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 820)
        self.setWindowTitle("Model herbivores and carnivores on an island")

        # Create the tabs:
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Draw:
        draw_widget = QWidget()
        draw_layout = QVBoxLayout()
        draw_widget.setLayout(draw_layout)

        self.draw = Draw()
        draw_layout.addWidget(self.draw)
        self.tabs.addTab(self.draw, 'Draw')

        # Populate:
        populate_widget = QWidget()
        populate_layout = QVBoxLayout()
        populate_widget.setLayout(populate_layout)

        self.populate = Populate()
        populate_layout.addWidget(self.populate)
        self.tabs.addTab(self.populate, 'Populate')

        # Simulate:
        simulate_widget = QWidget()
        simulate_layout = QVBoxLayout()
        simulate_widget.setLayout(simulate_layout)

        self.simulate = Simulate()
        simulate_layout.addWidget(self.simulate)
        self.tabs.addTab(self.simulate, 'Simulate')

        # History:
        history_widget = QWidget()
        history_layout = QVBoxLayout()
        history_widget.setLayout(history_layout)

        self.history = History()
        history_layout.addWidget(self.history)
        self.tabs.addTab(self.history, 'History')

        # Advanced:
        advanced_widget = QWidget()
        advanced_layout = QVBoxLayout()
        advanced_widget.setLayout(advanced_layout)

        self.advanced = Advanced()
        advanced_layout.addWidget(self.advanced)
        self.tabs.addTab(self.advanced, 'Advanced settings')

        self.previous = 0
        self.tabs.currentChanged.connect(self.change)

    def change(self, index):
        """Switching to new tabs executes the following."""
        if index == 0:  # Switching to draw page.
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Warning)
            msg_box.setText(
                "Are you sure you want to switch to the draw page? This will reset everything."
            )
            msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg_box.setDefaultButton(QMessageBox.Cancel)
            result = msg_box.exec_()
            if result == QMessageBox.Cancel:
                self.tabs.setCurrentIndex(self.previous)
                return

            self.simulate.reset()
            VARIABLE["modified"].clear()
            VARIABLE["history"].clear()
            VARIABLE["island"] = ["W" * 21 for _ in range(21)]
            self.draw.plot.update()
        elif index == 1:  # Switching to populate page.
            self.populate.plot.update()
        elif index == 2:  # Switching to simulate page.
            try:
                VARIABLE["biosim"].should_stop = False
            except AttributeError:
                pass
        elif index == 3:  # Switching to history page.
            self.history.update()
        elif index == 4:  # Switching to advanced page.
            self.advanced.update()
        if self.previous == 0 and index != 0:  # Switching from draw page.
            BioSimGUI.restart()
            self.populate.plot.update()
        elif self.previous == 2 and index != 2:
            self.simulate.stop()
            self.history.update()

        self.previous = index


class Draw(QWidget):
    """Class for drawing the island."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setWindowTitle("Model herbivores and carnivores on an island")

        self.layout = QHBoxLayout()

        self.plot = Map()
        self.plot.setGeometry(QRect(0, 0, 800, 800))
        self.layout.addWidget(self.plot)

        self.selection = []

        self.buttons()
        self.plot.update()

        self.setLayout(self.layout)

    def buttons(self):
        """Add buttons to the window."""
        buttons = QVBoxLayout()

        bigger_button = QPushButton("Bigger")
        bigger_button.setFixedSize(120, 120)
        bigger_button.setStyleSheet("background-color: #FBFAF5; color: black;")
        bigger_button.clicked.connect(self.bigger)

        smaller_button = QPushButton("Smaller")
        smaller_button.setFixedSize(120, 120)
        smaller_button.setStyleSheet("background-color: #FBFAF5; color: black;")
        smaller_button.clicked.connect(self.smaller)

        buttons.addWidget(bigger_button)
        buttons.addSpacing(5)
        buttons.addWidget(smaller_button)
        buttons.addStretch(1)

        # Select terrain type:
        color_map = {"W": "Water", "H": "Highland", "L": "Lowland", "M": "Mountain"}
        for name, color in VARIABLE["colours"].items():
            button = QPushButton(color_map[name])
            button.setFixedSize(120, 120)
            button.setStyleSheet(f"background-color: {color}; color: black;")
            button.clicked.connect(lambda _, name=name: self.color_clicked(name))
            buttons.addWidget(button)
            buttons.addSpacing(5)
            self.selection.append(button)

        buttons.setAlignment(Qt.AlignCenter)
        self.layout.addLayout(buttons)

    def color_clicked(self, name):
        """
        Change the selected terrain type.

        Parameters
        ----------
        name : str
        """
        self.plot.terrain = name[0]
        for button in self.selection:
            if button.text()[0] == name:
                button.setStyleSheet(
                    f"background-color: {VARIABLE['colours'][name[0]]}; color: black; "
                    f"border: 2px solid black"
                )
            else:
                button.setStyleSheet(
                    f"background-color: {VARIABLE['colours'][button.text()[0]]}; color: black;"
                )

    def bigger(self):
        """Increase the size of the map."""
        if len(VARIABLE["island"][0]) >= 44:
            return

        new = ["W" * (len(VARIABLE["island"][0]) + 2)]
        for row in VARIABLE["island"]:
            _row = "W" + row + "W"
            new.append(_row)
        new.append("W" * (len(VARIABLE["island"][0]) + 2))

        VARIABLE["island"] = new
        self.plot.update()

    def smaller(self):
        """Decrease the size of the map."""
        if len(VARIABLE["island"][0]) <= 4:
            return

        new = ["W" * (len(VARIABLE["island"][0]) - 2)]
        for row in VARIABLE["island"][2:-2]:
            _row = "W" + row[2:-2] + "W"
            new.append(_row)
        new.append("W" * (len(VARIABLE["island"][0]) - 2))

        VARIABLE["island"] = new
        self.plot.update()


class Map(QGraphicsView):
    """
    Class for visualising the island.

    Parameters
    ----------
    terrain : str, optional
        Currently selected terrain type.
    drawing : bool, optional
        Whether the map can be drawn on or not.
    """
    def __init__(self, terrain="W", drawing=True):
        super().__init__()

        self.terrain = terrain
        self.drawing = drawing
        self.size = 100

        self.scene = QGraphicsScene(self)
        self.scene.setBackgroundBrush(QBrush(QColor(VARIABLE['colours']["W"])))
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setFixedSize(800, 800)

        if self.drawing:
            self.setCursor(Qt.CrossCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
            self.setAcceptDrops(True)

    def update(self):
        """Update the scene."""
        self.scene.clear()
        pen = QPen(Qt.NoPen)
        for j, row in enumerate(VARIABLE["island"]):
            for i, cell in enumerate(row):
                brush = QBrush(QColor(VARIABLE['colours'][cell]))
                rect = QRectF(i * self.size, j * self.size, self.size, self.size)
                self.scene.addRect(rect, pen, brush)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def resizeEvent(self, event):
        """Resizes the plot to fit within the scene."""
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        """Executed when the mouse is pressed."""
        if self.drawing:
            self.mouseMoveEvent(event)
            return

        # Handles selection of cell when populating the island.
        if event.buttons() == Qt.LeftButton and self.terrain == "SELECT":
            position = self.mapToScene(event.pos())
            i = int(position.x() // self.size)
            j = int(position.y() // self.size)

            if VARIABLE["island"][j][i] != "W":
                selected = VARIABLE["selected"][1]
                if selected is None:
                    msg = QMessageBox()
                    msg.setText("Please select a species by clicking or drag-dropping to the map.")
                    msg.exec_()
                    return

                image = QPixmap(VARIABLE["dir"] + f"/{selected}.jpg").scaled(self.size, self.size)

                item = QGraphicsPixmapItem(image)
                item.setPos(i * self.size, j * self.size)
                self.scene.addItem(item)

                VARIABLE["selected"][0] = (i, j)

                num_animals, ok = QInputDialog.getInt(self, "Number of Animals",
                                                      "How many?",
                                                      1, 1, 1000)
                if ok:
                    VARIABLE["selected"][2] = num_animals
                    Populate.populate()
                else:
                    VARIABLE["selected"][2] = None
            else:
                msg = QMessageBox()
                msg.setText("Cannot place animals in water.")
                msg.exec_()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        """Prevents warning message when dragged into map and then out again."""
        return

    def dragMoveEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            position = self.mapToScene(event.pos())
            i = int(position.x() // self.size)
            j = int(position.y() // self.size)

            if VARIABLE["island"][j][i] != "W":
                selected = event.mimeData().text()
                image = QPixmap(VARIABLE["dir"] + f"/{selected}.jpg").scaled(self.size, self.size)

                item = QGraphicsPixmapItem(image)
                item.setPos(i * self.size, j * self.size)
                self.scene.addItem(item)

                VARIABLE["selected"] = [(i, j), event.mimeData().text(), "R-selected"]

                num_animals, ok = QInputDialog.getInt(self, "Number of Animals",
                                                      "How many?",
                                                      1, 1, 1000)
                if ok:
                    VARIABLE["selected"][2] = num_animals
                    Populate.populate()
                else:
                    VARIABLE["selected"][2] = None
            else:
                msg = QMessageBox()
                msg.setText("Cannot place animals in water.")
                msg.exec_()

    def mouseMoveEvent(self, event):
        """Executed when the mouse is pressed-moved."""
        if event.buttons() == Qt.LeftButton and self.drawing:
            position = self.mapToScene(event.pos())
            i = int(position.x() // self.size)
            j = int(position.y() // self.size)

            if 0 < i < len(VARIABLE["island"][0])-1 and 0 < j < len(VARIABLE["island"])-1:
                VARIABLE["island"][j] = (VARIABLE["island"][j][:i] +
                                         self.terrain +
                                         VARIABLE["island"][j][i + 1:])

                pen = QPen(Qt.NoPen)
                self.scene.addRect(
                    i * self.size, j * self.size,
                    self.size, self.size,
                    pen, QBrush(QColor(VARIABLE['colours'][self.terrain]))
                )


class Species(QLabel):
    """
    Class for representing a species that can be dragged and dropped onto the map.

    Parameters
    ----------
    pixmap : QPixmap
        The pixmap to display for the species.
    species : str
    """
    selected = None

    def __init__(self, pixmap, species):
        super().__init__()

        self.pixmap = pixmap

        self.setPixmap(pixmap.scaled(QSize(200, 200), Qt.KeepAspectRatio))
        self.setFixedSize(180, 180)
        self.setScaledContents(True)
        self.setAcceptDrops(True)
        self.setStyleSheet("background-color: white;")

        # Define the size attribute.
        self.size = 10
        self.species = species

    def mousePressEvent(self, event):
        """Handles the mouse press event."""
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.species)
            mime_data.setImageData(self.pixmap.toImage())
            drag.setPixmap(self.pixmap.scaled(QSize(100, 100), Qt.KeepAspectRatio))
            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction)

            if Species.selected is not None:
                Species.selected.setStyleSheet("")

            Species.selected = self
            self.setStyleSheet("border: 4px solid #a4ab90")

            VARIABLE["selected"][1] = self.species

    def mouseMoveEvent(self, event):
        """Handles the mouse move event."""
        if event.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime_data = QMimeData()
            mime_data.setText(self.species)
            mime_data.setImageData(self.pixmap.toImage())
            drag.setMimeData(mime_data)
            drag.setPixmap(self.pixmap.scaled(QSize(100, 100), Qt.KeepAspectRatio))
            drag.exec_(Qt.CopyAction)

            self.setStyleSheet("")


class Populate(QWidget):
    """Class for populating the island."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setWindowTitle("Model herbivores and carnivores on an island")

        self.plot = None
        self.buttons = []

        self.initialise()

    def initialise(self):
        """Initialise the window."""
        layout = QHBoxLayout()

        # Creating the map.
        self.plot = Map(drawing=False, terrain="SELECT")
        self.plot.setGeometry(QRect(0, 0, 800, 800))
        layout.addWidget(self.plot)

        # Creating the input boxes.
        specifications = QVBoxLayout()
        top = QVBoxLayout()
        bottom = QVBoxLayout()

        # Species selection.
        species = QGroupBox()
        _species = QVBoxLayout()
        species.setLayout(_species)
        herbivore = Species(QPixmap(VARIABLE["dir"] + "/Herbivore.jpg"), "Herbivore")
        carnivore = Species(QPixmap(VARIABLE["dir"] + "/Carnivore.jpg"), "Carnivore")
        _species.addWidget(herbivore)
        _species.addWidget(carnivore)
        _species.setAlignment(Qt.AlignHCenter)

        top.addWidget(species)

        # R- and K-selected herbivore buttons.
        selection = QHBoxLayout()
        for name in ["R-selected", "K-selected"]:
            button = QPushButton(name)
            button.setFixedSize(95, 95)
            button.setStyleSheet("background-color: #FBFAF5; color: black;")
            button.clicked.connect(lambda _, name=name: self.selection(name))
            selection.addWidget(button)
            if name == "R-selected":
                selection.addSpacing(10)
            self.buttons.append(button)

        bottom.addLayout(selection)

        # Reset button.
        reset = QHBoxLayout()
        _reset = QPushButton("Slaughter population")
        _reset.setFixedSize(200, 100)
        _reset.setStyleSheet("background-color: #FBFAF5; color: black;")
        _reset.clicked.connect(self.reset)
        reset.addWidget(_reset)

        bottom.addLayout(reset)

        top.setAlignment((Qt.AlignHCenter | Qt.AlignTop))
        specifications.addLayout(top)
        specifications.addSpacing(10)
        bottom.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
        specifications.addLayout(bottom)
        layout.addLayout(specifications)

        self.setLayout(layout)
        self.selection("R-selected")

    def selection(self, name):
        """
        Executed when the selection changes.

        Parameters
        ----------
        name : str
            Text of the button that was clicked.
        """
        for button in self.buttons:
            if button.text() == name:
                button.setStyleSheet("background-color: #B7BFA1; color: black; "
                                     "border: 4px solid #a4ab90")
            else:
                button.setStyleSheet("background-color: #FBFAF5; color: black;")
        VARIABLE["history"].clear()
        VARIABLE["selected"][2] = name

        try:
            if VARIABLE["biosim"].island.year != 0:
                BioSimGUI.restart()

                hist_spec = {"K-selected": {'age': {'max': 45, 'delta': 5},
                                            'weight': {'max': 300, 'delta': 20},
                                            'fitness': {'max': 1, 'delta': 0.1}},
                             "R-selected": {'age': {'max': 45, 'delta': 5},
                                            'weight': {'max': 60, 'delta': 5},
                                            'fitness': {'max': 1, 'delta': 0.1}}}
                VARIABLE["biosim"].graphics.hist_specs = hist_spec[name]

                msg = QMessageBox()
                msg.setText("Simulation and population has been reset.")
                msg.exec_()

        except AttributeError:
            pass

        Herbivore.set_parameters(VARIABLE["selection"]["Herbivore"][name])
        Carnivore.set_parameters(VARIABLE["selection"]["Carnivore"][name])

    @staticmethod
    def populate():
        """Populate the island with animals."""
        j, i = VARIABLE["selected"][0]

        if i is None or j is None:
            msg = QMessageBox()
            msg.setText("Please select a cell by clicking on the map or drag-dropping an animal.")
            msg.exec_()
            return

        species = VARIABLE["selected"][1]
        if species is None:
            msg = QMessageBox()
            msg.setText("Please select a species by clicking or drag-dropping to the map.")
            msg.exec_()
            return

        age = 0
        weight = None
        amount = VARIABLE["selected"][2] if VARIABLE["selected"][2] is not None else 1

        animals = [{
            "loc": (int(i) + 1, int(j) + 1),
            "pop": [{"species": species,
                     "age": age,
                     "weight": weight} for _ in range(amount)]}]

        VARIABLE["biosim"].add_population(animals)

    @staticmethod
    def reset():
        """Reset the population on the island."""
        VARIABLE["biosim"].island.slaughter()


class Simulate(QWidget):
    """Class for simulating the population on the island."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setLayout(QVBoxLayout())

        self.fig = None
        self.canvas = None

        self.years = None
        self.year = None

        self.simulation()
        self.plot()

    def simulation(self):
        """Add simulation selection to the window."""
        self.years = QSlider(Qt.Horizontal)
        self.years.setMinimum(1)
        self.years.setMaximum(1000)
        self.years.setValue(100)
        self.years.valueChanged.connect(self._years)
        self.years.setFixedWidth(200)
        self.year = QLabel()
        self.year.setFixedWidth(40)
        self._years()

        simulate_button = QPushButton("Simulate")
        simulate_button.clicked.connect(self.simulate)

        pause = QPushButton("Pause")
        pause.clicked.connect(self.stop)

        faster = QPushButton("Faster")
        faster.clicked.connect(self.faster)

        slower = QPushButton("Slower")
        slower.clicked.connect(self.slower)

        reset = QPushButton("Reset iteration count")
        reset.clicked.connect(self.restart_years)
        reset.setFixedWidth(200)

        simulation = QHBoxLayout()
        simulation.addWidget(QLabel("Iterations to simulate:"))
        simulation.addWidget(self.years)
        simulation.addWidget(self.year)
        simulation.addWidget(simulate_button)
        simulation.addWidget(pause)
        simulation.addWidget(faster)
        simulation.addWidget(slower)
        simulation.addSpacing(100)
        simulation.addWidget(reset)
        self.layout().addLayout(simulation)

    def _years(self):
        """Executed when the number of years to simulate changes."""
        self.year.setText(str(self.years.value()))

    def plot(self):
        """Plot the population on the island."""
        self.fig = plt.Figure(figsize=(15, 10))

        self.canvas = FigureCanvas(self.fig)
        self.layout().addWidget(self.canvas)

    @staticmethod
    def restart_years():
        """Clears the population list."""
        Simulate.stop()
        VARIABLE["biosim"].island.year = 0
        VARIABLE["biosim"].graphics.reset_counts()
        VARIABLE["history"] = {"Herbivore": {"Age": [],
                                             "Weight": [],
                                             "Fitness": []},
                               "Carnivore": {"Age": [],
                                             "Weight": [],
                                             "Fitness": []}}
        VARIABLE["biosim"].history = VARIABLE["history"]

    def simulate(self):
        """
        Simulates the population on the map for the given number of years.

        Raises
        ------
        ValueError
            If number of years to simulate has not been specified.
        """
        years = int(self.years.value())
        VARIABLE["biosim"].should_stop = False

        VARIABLE["history"] = VARIABLE["biosim"].simulate(years,
                                                          figure=self.fig, canvas=self.canvas,
                                                          history=True)

    @staticmethod
    def stop():
        """Stops the simulation."""
        VARIABLE["biosim"].should_stop = True

    @staticmethod
    def faster():
        """Increase plot update speed."""
        try:
            VARIABLE["biosim"].graphics._speed /= 2
        except TypeError:
            return

    @staticmethod
    def slower():
        """Decrease plot update speed."""
        try:
            VARIABLE["biosim"].graphics._speed *= 2
        except TypeError:
            return

    def reset(self):
        """Reset the simulation."""
        VARIABLE["biosim"].island.year = 0
        VARIABLE["history"] = {"Herbivore": {"Age": [],
                                             "Weight": [],
                                             "Fitness": []},
                               "Carnivore": {"Age": [],
                                             "Weight": [],
                                             "Fitness": []}}
        self.fig.clear()


class History(QWidget):
    """Class for visualising the history."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setLayout(QVBoxLayout())

        self.fig = plt.Figure(figsize=(15, 10))
        self.canvas = FigureCanvas(self.fig)
        self.layout().addWidget(self.canvas)

    def update(self):
        """Updates the graphics."""
        self.fig.clear()
        self.plot()

    def plot(self):
        """Plot the history."""
        year = VARIABLE["biosim"].island.year if VARIABLE["biosim"] else None
        if year is None:
            return

        self.fig.clear()
        try:
            years = [year for year in range(len(VARIABLE["history"]["Herbivore"]["Age"]))]
        except KeyError:
            return

        old = self.fig.add_subplot(311)
        thick = self.fig.add_subplot(312)
        fit = self.fig.add_subplot(313)

        # set the titles of the subplots
        old.set_title("Age")
        thick.set_title("Weight")
        fit.set_title("Fitness")

        old.plot(years, VARIABLE["history"]["Herbivore"]["Age"],
                 label="Herbivore", color=(0.71764, 0.749, 0.63137))
        old.plot(years, VARIABLE["history"]["Carnivore"]["Age"],
                 label="Carnivore", color=(0.949, 0.7647, 0.56078))
        old.legend()
        old.set_xticks([])

        thick.plot(years, VARIABLE["history"]["Herbivore"]["Weight"],
                   color=(0.71764, 0.749, 0.63137))
        thick.plot(years, VARIABLE["history"]["Carnivore"]["Weight"],
                   color=(0.949, 0.7647, 0.56078))
        thick.set_ylabel("Mean value")
        thick.set_xticks([])

        fit.plot(years, VARIABLE["history"]["Herbivore"]["Fitness"],
                 color=(0.71764, 0.749, 0.63137))
        fit.plot(years, VARIABLE["history"]["Carnivore"]["Fitness"],
                 color=(0.949, 0.7647, 0.56078))
        fit.set_xlabel("Iteration")

        self.canvas.draw()


class Advanced(QWidget):
    """Class for visualising the advanced settings."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setLayout(QVBoxLayout())

        self.species = None
        self.parameter = None
        self.movement = None
        self.movement_value = None
        self.value = None
        self.label = None
        self.interval = None
        self.values = {
            "w_birth": (0, 20, 0.1),
            "sigma_birth": (0, 10, 0.01),
            "beta": (0, 5, 0.01),
            "eta": (0, 3, 0.01),
            "a_half": (0, 80, 0.5),
            "phi_age": (0, 10, 0.001),
            "w_half": (0, 20, 1),
            "phi_weight": (0, 10, 0.001),
            "mu": (0, 20, 0.1),
            "gamma": (0, 3, 0.1),
            "zeta": (0, 40, 0.1),
            "xi": (0, 3, 0.1),
            "omega": (0, 1.5, 0.01),
            "F": (0, 100, 5),
            "DeltaPhiMax": (0.1, 100, 0.1),
            "Highland": (0, 1000, 10),
            "H": (0, 1, 1),
            "Lowland": (0, 1000, 10),
            "L": (0, 1, 1),
            "Mountain": (0, 1000, 10),
            "M": (0, 1, 1),
            "Water": (0, 1000, 10),
            "W": (0, 1, 1),
            "Stride": (0, len(VARIABLE["island"]), 1),
            "Growth reduction (alpha)": (0, 1, 0.01),
            "Growth factor (v_max)": (0, 1500, 10)
        }

        self.top = QHBoxLayout()
        self.bottom = QHBoxLayout()

        self.parameters()
        self._parameter()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Time", "Species", "Parameter", "Value"])
        self.bottom.addWidget(self.table)

        reset = QPushButton("Clear history")
        reset.clicked.connect(self.reset)
        reset.setFixedWidth(200)
        self.bottom.addWidget(reset)

        self.layout().addLayout(self.top)
        self.layout().addLayout(self.bottom)

        self.update()

    def update(self):
        """Update the window."""
        self.table.setRowCount(len(VARIABLE["modified"]))
        for row, (time, (species, parameter, value)) in enumerate(
                sorted(VARIABLE["modified"].items(), reverse=True)):
            time_item = QTableWidgetItem(time.split()[0])
            species_item = QTableWidgetItem(species)
            parameter_item = QTableWidgetItem(parameter)
            value_item = QTableWidgetItem(str(value))
            self.table.setItem(row, 0, time_item)
            self.table.setItem(row, 1, species_item)
            self.table.setItem(row, 2, parameter_item)
            self.table.setItem(row, 3, value_item)

    def parameters(self):
        """Add parameter selection to the window."""
        self.species = QComboBox()
        self.species.addItems(["Herbivore", "Carnivore", "Fodder"])
        self.species.currentIndexChanged.connect(self._species)

        self.parameter = QComboBox()
        self.parameter.currentIndexChanged.connect(self._parameter)

        self.movement = QComboBox()
        self.movement.addItems(["Stride", "Highland", "Lowland", "Mountain", "Water"])
        self.movement.currentIndexChanged.connect(self._movement)
        self.movement.setVisible(False)
        self.movement_value = QSlider(Qt.Horizontal)
        self.movement_value.valueChanged.connect(self._value)
        self.movement_value.setVisible(False)

        self.value = QSlider(Qt.Horizontal)
        self.value.valueChanged.connect(self._value)
        self.label = QLabel()

        add = QPushButton("Set parameter")
        add.clicked.connect(self.set_parameter)
        add.setFixedWidth(140)

        reset_parameter = QPushButton("Reset parameter")
        reset_parameter.clicked.connect(self.reset_parameter)
        reset_parameter.setFixedWidth(140)

        reset_all_parameters = QPushButton("Reset all")
        reset_all_parameters.clicked.connect(self.reset_all_parameters)
        reset_all_parameters.setFixedWidth(200)

        parameters = QHBoxLayout()
        parameters.addWidget(self.species)
        parameters.addWidget(self.parameter)
        parameters.addWidget(self.movement)
        parameters.addWidget(self.movement_value)
        parameters.addWidget(self.value)
        parameters.addWidget(self.label)
        parameters.addWidget(add)
        parameters.addWidget(reset_parameter)
        parameters.addSpacing(100)
        parameters.addWidget(reset_all_parameters)
        self.top.addLayout(parameters)

        self._species()

    def _species(self):
        """Executed when the species selection changes."""
        species = self.species.currentText()
        self.parameter.clear()
        self.parameter.addItems(VARIABLE["parameters"][species].keys())

        self._parameter()

    def _parameter(self):
        """Executed when the parameter selection changes."""
        parameter = self.parameter.currentText()
        if parameter == "":
            # This check is needed because the function is called when the species is changed,
            # before the new species is 'selected'.
            return

        species = self.species.currentText()

        if parameter == "Movement":
            self.value.setVisible(False)
            self.movement.setVisible(True)
            self.movement_value.setVisible(True)

            self._movement()
            return

        self.movement.setVisible(False)
        self.movement_value.setVisible(False)
        self.value.setVisible(True)

        start, stop, self.interval = self.values[parameter]
        default = VARIABLE["parameters"][species][parameter] / self.interval

        self.value.setMinimum(int(start))
        self.value.setMaximum(int(stop/self.interval))
        self.value.setValue(int(default))

        self._value()

    def _movement(self):
        """Executed when the movement selection changes."""
        if self.parameter.currentText() == "":
            # This check is needed because the function is called when the species is changed,
            # before the new species is 'selected'.
            return

        parameter = self.movement.currentText()
        parameter = parameter[0] if parameter != "Stride" else parameter

        start, stop, self.interval = self.values[parameter]
        self.movement_value.setMinimum(start)
        self.movement_value.setMaximum(stop)
        self.movement_value.setValue(1)

        self._value()

    def _value(self):
        """Executed when the value selection changes."""
        if self.parameter.currentText() != "Movement":
            self.label.setText(f"{self.value.value() * self.interval:.2f}")
            return

        if self.movement.currentText() != "Stride":
            values = {1: "True", 0: "False"}
            self.label.setText(values[self.movement_value.value()])
        else:
            self.label.setText(f"{self.movement_value.value():.0f}")

    def set_parameter(self):
        """Set the parameter for the selected species."""
        species = self.species.currentText()
        parameter = self.parameter.currentText()

        if parameter == "Movement":
            mapping = {
                "Herbivore": Herbivore,
                "Carnivore": Carnivore,
                "1": True,
                "0": False
            }

            parameter = self.movement.currentText()
            value = self.movement_value.value()

            if parameter == "Stride":
                mapping[species].set_motion(new_stride=int(value))
            else:
                parameter = parameter[0]
                value = mapping[str(value)]
                mapping[species].set_motion(new_movable={parameter: value})
        else:
            value = float(self.label.text())

            if species == "Herbivore":
                Herbivore.set_parameters({parameter: value})
            elif species == "Carnivore":
                Carnivore.set_parameters({parameter: value})
            elif species == "Fodder":
                parameter = VARIABLE["parameters"]["rename"][parameter]

                Island.set_fodder_parameters({parameter: value})
                self.values["Growth factor (v_max)"] = (
                    0,
                    max(value, self.values["Growth factor (v_max)"][1]),
                    10
                )

        now = datetime.datetime.now()
        when = f"{now.hour}:{now.minute}.{now.second} {now.microsecond}"
        VARIABLE["modified"][when] = (species, parameter, value)

        self.update()

    def reset_parameter(self):
        """Reset the parameter for the species."""
        species = self.species.currentText()
        parameter = self.parameter.currentText()

        if parameter == "Movement":
            mapping = {
                "Herbivore": Herbivore,
                "Carnivore": Carnivore,
                1: "True",
                0: "False"
            }

            parameter = self.movement.currentText()
            value = self.movement_value.value()

            if parameter == "Stride":
                mapping[species].set_motion(new_stride=mapping[species].default_motion()["stride"])
            else:
                parameter = parameter[0]
                value = mapping[value]
                mapping[species].set_motion(
                    new_movable={parameter: mapping[species].default_motion()["movable"][parameter]}
                )
        else:
            if species == "Herbivore":
                current = VARIABLE["selected"][2]
                Herbivore.set_parameters({
                    parameter: VARIABLE["selection"][species][current][parameter]
                })
                value = Herbivore.default_parameters()[parameter]
            elif species == "Carnivore":
                Carnivore.set_parameters({
                    parameter: Carnivore.default_parameters()[parameter]
                })
                value = Carnivore.default_parameters()[parameter]
            elif species == "Fodder":
                parameter = VARIABLE["parameters"]["rename"][parameter]
                Island.set_fodder_parameters(
                    {parameter: Island.default_fodder_parameters()[parameter]}
                )
                value = Island.default_fodder_parameters()[parameter]

        now = datetime.datetime.now()
        when = f"{now.hour}:{now.minute}.{now.second} {now.microsecond}"
        VARIABLE["modified"][when] = (species, parameter, value)

        self.update()

    def reset_all_parameters(self):
        """Reset all parameters to their default values."""
        current = VARIABLE["selected"][2]
        Herbivore.set_parameters(VARIABLE["selection"]["Herbivore"][current])
        Herbivore.set_motion(new_stride=Herbivore.default_motion()["stride"],
                             new_movable=Herbivore.default_motion()["movable"])
        Carnivore.set_parameters(Carnivore.default_parameters())
        Carnivore.set_parameters(VARIABLE["selection"]["Carnivore"][current])
        Carnivore.set_motion(new_stride=Carnivore.default_motion()["stride"],
                             new_movable=Carnivore.default_motion()["movable"])
        Island.set_fodder_parameters(Island.default_fodder_parameters())

        now = datetime.datetime.now()
        when = f"{now.hour}:{now.minute}.{now.second} {now.microsecond}"

        i = 0
        for species in ["Herbivore", "Carnivore", "Fodder"]:
            for parameter, value in VARIABLE["parameters"][species].items():
                if parameter != "Movement":
                    VARIABLE["modified"][when + f"{i}"] = (species, parameter, value)
                else:
                    for parameter, value in VARIABLE["parameters"][species]["Movement"].items():
                        VARIABLE["modified"][when + f"{i}"] = (species, parameter, value)
                        i += 1
                i += 1

        self.update()

    def reset(self):
        """Reset the parameter history."""
        VARIABLE["modified"].clear()

        self.update()
