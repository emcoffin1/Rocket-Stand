import socket
import threading
import json
from PyQt6.QtCore import QObject, pyqtSignal
import controllers
import file_handler
import misc


class ESP32Client(QObject):
    """Handles ESP32 connection, listening, and sending commands."""
    message_received = pyqtSignal(dict)  # Signal to update GUI when a new message is received
    connection_status = pyqtSignal(bool)  # Signal to update connection status in GUI
    test_active = pyqtSignal(bool)
    arm_stand = pyqtSignal(bool)

    def __init__(self, ip, port):
        super().__init__()
        self.client = None
        self.running = True
        self.listener_thread = None
        self.calibrator = controllers.CalibrationProcessor()
        self.ip = ip
        self.port = port

    def is_esp32_connected(self):
        """Check if ESP32 is reachable before attempting connection."""

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((self.ip, self.port))
            sock.close()
            return True
        except (socket.timeout, socket.error):
            return False

    def connect_to_esp32(self):
        """Establish connection to ESP32."""
        self.stop()

        if self.is_esp32_connected():
            if self.client is None:
                try:
                    self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.client.connect((self.ip, self.port))
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
        formulas = file_handler.load_json("Loggers/calibration.json").keys()


        while self.running:
            if not self.client:
                break

            try:
                response = self.client.recv(1024).decode()

                if response:

                    try:

                        raw_data = dict(json.loads(response))

                        # check if there is test in the data
                        if "TEST" in raw_data.keys():
                            # Get test info (should be a dict)
                            valve_data = raw_data["TEST"]
                            # Emit test type, valve
                            self.test_active.emit(raw_data["TEST"][1], raw_data["TEST"][2])
                            continue

                        if raw_data["ARM"] == True:
                            # Check if pad is armed
                            armed = True
                            self.arm_stand.emit(armed)


                        # Store the new calibrated data being created for emitting
                        calibrated_data = {}

                        for sensor, value in raw_data.items():
                            if sensor in formulas:

                                try:
                                    # Pass through correct calibration equation
                                    calib_val = self.calibrator.compute(name=sensor, xvalue=value)
                                    # Add it to list
                                    calibrated_data[sensor] = calib_val
                                except Exception as e:
                                    misc.event_logger("ERROR", "SYSTEM", f"listen - Calibration failed for {sensor}:{e}")
                                    calibrated_data[sensor] = value
                            else:
                                calibrated_data[sensor] = value

                        # Emits structured, calibrated data to update table
                        self.message_received.emit(calibrated_data)

                    except json.JSONDecodeError as e:
                        misc.event_logger("WARNING", "SYSTEM", f"Recieved malformed data: {e}")


            except Exception as e:
                misc.event_logger("ERROR", "SYSTEM", f"Connection Lost: {e}")
                self.connection_status.emit(False)
                self.client = None
                break  # Stop listening if connection is lost

    def send_command(self, message, test=False):
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
            try:
                self.client.shutdown(socket.SHUT_RDWR)
                self.client.close()
            except Exception as e:
                misc.event_logger("WARNING", "SYSTEM", f'WiFi Stop: {e}')

            self.client = None
            self.connection_status.emit(False)

        if self.listener_thread:
            self.listener_thread.join(timeout=2)
            self.listener_thread = None