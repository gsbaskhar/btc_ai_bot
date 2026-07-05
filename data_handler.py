import pandas as pd

from binance_connector import client

from config import *


def get_candles(limit=500):

    klines = client.futures_klines(

        symbol=SYMBOL,

        interval=INTERVAL,

        limit=limit
    )

    df = pd.DataFrame(

        klines,

        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_asset_volume",
            "number_of_trades",
            "taker_buy_base",
            "taker_buy_quote",
            "ignore"
        ]
    )

    df = df[[
        "open_time",
        "open",
        "high",
        "low",
        "close",
        "volume"
    ]]

    df.rename(
        columns={
            "open_time": "time"
        },
        inplace=True
    )

    df["time"] = pd.to_datetime(
        df["time"],
        unit="ms"
    )

    numeric = [

        "open",
        "high",
        "low",
        "close",
        "volume"

    ]

    df[numeric] = df[numeric].astype(float)

    return df


def clean_data(df):

    df.dropna(inplace=True)

    df.reset_index(

        drop=True,

        inplace=True

    )

    return df