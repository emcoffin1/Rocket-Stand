from datetime import datetime
import pandas as pd
import os
import time
from PyQt6.QtWidgets import QLabel, QFrame, QMessageBox, QVBoxLayout, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer, Qt, pyqtSignal
import file_handler
from scipy.optimize import curve_fit
import numpy as np




def event_logger(event, user, comments=''):
    """Logs key / critical events for reference or debugging"""
    # Format username to a specific size
    if len(user) < 10:
        user = f"{user}" + " " * (10 - len(user))
    else:
        user = user[0:10]

    # Access file
    log_file = f"data/Loggers/event_log_{datetime.now().strftime('%Y-%m-%d')}.csv"

    # Format new entry
    new_entry = pd.DataFrame({
        "Timestamp": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "User": [f"    {user}"],
        "Event": [f"    {event}"],
        "Comments": [f"    {comments}"]
    })

    if os.path.exists(log_file):
        existing_data = pd.read_csv(log_file)
        updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
    else:
        updated_data = new_entry
    updated_data.to_csv(log_file, index=False)


def data_logger(calibrated_data:dict):
    """Logs calibrated data when record data turned on or during fire"""

    # Access file
    log_file = file_handler.load_csv(f"Loggers/Data_log_{datetime.now().strftime('%Y-%m-%d')}")
    new_entry = {}

    # Log Time then values
    new_entry["Time"] = [datetime.now().strftime('%H:%M:%S')]
    for sensor, value in calibrated_data.items():
        new_entry[sensor] = value
    new_entry = pd.DataFrame(new_entry)

    # If the path exists
    if os.path.exists(log_file):
        existed_data = pd.read_csv(log_file)
        updated_data = pd.concat([existed_data, new_entry], ignore_index=True)
    else:
        updated_data = new_entry
    updated_data.to_csv(log_file, index=False)


def get_name(home_page_instance):
    # Access the QLineEdit text from HomePage
    name = home_page_instance.line_edit.text()
    return name


def label_maker(input, style="Helvetica", size=20, weight=QFont.Weight.Medium, ital=False):
    label = QLabel(input)
    font = QFont(style, size, weight)
    font.setItalic(ital)
    label.setFont(font)
    return label

def horizontal_line():
    h_line = QFrame()
    h_line.setFrameShape(QFrame.Shape.HLine)
    return h_line

def check_user(user, password):
    """Checks if person logging into fire control is allowed to"""
    try:

        users = file_handler.load_json("data/Loggers/verified_users.json")

        if user in users:

            if users[user] == str(password):
                return True
            else:
                QMessageBox.warning(None,"Wrong Password", "Please try again")
        else:
            return False

    except Exception as e:
        event_logger("ERROR", "SYSTEM", f"check_user: {e}")


class CurverFitter:
    def __init__(self, x_data, y_data):
        self.x_data = np.array(x_data, dtype=float)
        self.y_data = np.array(y_data, dtype=float)
        self.models = {
            "Linear": self.linear,
            "Quadratic": self.quadratic,
            "Exponential": self.exponential
        }
        self.best_model = None
        self.best_params = None
        self.best_r2 = -np.inf


    def is_perfectly_linear(self, tolerance=1e-6):
        """Checks if fit is perfectly linear, will break software"""
        dy_dx = np.diff(self.y_data) / np.diff(self.x_data)
        if np.allclose(dy_dx, dy_dx[0]):
            a,b = np.polyfit(self.x_data, self.y_data, 1)
            return f"{a:.2f}*x + {b:.2f}"
        r = np.corrcoef(self.x_data, self.y_data)[0,1]
        if abs(r) >= 0.9999:
            a, b = np.polyfit(self.x_data, self.y_data, 1)
            return f"{a}*x + {b}"

        return False

    def get_equation(self):
        """Takes 10 x and 10 y values to compute the calibration equation"""
        if self.best_model is None:
            return "No best fit found"

        if self.best_model == "Linear":
            a, b = self.best_params
            return f"{a:.4f}*x + {b:.4f}"

        elif self.best_model == "Quadratic":
            a, b, c = self.best_params
            return f"{a:.4f}x**2 + {b:.4f}*x + {c:.4f}"

        elif self.best_model == "Exponential":
            a, b = self.best_params
            return f"{a:.4f}*exp({b:.4f}*x)"

        return "No Equation"

    def r_squared(self, y_true, y_pred):
        ss_res = sum((y_true- y_pred) ** 2)
        ss_tot = sum((y_true - np.mean(y_true)) **2)
        return 1- (ss_res/ss_tot)

    def fit_best_model(self):
        for name, func in self.models.items():
            try:
                params, _ = curve_fit(func, self.x_data, self.y_data, maxfev=10000)
                y_pred = func(self.x_data, *params)
                r2 = self.r_squared(self.y_data, y_pred)

                if r2 > self.best_r2:
                    self.best_r2 = r2
                    self.best_model = name
                    self.best_params = params

            except RuntimeError as e:
                event_logger("ERROR", "SYSTEM", f"Calibration error: {e}")

        return self.best_r2, self.best_params
    def linear(self, x, a, b):
        return a*x + b


    def quadratic(self, x, a, b, c):
        return a*x**2 + b*x + c


    def exponential(self, x, a, b):
        return a * np.exp(b*x)


class countTimer(QWidget):
    # Emits to signal end of timer only for fire sequence
    end_countdown_fire = pyqtSignal(bool)

    def __init__(self, direction="down", duration=5):
        super().__init__()

        # Setup time class
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.counting_up = False

        # Setup timer parameters
        self.duration = duration
        self.time_left = 0 if direction == "up" else duration
        self.direction = direction.lower()

        # Layout of label
        self.layout = QVBoxLayout(self)

        # UI Element
        self.label = label_maker(f"T-{5}", size=20, weight=QFont.Weight.Bold)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def format_timer(self, seconds):
        """Converts to a nicer format (MM:SS)"""
        minutes = seconds//60
        seconds = seconds % 60
        return f"{minutes:02}:{seconds:02}"

    def start_timer(self, direction=None, duration=None):
        """Starts countdown, can overwrite initial values"""
        try:
            if duration is not None:
                self.duration = duration
            if direction is not None:
                self.counting_up = (direction.lower() == "up")

            self.time_left = self.duration if not self.counting_up else 0
            self.label.setText(f"T-{str(self.format_timer(self.time_left))}")
            self.timer.start(1000)

        except Exception as e:
            event_logger("ERROR", "SYSTEM", f"start_timer: {e}")

    def update_timer(self):
        """Handles countdown and switch to T+"""
        try:
            if not self.counting_up:
                self.time_left -= 1
                self.label.setText(f"T-{str(self.format_timer(self.time_left))}")

                if self.time_left <= 0:
                    self.counting_up = True
                    self.end_countdown_fire.emit(True)

            else:
                self.time_left += 1
                self.label.setText(f"T+{str(self.format_timer(self.time_left))}")
        except Exception as e:
            event_logger("ERROR", "SYSTEM", f"update_timer: {e}")
    def stop_timer(self):
        """Stops timer manually"""
        try:
            self.timer.stop()
            self.label.setText(f"T-{self.duration}")
        except Exception as e:
            event_logger("ERROR", "SYSTEM", f"stop_timer: {e}")