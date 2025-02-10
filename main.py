import engine_tests, controllers, table_controlller
import sys
from file_handler import load_json
import fire_controller
import misc
from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QLineEdit, QFormLayout, QComboBox, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QFrame
)
from PyQt6.QtGui import QFont, QPixmap
import wifi


# Initialize Window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Main window settings
        self.setWindowTitle("Fuel and Rocket Test Stand")
        self.setGeometry(100, 100, 600, 500)
        self.setMinimumSize(600, 600)

        # Tab initialize
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Init esp32 server
        config = load_json("config.json")

        self.esp_client = wifi.ESP32Client(ip=config["ESP32_IP"], port=config["PORT"])

        # Create Tabs
        self.home_page = HomePage()
        self.fire_tab = FireTab(self.home_page, self.esp_client,sensors=config["SENSORS"], valves=config["VALVES"],
                                colormap=config["Valve_ColorMap"])
        self.test_tab = TestTab(self.home_page, self.esp_client,
                                config=config, colormap=config["Valve_ColorMap"])
        self.graphs_tab = ValuesTab(self.home_page, self.esp_client)
        self.connections_tab = ConnectionsTab(self.home_page, self.esp_client)

        # Add Tabs
        self.tabs.addTab(self.home_page, "Home")
        self.tabs.addTab(self.fire_tab, "Fire")
        self.tabs.addTab(self.test_tab, "Tests")
        self.tabs.addTab(self.graphs_tab, "Values")
        self.tabs.addTab(self.connections_tab, "Settings")

        # Flag a tab change
        self.tabs.currentChanged.connect(self.on_tab_change)

    def on_tab_change(self,index):
        """Detects when tabs change"""
        if index != self.tabs.indexOf(self.fire_tab):
            if self.fire_tab.stacked.currentIndex() == 1:
                self.fire_tab.stacked.setCurrentIndex(0)


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
        self.title = misc.label_maker("FARTS", size=40, weight=QFont.Weight.DemiBold)
        self.title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title.setFont(QFont("Times", 40, QFont.Weight.DemiBold))

        self.subtitle = misc.label_maker("Fuel and Rocket Test Stand", size=15,
                                         weight=QFont.Weight.ExtraLight, ital=True)
        self.subtitle.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Current User Input Form using QFormLayout
        form_line = QFormLayout()
        form_line.setSpacing(2)
        user_message = QLabel("Current User:")

        # Store QLineEdit as an attribute, so it can be accessed later
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

class FireTab(QWidget):
    def __init__(self, home_page_instance, esp_client, sensors, valves, colormap):
        super().__init__()
        self.home_page = home_page_instance
        layout = QVBoxLayout()
        esp_client = esp_client


        # Stacked widget
        self.stacked = QStackedWidget()

        self.fire_controller_page = fire_controller.FireController(esp_client=esp_client,
                                                                   sensors=sensors, valves=valves, colormap=colormap)
        self.login = fire_controller.FireLogin()

        self.login.login_successful.connect(self.switch)

        self.stacked.addWidget(self.login)
        self.stacked.addWidget(self.fire_controller_page)

        layout.addWidget(self.stacked)

        self.setLayout(layout)


    def switch(self):
        if self.stacked.currentIndex() == 0:
            self.stacked.setCurrentIndex(1)
        else:
            self.stacked.setCurrentIndex(0)

class TestTab(QWidget):
    def __init__(self, home_page_instance, esp32_client, config, colormap):
        super().__init__()
        layout = QVBoxLayout()
        self.esp32_client = esp32_client
        self.home_page = home_page_instance
        self.config = config


        # Dropdown Menu to switch between tests
        self.dropdown = QComboBox()
        self.dropdown.addItems(["Click Test", "Leak Test"])
        self.dropdown.currentIndexChanged.connect(self.switch_test)

        # Add items to layout
        layout.addWidget(self.dropdown, alignment=Qt.AlignmentFlag.AlignLeft)

        # All widgets should be in a stacked_widget
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(engine_tests.ClickTestLayout(self.home_page, esp32_client, config=self.config, colorMap=colormap))
        self.stacked_widget.addWidget(engine_tests.LeakTestLayout(self.home_page, esp32_client, config=self.config))
        layout.addWidget(self.stacked_widget)

        self.setLayout(layout)

    def switch_test(self, index):
        self.stacked_widget.setCurrentIndex(index)

class ValuesTab(QWidget):
    def __init__(self, home_page_instance, esp_client):
        super().__init__()
        self.home_page = home_page_instance
        self.esp_client = esp_client
        layout = QVBoxLayout()
        label = misc.label_maker("Values")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Horizontal Seperator
        layout.addWidget(misc.horizontal_line())

        # Table Layout
        tlayout = QHBoxLayout()

        # Table List
        self.tableL = table_controlller.Table(["High Press 1", "High Press 2", "LOX Tank 1",
                                               "LOX Tank 2", "Fuel Tank 1", "Fuel Tank 2"])
        self.tableR = table_controlller.Table(["LOX Dome Reg", "Fuel Dome Reg", "LOX Inlet",
                                               "Fuel Inlet", "Chamber 1", "Chamber 2"])

        # Record Data Button
        self.record = QPushButton("Record Data")
        self.record.clicked.connect(self.record_data)
        self.record.setMinimumHeight(50)
        self.record.setFont(QFont('Helvetica', 20, QFont.Weight.Bold))
        self.record.setStyleSheet("""
            QPushButton {background-color: #D86456; color: White;}
            QPushButton:hover {background-color: #AD4242; color: #AD4242;}
            """)
        self.is_recording = False


        # Layout
        tlayout.addStretch(1)
        tlayout.addWidget(self.tableL)
        tlayout.addWidget(self.tableR)
        tlayout.addStretch(1)
        layout.addLayout(tlayout)
        layout.addStretch(1)
        layout.addWidget(self.record)
        self.setLayout(layout)

        self.esp_client.message_received.connect(self.update_tables)



    def update_tables(self, calibrated_data):
        """Updates table cell with calibrated data"""
        try:
            self.tableR.update_table(calibrated_data)
            self.tableL.update_table(calibrated_data)
        except Exception as e:
            misc.event_logger("DEBUG", "SYSTEM", f"ValTab-update_tables: {e}")


    def record_data(self):
        """Starts and Stops data recording"""
        if self.record.text() == "Record Data":
            self.record.setStyleSheet("""
            QPushButton {background-color: #858585; color: White;}
            QPushButton:hover {background-color: #AD4242; color: #AD4242;}
            """)
            self.record.setText("Stop Recording")
            misc.event_logger("Recording Started", misc.get_name(self.home_page))
            self.is_recording = True

        else:
            self.record.setText("Record Data")
            self.record.setStyleSheet("""
            QPushButton {background-color: #D86456; color: White;}
            QPushButton:hover {background-color: #AD4242; color: #AD4242;}
            """)
            misc.event_logger("Recording Stopped", misc.get_name(self.home_page))
            self.is_recording = False

class ConnectionsTab(QWidget):
    def __init__(self, home_page_instance, espclient):
        super().__init__()
        layout = QVBoxLayout()
        self.home_page = home_page_instance
        # Title
        label = QLabel("Connections and Settings")
        label.setFont(QFont("Helvetica", 20, QFont.Weight.Medium))

        # Form for connections
        self.connection_form_layout = QFormLayout()

        # Form creation
        self.formline1 = QHBoxLayout()
        input1 = QLabel("Controller Connection:")
        self.status1 = QLabel("Disconnected")
        self.status1.setStyleSheet("Color: Red")
        self.discon1 = QPushButton("Disconnect")
        self.connect1 = QPushButton("Connect")
        self.connect1.clicked.connect(self.connect_esp32)
        self.discon1.clicked.connect(self.close_esp)
        self.formline1.addWidget(input1)
        self.formline1.addWidget(self.status1)
        self.formline1.addStretch(1)
        self.formline1.addWidget(self.discon1)
        self.formline1.addWidget(self.connect1)


        self.connection_form_layout.addRow(self.formline1)

        # Calibration Equation editor
        self.calib = QPushButton("Adjust Calibration Equations")
        self.calib.clicked.connect(self.open_editor)
        self.calib_maker = QPushButton("Create Calibration Equations")
        self.calib_maker.clicked.connect(self.open_maker)

        self.calib_editor = None

        # ESP32 Client Instance
        self.esp32_client = espclient

        # Connect Signals to Update GUI
        self.esp32_client.connection_status.connect(self.update_connection_status)
        self.connect_esp32()


        # Layout adjustments
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(misc.horizontal_line())
        layout.addLayout(self.connection_form_layout)
        layout.addStretch(1)
        layout.addWidget(self.calib, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(self.calib_maker, alignment=Qt.AlignmentFlag.AlignLeft)
        self.setLayout(layout)

    def open_editor(self):
        """Ensures only one instance of CalibrationEditor is opened"""
        if self.calib_editor and self.calib_editor.isVisible():
            self.calib_editor.raise_()
            return
        self.calib_editor = controllers.CalibrationEditor(self.home_page)
        self.calib_editor.show()

    def open_maker(self):
        """Ensures only one instance of CalibrationMaker is opened"""
        if hasattr(self, 'calib_maker_window') and self.calib_maker.isVisible():
            self.calib_maker_window.raise_()
            return
        self.calib_maker = controllers.CalibrationMaker()
        self.calib_maker.show()

    def connect_esp32(self):
        """Try connecting to ESP32."""
        self.esp32_client.connect_to_esp32()
    def close_esp(self):
        """Close ESP32 connection"""
        self.esp32_client.stop()


    def update_connection_status(self, is_connected):
        """Update connection status label."""
        if is_connected:
            self.status1.setText("Connected")
            self.status1.setStyleSheet("Color: Green")
            self.connect1.setEnabled(False)
            self.discon1.setEnabled(True)

            if not hasattr(self, "listener_thread") or self.listener_thread is None or self.listener_thread.isRunning():
                self.listener_thread = QThread()
                self.esp32_client.moveToThread(self.listener_thread)
                self.listener_thread.started.connect(self.esp32_client.listen_for_responses)
                self.listener_thread.start()

        else:
            self.status1.setText("Disconnected")
            self.status1.setStyleSheet("Color: Red")
            self.connect1.setEnabled(True)
            self.discon1.setEnabled(False)

            if hasattr(self, "listener_thread") and self.listener_thread:

                self.listener_thread.quit()
                self.listener_thread.wait()
                self.listener_thread = None



    def send_command(self, command):
        """Send a command to ESP32."""
        self.esp32_client.send_command(command)




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

