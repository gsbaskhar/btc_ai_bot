import csv
import os

# =========== LOG FILE ============

LOG_FILE = "logs/trades.csv"

# ========== INITIALIZE LOG ==============

def initialize_log():

    if os.path.exists(LOG_FILE):

        return

    with open(

        LOG_FILE,

        'w',

        newline=''
    ) as file:

        writer = csv.writer(file)

        writer.writerow([

            'time',

            'direction',

            'entry',

            'sl',

            'tp',

            'profit'
        ])

# ============ LOG TRADE =============

def log_trade(data):

    with open(

        LOG_FILE,

        'a',

        newline=''
    ) as file:

        writer = csv.writer(file)

        writer.writerow(data)