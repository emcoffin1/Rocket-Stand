import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QTableWidget, QHeaderView, QTableWidgetItem, QHBoxLayout, QSplitter
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush
import misc
import table_controlller
import test_logic
#import test_logic
from controllers import CalibrationProcessor
from wifi import ESP32Client
from file_handler import load_json



class ClickTestLayout(QWidget):
    def __init__(self, home_page_instance, esp32_client, config, colorMap):
        super().__init__()
        # Init passed through items
        self.home_page = home_page_instance
        self.esp32_client = esp32_client
        self.colorMap = colorMap
        self.config = config


        # Init primary layout
        layout = QVBoxLayout()

        # Splitters
        value_state_splitter = QSplitter(Qt.Orientation.Horizontal)
        value_state_splitter.setSizes([300,300])

        # Label
        self.label = self.title_section()

        # Left side
        self.left_t = self.table_values()

        # Right side
        self.right_t = self.test_values()

        # Start Button
        self.start_button = self.start_test_section()

        # Test logic
        self.altMap = {"red": 0, "yellow": 1, "green": 2}

        self.test = test_logic.ClickTest_logic(esp_client=self.esp32_client, config=self.config,
                                               tables=self.table_R, label=self.cur_sens, colorMap=self.altMap)

        # Form Layout
        value_state_splitter.addWidget(self.left_t)
        value_state_splitter.addWidget(self.right_t)


        # Layout
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(misc.horizontal_line())
        layout.addWidget(value_state_splitter)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def title_section(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Label
        label_title = misc.label_maker("Click Test")

        layout.addWidget(label_title)
        layout.addWidget(misc.horizontal_line())
        widget.setLayout(layout)

        return widget
    def table_values(self):
        # Init widget and layout
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Init table and text
        label = misc.label_maker("Position", size=15, weight=QFont.Weight.DemiBold)

        self.table_L = table_controlller.Controller_Spread(labels=self.config["VALVES"], colorMap=self.altMap)

        # Make layout
        layout.addWidget(label)
        layout.addLayout(self.table_L)
        widget.setLayout(layout)
        return widget

    def test_values(self):
        # Init widget and layout
        widget = QWidget()
        over_layout = QVBoxLayout(widget)
        layout = QHBoxLayout()

        starting_value = {}
        # Set all test value to 0
        for x in self.config["VALVES"]:
            starting_value[x] = 0

        # Init table and labels
        self.table_R = table_controlller.Controller_Spread(labels=self.config["VALVES"], colorMap=self.colorMap)
        label = misc.label_maker("Test Check", size=15, weight=QFont.Weight.DemiBold)
        self.cur_sens = misc.label_maker("Inactive")
        self.table_R.update_states(states=starting_value)


        # Layout
        over_layout.addWidget(label)
        layout.addLayout(self.table_R)
        layout.addStretch(1)
        layout.addWidget(self.cur_sens)
        layout.addStretch(2)
        over_layout.addLayout(layout)
        widget.setLayout(over_layout)

        return widget

    def start_test_section(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Start Button
        self.start_b = QPushButton("Start Test")
        self.start_b.resize(50, 75)
        self.start_b.setStyleSheet('background-color: #BF1F0C; color: White')
        self.start_b.clicked.connect(self.run_test)

        # Layout
        layout.addWidget(self.start_b)
        widget.setLayout(layout)

        return widget

    def update_tables(self, data=None, confirmed=None):
        """Update the tables as data comes in (left) and as tests are confirmed (right)"""
        self.table_R.update_states(states=confirmed)
        self.table_L.update_states(states=data)

    def run_test(self):
        """Begin Running the test"""
        self.test.start_test()


class LeakTestLayout(QWidget):
    def __init__(self, home_page_instance, esp32_client, config):
        super().__init__()
        self.home_page = home_page_instance
        self.esp32_client = esp32_client
        self.config = config
        layout = QVBoxLayout()
        # Test Title
        label = misc.label_maker("Leak Test")

        # Value Table
        self.table = QTableWidget(7,4)
        self.table.setHorizontalHeaderLabels(['Fuel Tank PT', "LOX Tank PT", "Pneumatics", "High Pressure PT"])
        self.table.setVerticalHeaderLabels(["0 min","1 min", "2 min", "3 min", "4 min", "5 min", "Average"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("alternate-background-color: lightgray; background-color: white;")
        self.table.setFixedHeight(self.table.verticalHeader().length() + self.table.horizontalHeader().height() + 2)

        # Start Button
        self.start_b = QPushButton("Start Test")
        self.start_b.resize(50, 75)

        self.start_b.setStyleSheet('background-color: #BF1F0C; color: White')
        self.start_b.clicked.connect(self.confirm_start)

        # Timer
        self.test_timer = QLabel("0:00")
        self.test_timer.setFont(QFont("Arial", 20))

        # Stylize Layout
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(misc.horizontal_line())
        layout.addWidget(self.table)
        layout.addWidget(misc.horizontal_line())
        layout.addWidget(self.test_timer, alignment=Qt.AlignmentFlag.AlignHCenter)
        layout.addStretch(1)
        layout.addWidget(self.start_b, alignment=Qt.AlignmentFlag.AlignBottom)

        # Starts Calibrator
        self.calibration_processor = CalibrationProcessor()
        self.setLayout(layout)

        # Starts timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.time_elapsed = 0
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)


        self.sensor_values = {"FTPT": [], "LTPT": [], "Pneum": [], "HPPT": []}
        self.current_row = 0



    def confirm_start(self):
        reply = QMessageBox.question(
            self,
            "Confirm Test Start",
            "Are you sure you would like to start a LEAK TEST",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.start_test()
        else:
            pass

    def start_test(self):
        misc.event_logger("Leak Test Started", misc.get_name(self.home_page))
        self.esp32_client.send_command("START_LEAK_TEST")


        # Begin Test
        self.time_elapsed = 0
        self.test_timer.setText("0:00")
        self.time_timer.start(1000)
        self.current_row = 0
        self.sensor_values = {"FTPT": [], "LTPT": [], "Pneum": [], "HPPT": []}
        self.clear_table()
        self.timer.start(500)
        self.start_b.setEnabled(False)
        self.update_table()

    def update_table(self):
        if self.current_row >= 6:
            self.timer.stop()
            self.start_b.setEnabled(True)
            self.calculate_avg()
            return

        new_values = {
           "FTPT": round(random.uniform(50, 55), 2),
           "LTPT": round(random.uniform(50, 52), 2),
           "Pneum": round(random.uniform(50, 52), 2),
           "HPPT": round(random.uniform(50, 75), 2),
        }
        for key in self.sensor_values:
            self.sensor_values[key].append(new_values[key])

        for col, key in enumerate(self.sensor_values.keys()):
            self.table.setItem(self.current_row, col, QTableWidgetItem(str(new_values[key])))

        self.current_row += 1

    def calculate_avg(self):
        avg_diff = {}
        self.time_timer.stop()

        for key in self.sensor_values:
            total_diff = sum(
                abs(self.sensor_values[key][i] - self.sensor_values[key][i - 1])
                for i in range(1, len(self.sensor_values[key]))
            )
            avg_diff[key] = total_diff / (len(self.sensor_values[key]) - 1)


        for col, key in enumerate(self.sensor_values.keys()):
            if key == "HPPT":
                value = f"{avg_diff[key]:.2f}"
                item = QTableWidgetItem(value)

                if avg_diff[key] > 10:
                    item.setForeground(QBrush(QColor("red")))
                else:
                    item.setForeground(QBrush(QColor('green')))

                self.table.setItem(6, col, item)

            else:
                value = f"{avg_diff[key]:.2f}"
                item = QTableWidgetItem(value)

                if avg_diff[key] > 1:
                    item.setForeground(QBrush(QColor("red")))
                else:
                    item.setForeground(QBrush(QColor('green')))

                self.table.setItem(6, col, item)


        misc.event_logger("Leak Test Completed", misc.get_name(self.home_page), comments=self.sensor_values)


    def clear_table(self):
        for row in range(7):
            for col in range(4):
                self.table.setItem(row,col, QTableWidgetItem(""))


    def update_time(self):
        self.time_elapsed += 1
        minutes = self.time_elapsed // 60
        seconds = self.time_elapsed % 60
        self.test_timer.setText(f"{minutes}:{seconds:02d}")









