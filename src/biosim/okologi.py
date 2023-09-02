"""
Improved graphical user interface for BioSim.

Copyright (c) 2023 Hallvard Høyland Lavik / NMBU
This file is part of the BioSim-package, adding a more intuitive GUI.
Released under the MIT License, see included LICENSE file.
"""


from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QApplication, QWidget,
    QHBoxLayout, QVBoxLayout, QLineEdit, QGroupBox,
    QLabel, QPushButton, QRadioButton, QComboBox, QSlider,
    QGraphicsView, QGraphicsScene,
    QMessageBox
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
import numpy as np

from .simulation import BioSim
from .animals import Herbivore, Carnivore
from .island import Island


VARIABLE = {
    "island": ["W" * 11 for _ in range(11)],
    "selected": (None, None),
    "biosim": None,
}
DEFAULT_PARAMETERS = {
    "Herbivore": Herbivore.default_parameters(),
    "Carnivore": Carnivore.default_parameters(),
    "Fodder": Island.default_fodder_parameters()
}


def ecol_100():
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
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Draw:
        self.draw_widget = QWidget()
        self.draw_layout = QVBoxLayout()
        self.draw_widget.setLayout(self.draw_layout)

        self.draw = Draw()
        self.draw_layout.addWidget(self.draw)
        self.tabs.addTab(self.draw, 'Draw')

        # Populate:
        self.populate_widget = QWidget()
        self.populate_layout = QVBoxLayout()
        self.populate_widget.setLayout(self.populate_layout)

        self.populate = Populate()
        self.populate_layout.addWidget(self.populate)
        self.tabs.addTab(self.populate, 'Populate')

        # Simulate:
        self.plot_widget = QWidget()
        self.plot_layout = QVBoxLayout()
        self.plot_widget.setLayout(self.plot_layout)

        self.plot = Simulate()
        self.plot_layout.addWidget(self.plot)
        self.tabs.addTab(self.plot, 'Simulate')

        self.previous = 0
        self.tabs.currentChanged.connect(self.change)

    def change(self, index):
        """Switching to new tabs executes the following."""
        if index == 1:  # Switching to populate page
            self.populate.plot.update()

        # Resetting the island when switching to draw page:
        if index == 0:
            self.plot.reset()

            msg = QMessageBox()
            msg.setText("Population has been reset.")
            msg.exec_()

        # Updating the island when switching from draw page:
        if self.previous == 0 and index != 0:
            geogr = "\n".join(VARIABLE["island"])
            VARIABLE["biosim"] = BioSim(island_map=geogr)
            VARIABLE["selected"] = (None, None)

        self.previous = index


class Draw(QWidget):
    """Class for drawing the island."""
    def __init__(self):
        super().__init__()

        self.colours = {
            "Water": "#95CBCC",
            "Highland": "#E8EC9E",
            "Lowland": "#B9D687",
            "Desert": "#FFEEBA"
        }

        self.setGeometry(400, 200, 1000, 800)
        self.setWindowTitle("Model herbivores and carnivores on an island")
        self.setLayout(QVBoxLayout())

        self.plot = Map()
        self.plot.setGeometry(QRect(0, 0, 800, 800))
        self.layout().addWidget(self.plot)

        self.color_layout = None
        self.color_widget = None
        self.bigger_button = None
        self.smaller_button = None

        self.buttons()
        self.plot.update()

    def buttons(self):
        """Add buttons to the window."""
        txt = QLabel("Select terrain type to draw.", self)
        txt.setGeometry(850, 290, 200, 100)

        # Select terrain type:
        self.color_layout = QVBoxLayout()
        for name, color in self.colours.items():
            button = QPushButton(name, self)
            button.setFixedSize(100, 100)
            button.setStyleSheet(f"background-color: {color}")
            button.clicked.connect(lambda _, name=name: self.color_clicked(name))
            self.color_layout.addWidget(button)

        self.color_widget = QWidget(self)
        self.color_widget.setLayout(self.color_layout)
        self.color_widget.setGeometry(QRect(880, 350, 450, 450))

        # Modify map:
        txt = QLabel("Increase/decrease map size.", self)
        txt.setGeometry(850, 0, 200, 100)

        self.bigger_button = QPushButton("Bigger", self)
        self.bigger_button.setGeometry(QRect(880, 70, 110, 100))
        self.bigger_button.clicked.connect(self.bigger)

        self.smaller_button = QPushButton("Smaller", self)
        self.smaller_button.setGeometry(QRect(880, 170, 110, 100))
        self.smaller_button.clicked.connect(self.smaller)

    def color_clicked(self, name):
        """
        Change the selected terrain type.

        Parameters
        ----------
        name : str
        """
        self.plot.terrain = name[0]
        for button in self.color_widget.findChildren(QPushButton):
            if button.text() == name:
                button.setStyleSheet(
                    f"background-color: {self.colours[name]}; border: 2px solid black"
                )
            else:
                button.setStyleSheet(
                    f"background-color: {self.colours[button.text()]}"
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
    def __init__(self, terrain="W", can_draw=True, size=800):
        super().__init__()

        self.can_draw = can_draw

        self.terrain = terrain
        self.size = 10
        self.colours = {
            "W": "#95CBCC",
            "H": "#E8EC9E",
            "L": "#B9D687",
            "D": "#FFEEBA"
        }

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setFixedSize(size, size)

    def update(self):
        """Update the scene."""
        self.scene.clear()
        pen = QPen(Qt.black)
        pen.setWidthF(0.2)
        for j, row in enumerate(VARIABLE["island"]):
            for i, cell in enumerate(row):
                brush = QBrush(QColor(self.colours[cell]))
                rect = QRectF(i * self.size, j * self.size, self.size, self.size)
                self.scene.addRect(rect, pen, brush)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        if self.width() > self.scene.width() or self.height() > self.scene.height():
            self.fitInView(self.scene.sceneRect(), Qt.IgnoreAspectRatio)

    def resizeEvent(self, event):
        """Resize the scene."""
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        """Executed when the mouse is pressed."""
        if self.can_draw:
            self.mouseMoveEvent(event)
            return

        if event.buttons() == Qt.LeftButton and self.terrain == "SELECT":
            position = self.mapToScene(event.pos())
            i = int(position.x() // self.size)
            j = int(position.y() // self.size)

            if VARIABLE["island"][j][i] != "W":
                self.update()

                # Updating the scene:
                pen = QPen(Qt.black)
                pen.setWidthF(0.2)
                brush = QBrush(QColor("black"))

                self.scene.addRect(
                    i * self.size, j * self.size,
                    self.size, self.size,
                    pen, brush
                )

                VARIABLE["selected"] = (i, j)
            else:
                msg = QMessageBox()
                msg.setText("Cannot place animals in water.")
                msg.exec_()

    def mouseMoveEvent(self, event):
        """Executed when the mouse is pressed-moved."""
        if event.buttons() == Qt.LeftButton and self.can_draw:
            position = self.mapToScene(event.pos())
            i = int(position.x() // self.size)
            j = int(position.y() // self.size)

            if 0 < i < len(VARIABLE["island"][0])-1 and 0 < j < len(VARIABLE["island"])-1:
                VARIABLE["island"][j] = (VARIABLE["island"][j][:i] +
                                         self.terrain +
                                         VARIABLE["island"][j][i + 1:])

                # Updating the scene:
                pen = QPen(Qt.black)
                pen.setWidthF(0.2)
                brush = QBrush(QColor(self.colours[self.terrain]))

                self.scene.addRect(
                    i * self.size, j * self.size,
                    self.size, self.size,
                    pen, brush
                )


class Populate(QWidget):
    """Class for populating the island."""
    def __init__(self):
        super().__init__()

        self.plot = None
        self.input_layout = None
        self.species_group = None
        self.species_layout = None
        self.species_herbivore = None
        self.species_carnivore = None
        self.age = None
        self.weight = None
        self.amount = None
        self.layout = None

        self.initialise()

    def initialise(self):
        """Initialise the window."""
        self.plot = Map(can_draw=False, terrain="SELECT")
        self.plot.setGeometry(QRect(0, 0, 800, 800))

        # Create the input boxes layout
        self.input_layout = QVBoxLayout()

        # Create the species group
        self.species_group = QGroupBox()
        self.species_layout = QVBoxLayout()
        self.species_group.setLayout(self.species_layout)
        self.species_herbivore = QRadioButton("Herbivore")
        self.species_carnivore = QRadioButton("Carnivore")
        self.species_layout.addWidget(self.species_herbivore)
        self.species_layout.addWidget(self.species_carnivore)
        self.species_herbivore.setChecked(True)
        self.species_group.setFixedSize(200, 80)
        self.species_layout.setAlignment(Qt.AlignHCenter)

        # Create the age label and entry
        age_layout = QHBoxLayout()
        age_label = QLabel("Age:")
        self.age = QLineEdit()
        self.age.setFixedSize(100, 40)
        age_layout.addWidget(age_label)
        age_layout.addWidget(self.age)

        # Create the weight label and entry
        weight_layout = QHBoxLayout()
        weight_label = QLabel("Weight:")
        self.weight = QLineEdit()
        self.weight.setFixedSize(100, 40)
        weight_layout.addWidget(weight_label)
        weight_layout.addWidget(self.weight)

        # Create the number of animals label and entry
        amount_layout = QHBoxLayout()
        amount_label = QLabel("Amount:")
        self.amount = QLineEdit()
        self.amount.setFixedSize(100, 40)
        amount_layout.addWidget(amount_label)
        amount_layout.addWidget(self.amount)

        # Create the add button
        add = QPushButton("Add")
        add.setFixedSize(200, 200)
        add.clicked.connect(self.populate)

        # Create the reset button
        reset = QPushButton("Reset population")
        reset.setFixedSize(200, 100)
        reset.clicked.connect(self.reset)

        self.age.setValidator(QIntValidator())
        self.weight.setValidator(QDoubleValidator())
        self.amount.setValidator(QIntValidator())

        # Add the input boxes to the input layout
        self.input_layout.addWidget(self.species_group)
        self.input_layout.addLayout(age_layout)
        self.input_layout.addLayout(weight_layout)
        self.input_layout.addLayout(amount_layout)
        self.input_layout.addStretch(5)
        self.input_layout.addWidget(add)
        self.input_layout.addStretch(20)
        self.input_layout.addWidget(reset)

        # Create the plot and input boxes layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.plot)
        self.layout.addLayout(self.input_layout)

        self.setLayout(self.layout)

    def populate(self):
        """Populate the island with animals."""
        j, i = VARIABLE["selected"]

        if i is None or j is None:
            msg = QMessageBox()
            msg.setText("Please select a cell by clicking on the map.")
            msg.exec_()
            return

        species = "Herbivore" if self.species_herbivore.isChecked() else "Carnivore"
        age = int(self.age.text()) if self.age.text() else None
        weight = float(self.weight.text()) if self.weight.text() else None
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
        geogr = "\n".join(VARIABLE["island"])
        VARIABLE["biosim"] = BioSim(island_map=geogr)


class Simulate(QWidget):
    """Class for simulating the population on the island."""
    def __init__(self):
        super().__init__()

        self.setGeometry(400, 200, 1000, 800)
        self.setLayout(QVBoxLayout())

        self.fig = None
        self.canvas = None

        self.species_dropdown = None
        self.parameter_dropdown = None
        self.value_slider = None
        self.label = None
        self.interval = None
        self.years = None

        self.buttons()
        self.plot()

    def buttons(self):
        """Add buttons to the window."""
        self.parameter_selection()
        self.simulate_selection()

    def parameter_selection(self):
        """Add parameter selection to the window."""
        self.species_dropdown = QComboBox()
        self.species_dropdown.addItems(["PARAMETERS", "Herbivore", "Carnivore", "Fodder"])
        self.species_dropdown.currentIndexChanged.connect(self.species_changed)

        # Create the parameter dropdown
        self.parameter_dropdown = QComboBox()
        self.parameter_dropdown.currentIndexChanged.connect(self.parameter_changed)

        # Create the value dropdown
        self.value_slider = QSlider(Qt.Horizontal)
        self.label = QLabel()

        # Create the add button
        add_button = QPushButton("Set parameter")
        add_button.clicked.connect(self.set_parameter)

        reset_parameter = QPushButton("Reset parameter")
        reset_parameter.clicked.connect(self.reset_parameter)

        reset_all_parameters = QPushButton("Reset all parameters")
        reset_all_parameters.clicked.connect(self.reset_all_parameters)
        reset_all_parameters.setFixedWidth(200)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.species_dropdown)
        top_layout.addWidget(self.parameter_dropdown)
        top_layout.addWidget(self.value_slider)
        top_layout.addWidget(self.label)
        top_layout.addWidget(add_button)
        top_layout.addWidget(reset_parameter)
        top_layout.addSpacing(100)
        top_layout.addWidget(reset_all_parameters)
        self.layout().addLayout(top_layout)

        self.parameter_changed()

    def simulate_selection(self):
        """Add simulation selection to the window."""
        box_layout = QHBoxLayout()

        box_layout.addStretch(10)

        label = QLabel("Number of years to simulate:")
        box_layout.addWidget(label)

        self.years = QComboBox()
        self.years.addItems([str(val) for val in np.arange(1, 25, 1)] +
                            [str(val) for val in np.arange(25, 525, 25)])
        self.years.setFixedWidth(100)
        self.years.setCurrentIndex(27)
        box_layout.addWidget(self.years)

        simulate_button = QPushButton("Simulate")
        simulate_button.clicked.connect(self.simulate)
        box_layout.addWidget(simulate_button)

        stop_button = QPushButton("Pause simulation")
        stop_button.clicked.connect(self.stop)
        box_layout.addWidget(stop_button)

        box_layout.addStretch(5)

        reset_button = QPushButton("Reset years")
        reset_button.clicked.connect(self.restart_years)
        reset_button.setFixedWidth(200)
        box_layout.addWidget(reset_button)

        self.layout().addLayout(box_layout)

    def species_changed(self):
        """Executed when the species selection changes."""
        species = self.species_dropdown.currentText()
        self.parameter_dropdown.clear()

        # Update the parameter dropdown based on the selected species
        if species == "Herbivore":
            self.parameter_dropdown.addItems(Herbivore.default_parameters().keys())
        elif species == "Carnivore":
            self.parameter_dropdown.addItems(Carnivore.default_parameters().keys())
        elif species == "Fodder":
            self.parameter_dropdown.addItems(["Highland", "Lowland", "Desert",
                                              "Growth reduction (alpha)", "Growth factor (delta)"])

        # Update the value dropdown based on the selected parameter
        self.parameter_changed()

    def parameter_changed(self):
        """Executed when the parameter selection changes."""
        if self.parameter_dropdown.currentText() == "":
            return

        species = self.parameter_dropdown.currentText()

        if species in ["Highland", "Lowland", "Desert"]:
            species = species[0]
        elif species == "Growth reduction (alpha)":
            species = "alpha"
        elif species == "Growth factor (delta)":
            species = "delta"

        start, stop, self.interval = self.valid_values[species]
        default = DEFAULT_PARAMETERS[self.species_dropdown.currentText()][species] / self.interval

        self.value_slider.setMinimum(int(start))
        self.value_slider.setMaximum(int(stop/self.interval))
        self.value_slider.setValue(int(default))
        self.value_slider.setSingleStep(stop)

        self.update_value()
        self.value_slider.valueChanged.connect(self.update_value)

    def update_value(self):
        self.label.setText("{:.2f}".format(self.value_slider.value() * self.interval))

    @property
    def valid_values(self):
        """Returns a dictionary of valid values for each parameter."""
        fodder = max([Island.get_fodder_parameter(ter) for ter in ["H", "L", "D"]])

        return {
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
            "H": (0, 1000, 10),
            "L": (0, 1000, 10),
            "D": (0, 1000, 10),
            "alpha": (0, 1, 0.01),
            "delta": (0, fodder, 10)
        }

    def set_parameter(self):
        """Set the parameter for the selected species."""
        species = self.species_dropdown.currentText()

        if species == "PARAMETERS":
            return

        parameter = self.parameter_dropdown.currentText()
        value = float(self.label.text())

        if species == "Herbivore":
            Herbivore.set_parameters({parameter: value})
        elif species == "Carnivore":
            Carnivore.set_parameters({parameter: value})
        elif species == "Fodder":
            if parameter in ["Highland", "Lowland", "Desert"]:
                parameter = parameter[0]
            elif parameter == "Growth reduction (alpha)":
                parameter = "alpha"
            elif parameter == "Growth factor (delta)":
                parameter = "delta"

            Island.set_fodder_parameters({parameter: value})

            # TODO: Legge til loggefunksjoner som dokumenterer når hvilke parameter ble endret.

    def reset_parameter(self):
        """Reset the parameter for the species."""
        species = self.species_dropdown.currentText()

        if species == "PARAMETERS":
            return

        parameter = self.parameter_dropdown.currentText()

        if species == "Herbivore":
            Herbivore.set_parameters({parameter: Herbivore.default_parameters()[parameter]})
        elif species == "Carnivore":
            Carnivore.set_parameters({parameter: Carnivore.default_parameters()[parameter]})
        elif species == "Fodder":
            if parameter in ["Highland", "Lowland", "Desert"]:
                parameter = parameter[0]
            elif parameter == "Growth reduction (alpha)":
                parameter = "alpha"
            elif parameter == "Growth factor (delta)":
                parameter = "delta"

            Island.set_fodder_parameters(
                {parameter: Island.default_fodder_parameters()[parameter]}
            )

    @staticmethod
    def reset_all_parameters():
        """Reset all parameters to their default values."""
        Herbivore.set_parameters(Herbivore.default_parameters())
        Carnivore.set_parameters(Carnivore.default_parameters())
        Island.set_fodder_parameters(Island.default_fodder_parameters())

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
        years = int(self.years.currentText())
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
