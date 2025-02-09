import csv, json, os, sys

import misc

def load_config(config_file):
    try:
        config = load_json(config_file)
        return config
    except Exception as e:
        misc.event_logger("DEBUG", "SYSTEM", f"load_config: {e}")

def get_data_path(filename):
    """Get the correct path for reading/writing data files"""
    try:
        if getattr(sys, 'frozen', False): # Running as exe
            base_path = os.path.dirname(sys.executable)

        else:
            base_path = os.path.dirname(__file__)

        data_folder = os.path.join(base_path, "data")
        os.makedirs(data_folder, exist_ok=True) # Ensure folder exists
        return os.path.join(data_folder, filename)
    except Exception as e:
        misc.event_logger("ERROR", "SYSTEM", f"get_data_path: {e}")


def load_json(filename):
    """Load JSON data from file"""
    try:
        path = get_data_path(filename)

        if not path or not os.path.exists(path):
            print("error")
            #misc.event_logger("WARNING", "SYSTEM", f"Config file: {filename} not found")
            return {}

        with open(path, 'r', encoding="utf-8") as file:

            return json.load(file)
    except Exception as e:
        misc.event_logger("DEBUG", "SYSTEM", f"load_json: {e}")
        return {}


def save_json(filename,data):
    """Save JSON data to file"""
    path = get_data_path(filename)
    with open(path, 'w', encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def load_csv(filename):
    """Load CSV data from file"""
    path = get_data_path(filename)
    if not os.path.exists(path):
        return []
    with open(path, 'r', newline="", encoding="utf-8") as file:
        reader = csv.reader(file)
        return list(reader)

def save_csv(filename,data):
    """Append a row to a CSV file"""
    path = get_data_path(filename)
    with open(path, 'a', newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)

