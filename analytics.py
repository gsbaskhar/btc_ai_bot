from config import *

def calculate_qty(price):

    qty = (

        USDT_PER_TRADE

        * LEVERAGE

    ) / price

    return round(
        qty,
        3
    )