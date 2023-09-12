"""
Improved graphical user interface for BioSim.

Copyright (c) 2023 Hallvard Høyland Lavik / NMBU
This file is part of the BioSim-package, adding a more intuitive GUI.
Released under the MIT License, see included LICENSE file.
"""


import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QApplication, QWidget,
    QHBoxLayout, QVBoxLayout, QLineEdit, QGroupBox,
    QLabel, QPushButton, QRadioButton, QComboBox, QSlider,
    QGraphicsView, QGraphicsScene,
    QMessageBox, QTableWidget, QTableWidgetItem
)
from PyQt5.QtGui import (
    QPainter, QPen, QBrush, QColor,
    QDoubleValidator, QIntValidator
)
from PyQt5.QtCore import (
    Qt, QRect, QRectF
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from .simulation import BioSim
from .animals import Herbivore, Carnivore
from .island import Island


VARIABLE = {
    "island": ["W" * 21 for _ in range(21)],
    "selected": (None, None),
    "biosim": None,
    "colours": {
        "W": "#95CBCC",
        "H": "#E8EC9E",
        "L": "#B9D687",
        "M": "#808080"
    }
}
PARAMETERS = {
    "Herbivore": Herbivore.default_parameters(),
    "Carnivore": Carnivore.default_parameters(),
    "rename": {
        "Highland": "H",
        "Lowland": "L",
        "Mountain": "M",
        "Water": "W",
        "Growth reduction (alpha)": "alpha",
        "Growth factor (v_max)": "v_max"
    }
}
PARAMETERS["Herbivore"].update({"Movement": Herbivore.default_motion()})
PARAMETERS["Carnivore"].update({"Movement": Carnivore.default_motion()})
PARAMETERS["Fodder"] = {{v: k for k, v in PARAMETERS["rename"].items()}.get(k, k): v
                        for k, v in Island.default_fodder_parameters().items()}
MODIFIED_PARAMETERS = {}


class BioSimGUI:
    def __init__(self):
        """Initialises and starts the application."""
        app = QApplication([])
        window = Main()
        window.show()
        app.exec_()


class Main(QMainWindow):
    """Class for the main window."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 820)
        self.setWindowTitle("Model herbivores and carnivores on an island")

        # Create the tabs:
        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        # Draw:
        draw_widget = QWidget()
        draw_layout = QVBoxLayout()
        draw_widget.setLayout(draw_layout)

        self.draw = Draw()
        draw_layout.addWidget(self.draw)
        tabs.addTab(self.draw, 'Draw')

        # Populate:
        populate_widget = QWidget()
        populate_layout = QVBoxLayout()
        populate_widget.setLayout(populate_layout)

        self.populate = Populate()
        populate_layout.addWidget(self.populate)
        tabs.addTab(self.populate, 'Populate')

        # Simulate:
        simulate_widget = QWidget()
        simulate_layout = QVBoxLayout()
        simulate_widget.setLayout(simulate_layout)

        self.simulate = Simulate()
        simulate_layout.addWidget(self.simulate)
        tabs.addTab(self.simulate, 'Simulate')

        # Parameter history:
        history_widget = QWidget()
        history_layout = QVBoxLayout()
        history_widget.setLayout(history_layout)

        self.history = History()
        history_layout.addWidget(self.history)
        tabs.addTab(self.history, 'Parameter history')

        self.previous = 0
        tabs.currentChanged.connect(self.change)

    def change(self, index):
        """Switching to new tabs executes the following."""
        if index == 0: # Switching to draw page.
            self.simulate.reset()
            MODIFIED_PARAMETERS.clear()

            # May need to be removed if ECOL100 is run from server:
            msg = QMessageBox()
            msg.setText("Population and parameters has been reset.")
            msg.exec_()
        elif index == 1:  # Switching to populate page.
            self.populate.plot.update()
        elif index == 2:  # Switching to simulate page.
            try:
                VARIABLE["biosim"].should_stop = False
            except AttributeError:
                pass
        elif index == 3: # Switching to history page.
            self.history.update()

        if self.previous == 0 and index != 0:  # Switching from draw page.
            geogr = "\n".join(VARIABLE["island"])
            VARIABLE["biosim"] = BioSim(island_map=geogr)
            VARIABLE["selected"] = (None, None)
        elif self.previous == 2 and index != 2:
            self.simulate.stop()

        self.previous = index


class Draw(QWidget):
    """Class for drawing the island."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setWindowTitle("Model herbivores and carnivores on an island")
        self.setLayout(QVBoxLayout())

        self.plot = Map()
        self.plot.setGeometry(QRect(0, 0, 800, 800))
        self.layout().addWidget(self.plot)

        self.color_widget = None

        self.buttons()
        self.plot.update()

    def buttons(self):
        """Add buttons to the window."""
        txt = QLabel("Select terrain type to draw.", self)
        txt.setGeometry(850, 290, 200, 100)

        # Select terrain type:
        color_map = {"W": "Water", "H": "Highland", "L": "Lowland", "M": "Mountain"}
        color_layout = QVBoxLayout()
        for name, color in VARIABLE["colours"].items():
            button = QPushButton(color_map[name], self)
            button.setFixedSize(100, 100)
            button.setStyleSheet(f"background-color: {color}")
            button.clicked.connect(lambda _, name=name: self.color_clicked(name))
            color_layout.addWidget(button)

        self.color_widget = QWidget(self)
        self.color_widget.setLayout(color_layout)
        self.color_widget.setGeometry(QRect(880, 350, 450, 450))

        # Modify map:
        bigger_button = QPushButton("Bigger", self)
        bigger_button.setGeometry(QRect(880, 10, 110, 100))
        bigger_button.clicked.connect(self.bigger)

        smaller_button = QPushButton("Smaller", self)
        smaller_button.setGeometry(QRect(880, 120, 110, 100))
        smaller_button.clicked.connect(self.smaller)

    def color_clicked(self, name):
        """
        Change the selected terrain type.

        Parameters
        ----------
        name : str
        """
        self.plot.terrain = name[0]
        for button in self.color_widget.findChildren(QPushButton):
            if button.text()[0] == name:
                button.setStyleSheet(
                    f"background-color: {VARIABLE['colours'][name[0]]}; border: 2px solid black"
                )
            else:
                button.setStyleSheet(
                    f"background-color: {VARIABLE['colours'][button.text()[0]]}"
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
    """Class for visualising the island."""
    def __init__(self, terrain="W", drawing=True):
        super().__init__()

        self.terrain = terrain
        self.drawing = drawing
        self.size = 10

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setFixedSize(800, 800)

    def update(self):
        """Update the scene."""
        self.scene.clear()
        pen = QPen(Qt.black)
        pen.setWidthF(0.1)
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
                self.update()

                pen = QPen(Qt.black)
                pen.setWidthF(0.1)
                self.scene.addRect(
                    i * self.size, j * self.size,
                    self.size, self.size,
                    pen, QBrush(QColor("black"))
                )

                VARIABLE["selected"] = (i, j)
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

                pen = QPen(Qt.black)
                pen.setWidthF(0.1)
                self.scene.addRect(
                    i * self.size, j * self.size,
                    self.size, self.size,
                    pen, QBrush(QColor(VARIABLE['colours'][self.terrain]))
                )


class Populate(QWidget):
    """Class for populating the island."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setWindowTitle("Model herbivores and carnivores on an island")

        self.plot = None
        self.herbivore = None
        self.add = None
        self.buttons = []
        self.amount = None

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
        self.herbivore = QRadioButton("Herbivore")
        carnivore = QRadioButton("Carnivore")
        _species.addWidget(self.herbivore)
        _species.addWidget(carnivore)
        _species.setAlignment(Qt.AlignHCenter)
        species.setFixedSize(200, 80)

        top.addWidget(species)

        # Amount of animals.
        amount = QHBoxLayout()
        label = QLabel("Number of animals:")
        self.amount = QLineEdit()
        # self.amount.setFixedSize(90, 40)
        self.amount.setValidator(QIntValidator())
        amount.addWidget(label)
        amount.addWidget(self.amount)
        amount.setGeometry(QRect(0, 0, 500, 200))

        top.addLayout(amount)

        # Add button.
        add = QHBoxLayout()
        self.add = QPushButton("Add")
        self.add.setFixedSize(200, 100)
        self.add.setStyleSheet("background-color: #B7BFA1")
        self.add.clicked.connect(self.populate)
        add.addWidget(self.add)

        top.addSpacing(20)
        top.addLayout(add)

        # R- and K-selected herbivore buttons.
        selection = QHBoxLayout()
        for name in ["R-selected", "K-selected"]:
            button = QPushButton(name)
            button.setFixedSize(100, 100)
            button.setStyleSheet(f"background-color: #C0C0C0")
            button.clicked.connect(lambda _, name=name: self.selection(name))
            selection.addWidget(button)
            self.buttons.append(button)

        bottom.addLayout(selection)

        # Reset button.
        reset = QHBoxLayout()
        _reset = QPushButton("Slaughter population")
        _reset.setFixedSize(200, 100)
        _reset.setStyleSheet("background-color: #C0C0C0")
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
        self.herbivore.toggled.connect(self.species)
        self.herbivore.setChecked(True)
        self.selection("R")

    def selection(self, name):
        """Executed when the selection changes."""
        for button in self.buttons:
            if button.text() == name:
                button.setStyleSheet(
                    f"background-color: #B7BFA1; border: 4px solid black"
                )
            else:
                button.setStyleSheet(
                    f"background-color: #C0C0C0"
                )

        if name == "R-selected":
            pass
            # TODO: Set parameters
        else:
            pass
            # TODO: Set parameters

        try:
            if VARIABLE["biosim"].island.year != 0:
                geogr = "\n".join(VARIABLE["island"])
                VARIABLE["biosim"] = BioSim(island_map=geogr)

                msg = QMessageBox()
                msg.setText("Simulation and population has been reset.")
                msg.exec_()
        except AttributeError:
            pass

    def species(self):
        """Executed when the species selection changes."""
        if self.herbivore.isChecked():
            self.add.setStyleSheet("background-color: #B7BFA1")
        else:
            self.add.setStyleSheet("background-color: #F2C38F")

    def populate(self):
        """Populate the island with animals."""
        j, i = VARIABLE["selected"]

        if i is None or j is None:
            msg = QMessageBox()
            msg.setText("Please select a cell by clicking on the map.")
            msg.exec_()
            return

        species = "Herbivore" if self.herbivore.isChecked() else "Carnivore"
        age = None
        weight = 5  # TODO: Endre på denne?
        amount = int(self.amount.text()) if self.amount.text() else 1

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

        self.values = {
            "w_birth": (0, 20, 0.1),
            "sigma_birth": (0, 5, 0.1),
            "beta": (0, 5, 0.1),
            "eta": (0, 1, 0.01),
            "a_half": (0, 80, 1),
            "phi_age": (0, 2, 0.01),
            "w_half": (0, 30, 0.5),
            "phi_weight": (0, 2, 0.01),
            "mu": (0, 4, 0.01),
            "gamma": (0, 8, 0.01),
            "zeta": (0, 20, 0.1),
            "xi": (0, 10, 0.1),
            "omega": (0, 8, 0.1),
            "F": (0, 100, 5),
            "DeltaPhiMax": (1, 50, 0.5),
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

        self.fig = None
        self.canvas = None

        self.species = None
        self.parameter = None
        self.movement = None
        self.movement_value = None
        self.value = None
        self.label = None
        self.interval = None

        self.years = None
        self.year = None

        self.parameters()
        self.simulation()

        self.plot()

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

        reset_all_parameters = QPushButton("Reset all parameters")
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
        self.layout().addLayout(parameters)

        self._species()
        self._parameter()

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
        simulate_button.setFixedWidth(140)

        pause = QPushButton("Pause simulation")
        pause.clicked.connect(self.stop)
        pause.setFixedWidth(140)

        reset = QPushButton("Reset years")
        reset.clicked.connect(self.restart_years)
        reset.setFixedWidth(200)

        simulation = QHBoxLayout()
        simulation.addWidget(QLabel("Number of years to simulate:"))
        simulation.addWidget(self.years)
        simulation.addWidget(self.year)
        simulation.addWidget(simulate_button)
        simulation.addWidget(pause)
        simulation.addSpacing(100)
        simulation.addWidget(reset)
        self.layout().addLayout(simulation)

    def _species(self):
        """Executed when the species selection changes."""
        species = self.species.currentText()
        self.parameter.clear()
        self.parameter.addItems(PARAMETERS[species].keys())

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
        default = PARAMETERS[species][parameter] / self.interval

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

    def _years(self):
        """Executed when the number of years to simulate changes."""
        self.year.setText(str(self.years.value()))

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
                parameter = PARAMETERS["rename"][parameter]

                Island.set_fodder_parameters({parameter: value})
                self.values["Growth factor (v_max)"] = (
                    0,
                    max(value, self.values["Growth factor (v_max)"][1]),
                    10
                )

        now = datetime.datetime.now()
        when = f"{now.hour}:{now.minute}.{now.second} {now.microsecond}"
        MODIFIED_PARAMETERS[when] = (species, parameter, value)

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
                Herbivore.set_parameters({parameter: Herbivore.default_parameters()[parameter]})
                value = Herbivore.default_parameters()[parameter]
            elif species == "Carnivore":
                Carnivore.set_parameters({parameter: Carnivore.default_parameters()[parameter]})
                value = Carnivore.default_parameters()[parameter]
            elif species == "Fodder":
                parameter = PARAMETERS["rename"][parameter]
                Island.set_fodder_parameters(
                    {parameter: Island.default_fodder_parameters()[parameter]}
                )
                value = Island.default_fodder_parameters()[parameter]

        now = datetime.datetime.now()
        when = f"{now.hour}:{now.minute}.{now.second} {now.microsecond}"
        MODIFIED_PARAMETERS[when] = (species, parameter, value)

    @staticmethod
    def reset_all_parameters():
        """Reset all parameters to their default values."""
        Herbivore.set_parameters(Herbivore.default_parameters())
        Herbivore.set_motion(new_stride=Herbivore.default_motion()["stride"],
                             new_movable=Herbivore.default_motion()["movable"])
        Carnivore.set_parameters(Carnivore.default_parameters())
        Carnivore.set_motion(new_stride=Carnivore.default_motion()["stride"],
                             new_movable=Carnivore.default_motion()["movable"])
        Island.set_fodder_parameters(Island.default_fodder_parameters())

        now = datetime.datetime.now()
        when = f"{now.hour}:{now.minute}.{now.second} {now.microsecond}"

        i = 0
        for species in ["Herbivore", "Carnivore", "Fodder"]:
            for parameter, value in PARAMETERS[species].items():
                if parameter != "Movement":
                    MODIFIED_PARAMETERS[when + f"{i}"] = (species, parameter, value)
                else:
                    for parameter, value in PARAMETERS[species]["Movement"].items():
                        MODIFIED_PARAMETERS[when + f"{i}"] = (species, parameter, value)
                        i += 1
                i += 1

    def plot(self):
        """Plot the population on the island."""
        self.fig = plt.Figure(figsize=(15, 10))

        self.canvas = FigureCanvas(self.fig)
        self.layout().addWidget(self.canvas)

    @staticmethod
    def restart_years():
        """Clears the population list."""
        VARIABLE["biosim"].island.year = 0
        VARIABLE["biosim"].graphics.reset_counts()

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
        VARIABLE["biosim"].simulate(years, figure=self.fig, canvas=self.canvas)

    @staticmethod
    def stop():
        """Stops the simulation."""
        VARIABLE["biosim"].should_stop = True

    @staticmethod
    def reset():
        """Reset the simulation."""
        VARIABLE["biosim"].island.year = 0
        VARIABLE["biosim"].graphics.reset_graphics()


class History(QWidget):
    """Class for visualising the parameter history."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setLayout(QHBoxLayout())

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Time", "Species", "Parameter", "Value"])
        self.layout().addWidget(self.table)

        reset = QPushButton("Clear history")
        reset.clicked.connect(self.reset)
        self.layout().addWidget(reset)

        self.update()

    def update(self):
        """Update the window."""
        self.table.setRowCount(len(MODIFIED_PARAMETERS))
        for row, (time, (species, parameter, value)) in enumerate(MODIFIED_PARAMETERS.items()):
            time_item = QTableWidgetItem(time.split()[0])
            species_item = QTableWidgetItem(species)
            parameter_item = QTableWidgetItem(parameter)
            value_item = QTableWidgetItem(str(value))
            self.table.setItem(row, 0, time_item)
            self.table.setItem(row, 1, species_item)
            self.table.setItem(row, 2, parameter_item)
            self.table.setItem(row, 3, value_item)

    def reset(self):
        """Reset the parameter history."""
        MODIFIED_PARAMETERS.clear()
        self.update()
