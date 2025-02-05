import sys
import random
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton
)
from PyQt6.QtCore import QTimer


class LiveTableApp(QMainWindow):
    """PyQt6 GUI to update a 4x5 table from top to bottom every minute after clicking a button."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("5-Minute Click-to-Start Test")
        self.resize(500, 300)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create Table (4 Columns, 5 Rows)
        self.table = QTableWidget(5, 4)
        self.table.setHorizontalHeaderLabels(["Column 1", "Column 2", "Column 3", "Column 4"])
        layout.addWidget(self.table)

        # Start Button
        self.start_button = QPushButton("Start Test")
        self.start_button.clicked.connect(self.start_test)
        layout.addWidget(self.start_button)

        # Timer for updating every minute (disabled until button is clicked)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.current_row = 0  # Track the row being filled

    def start_test(self):
        """Starts the 5-minute test when the button is clicked."""
        self.current_row = 0  # Reset row count in case of restart
        self.timer.start(60000)  # Update every 1 minute
        self.start_button.setEnabled(False)  # Disable button after starting
        self.update_table()  # Fill the first row immediately

    def update_table(self):
        """Fills one row every minute from top to bottom."""
        if self.current_row >= 5:  # Stop after filling all 5 rows
            self.timer.stop()
            print("Test completed. Stopping updates.")
            return

        # Insert new random data in the current row
        for col in range(4):
            new_value = str(random.randint(1, 100))  # Replace with actual data source
            self.table.setItem(self.current_row, col, QTableWidgetItem(new_value))

        print(f"Filled row {self.current_row + 1}")  # Debugging print
        self.current_row += 1  # Move to the next row for the next update


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LiveTableApp()
    window.show()
    sys.exit(app.exec())
