import os
from datetime import datetime

INSTALL_DATE_FILE = os.path.join(os.path.dirname(__file__), ".install_date")

def get_install_date():
    if os.path.exists(INSTALL_DATE_FILE):
        with open(INSTALL_DATE_FILE, "r") as f:
            return f.read().strip()
    else:
        today = datetime.today().strftime("%Y-%m-%d")
        with open(INSTALL_DATE_FILE, "w") as f:
            f.write(today)
        return today
