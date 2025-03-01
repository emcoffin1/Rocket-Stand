from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
                             QSplitter, QFrame, QHeaderView, QFormLayout, QLabel,
                             QPushButton)
from PyQt6.QtCore import Qt

import misc


class Table(QTableWidget):
    def __init__(self, labels):
        super().__init__()
        self.setHorizontalHeaderLabels(labels)
        self.setRowCount(len(labels))
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
        """Updates table as new value arrive"""
        try:
            # Check if data is passed, use this if not
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
                        self.setItem(row, 0, QTableWidgetItem(formatted_value))
        except Exception as e:
            misc.event_logger("DEBUG", "SYSTEM", f"Table Editor: {e}")


class Controller_Spread(QFormLayout):
    def __init__(self, labels: list, colorMap, enabled=True):
        super().__init__()
        self.colorMap = colorMap
        self.enabled = enabled

        self.lab_val = {}

        # Sensor, Checkbox State
        for sensor in labels:
            box = QPushButton()
            box.setStyleSheet("color: Red")
            box.setMinimumSize(30, 30)
            box.setMaximumSize(30,30)
            box.setStyleSheet(f"background-color: yellow")
            box.setEnabled(self.enabled)
            label = QLabel(sensor)
            label.setAlignment(Qt.AlignmentFlag.AlignVCenter)
            self.lab_val[sensor] = box
            self.addRow(label, box)



    def update_states(self, states: dict, colorMap=None):
        """Updates valve state: red: open(0), yellow: disconnected(1), green: closed(2)"""
        # Check if colorMap is being overwritten
        if colorMap is None:

            try:
                for sensor, state in states.items():
                    # Check if sensor exists
                    if sensor in self.lab_val:
                        button = self.lab_val[sensor]
                        colorState = next((k for k, v in self.colorMap.items() if v == state), None)
                        button.setStyleSheet(f"background-color: {colorState}")

            except Exception as e:
                misc.event_logger("DEBUG", "SYSTEM", f"Table Controller: {e}")
        # Overwritten for click test
        # Send new data and map
        if colorMap is not None:
            try:
                for sensor, state in states.items():
                    # Check if sensor exists
                    if sensor in self.lab_val:
                        button = self.lab_val[sensor]
                        colorState = next((k for k, v in colorMap.items() if v == state), None)
                        button.setStyleSheet(f"background-color: {colorState}")

            except Exception as e:
                misc.event_logger("DEBUG", "SYSTEM", f"Table Controller: {e}")
