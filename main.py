import engine_tests, controllers
import os.path
import sys
import misc
import time
import numpy as np
import pandas as pd
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedLayout, QLineEdit, QFormLayout, QComboBox, QStackedWidget,
    QFrame
)
from PyQt6.QtGui import QFont, QPixmap
from wifi import ESP32Client

# Initialize Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window settings
        self.setWindowTitle("Fuel and Rocket Test Stand")
        self.setGeometry(100, 100, 600, 500)
        self.setMinimumSize(600, 500)

        # Tab initialize
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create Tabs
        self.home_page = HomePage()
        self.test_tab = TestTab(self.home_page)
        self.graphs_tab = GraphsTab(self.home_page)
        self.connections_tab = ConnectionsTab(self.home_page)

        # Add Tabs
        self.tabs.addTab(self.home_page, "Home")
        self.tabs.addTab(self.test_tab, "Tests")
        self.tabs.addTab(self.graphs_tab, "Graphs")
        self.tabs.addTab(self.connections_tab, "Settings")

class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        # Logo
        bgd = QPixmap("pictures/raptor bg.jpg")
        self.bgd_l = QLabel(self)
        self.bgd_l.setPixmap(bgd)
        self.bgd_l.setScaledContents(True)
        self.bgd_l.setFixedSize(120, 100)

        # Title and Subtitle
        self.title = QLabel("FARTS")
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Times", 40, QFont.Weight.DemiBold))
        # self.title.setStyleSheet("color: Blue")

        self.subtitle = QLabel('Fuel and Rocket Test Stand')
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        subt_font = QFont("Helvetica", 15, QFont.Weight.ExtraLight)
        subt_font.setItalic(True)
        self.subtitle.setFont(subt_font)

        # Current User Input Form using QFormLayout
        form_line = QFormLayout()
        form_line.setSpacing(2)
        user_message = QLabel("Current User:")

        # Store QLineEdit as an attribute so it can be accessed later
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Name")
        self.line_edit.setFixedWidth(150)

        form_line.addWidget(user_message)
        form_line.addWidget(self.line_edit)

        # Add widgets to layout and format layout
        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.bgd_l, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addStretch(1)
        layout.addLayout(form_line)
        self.setLayout(layout)

class TestTab(QWidget):
    def __init__(self, home_page_instance):
        super().__init__()
        layout = QVBoxLayout()

        self.home_page = home_page_instance

        # Dropdown Menu to switch between tests
        self.dropdown = QComboBox()
        self.dropdown.addItems(["Click Test", "Leak Test"])
        self.dropdown.currentIndexChanged.connect(self.switch_test)

        # Add items to layout
        layout.addWidget(self.dropdown, alignment=Qt.AlignmentFlag.AlignLeft)

        # All widgets should be in a stacked_widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(engine_tests.ClickTestLayout(self.home_page))
        self.stacked_widget.addWidget(engine_tests.LeakTestLayout(self.home_page))
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)

    def switch_test(self, index):
        self.stacked_widget.setCurrentIndex(index)

class GraphsTab(QWidget):
    def __init__(self, home_page_instance):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("GRAPHs"))
        self.setLayout(layout)

class ConnectionsTab(QWidget):
    def __init__(self, home_page_instance):
        super().__init__()
        layout = QVBoxLayout()
        self.home_page = home_page_instance
        # Title
        label = QLabel("Connections and Settings")
        label.setFont(QFont("Helvetica", 20, QFont.Weight.Medium))

        # Form for connections
        self.con_form_layout = QFormLayout()


        self.formline1 = QHBoxLayout()
        input1 = QLabel("Controller Connection:")
        self.status1 = QLabel("Disconnected")
        self.status1.setStyleSheet("Color: Red")
        connect1 = QPushButton("Connect")
        self.formline1.addWidget(input1)
        self.formline1.addWidget(self.status1)
        self.formline1.addStretch(1)
        self.formline1.addWidget(connect1)

        self.formline2 = QHBoxLayout()
        input2 = QLabel("DAQ Connection:")
        self.status2 = QLabel("Disconnected")
        self.status2.setStyleSheet("Color: Red")
        connect2 = QPushButton("Connect")
        self.formline2.addWidget(input2)
        self.formline2.addWidget(self.status2)
        self.formline2.addStretch(1)
        self.formline2.addWidget(connect2)

        self.con_form_layout.addRow(self.formline1)
        self.con_form_layout.addRow(self.formline2)

        # Calibration Equation editor
        self.calib = QPushButton("Adjust Calibration Equations")
        self.calib.clicked.connect(self.open_editor)

        self.calib_editor = None

        # ESP32 Client Instance
        self.esp32_client = ESP32Client()

        # Connect Signals to Update GUI
        self.esp32_client.connection_status.connect(self.update_connection_status)
        self.esp32_client.message_received.connect(self.display_esp32_message)
        self.connect_esp32()

        # Layout adjustments
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addLayout(self.con_form_layout)
        layout.addStretch(1)
        layout.addWidget(self.calib, alignment=Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

    def open_editor(self):
        """Ensures only one instance of CalibrationEditor is opened"""
        if self.calib_editor and self.calib_editor.isVisible():
            self.calib_editor.raise_()
            return
        self.calib_editor = controllers.CalibrationEditor(self.home_page)
        self.calib_editor.show()

    def connect_esp32(self):
        """Try connecting to ESP32."""
        print("Connecting to esp32")
        self.esp32_client.connect_to_esp32()


    def update_connection_status(self, is_connected):
        """Update connection status label."""
        print("Updating connection status")
        if is_connected:
            print("Show connected")
            self.status1.setText("Connected")
            self.status1.setStyleSheet("Color: Green")
        else:
            print("Not connected")
            self.status1.setText("Disconnected")
            self.status1.setStyleSheet("Color: Red")

    def send_command(self, command):
        """Send a command to ESP32."""
        self.esp32_client.send_command(command)

    def display_esp32_message(self, message):
        """Display ESP32 messages in GUI."""
        print(f"[ESP32]: {message}")  # You can update this to display in a GUI element




if __name__ == "__main__":
    # Initialize APP
    app = QApplication(sys.argv)

    # Trigger event logger
    misc.event_logger("Program Started", "SYSTEM")
    app.aboutToQuit.connect(lambda: misc.event_logger("Program End", "SYSTEM"))

    # Open window
    window = MainWindow()
    window.show()
    # Close window
    sys.exit(app.exec())

