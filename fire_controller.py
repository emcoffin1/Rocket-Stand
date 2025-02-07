from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QLineEdit, QFrame, QFormLayout, QSplitter)

import misc
import table_controlller


class FireController(QWidget):
    def __init__(self):
        super().__init__()

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





    def layout_left(self):
        """Used for values"""
        # Init widget and layout
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_form = QFormLayout()

        # Add rows of controls
        left_form.addRow(misc.label_maker("Test", size=12), QPushButton("test"))

        # Format layout
        left_layout.addLayout(left_form)
        left_layout.addStretch(1)
        left_widget.setLayout(left_layout)
        return left_widget


    def layout_right(self):
        """Used for controls"""
        # Init widget and layout
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        # Table List
        tableL = table_controlller.Table(["LOX Vent", "Fuel Vent", "LOX Dome Vent",
                                          "LOX Dome Reg", "Fuel Dome Vent"])
        tableR = table_controlller.Table(["Fuel Dome Reg", "LOX MV", "FUEL MV",
                                          "High Pressure", "High Vent"])

        # Format right column tables
        right_layout.addWidget(tableL)
        right_layout.addWidget(tableR)
        right_widget.setLayout(right_layout)
        return right_widget

    def layout_bottom(self):
        """Used to initiate fire sequence and maybe more
           (include a timer for the countdown)"""
        # Init layout and widget
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)

        # Add items
        fire_button = QPushButton("FIRE")

        # Format layout
        bottom_layout.addWidget(fire_button)
        bottom_widget.setLayout(bottom_layout)
        return bottom_widget

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
