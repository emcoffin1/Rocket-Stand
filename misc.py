from datetime import datetime
import pandas as pd
import os
from PyQt6.QtWidgets import QLabel, QFrame, QMessageBox
from PyQt6.QtGui import QFont
import json
import sys, csv, json
import file_handler
from scipy.optimize import curve_fit
from numpy import exp, inf, sum, mean, array



def event_logger(event, user, comments=''):
    # Format username to a specific size
    if len(user) < 10:
        user = f"{user}" + " " * (10 - len(user))
    else:
        user = user[0:10]

    # Access file
    log_file = f"Loggers/event_log_{datetime.now().strftime('%Y-%m-%d')}.csv"

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


def data_logger(calibrated_data):
    """Logs calibrated data when record data turned on"""
    log_file = f"Loggers/data_log_{datetime.now().strftime('%Y-%m-%d')}.csv"

    new_entry = pd.DataFrame({
        "": [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
        "LOX Vent": [calibrated_data.get("LOX Vent", "")],
        "Fuel Vent": [calibrated_data.get("Fuel Vent", "")],
        "LOX Dome Vent": [calibrated_data.get("LOX Dome Vent", "")],
        "LOX Dome Reg": [calibrated_data.get("LOX Dome Reg", "")],
        "Fuel Dome Vent": [calibrated_data.get("Fuel Dome Vent", "")],
        "Fuel Dome Reg": [calibrated_data.get("Fuel Dome Reg", "")],
        "LOX MV": [calibrated_data.get("LOX MV", "")],
        "Fuel MV": [calibrated_data.get("Fuel MV", "")],
        "High Pressure": [calibrated_data.get("High Pressure", "")],
        "High Vent": [calibrated_data.get("High Vent", "")],
    })

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
        users = file_handler.load_json("verified_user.json")
        if user in users:
            if users[user] == password:
                return True
            else:
                QMessageBox.warning(None,"Wrong Password", "Please try again")
        else:
            return False

    except Exception as e:
        event_logger("ERROR", "SYSTEM", "Verified Users file does not exist")


class CurverFitter:
    def __init__(self, x_data, y_data):
        self.x_data = array(x_data, dtype=float)
        self.y_data = array(y_data, dtype=float)
        self.models = {
            "Linear": self.linear,
            "Quadratic": self.quadratic,
            "Exponential": self.exponential
        }
        self.best_model = None
        self.best_params = None
        self.best_r2 = -inf



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
        ss_tot = sum((y_true - mean(y_true)) **2)
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
        return a * exp(b*x)
