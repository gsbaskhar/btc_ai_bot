# ============ LIQUIDITY SWEEP DETECTION =========

def detect_liquidity_sweep(df):

    last = df.iloc[-1]

    # ============ BODY =============

    body = abs(

        last.close - last.open
    )

    # =========== WICKS =============

    upper_wick = (

        last.high
        -
        max(last.open, last.close)
    )

    lower_wick = (

        min(last.open, last.close)
        -
        last.low
    )

    # =========== SELL SIDE SWEEP ===========

    if lower_wick > body * 2:

        return "BUY_SWEEP"

    # ========== BUY SIDE SWEEP ==========

    if upper_wick > body * 2:

        return "SELL_SWEEP"

    return None