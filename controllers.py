import json
import misc
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton,
                             QTextEdit, QFileDialog, QMessageBox, QHBoxLayout, QLineEdit)



class CalibrationMaker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibrator")
        self.resize(400,400)

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
        self.equation = misc.label_maker("")

        # Submit
        self.submit = QPushButton("Submit")

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
        over_lay.addWidget(self.equation)
        over_lay.addStretch(1)
        over_lay.addWidget(self.submit)

        self.setLayout(over_lay)





    def retrieve_inputs(self):
        x_values = [values.text() for values in self.x_inputs]
        y_values = [values.text() for values in self.y_inputs]

        x_floats = []
        y_floats = []
        for x in x_values:
            try:
                x_floats.append(float(x))
            except ValueError:
                QMessageBox.warning(self, "Value Error", "Input numbers only")

        for y in y_values:
            try:
                y_floats.append(float(y))
            except ValueError:
                QMessageBox.warning(self, "Value Error", "Input numbers only")
        return x_floats, y_floats



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

    def __init__(self, json_file="Loggers/calibration.json"):
        self.json_file = json_file
        self.equations = self.load_equations()

    def load_equations(self):
        try:
            with open(self.json_file, "r") as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def compute(self, name, xvalue):

        equation = self.equations.get(name)
        if not equation:
            misc.event_logger("ERROR", "SYSTEM", f"Calibration equation not found for: {name}")

        # Formats json properly
        equation = equation.replace("^", "**")

        try:
            y = eval(equation, {"x": xvalue})
            return y, None

        except Exception as e:
            misc.event_logger("ERROR", "SYSTEM", f"Error applying calibration: {e}")



