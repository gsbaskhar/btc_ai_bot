from config import *


def get_breakout_signal(df, trend):

    last = df.iloc[-1]

    prev = df.iloc[-2]

    body = abs(

        last["close"]

        - last["open"]

    )

    avg_body = (

        abs(

            df["close"]

            -

            df["open"]

        )

        .tail(20)

        .mean()

    )

    strong_candle = (

        body >=

        avg_body * 0.60

    )

    bullish_breakout = (

        last["close"]

        >

        prev["high"]

    )

    bearish_breakout = (

        last["close"]

        <

        prev["low"]

    )

    volume_ok = (

        last["volume_ratio"] >= 1.20

    )

    macd_buy = (

        last["macd"]

        >

        last["macd_signal"]

    )

    macd_sell = (

        last["macd"]

        <

        last["macd_signal"]

    )

    buy = (

        trend == "BULLISH"

        and bullish_breakout

        and strong_candle

        and volume_ok

        and macd_buy

        and last["bullish_ob"]

    )

    sell = (

        trend == "BEARISH"

        and bearish_breakout

        and strong_candle

        and volume_ok

        and macd_sell

        and last["bearish_ob"]

    )

    print("=" * 60)

    print(f"Trend          : {trend}")

    print(f"Close          : {last['close']}")

    print(f"EMA50          : {last['ema50']}")

    print(f"EMA200         : {last['ema200']}")

    print(f"RSI            : {last['rsi']:.2f}")

    print(f"MACD           : {last['macd']:.2f}")

    print(f"MACD SIGNAL    : {last['macd_signal']:.2f}")

    print(f"Volume Ratio   : {last['volume_ratio']:.2f}")

    print(f"Bullish OB     : {last['bullish_ob']}")

    print(f"Bearish OB     : {last['bearish_ob']}")

    print(f"Strong Candle  : {strong_candle}")

    print(f"Bull Breakout  : {bullish_breakout}")

    print(f"Bear Breakout  : {bearish_breakout}")

    print("=" * 60)

    if buy:

        print("BUY SIGNAL")

        return "BUY"

    if sell:

        print("SELL SIGNAL")

        return "SELL"

    return None