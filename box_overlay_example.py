from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QSplitter, QFrame, QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
import sys

class TabLayout(QWidget):
    def __init__(self):
        super().__init__()

        # --- Top Section: Two Horizontal Frames ---
        top_splitter = QSplitter(Qt.Orientation.Horizontal)  # Split into left & right
        left_frame = self.create_frame("Left Top")
        right_frame = self.create_frame("Right Top")
        top_splitter.addWidget(left_frame)
        top_splitter.addWidget(right_frame)
        top_splitter.setSizes([300, 300])  # Adjust initial sizes

        # --- Bottom Section: Table ---
        table = self.create_table()

        # --- Main Splitter for Top and Bottom ---
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(table)  # Table instead of a frame
        main_splitter.setSizes([200, 300])  # Adjust heights

        # --- Layout ---
        layout = QVBoxLayout(self)
        layout.addWidget(main_splitter)
        self.setLayout(layout)

        self.setWindowTitle("Tab with Table in Section")
        self.resize(600, 500)

    def create_frame(self, text):
        """Helper function to create a styled frame"""
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.Box)  # Adds a border
        frame.setStyleSheet("background-color: lightgray; border: 2px solid black;")
        return frame

    def create_table(self):
        """Creates a QTableWidget and populates it with data"""
        table = QTableWidget(5, 3)  # 5 rows, 3 columns
        table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3"])

        # Populate table with dummy data
        for row in range(5):
            for col in range(3):
                item = QTableWidgetItem(f"Row {row+1}, Col {col+1}")
                table.setItem(row, col, item)

        return table

app = QApplication(sys.argv)
window = TabLayout()
window.show()
sys.exit(app.exec())




