import random
import time
from PyQt6.QtCore import QObject, pyqtSignal, QTimer


class MockESP32Client(QObject):
    """Simulates an ESP32 client for testing purposes."""
    confirmed_check = pyqtSignal(dict)  # Mimics ESP32 response signal

    def __init__(self):
        super().__init__()

    def send_command(self, message, test=False):
        """Mimics sending a command and receiving a response asynchronously."""
        #print(f"Sent command: {message}")

        if test:
            # Simulate a network delay using QTimer
            QTimer.singleShot(50, self.mock_response)  # 1 second delay

    def mock_response(self):
        """Generate a mock response with TEST = 0 or 1."""
        response = {"TEST": 1}  # Randomly pick 0 or 1
        #print(f"Received response: {response}")
        self.confirmed_check.emit(response)  # Emit the signal with response
