from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QSplitter, QFrame, QHeaderView)
from PyQt6.QtCore import Qt


class Table(QTableWidget):
    def __init__(self, labels):
        super().__init__()
        self.setHorizontalHeaderLabels(labels)
        self.setRowCount(5)
        self.setColumnCount(1)
        self.setMaximumWidth(200)
        self.labels = {}
        for index, items in enumerate(labels):
            self.labels[items] = index

        # Set labels
        self.setVerticalHeaderLabels(labels)
        self.verticalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignRight)

        # Top Header Remover
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.horizontalHeader().setVisible(False)

    def update_table(self, calibrated_data):
        # Check if data is passed
        if not calibrated_data:
            for sensor in self.labels.keys():
                # Get index
                row = self.labels[sensor]
                # Paste a zero
                self.setItem(row, 1, QTableWidgetItem("0"))

        # If it is, send data through
        else:
            for sensor, value in calibrated_data.items():
                formatted_value = f"{value:.2f}"

                # Filter if sensor is in table listed
                if sensor in self.labels.keys():
                    # Get index of sensor
                    row = self.labels[sensor]
                    # index, column, value
                    self.setItem(row, 1, QTableWidgetItem(formatted_value))

