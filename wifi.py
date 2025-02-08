import socket
import threading
import json
from PyQt6.QtCore import QObject, pyqtSignal

import controllers
import misc

ESP_IP = "192.168.4.1"  # ESP32 AP IP
PORT = 80

class ESP32Client(QObject):
    """Handles ESP32 connection, listening, and sending commands."""
    message_received = pyqtSignal(dict)  # Signal to update GUI when a new message is received
    connection_status = pyqtSignal(bool)  # Signal to update connection status in GUI


    def __init__(self):
        super().__init__()
        self.client = None
        self.running = True
        self.listener_thread = None
        self.calibrator = controllers.CalibrationProcessor("Loggers/calibration.json")


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
                    misc.event_logger("WiFi Connected", "SYSTEM")

                    if not hasattr(self, "listener_thread"):
                        self.listener_thread = threading.Thread(target=self.listen_for_responses, daemon=True)
                        self.listener_thread.start()
                except Exception as e:
                    misc.event_logger("WiFi Connection Failed", "SYSTEM")
            else:
                pass
        else:
            self.connection_status.emit(False)

    def listen_for_responses(self):
        """Continuously listen for messages from ESP32 and update GUI."""
        calibration_file = "Loggers/calibration.json"
        try:
            with open(calibration_file, 'r') as file:
                calibration_data = json.load(file)

        except Exception as e:
            misc.event_logger("ERROR", "SYSTEM", f"Failed to load calibration file: {e}")
            calibration_data = {}


        while self.running:
            if self.client:
                try:
                    response = self.client.recv(1024).decode()
                    print(response)
                    if response:
                        try:
                            raw_data = json.loads(response)
                            #print(f"Received input: {raw_data}")
                            #misc.event_logger("DEBUG", "SYSTEM", f"Raw sensor data: {raw_data}")

                            calibrated_data = {}
                            for sensor, value in raw_data.items():
                                if sensor in calibration_data:
                                    equation = calibration_data[sensor]
                                    try:
                                        # Pass through correct calibration equation
                                        calib_value, _ = self.calibrator.compute(sensor, value)
                                        calibrated_data[sensor] = eval(equation, {'x': round(calib_value,2)})
                                    except Exception as e:
                                        misc.event_logger("ERROR", "SYSTEM", f"Calibration failed for {sensor}: {e}")
                                        calibrated_data[sensor] = value
                                else:
                                    calibration_data[sensor] = value

                            #misc.event_logger("DEBUG", "SYSTEM", f"Calibrated Data: {calibrated_data}")
                            # Emits structured, calibrated data to update table
                            self.message_received.emit(calibrated_data)

                        except json.JSONDecodeError as e:
                            misc.event_logger("WARNING", "SYSTEM", f"Recieved malformed data: {e}")


                except Exception as e:
                    misc.event_logger("ERROR", "SYSTEM", f"Connection Lost: {e}")
                    self.connection_status.emit(False)
                    self.client = None
                    break  # Stop listening if connection is lost

    def send_command(self, message):
        """Send command to ESP32."""
        if self.client:
            try:
                self.client.sendall(message.encode() + b'\n')
            except Exception as e:
                misc.event_logger("ERROR", "SYSTEM", f"Sending command failed: {e}")

    def stop(self):
        """Close connection when exiting."""
        self.running = False
        if self.client:
            self.client.close()
            self.client = None
