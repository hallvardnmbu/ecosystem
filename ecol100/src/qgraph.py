"""Graphical user interface for ECOL100."""


from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox,
                             QTabWidget, QMainWindow, QVBoxLayout, QGraphicsView, QGraphicsScene)
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QBrush
from PyQt5.QtCore import QRect, Qt, QRectF
from PyQt5.QtGui import QTransform
from PyQt5.QtWidgets import (
    QButtonGroup,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QWidget,
    QGroupBox,
)
from PyQt5.QtGui import QDoubleValidator, QIntValidator


variable = {
    "island": ["W" * 10 for _ in range(10)],
    "population": [],
    "selected": (None, None)
}


def run():
    """Initialises and starts the application."""
    app = QApplication([])
    window = ECOL100()
    window.show()
    app.exec_()


class ECOL100(QMainWindow):
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

        self.tabs.currentChanged.connect(self.drawing)

    def drawing(self, index):
        """Resets the population when switching to drawing tab."""
        if index == 0:
            variable["population"] = []
        if index == 1:
            self.populate.plot.update()


class Draw(QWidget):
    """Class for drawing the island."""
    def __init__(self):
        """
        Initialises the window.

        Parameters
        ----------
        island : list of str, optional
        """
        super().__init__()

        self.colours = {
            "W": "#95CBCC",
            "H": "#E8EC9E",
            "L": "#B9D687",
            "D": "#FFEEBA"
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
        self.plot.terrain = name
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
        if len(variable["island"][0]) >= 44:
            return

        new = ["W" * (len(variable["island"][0]) + 2)]
        for row in variable["island"]:
            _row = "W" + row + "W"
            new.append(_row)
        new.append("W" * (len(variable["island"][0]) + 2))

        variable["island"] = new
        variable["population"] = []
        self.plot.update()

    def smaller(self):
        """Decrease the size of the map."""
        if len(variable["island"][0]) <= 4:
            return

        new = ["W" * (len(variable["island"][0]) - 2)]
        for row in variable["island"][2:-2]:
            _row = "W" + row[2:-2] + "W"
            new.append(_row)
        new.append("W" * (len(variable["island"][0]) - 2))

        variable["island"] = new
        variable["population"] = []
        self.plot.update()


class Map(QGraphicsView):
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
        self.scene.clear()
        pen = QPen(Qt.black)
        pen.setWidthF(0.2)
        for j, row in enumerate(variable["island"]):
            for i, cell in enumerate(row):
                brush = QBrush(QColor(self.colours[cell]))
                rect = QRectF(i * self.size, j * self.size, self.size, self.size)
                self.scene.addRect(rect, pen, brush)
        self.scene.setSceneRect(self.scene.itemsBoundingRect())
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)
        if self.width() > self.scene.width() or self.height() > self.scene.height():
            self.fitInView(self.scene.sceneRect(), Qt.IgnoreAspectRatio)

    def resizeEvent(self, event):
        self.fitInView(self.scene.sceneRect(), Qt.KeepAspectRatio)

    def mousePressEvent(self, event):
        if self.can_draw:
            self.mouseMoveEvent(event)

        if event.buttons() == Qt.LeftButton and self.terrain == "SELECT":
            position = self.mapToScene(event.pos())
            i = int(position.x() // self.size)
            j = int(position.y() // self.size)

            if variable["island"][j][i] != "W":
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

                variable["selected"] = (i, j)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.can_draw:
            position = self.mapToScene(event.pos())
            i = int(position.x() // self.size)
            j = int(position.y() // self.size)

            if 0 < i < len(variable["island"][0])-1 and 0 < j < len(variable["island"])-1:
                variable["island"][j] = (variable["island"][j][:i] +
                                         self.terrain +
                                         variable["island"][j][i + 1:])

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
    def __init__(self):
        """
        Initialises the window.

        Parameters
        ----------
        island : list of str
        population : list of dict, optional
        """
        super().__init__()

        self.initialise()

    def initialise(self):
        self.plot = Map(can_draw=False, terrain="SELECT")
        self.plot.setGeometry(QRect(0, 0, 800, 800))

        # Create the input boxes layout
        self.input_layout = QVBoxLayout()

        txt = QLabel("Click on a cell to add animal(s).")
        txt.setFixedSize(200, 40)

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
        self.add = QPushButton("Add")
        self.add.setFixedSize(200, 200)
        self.add.clicked.connect(self.add_info)

        self.age.setValidator(QIntValidator())
        self.weight.setValidator(QDoubleValidator())
        self.amount.setValidator(QIntValidator())

        # Add the input boxes to the input layout
        self.input_layout.addWidget(txt)
        self.input_layout.addWidget(self.species_group)
        self.input_layout.addLayout(age_layout)
        self.input_layout.addLayout(weight_layout)
        self.input_layout.addLayout(amount_layout)
        self.input_layout.addWidget(self.add)

        # Create the plot and input boxes layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.plot)
        self.layout.addLayout(self.input_layout)

        self.setLayout(self.layout)

    def add_info(self):
        pass


if __name__ == "__main__":

    run()
