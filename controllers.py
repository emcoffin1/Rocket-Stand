import json
import misc
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTextEdit, QFileDialog, QMessageBox)



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



