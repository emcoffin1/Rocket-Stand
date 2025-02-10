from wifi import ESP32Client


class ClickTest_logic:
    """Performs the backend for Click Test"""
    def __init__(self, esp_client, config: dict, tables: list):
        super().__init__()
        # Pass through: esp, tables to be updated, valves for test
        self.esp_client = esp_client
        self.config = config
        self.tables = tables
        self.valves = self.config["VALVES"]


    def start_test(self):
        """When initialized, test begins"""
        try:
            for x in self.valves:
                # Filter through each valve:
                # open valve, receive open, close valve, receive close
                # if both, confirm
                self.esp_client.send_command(message=f"{x.upper()}", test=True)
                pass


        except Exception as e:
            pass


