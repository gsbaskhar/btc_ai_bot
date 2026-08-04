import pandas as pd
import MetaTrader5 as mt5


def get_htf_trend(symbol):
    # Exclude the still-forming H1 bar for the same reason as the M5 signal.
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 1, 300)
    if rates is None or len(rates) < 200:
        raise RuntimeError("Insufficient H1 candles")
    close = pd.DataFrame(rates)["close"]
    return "BULLISH" if close.ewm(span=50, adjust=False).mean().iloc[-1] > close.ewm(span=200, adjust=False).mean().iloc[-1] else "BEARISH"
