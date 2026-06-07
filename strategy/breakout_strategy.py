from config import *

# ==========================================
# BREAKOUT SIGNAL
# ==========================================

def get_breakout_signal(df, trend):

    last = df.iloc[-1]
    prev = df.iloc[-2]

    body = abs(last.close - last.open)

    avg_range = (
        (df["high"] - df["low"])
        .iloc[-10:]
        .mean()
    )

    strong_candle = body > avg_range * 0.05

    # BREAKOUT

    bullish_breakout = (
        last.high > prev.high
    )

    bearish_breakout = (
        last.low < prev.low
    )

    # DEBUG

    print(f"Close      : {last.close}")
    print(f"Prev High  : {prev.high}")
    print(f"Prev Low   : {prev.low}")
    print(f"EMA50      : {last.ema50}")
    print(f"RSI        : {last.rsi}")
    print(f"Body       : {body}")
    print(f"Avg Range  : {avg_range}")
    print(f"Strong     : {strong_candle}")
    print(f"Bull BO    : {bullish_breakout}")
    print(f"Bear BO    : {bearish_breakout}")

    # buy_signal = (
    #     trend == "BULLISH"
    #     and last.close > last.ema50
    #     and bullish_breakout
    #     and last.rsi > 50
    #     and strong_candle
    # )

    # sell_signal = (
    #     trend == "BEARISH"
    #     and last.close < last.ema50
    #     and bearish_breakout
    #     and last.rsi < 50
    #     and strong_candle
    # )

    buy_signal = (
    trend == "BULLISH"
    and last.close > last.ema50
    and last.rsi > 50
    )

    sell_signal = (
    trend == "BEARISH"
    and last.close < last.ema50
    and last.rsi < 50
    )

    if buy_signal:
        print("BUY CONDITIONS MET")
        return "BUY"

    if sell_signal:
        print("SELL CONDITIONS MET")
        return "SELL"

    print("NO SIGNAL CONDITIONS MET")

    return None