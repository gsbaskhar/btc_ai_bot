import MetaTrader5 as mt5

import pandas as pd

from config import *

# ============ CONVERT DATAFRAME ============

def convert_dataframe(rates):

    df = pd.DataFrame(rates)

    df['time'] = pd.to_datetime(

        df['time'],

        unit='s'
    )

    return df

# =============== CLEAN DATA ==============

def clean_data(df):

    # ========= REMOVE DUPLICATES ==========

    df = df.drop_duplicates()

    # ======== SORT BY TIME ============

    df = df.sort_values(

        by='time'
    )

    # ========== RESET INDEX ==========

    df = df.reset_index(

        drop=True
    )

    # ========= REMOVE NaN ==========

    df = df.dropna()

    return df

# ============ GET CANDLES ================

def get_candles(bars=500):

    rates = mt5.copy_rates_from_pos(

        SYMBOL,

        TIMEFRAME,

        0,

        bars
    )

    # ========== VALIDATION ============

    if rates is None:

        print("NO DATA RECEIVED")

        return None

    if len(rates) == 0:

        print("EMPTY DATA")

        return None

    # ======== CONVERT =====

    df = convert_dataframe(

        rates
    )

    # ========= CLEAN =========

    df = clean_data(df)

    # ========= FINAL CHECK ==========

    if len(df) < 50:

        print("NOT ENOUGH CANDLES")

        return None

    return df