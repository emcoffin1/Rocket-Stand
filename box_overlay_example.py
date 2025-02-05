import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QRect

class ImageWithBoxes(QWidget):
    def __init__(self):
        super().__init__()

        # Load the image
        self.pixmap = QPixmap("pictures/raptor bg.jpg")  # Change to your image file

        # Resize the widget to match the image
        self.setFixedSize(self.pixmap.width(), self.pixmap.height())

        # Define box positions and colors
        self.boxes = [
            {"rect": QRect(50, 50, 100, 100), "color": QColor(255, 0, 0, 150)},  # Box 1 (Initially Red)
            {"rect": QRect(200, 50, 100, 100), "color": QColor(0, 255, 0, 150)},  # Box 2 (Green)
            {"rect": QRect(350, 50, 100, 100), "color": QColor(0, 0, 255, 150)},  # Box 3 (Blue)
        ]

        # List of colors to cycle through
        self.color_cycle = [
            QColor(255, 0, 0, 150),    # Red
            QColor(0, 255, 0, 150),    # Green
            QColor(0, 0, 255, 150),    # Blue
            QColor(255, 255, 0, 150),  # Yellow
            QColor(255, 0, 255, 150),  # Magenta
            QColor(0, 255, 255, 150)   # Cyan
        ]
        self.current_color_index = 0  # Start at first color

    def paintEvent(self, event):
        """ Custom drawing function to overlay boxes on the image """
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self.pixmap)  # Draw the image

        for box in self.boxes:
            painter.setBrush(box["color"])
            painter.setPen(Qt.GlobalColor.black)  # Black border
            painter.drawRect(box["rect"])  # Draw the box

    def cycle_box_color(self, index):
        """ Cycle through the list of colors for a specific box """
        if 0 <= index < len(self.boxes):
            self.current_color_index = (self.current_color_index + 1) % len(self.color_cycle)
            self.boxes[index]["color"] = self.color_cycle[self.current_color_index]
            self.update()  # Redraw the widget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image with Overlayed Boxes")

        self.image_widget = ImageWithBoxes()

        # Button to cycle box colors
        self.button = QPushButton("Cycle Box 1 Color")
        self.button.clicked.connect(lambda: self.image_widget.cycle_box_color(0))

        # Layout setup
        layout = QVBoxLayout()
        layout.addWidget(self.image_widget)
        layout.addWidget(self.button)
        self.setLayout(layout)

# Run Application
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
