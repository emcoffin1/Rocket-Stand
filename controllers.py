import json

import file_handler
import misc
from PyQt6.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton,
                             QTextEdit, QFileDialog, QMessageBox, QHBoxLayout, QLineEdit)
from PyQt6.QtGui import QClipboard, QIcon
from PyQt6.QtCore import QSize


class CalibrationMaker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibrator")
        self.resize(400,400)
        self.equation = None

        # Forms vertical input layout
        over_lay = QVBoxLayout()
        title = misc.label_maker("Calibration")
        # Forms horizontal layout
        layout = QHBoxLayout()

        # Form vertical layouts
        x_layout = QVBoxLayout()
        self.x_inputs = []
        y_layout = QVBoxLayout()
        self.y_inputs = []

        # Make X inputs
        for i in range(10):
            x_lineedit = QLineEdit()
            self.x_inputs.append(x_lineedit)
            x_layout.addWidget(x_lineedit)
        # Make Y Inputs
        for i in range(10):
            y_lineedit = QLineEdit()
            self.y_inputs.append(y_lineedit)
            y_layout.addWidget(y_lineedit)


        # Paste Equation
        #self.equation = misc.label_maker("", size=12)
        self.equation = QLineEdit()
        self.copy = QPushButton()
        self.copy.setIcon(QIcon("pictures/copy_logo.jpg"))
        self.copy.setMaximumSize(50,50)
        self.copy.setIconSize(QSize(32,32))
        self.copy.clicked.connect(self.copy_function)

        # Submit
        self.submit = QPushButton("Submit")
        self.submit.clicked.connect(self.retrieve_inputs)

        # Format
        over_lay.addWidget(title)
        over_lay.addWidget(misc.horizontal_line())

        layout.addStretch(2)
        layout.addLayout(x_layout)
        layout.addStretch(1)
        layout.addLayout(y_layout)
        layout.addStretch(2)
        over_lay.addLayout(layout)

        over_lay.addStretch(1)

        equation_line = QHBoxLayout()
        equation_line.addStretch(1)
        equation_line.addWidget(self.equation)
        equation_line.addWidget(self.copy)
        equation_line.addStretch(1)
        over_lay.addLayout(equation_line)

        over_lay.addStretch(1)
        over_lay.addWidget(self.submit)

        self.setLayout(over_lay)



    def copy_function(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.equation.text())

    def retrieve_inputs(self):
        x_values = [values.text() for values in self.x_inputs]
        y_values = [values.text() for values in self.y_inputs]

        x_floats = []
        y_floats = []
        for x in x_values:
            if x_values == "":
                pass
            try:
                x_floats.append(float(x))
            except ValueError:
                QMessageBox.warning(self, "Value Error", "Input numbers only")
                break

        for y in y_values:
            if y_values == "":
                pass
            try:
                y_floats.append(float(y))
            except ValueError:
                QMessageBox.warning(self, "Value Error", "Input numbers only")
                break

        self.calibrate(x_floats, y_floats)

    def calibrate(self, x_values, y_values):
        calib_class = misc.CurverFitter(x_values, y_values)
        test_values = calib_class.is_perfectly_linear()
        if test_values:
            self.equation.setText(f"{test_values}")

        else:
            r2, equation = calib_class.fit_best_model()

            equation = calib_class.get_equation()
            self.equation = equation
            self.equation.setText(f"{equation} -- R2:{r2:.2f}")


class CalibrationEditor(QWidget):
    def __init__(self, home_page_instance):
        super().__init__()
        self.setWindowTitle("Calibration Equation Editor")
        self.resize(400, 400)

        self.home_page = home_page_instance
        self.json_file = None

        layout = QVBoxLayout()

        self.openbutton = QPushButton("Open File")
        self.openbutton.clicked.connect(self.open_file)
        layout.addWidget(self.openbutton)


        self.json_edit = QTextEdit()
        layout.addWidget(self.json_edit)

        self.save = QPushButton("Save File")
        self.save.clicked.connect(self.save_file)
        layout.addWidget(self.save)

        self.setLayout(layout)




    def open_file(self):
        file_diag = QFileDialog()
        file_path, _ = file_diag.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")

        if file_path:
            try:
                with open(file_path, 'r') as file:
                    json_data = json.load(file)

                formatted_json = json.dumps(json_data, indent=4)
                self.json_edit.setText(formatted_json)
                self.json_file = file_path

            except json.JSONDecodeError:
                QMessageBox.critical(self, "Error", "Invalid JSON format. Please check your file.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open JSON file: \n{e}")


    def save_file(self):
        if not self.json_file:
            QMessageBox.warning(self, "No File", "Please open a JSON file first")
            return

        try:
            json_data = json.loads(self.json_edit.toPlainText())

            with open(self.json_file, 'w') as file:
                json.dump(json_data, file, indent=4)

            QMessageBox.information(self, "Success", "File saved successfully")
            misc.event_logger("Calibration Equation Updated", misc.get_name(self.home_page))
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Error", "Invalid JSON format")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")


class CalibrationProcessor:

    def __init__(self):
        self.json_file = file_handler.load_json("loggers/calibration.json")


    def compute(self, name, xvalue):
        # Get correct equation based on sensor name
        equation = self.json_file[name]
        if not equation:
            misc.event_logger("ERROR", "SYSTEM", f"Compute-Calibration equation not found for: {name}")

        # Formats json properly
        equation = equation.replace("^", "**")

        try:
            # Evaluate equation
            y = eval(equation, {"x": int(xvalue)})
            return y

        except Exception as e:
            misc.event_logger("ERROR", "SYSTEM", f" Compute-Error applying calibration: {e}")



