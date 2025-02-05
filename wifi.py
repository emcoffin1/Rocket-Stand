import platform
import socket
import threading
import subprocess
from PyQt6.QtCore import QObject, pyqtSignal

ESP_IP = "192.168.4.1"  # ESP32 AP IP
PORT = 80

class ESP32Client(QObject):
    """Handles ESP32 connection, listening, and sending commands."""
    message_received = pyqtSignal(str)  # Signal to update GUI when a new message is received
    connection_status = pyqtSignal(bool)  # Signal to update connection status in GUI


    def __init__(self):
        super().__init__()
        self.client = None
        self.running = True
        self.listener_thread = None


    def is_esp32_connected(self):
        """Check if ESP32 is reachable before attempting connection."""

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((ESP_IP, PORT))
            sock.close()
            return True
        except (socket.timeout, socket.error):
            return False

    def connect_to_esp32(self):
        """Establish connection to ESP32."""
        if self.is_esp32_connected():
            if self.client is None:
                try:
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client.connect((ESP_IP, PORT))
                    self.connection_status.emit(True)

                    if not hasattr(self, "listener_thread"):
                        self.listener_thread = threading.Thread(target=self.listen_for_responses, daemon=True)
                        self.listener_thread.start()
                except Exception as e:
                    print(f"[ERROR] Connection Failed: {e}")
            else:
                print("[WARNING] ESP32 is already connected.")
        else:
            print("[WARNING] WiFi not available")
            self.connection_status.emit(False)

    def listen_for_responses(self):
        """Continuously listen for messages from ESP32 and update GUI."""
        while self.running:
            if self.client:
                try:
                    response = self.client.recv(1024).decode()
                    if response:
                        self.message_received.emit(response)  # Emit signal to update GUI
                except Exception as e:
                    print(f"[ERROR] Connection lost: {e}")
                    self.connection_status.emit(False)
                    self.client = None
                    break  # Stop listening if connection is lost

    def send_command(self, message):
        """Send command to ESP32."""
        if self.client:
            try:
                self.client.sendall(message.encode() + b'\n')
            except Exception as e:
                print("[Error] Sending command failed:", e)

    def stop(self):
        """Close connection when exiting."""
        self.running = False
        if self.client:
            self.client.close()
            self.client = None
