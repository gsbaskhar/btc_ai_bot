from config import *

# =========== TREND DETECTION =============

def get_trend(df):

    last = df.iloc[-1]

    # =========== BULLISH ============

    bullish = (

        last.close > last.ema200

        and

        last.ema50 > last.ema200

        and

        last.rsi > 50
    )

    # =========== BEARISH ============

    bearish = (

        last.close < last.ema200

        and

        last.ema50 < last.ema200

        and

        last.rsi < 50
    )

    # =========== RETURN ============

    if bullish:

        return "BULLISH"

    if bearish:

        return "BEARISH"

    return "SIDEWAYS"