"""
Graphical user interface for the BioSim package.

Copyright (c) 2023 Hallvard Høyland Lavik / NMBU
This file is part of the BioSim-package, adding a more intuitive GUI.
Released under the MIT License, see included LICENSE file.
"""


import sys
import time
import math
from perlin_noise import PerlinNoise
from PyQt5.QtCore import Qt, QRect, QRectF, QMimeData, QSize
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QDrag, QPixmap, QIcon
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QApplication, QWidget, QHBoxLayout,
                             QVBoxLayout, QGroupBox, QGridLayout, QLabel, QPushButton, QSlider,
                             QGraphicsView, QGraphicsScene, QMessageBox, QGraphicsPixmapItem,
                             QInputDialog)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from .simulation import BioSim
from .animals import Herbivore, Carnivore
from .island import Island

VARIABLE = {"island": ["W" * 21 for _ in range(21)],
            "perlin": {"octaves": 4,            # Density of land (higher = more 'islands').
                       "lower": -0.23,          # Water < 'lower'.
                       "middle": 0.0,           # 'lower' < Lowland < 'middle'.
                       "upper": 0.2},           # 'middle' < Highland < 'upper'. Otherwise Mountain.
            "selected": {"pos": (int, int), "species": str, "amount": int},
            "biosim": None,
            "speed": 8e-6,
            "colours": {"W": "#95CBCC",
                        "H": "#E8EC9E",
                        "L": "#B9D687",
                        "M": "#808080"},
            "parameters": {"Herbivore": Herbivore.default_parameters(),
                           "Carnivore": Carnivore.default_parameters(),
                           "Fodder": {},
                           "rename": {"Highland": "H",
                                      "Lowland": "L",
                                      "Mountain": "M",
                                      "Water": "W",
                                      "Growth reduction (alpha)": "alpha",
                                      "Growth factor (v_max)": "v_max"}},
            "modified": {},
            "history": {},
            "dir": str(sys._MEIPASS) if getattr(sys, 'frozen', False) else "src/biosim/_static"}

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
        This is made to a class in order to be visually pleasing (capital letters) without
        "raising" an error.
        """
        Herbivore.set_parameters(Herbivore.default_parameters())
        Carnivore.set_parameters(Carnivore.default_parameters())

        app = QApplication([])
        app.setStyleSheet("""
            QPushButton {
                background-color: #FBFAF5;
                color: black;
                border: 1px solid black;
                border-radius: 5px;
            }
        """)
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
        VARIABLE["biosim"].graphics.hist_specs = {
            'age': {'max': 45, 'delta': 5},
            'weight': {'max': 60, 'delta': 5},
            'fitness': {'max': 1, 'delta': 0.1}
        }
        VARIABLE["history"].clear()


class Main(QMainWindow):
    """Class for the main window."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 820)
        self.setWindowTitle("Modeller plante- og kjøttetere på en øy")

        # Create the tabs:
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Draw:
        draw_widget = QWidget()
        draw_layout = QVBoxLayout()
        draw_widget.setLayout(draw_layout)

        self.draw = Draw()
        draw_layout.addWidget(self.draw)
        self.tabs.addTab(self.draw, 'Tegn')

        # Populate:
        populate_widget = QWidget()
        populate_layout = QVBoxLayout()
        populate_widget.setLayout(populate_layout)

        self.populate = Populate()
        populate_layout.addWidget(self.populate)
        self.tabs.addTab(self.populate, 'Befolk')

        # Simulate:
        simulate_widget = QWidget()
        simulate_layout = QVBoxLayout()
        simulate_widget.setLayout(simulate_layout)

        self.simulate = Simulate()
        simulate_layout.addWidget(self.simulate)
        self.tabs.addTab(self.simulate, 'Simuler')

        # History:
        history_widget = QWidget()
        history_layout = QVBoxLayout()
        history_widget.setLayout(history_layout)

        self.history = History()
        history_layout.addWidget(self.history)
        self.tabs.addTab(self.history, 'Historie')

        self.previous = 0
        self.tabs.currentChanged.connect(self.change)

    def change(self, index):
        """Switching to new tabs executes the following."""
        if index == 0:  # Switching to draw page.
            if any(cell != "W" for row in VARIABLE["island"] for cell in row):
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Warning)
                msg_box.setText(
                    "Er du sikker på at du vil tegne? Dette nullstiller alt."
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
            self.draw.plot.update()
        elif index == 1:  # Switching to populate page.
            self.populate.plot.update()
        elif index == 2:  # Switching to simulate page.
            if not VARIABLE["biosim"]:
                BioSimGUI.restart()
            try:
                VARIABLE["biosim"].should_stop = False
            except AttributeError:
                pass
            try:
                self.simulate.simulate()
            except:
                pass
        elif index == 3:  # Switching to history page.
            self.history.update()
        if self.previous == 0 and index != 0:  # Switching from draw page.
            BioSimGUI.restart()
            try:
                self.populate.plot.update()
            except AttributeError:
                pass
        elif self.previous == 2 and index != 2:
            self.simulate.stop()
            time.sleep(2)
            self.history.update()

        self.previous = index


class Draw(QWidget):
    """Class for drawing the island."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setWindowTitle("Modeller plante- og kjøttetere på en øy")

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

        size = 120

        modification_layout = QGridLayout()
        terrain_layout = QGridLayout()

        # Modification buttons.

        bigger_button = QPushButton()
        bigger_button.setFixedSize(size, size)
        bigger_button.setIcon(QIcon(VARIABLE["dir"] + "/zoom-out.png"))
        bigger_button.setIconSize(QSize(size//3, size//3))
        bigger_button.clicked.connect(self.bigger)

        smaller_button = QPushButton()
        smaller_button.setFixedSize(size, size)
        smaller_button.setIcon(QIcon(VARIABLE["dir"] + "/zoom-in.png"))
        smaller_button.setIconSize(QSize(size//3, size//3))
        smaller_button.clicked.connect(self.smaller)

        autocomplete_button = QPushButton()
        autocomplete_button.setFixedSize(size, size)
        autocomplete_button.setIcon(QIcon(VARIABLE["dir"] + "/stars.png"))
        autocomplete_button.setIconSize(QSize(size // 2, size // 2))
        autocomplete_button.clicked.connect(self.autocomplete)

        clear_button = QPushButton()
        clear_button.setFixedSize(size, size)
        clear_button.setIcon(QIcon(VARIABLE["dir"] + "/delete.png"))
        clear_button.setIconSize(QSize(size // 3, size // 3))
        clear_button.clicked.connect(self.clear)

        modification_layout.addWidget(bigger_button, 0, 0)
        modification_layout.addWidget(smaller_button, 0, 1)
        modification_layout.addWidget(autocomplete_button, 1, 0)
        modification_layout.addWidget(clear_button, 1, 1)

        # Brush selection.

        color_map = {"V": "Vann", "H": "Høyland", "L": "Lavland", "F": "Fjell"}
        mapping = {"W": "V", "H": "H", "L": "L", "M": "F"}
        terrain_buttons = {}
        for name, color in VARIABLE["colours"].items():
            _name = mapping[name]
            button = QPushButton(color_map[_name])
            button.setFixedSize(size, size)
            button.setStyleSheet(f"background-color: {color};")
            button.clicked.connect(lambda _, name=_name: self.color_clicked(name))
            terrain_buttons[_name] = button
            self.selection.append(button)

        terrain_layout.addWidget(terrain_buttons["V"], 0, 0)
        terrain_layout.addWidget(terrain_buttons["H"], 0, 1)
        terrain_layout.addWidget(terrain_buttons["L"], 1, 0)
        terrain_layout.addWidget(terrain_buttons["F"], 1, 1)

        # Combining the buttons.

        buttons.addLayout(modification_layout)
        buttons.addStretch(1)

        text = QLabel("Velg terreng å tegne med:")
        text.setAlignment(Qt.AlignCenter)
        buttons.addWidget(text)

        buttons.addLayout(terrain_layout)
        buttons.setAlignment(Qt.AlignCenter)

        self.layout.addLayout(buttons)

    def color_clicked(self, name):
        """
        Change the selected terrain type.

        Parameters
        ----------
        name : str
        """
        mapping = {"V": "W", "H": "H", "L": "L", "F": "M"}
        self.plot.terrain = mapping[name[0]]
        for button in self.selection:
            if button.text()[0] == name:
                button.setStyleSheet(
                    f"background-color: {VARIABLE['colours'][mapping[name[0]]]}; "
                    f"border: 3px solid black"
                )
            else:
                button.setStyleSheet(
                    f"background-color: {VARIABLE['colours'][mapping[button.text()[0]]]};"
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

    @staticmethod
    def center():
        """Computes the dynamic center based on user's drawings."""
        drawn = [(i, j) for i, row in enumerate(VARIABLE["island"])
                 for j, cell in enumerate(row) if cell != "W"]

        if not drawn:
            return len(VARIABLE["island"]) // 2, len(VARIABLE["island"][0]) // 2

        avg_i = sum(i for i, _ in drawn) / len(drawn)
        avg_j = sum(j for _, j in drawn) / len(drawn)

        return int(avg_i), int(avg_j)

    def autocomplete(self):
        """
        Autocomplete the map based on Perlin noise.

        Notes
        -----
        The Perlin noise is based on the distance from the center of the map if the map is empty.
        If the map contains drawn cells, the Perlin noise is based on the distance from the
        center of these.
        """
        size = len(VARIABLE["island"])
        center_i, center_j = self.center()

        noise = PerlinNoise(octaves=VARIABLE["perlin"]["octaves"])
        for i in range(1, size - 1):
            for j in range(1, size - 1):

                if VARIABLE["island"][i][j] != "W":
                    continue

                # Perlin noice based on distance from the center of the map (or drawn cells).
                distance = (math.sqrt((i - center_i) ** 2 + (j - center_j) ** 2) /
                            math.sqrt(2 * size ** 2))
                perlin = noise([i / size, j / size]) - distance

                if perlin < VARIABLE["perlin"]["lower"]:
                    terrain = "W"
                elif VARIABLE["perlin"]["lower"] <= perlin < VARIABLE["perlin"]["middle"]:
                    terrain = "L"
                elif VARIABLE["perlin"]["middle"] <= perlin < VARIABLE["perlin"]["upper"]:
                    terrain = "H"
                else:
                    terrain = "M"

                VARIABLE["island"][i] = (VARIABLE["island"][i][:j] +
                                         terrain +
                                         VARIABLE["island"][i][j + 1:])

        self.plot.update()

    def clear(self):
        """Clear the map."""
        VARIABLE["island"] = ["W" * len(VARIABLE["island"][0])
                              for _ in range(len(VARIABLE["island"]))]
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

        self.dropEvent(event)

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
        try:
            species = event.mimeData().text()
        except AttributeError:
            species = VARIABLE["selected"]["species"]

        if species is str:
            msg = QMessageBox()
            msg.setText("Velg et dyr først.")
            msg.exec_()
            return

        position = self.mapToScene(event.pos())
        i = int(position.x() // self.size)
        j = int(position.y() // self.size)

        if VARIABLE["island"][j][i] == "W":
            msg = QMessageBox()
            msg.setText("Dyr kan ikke plasseres i vann.")
            msg.exec_()
            return

        try:
            image = QPixmap(VARIABLE["dir"] + f"/{species}.png").scaled(self.size, self.size)
        except TypeError:
            return

        item = QGraphicsPixmapItem(image)
        item.setPos(i * self.size, j * self.size)
        self.scene.addItem(item)

        num_animals, ok = QInputDialog.getInt(self, "Antall dyr", "Hvor mange?", 1, 1, 1000)
        if ok:
            VARIABLE["selected"] = {
                "pos": (i, j),
                "species": species,
                "amount": num_animals
            }
            Populate.populate()
        else:
            self.scene.removeItem(item)

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
                try:
                    Species.selected.setStyleSheet("")
                except RuntimeError:
                    pass

            Species.selected = self
            self.setStyleSheet("border: 4px solid #a4ab90")

            VARIABLE["selected"]["species"] = self.species

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
        self.species = None
        self.herbivore = None
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
        _species = QGroupBox()
        self.species = QVBoxLayout()
        _species.setLayout(self.species)
        herbivore = Species(QPixmap(VARIABLE["dir"] + "/Herbivore.png"), "Herbivore")
        carnivore = Species(QPixmap(VARIABLE["dir"] + "/Carnivore.png"), "Carnivore")
        self.species.addWidget(carnivore)
        self.species.addWidget(herbivore)
        self.species.setAlignment(Qt.AlignHCenter)

        top.addWidget(_species)

        # Reset button.
        reset = QHBoxLayout()
        _reset = QPushButton()
        _reset.setFixedSize(200, 100)
        _reset.setIcon(QIcon(VARIABLE["dir"] + "/delete.png"))
        _reset.setIconSize(QSize(100 // 3, 100 // 3))
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

    @staticmethod
    def populate():
        """Populate the island with animals."""
        j, i = VARIABLE["selected"]["pos"]

        if i is None or j is None:
            msg = QMessageBox()
            msg.setText("Please select a cell by clicking on the map or drag-dropping an animal.")
            msg.exec_()
            return

        species = VARIABLE["selected"]["species"]
        if species is None:
            msg = QMessageBox()
            msg.setText("Please select a species by clicking or drag-dropping to the map.")
            msg.exec_()
            return

        age = 0
        weight = None
        amount = VARIABLE["selected"]["amount"] if VARIABLE["selected"]["amount"] is not None else 1

        animals = [{
            "loc": (int(i) + 1, int(j) + 1),
            "pop": [{"species": species,
                     "age": age,
                     "weight": weight} for _ in range(amount)]}]

        VARIABLE["biosim"].add_population(animals)

    def reset(self):
        """Reset the population on the island."""
        VARIABLE["biosim"].island.slaughter()

        for item in self.plot.scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                self.plot.scene.removeItem(item)


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
        self.years.setValue(200)
        self.years.valueChanged.connect(self._years)
        self.years.setFixedWidth(200)
        self.year = QLabel()
        self.year.setFixedWidth(40)
        self._years()

        simulate_button = QPushButton("Simulér")
        simulate_button.clicked.connect(self.simulate)

        pause = QPushButton("Pause")
        pause.clicked.connect(self.stop)

        faster = QPushButton("Raskere")
        faster.clicked.connect(self.faster)

        slower = QPushButton("Treigere")
        slower.clicked.connect(self.slower)

        reset = QPushButton("Nullstill")
        reset.clicked.connect(self.restart_years)
        reset.setFixedWidth(200)

        simulation = QHBoxLayout()
        simulation.addWidget(QLabel("Iterasjoner å simulere:"))
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

    def restart_years(self):
        """Clears the population list."""
        Simulate.stop()
        VARIABLE["biosim"].island.year = 0
        # VARIABLE["biosim"].graphics.reset_counts()
        VARIABLE["history"] = {"Herbivore": {"Age": [],
                                             "Weight": [],
                                             "Fitness": []},
                               "Carnivore": {"Age": [],
                                             "Weight": [],
                                             "Fitness": []}}
        VARIABLE["biosim"].history = VARIABLE["history"]

        animals, n_species, n_species_cell = VARIABLE["biosim"].island.animals()
        VARIABLE["biosim"].graphics.reset_counts()
        VARIABLE["biosim"].graphics.setup(1, n_species_cell, VARIABLE["speed"], self.fig)
        VARIABLE["biosim"].graphics.update_graphics(0,
                                                    n_species,
                                                    n_species_cell,
                                                    animals,
                                                    canvas=self.canvas)

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

        VARIABLE["biosim"].graphics.speed = VARIABLE["speed"]
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
            VARIABLE["biosim"].graphics.speed /= 2
            VARIABLE["speed"] = VARIABLE["biosim"].graphics.speed
        except TypeError:
            return

    @staticmethod
    def slower():
        """Decrease plot update speed."""
        try:
            VARIABLE["biosim"].graphics.speed *= 2
            VARIABLE["speed"] = VARIABLE["biosim"].graphics.speed
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
        # self.fig.clear()
        animals, n_species, n_species_cell = VARIABLE["biosim"].island.animals()
        VARIABLE["biosim"].graphics.reset_counts()

        VARIABLE["biosim"].graphics.setup(1, n_species_cell, VARIABLE["speed"], self.fig)
        VARIABLE["biosim"].graphics.update_graphics(0,
                                                    n_species,
                                                    n_species_cell,
                                                    animals,
                                                    canvas=self.canvas)


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
        old.set_title("Gjennomsnittlig alder")
        thick.set_title("Gjennomsnittlig vekt")
        fit.set_title("Gjennomsnittlig form")

        # Plotting the Age data
        herbivore_age_axis = old
        herbivore_age_axis.plot(years, VARIABLE["history"]["Herbivore"]["Age"],
                                label="Planteeter", color=(0.71764, 0.749, 0.63137))

        carnivore_age_axis = old.twinx()
        carnivore_age_axis.plot(years, VARIABLE["history"]["Carnivore"]["Age"],
                                label="Kjøtteter", color=(0.949, 0.7647, 0.56078))

        herbivore_age_axis.set_ylabel("Planteeter alder")
        carnivore_age_axis.set_ylabel("Kjøtteter alder")
        herbivore_age_axis.legend(loc='upper left', bbox_to_anchor=(0, 1.2))
        carnivore_age_axis.legend(loc='upper right', bbox_to_anchor=(1, 1.2))
        herbivore_age_axis.set_xticks([])

        # Plotting the Weight data
        herbivore_weight_axis = thick
        herbivore_weight_axis.plot(years, VARIABLE["history"]["Herbivore"]["Weight"],
                                   label="Planteeter vekt", color=(0.71764, 0.749, 0.63137))

        carnivore_weight_axis = thick.twinx()
        carnivore_weight_axis.plot(years, VARIABLE["history"]["Carnivore"]["Weight"],
                                   label="Kjøtteter vekt", color=(0.949, 0.7647, 0.56078))

        herbivore_weight_axis.set_ylabel("Planteeter vekt")
        carnivore_weight_axis.set_ylabel("Kjøtteter vekt")
        herbivore_weight_axis.set_xticks([])

        fit.plot(years, VARIABLE["history"]["Herbivore"]["Fitness"],
                 color=(0.71764, 0.749, 0.63137))
        fit.plot(years, VARIABLE["history"]["Carnivore"]["Fitness"],
                 color=(0.949, 0.7647, 0.56078))
        fit.set_xlabel("Iterasjon")

        self.canvas.draw()
