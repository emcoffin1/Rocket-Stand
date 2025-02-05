from datetime import datetime
import pandas as pd
from os import path


def event_logger(event, user, comments=''):
    # Format username to a specific size
    if len(user) < 10:
        user = f"{user}" + " " * (10 - len(user))
    else:
        user = user[0:10]

    # Access file
    log_file = f'Loggers/event_log_{datetime.now().strftime("%Y-%m-%d")}.csv'

    # Format new entry
    new_entry = pd.DataFrame({
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "User": [f"    {user}"],
        "Event": [f"    {event}"],
        "Comments": [f"    {comments}"]
    })

    if path.exists(log_file):
        existing_data = pd.read_csv(log_file)
        updated_data = pd.concat([existing_data, new_entry], ignore_index=True)
    else:
        updated_data = new_entry
    updated_data.to_csv(log_file, index=False)

def get_name(home_page_instance):
    # Access the QLineEdit text from HomePage
    name = home_page_instance.line_edit.text()
    return name