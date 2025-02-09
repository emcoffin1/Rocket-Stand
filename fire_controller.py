from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QLineEdit, QFrame, QFormLayout, QSplitter)
from PyQt6.QtGui import QFont
import misc, table_controlller


class FireController(QWidget):
    launch_countdown = pyqtSignal(bool)
    def __init__(self, esp_client):
        super().__init__()
        # ESP Client
        self.esp_client = esp_client

        # Main Layout
        top_bottom_splitter = QSplitter(Qt.Orientation.Vertical)

        # Left Section : Control Panel
        left_widget = self.layout_left()

        # Right Section: Tables
        right_widget = self.layout_right()

        # Bottom section: Fire Control
        bottom_widget = self.layout_bottom()

        # Add left and right to main splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        main_splitter.addWidget(left_widget)
        main_splitter.addWidget(right_widget)

        # Force Equal Width
        main_splitter.setSizes([300,300])



        # Add top and bottom to splitter
        top_bottom_splitter.addWidget(main_splitter)
        top_bottom_splitter.addWidget(bottom_widget)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(misc.label_maker("Fire Control"), alignment=Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(misc.horizontal_line())
        main_layout.addWidget(top_bottom_splitter)
        self.setLayout(main_layout)

        self.esp_client.message_received.connect(self.update_tables)

    def update_tables(self, calibrated_data):
        """Updates data as it comes in"""
        try:
            self.tableL.update_table(calibrated_data)
            self.tableR.update_table(calibrated_data)
            self.controller_table.update_states(calibrated_data)
        except Exception as e:
            misc.event_logger("DEBUG", "SYSTEM", f"Update Tables:{e}")

    def layout_left(self):
        """Used for values"""
        # Init widget and layout
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_form = QFormLayout()

        # Add controller panel
        self.controller_table = table_controlller.Controller_Spread(["High Press", "High Vent", "LOX Dome Reg",
                                                                "LOX Dome Vent", "Fuel Dome Reg", "Fuel Dome Vent",
                                                                "LOX Vent", "Fuel Vent", "LOX Main Valve",
                                                                "Fuel Main Valve"])

        # Format layout
        left_layout.addLayout(left_form)
        left_layout.addLayout(self.controller_table)
        left_layout.addStretch(1)
        left_widget.setLayout(left_layout)
        return left_widget


    def layout_right(self):
        """Used for controls"""
        # Init widget and layout
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Table List
        self.tableL = table_controlller.Table(["High Press 1", "High Press 2", "LOX Tank 1",
                                          "LOX Tank 2", "Fuel Tank 1", "Fuel Tank 2"])
        self.tableR = table_controlller.Table(["LOX Dome Reg S", "Fuel Dome Reg S", "LOX Inlet",
                                          "Fuel Inlet", "Chamber 1", "Chamber 2"])

        # Format right column tables
        right_layout.addWidget(self.tableL)
        right_layout.addWidget(self.tableR)
        right_widget.setLayout(right_layout)
        return right_widget

    def layout_bottom(self):
        """Used to initiate fire sequence and maybe more
           (include a timer for the countdown)"""
        # Init layout and widget
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)

        # Add items
        self.fire_button = QPushButton("FIRE")
        self.fire_button.setStyleSheet("background-color: red")
        self.fire_button.setFont(QFont("Arial", 20, QFont.Weight.DemiBold))
        self.fire_button.setMinimumSize(50,50)
        self.test = misc.countTimer("down", 5)
        self.fire_button.clicked.connect(self.count_down)

        # Format layout
        bottom_layout.addWidget(self.fire_button)
        bottom_layout.addWidget(self.test)
        bottom_widget.setLayout(bottom_layout)
        return bottom_widget

    def count_down(self):
        """Initiates launch countdown"""
        self.test.start_timer()
        self.fire_button.setText("ABORT")
        self.fire_button.setStyleSheet("background-color: orange")
        self.fire_button.clicked.connect(self.stop_countdown)

    def stop_countdown(self):
        """Stops countdown"""
        self.test.stop_timer()
        self.fire_button.setText("FIRE")
        self.fire_button.setStyleSheet("background-color: red")
        self.fire_button.clicked.connect(self.count_down)


class FireLogin(QWidget):
    login_successful = pyqtSignal()
    def __init__(self):
        super().__init__()

        # Frame
        self.mainlayout = QVBoxLayout()
        self.frame = QFrame(self)
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setStyleSheet("border: 0.25px solid black")

        # Layout for Login Box
        login_layout = QVBoxLayout()

        # Form Layout
        form = QFormLayout()

        # Form objects
        notice = misc.label_maker("Please LOGIN", size=15)

        user = misc.label_maker("USERNAME:", size=12)
        self.user_in = QLineEdit()
        self.user_line = form.addRow(user, self.user_in)
        self.user_in.setStyleSheet("border: 1px solid black;")

        passw = misc.label_maker("PASSWORD:", size=12)
        self.pass_in = QLineEdit()
        self.pass_line = form.addRow(passw, self.pass_in)
        self.pass_in.setStyleSheet("border: 1px solid black;")
        self.pass_in.setEchoMode(QLineEdit.EchoMode.Password)

        # Submit button
        submit = QPushButton("Submit")
        submit.clicked.connect(self.connect_user)
        submit.setMaximumWidth(100)
        submit.setStyleSheet("Border: 0.5px solid black")

        # Layout maker
        login_layout.addWidget(notice, alignment=Qt.AlignmentFlag.AlignCenter)
        login_layout.addLayout(form)
        self.frame.setLayout(login_layout)

        self.mainlayout.addStretch(1)
        self.mainlayout.addWidget(self.frame, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainlayout.addWidget(submit, alignment=Qt.AlignmentFlag.AlignCenter)
        self.mainlayout.addStretch(1)

        self.setLayout(self.mainlayout)

    def connect_user(self):
        """Send info for verification and launch fire system"""
        user = self.user_in.text()
        password = self.pass_in.text()
        valid = misc.check_user(user, password)
        valid = True
        if valid:

            self.user_in.setText("")
            self.pass_in.setText("")
            self.login_successful.emit()
            misc.event_logger("LOGIN", user.upper(), "Fire Control Login")
        else:
            self.user_in.setText("")
            self.pass_in.setText("")
            # misc.event_logger("SECURITY", "SYSTEM", f"{user} failed to login")



