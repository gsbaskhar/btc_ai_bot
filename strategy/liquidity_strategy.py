def detect_liquidity_sweep(df):

    last = df.iloc[-1]

    if last["buy_liquidity"]:

        print("BUY SIDE LIQUIDITY TAKEN")

        return "BUY"

    if last["sell_liquidity"]:

        print("SELL SIDE LIQUIDITY TAKEN")

        return "SELL"

    return None
    