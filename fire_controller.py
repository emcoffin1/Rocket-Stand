from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QLineEdit, QFrame, QFormLayout)

import misc


class FireController(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        label = misc.label_maker("Fire Control")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        layout.addWidget(misc.horizontal_line())
        layout.addStretch(1)

        self.setLayout(layout)

    def on_tab_changed(self, index):
        """Detect when tab changes and log out"""


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
        self.user_in.setStyleSheet("Border: 0.25px solid black")

        passw = misc.label_maker("PASSWORD:", size=12)
        self.pass_in = QLineEdit()
        self.pass_line = form.addRow(passw, self.pass_in)
        self.pass_in.setStyleSheet("Border: 0.25px solid black")

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
