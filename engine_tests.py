import random
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox,
    QTableWidget, QHeaderView, QTableWidgetItem
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QColor, QBrush
import misc
from controllers import CalibrationProcessor
from wifi import ESP32Client



class ClickTestLayout(QWidget):
    def __init__(self, home_page_instance):
        super().__init__()
        self.home_page = home_page_instance
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Click Test"))

        # Value Label
        self.lab = QLabel("0")
        layout.addWidget(self.lab)

        # Start Button
        self.start_b = QPushButton("Start Test")
        self.start_b.resize(50,75)
        layout.addWidget(self.start_b)
        self.start_b.setStyleSheet('background-color: #BF1F0C; color: White')


        self.setLayout(layout)


class LeakTestLayout(QWidget):
    def __init__(self, home_page_instance):
        super().__init__()
        self.home_page = home_page_instance
        layout = QVBoxLayout()

        # Test Title
        label = misc.label_maker("Leak Test", weight=QFont.Weight.Medium)

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

        self.esp32_client = ESP32Client()


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









