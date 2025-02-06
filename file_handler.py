import csv, json, os, sys

def get_data_path(filename):
    """Get the correct path for reading/writing data files"""
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)

    else:
        base_path = os.path.dirname(__file__)

    data_folder = os.path.join(base_path, "data")
    os.makedirs(data_folder, filename)

    return os.path.join(data_folder, filename)


def load_json(filename):
    """Load JSON data from file"""
    path = get_data_path(filename)
    if not os.path.exists(path):
        return {}

    with open(path, 'r', encoding="utf-8") as file:
        return json.load(file)

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
