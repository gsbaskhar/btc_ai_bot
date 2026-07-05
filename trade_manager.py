from binance_connector import client

from config import *

def open_buy(qty):

    return client.futures_create_order(

        symbol=SYMBOL,

        side="BUY",

        type="MARKET",

        quantity=qty
    )

def open_sell(qty):

    return client.futures_create_order(

        symbol=SYMBOL,

        side="SELL",

        type="MARKET",

        quantity=qty
    )

def close_position(side, qty):

    opposite = (

        "SELL"

        if side == "BUY"

        else "BUY"
    )

    return client.futures_create_order(

        symbol=SYMBOL,

        side=opposite,

        type="MARKET",

        quantity=qty
    )