"""New GUI."""

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor
from PyQt5.QtCore import QRect, Qt


class ECOL100:
    def __init__(self):
        app = QApplication([])
        Draw().show()
        app.exec_()


class Draw(QWidget):
    def __init__(self, island=None):
        super().__init__()

        self.island = ["W" * 10 for _ in range(10)] if island is None else island

        self.size = None
        self.selected = "W"
        self.colours = {"W": "#95CBCC",
                        "H": "#E8EC9E",
                        "L": "#B9D687",
                        "D": "#FFEEBA"}

        self.setGeometry(400, 200, 1000, 800)
        self.setWindowTitle("Model herbivores and carnivores on an island")

        self.canvas = QLabel(self)
        self.canvas.setGeometry(QRect(10, -75, 1000, 1000))
        self.canvas.setCursor(Qt.CrossCursor)
        self.canvas.mousePressEvent = self.mouse_press
        self.canvas.mouseMoveEvent = self.mouse_move

        self.color_layout = None
        self.color_widget = None
        self.bigger_button = None
        self.smaller_button = None

        self.populate = None
        self.parameters = None

        self.buttons()
        self.plot()

    def buttons(self):

        # Select colour:

        self.color_layout = QHBoxLayout()
        for name, color in self.colours.items():
            button = QPushButton(name, self)
            button.setFixedSize(30, 30)
            button.setStyleSheet(f"background-color: {color}")
            button.clicked.connect(lambda _, name=name: self.color_clicked(name))
            self.color_layout.addWidget(button)

        self.color_widget = QWidget(self)
        self.color_widget.setLayout(self.color_layout)
        self.color_widget.setGeometry(QRect(4, 4, 150, 40))

        # Modify map:

        self.bigger_button = QPushButton("Bigger", self)
        self.bigger_button.setGeometry(QRect(150, 0, 80, 30))
        self.bigger_button.clicked.connect(self.bigger)

        self.smaller_button = QPushButton("Smaller", self)
        self.smaller_button.setGeometry(QRect(150, 24, 80, 30))
        self.smaller_button.clicked.connect(self.smaller)

        # Page navigation:

        self.populate = QPushButton("Populate", self)
        self.populate.setGeometry(QRect(900, 0, 100, 30))
        self.populate.clicked.connect(lambda: Populate(self.island))

        self.parameters = QPushButton("Parameters", self)
        self.parameters.setGeometry(QRect(900, 30, 100, 30))
        self.parameters.clicked.connect(lambda: Parameters(self.island))

    def plot(self):

        self.size = 700 // len(self.island)

        pixmap = QPixmap(
            len(self.island[0]) * self.size,
            len(self.island) * self.size
        )

        painter = QPainter(pixmap)
        for y, row in enumerate(self.island):
            for x, cell in enumerate(row):

                painter.fillRect(
                    x * self.size,
                    y * self.size,
                    self.size, self.size,
                    QColor(self.colours[cell])
                )

                # Draw grid lines
                painter.setPen(QPen(Qt.black))
                painter.drawRect(
                    x * self.size,
                    y * self.size,
                    self.size - 1, self.size - 1
                )

        painter.end()

        self.canvas.setPixmap(pixmap)

    def color_clicked(self, name):
        self.selected = name
        for button in self.color_widget.findChildren(QPushButton):
            if button.text() == name:
                button.setStyleSheet(f"background-color: {self.colours[name]}; border: 2px solid black")
            else:
                button.setStyleSheet(f"background-color: {self.colours[button.text()]}")

    def mouse_press(self, event):
        self.mouse_move(event)

    def mouse_move(self, event):
        if event.buttons() == Qt.LeftButton:
            x = event.pos().x() // self.size
            y = (event.pos().y() + 2 * self.canvas.y()) // self.size

            if x <= 0 or x >= len(self.island[0])-1 or y <= 0 or y >= len(self.island)-1:
                return

            self.island[y] = self.island[y][:x] + self.selected + self.island[y][x + 1:]

            self.plot()

    def bigger(self):
        """
        Increase the size of the map.
        """
        if len(self.island[0]) >= 26:
            return

        new = ["W" * (len(self.island[0]) + 2)]
        for row in self.island:
            _row = "W" + row + "W"
            new.append(_row)
        new.append("W" * (len(self.island[0]) + 2))

        self.island = new

        self.plot()

    def smaller(self):
        """
        Decrease the size of the map.
        """
        if len(self.island[0]) <= 4:
            return

        new = ["W" * (len(self.island[0]) - 2)]
        for row in self.island[2:-2]:
            _row = "W" + row[2:-2] + "W"
            new.append(_row)
        new.append("W" * (len(self.island[0]) - 2))

        self.island = new

        self.plot()


class Populate(QWidget):

    def __init__(self, island, population=None):
        super().__init__()

        self.island = island
        self.population = [] if not population else population

        self.plot = None
        self.draw = None
        self.parameters = None

        self.buttons()

    def buttons(self):

        # Page navigation:

        self.plot = QPushButton("Plot", self)
        self.plot.setGeometry(QRect(900, 0, 100, 30))
        self.plot.clicked.connect(lambda: Plot(self.island, self.population))

        self.draw = QPushButton("Populate", self)
        self.draw.setGeometry(QRect(900, 30, 100, 30))
        self.draw.clicked.connect(lambda: ECOL100(self.island))

        self.parameters = QPushButton("Parameters", self)
        self.parameters.setGeometry(QRect(900, 60, 100, 30))
        self.parameters.clicked.connect(lambda: Parameters(self.island, self.population))


class Parameters(QWidget):

    def __init__(self, island, population=None):
        super().__init__()

        self.island = island
        self.population = [] if not population else population

        self.plot = None
        self.populate = None
        self.draw = None

        self.buttons()

    def buttons(self):

        # Page navigation:

        self.plot = QPushButton("Plot", self)
        self.plot.setGeometry(QRect(900, 0, 100, 30))
        self.plot.clicked.connect(lambda: Plot(self.island, self.population))

        self.populate = QPushButton("Parameters", self)
        self.populate.setGeometry(QRect(900, 30, 100, 30))
        self.populate.clicked.connect(lambda: Populate(self.island, self.population))

        self.draw = QPushButton("Populate", self)
        self.draw.setGeometry(QRect(900, 60, 100, 30))
        self.draw.clicked.connect(lambda: ECOL100(self.island))


class Plot(QWidget):

    def __init__(self, island, population=None):
        super().__init__()

        self.island = island

        if not population:
            self.population = []
            QMessageBox.warning(self, "Warning", "The island has not been populated yet.")
        else:
            self.population = population


if __name__ == "__main__":

    ECOL100()
