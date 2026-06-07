import MetaTrader5 as mt5

import pandas as pd

# =============== HTF TREND ================

def get_htf_trend(symbol):

    rates = mt5.copy_rates_from_pos(

        symbol,

        mt5.TIMEFRAME_H1,

        0,

        300
    )

    df = pd.DataFrame(rates)

    close = df['close']

    ema50 = (

        close
        .ewm(span=50)
        .mean()
    )

    ema200 = (

        close
        .ewm(span=200)
        .mean()
    )

    if ema50.iloc[-1] > ema200.iloc[-1]:

        return "BULLISH"

    return "BEARISH"