"""Graphical user interface for ECOL100."""


from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QLabel, QPushButton, QMessageBox,
                             QTabWidget, QMainWindow, QVBoxLayout, QGraphicsView, QGraphicsScene)
from PyQt5.QtGui import QPainter, QPen, QPixmap, QColor, QBrush
from PyQt5.QtCore import QRect, Qt, QRectF
from PyQt5.QtGui import QTransform


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
        self.populate = QWidget()
        self.populate_layout = QVBoxLayout()
        self.populate.setLayout(self.populate_layout)
        self.populate_label = QLabel('This is the second tab')
        self.populate_layout.addWidget(self.populate_label)
        self.tabs.addTab(self.populate, 'Populate')


class Draw(QWidget):
    """Class for drawing the island."""
    def __init__(self, island=None):
        """
        Initialises the window.

        Parameters
        ----------
        island : list of str, optional
        """
        super().__init__()

        self.island = ["W" * 10 for _ in range(10)] if island is None else island

        self.colours = {
            "W": "#95CBCC",
            "H": "#E8EC9E",
            "L": "#B9D687",
            "D": "#FFEEBA"
        }

        self.setGeometry(400, 200, 1000, 800)
        self.setWindowTitle("Model herbivores and carnivores on an island")

        self.plot = IslandPlot(self.island)
        self.plot.setGeometry(QRect(0, 0, 800, 800))
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.plot)

        self.color_layout = None
        self.color_widget = None
        self.bigger_button = None
        self.smaller_button = None

        self.buttons()
        self.plot.update()

    def buttons(self):
        """Add buttons to the window."""
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
        self.color_widget.setGeometry(QRect(880, 300, 450, 450))

        # Modify map:
        self.bigger_button = QPushButton("Bigger", self)
        self.bigger_button.setGeometry(QRect(880, 0, 110, 100))
        self.bigger_button.clicked.connect(self.bigger)

        self.smaller_button = QPushButton("Smaller", self)
        self.smaller_button.setGeometry(QRect(880, 100, 110, 100))
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
        if len(self.island[0]) >= 44:
            return

        new = ["W" * (len(self.island[0]) + 2)]
        for row in self.island:
            _row = "W" + row + "W"
            new.append(_row)
        new.append("W" * (len(self.island[0]) + 2))

        self.island = new
        self.plot.update(self.island)

    def smaller(self):
        """Decrease the size of the map."""
        if len(self.island[0]) <= 4:
            return

        new = ["W" * (len(self.island[0]) - 2)]
        for row in self.island[2:-2]:
            _row = "W" + row[2:-2] + "W"
            new.append(_row)
        new.append("W" * (len(self.island[0]) - 2))

        self.island = new
        self.plot.update(self.island)

# Next page: use self.plot.island instead of self.island


class IslandPlot(QGraphicsView):
    def __init__(self, island, terrain="W", size=800):
        super().__init__()

        self.island = island
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

    def update(self, island=None):
        self.island = island if island is not None else self.island
        self.scene.clear()
        pen = QPen(Qt.black)
        pen.setWidthF(0.2)
        for j, row in enumerate(self.island):
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
        self.mouseMoveEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            position = self.mapToScene(event.pos())
            i = int(position.x() // self.size)
            j = int(position.y() // self.size)

            if 0 < i < len(self.island[0])-1 and 0 < j < len(self.island)-1:
                self.island[j] = self.island[j][:i] + self.terrain + self.island[j][i + 1:]
                self.draw_cell(i, j)

    def draw_cell(self, x, y):
        pen = QPen(Qt.black)
        pen.setWidthF(0.2)
        brush = QBrush(QColor(self.colours[self.terrain]))

        self.scene.addRect(x * self.size, y * self.size, self.size, self.size, pen, brush)


if __name__ == "__main__":

    run()
