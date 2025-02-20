import box_overlay_example
import misc
from wifi import ESP32Client


class ClickTest_logic:
    """Performs the backend for Click Test"""
    def __init__(self, esp_client, config: dict, tables, label, colorMap):
        super().__init__()
        # Pass through: esp, tables to be updated, valves for test
        #self.esp_client = box_overlay_example.MockESP32Client()
        self.esp_client = esp_client
        self.config = config
        self.tables = tables
        self.valves = self.config["VALVES"]
        self.label = label
        self.colorMap = colorMap
        self.iterations = 0

        # Listen for response
        self.esp_client.test_active.connect(self.handle_response)

        # Better list
        self.command_que = iter(self.valves)
        self.current_valve = None

        # State of sensor test
        self.state = {}
        for x in self.valves:
            self.state[x] = 0

    def reset_test(self):
        """Resets test to original values"""
        for x in self.valves:
            self.state[x] = 0
        self.tables.update_states(states=self.state, colorMap=self.colorMap)

    def start_test(self):
        """When initialized, test begins"""
        try:
            self.process_next()

        except Exception as e:
            misc.event_logger("DEBUG", "ClickTest", f'startTest: {e}')


    def process_next(self):
        """Processes next valve when trigger received"""
        #print("moving on")
        try:
            self.current_valve = next(self.command_que)
            self.label.setText(self.current_valve)
            self.esp_client.send_command(message=self.current_valve, test=True)

        except StopIteration:
            self.label.setText("Complete")
            self.command_que = iter(self.valves)





    def handle_response(self, valve_data):
        """Handles response from arduino"""
        #print(valve_data)
        # determine if test was performed
        if "TEST" in valve_data:
            # Test was successful
            if valve_data["TEST"] == 1:
                self.state[self.current_valve] += 1
                self.tables.update_states(states=self.state)

            # Test unsuccessful
            else:
                misc.event_logger("ERROR", "Click Check", f"{self.current_valve.title()} either not found or faulty")

            self.process_next()
